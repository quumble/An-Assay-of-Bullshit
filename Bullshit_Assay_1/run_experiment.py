"""
Model comparison experiment runner.

Runs a fixed set of creative-writing prompts against multiple Claude and
OpenAI models, N times each at temperature=1.0, no system prompt, max 400
output tokens. Results are streamed to a JSONL file so partial progress is
preserved on crash.

Setup:
    pip install anthropic openai tqdm
    export ANTHROPIC_API_KEY=...
    export OPENAI_API_KEY=...

Run:
    python run_experiment.py
    python run_experiment.py --runs-per-cell 10 --output results.jsonl
    python run_experiment.py --resume   # skips cells already in output file
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from anthropic import Anthropic
    from openai import OpenAI
    from tqdm import tqdm
except ImportError as e:
    sys.exit(f"Missing dependency: {e}. Run: pip install anthropic openai tqdm")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROMPTS = [
    ("story_lt5",   "create a short story in fewer than 5 sentences."),
    ("story_lt10",  "create a short story in fewer than 10 sentences."),
    ("story_open",  "create a short story."),
    ("animal_lt5",  "create an animal and describe it in fewer than 5 sentences."),
    ("animal_lt10", "create an animal and describe it in fewer than 10 sentences."),
    ("animal_open", "create an animal and describe it."),
    ("poem_lt5",    "create a poem in fewer then 5 lines."),
    ("poem_lt10",   "create a poem in fewer then 10 lines."),
    ("poem_open",   "create a poem."),
]

ANTHROPIC_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-7",
]

OPENAI_MODELS = [
    "gpt-5.4-nano",
    "gpt-5.4-mini",
    "gpt-5.4",
]

TEMPERATURE = 1.0
MAX_TOKENS = 400


# ---------------------------------------------------------------------------
# Record format
# ---------------------------------------------------------------------------

@dataclass
class Record:
    run_id: str
    timestamp: str
    provider: str
    model: str
    prompt_id: str
    prompt_text: str
    iteration: int          # 0-indexed iteration within (model, prompt) cell
    temperature: float
    max_tokens: int
    response: Optional[str]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    latency_ms: Optional[int]
    error: Optional[str]


# ---------------------------------------------------------------------------
# Provider call helpers
# ---------------------------------------------------------------------------

def call_anthropic(client: Anthropic, model: str, prompt: str) -> dict:
    t0 = time.perf_counter()
    msg = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    text = "".join(
        block.text for block in msg.content if getattr(block, "type", None) == "text"
    )
    return {
        "response": text,
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
        "latency_ms": latency_ms,
    }


def call_openai(client: OpenAI, model: str, prompt: str) -> dict:
    t0 = time.perf_counter()
    # Using the Responses API per current OpenAI guidance for GPT-5.x models.
    resp = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    # output_text is a convenience accessor that concatenates text content
    text = getattr(resp, "output_text", None) or ""
    usage = getattr(resp, "usage", None)
    return {
        "response": text,
        "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
        "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
        "latency_ms": latency_ms,
    }


def call_with_retry(fn, *args, retries: int = 3, backoff: float = 2.0):
    last_err = None
    for attempt in range(retries):
        try:
            return fn(*args)
        except Exception as e:  # noqa: BLE001 - we want broad retry behavior
            last_err = e
            if attempt < retries - 1:
                time.sleep(backoff ** attempt)
    raise last_err  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Resume support
# ---------------------------------------------------------------------------

def load_completed_cells(path: Path) -> set[tuple[str, str, int]]:
    """Return set of (model, prompt_id, iteration) already present in output."""
    completed: set[tuple[str, str, int]] = set()
    if not path.exists():
        return completed
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("error"):
                # Don't count errored runs as complete; we'll retry them.
                continue
            completed.add((rec["model"], rec["prompt_id"], rec["iteration"]))
    return completed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-per-cell", type=int, default=10,
                        help="Iterations per (model, prompt) cell. Default: 10")
    parser.add_argument("--output", type=Path, default=Path("results.jsonl"),
                        help="JSONL output path. Default: results.jsonl")
    parser.add_argument("--resume", action="store_true",
                        help="Skip (model, prompt, iteration) cells already in output.")
    parser.add_argument("--anthropic-only", action="store_true")
    parser.add_argument("--openai-only", action="store_true")
    args = parser.parse_args()

    if args.anthropic_only and args.openai_only:
        sys.exit("Cannot pass both --anthropic-only and --openai-only.")

    # Validate API keys early
    need_anthropic = not args.openai_only
    need_openai = not args.anthropic_only
    if need_anthropic and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set.")
    if need_openai and not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY not set.")

    anthropic_client = Anthropic() if need_anthropic else None
    openai_client = OpenAI() if need_openai else None

    # Build full task list
    tasks: list[tuple[str, str, str, str, int]] = []  # (provider, model, pid, ptext, iter)
    if need_anthropic:
        for model in ANTHROPIC_MODELS:
            for pid, ptext in PROMPTS:
                for i in range(args.runs_per_cell):
                    tasks.append(("anthropic", model, pid, ptext, i))
    if need_openai:
        for model in OPENAI_MODELS:
            for pid, ptext in PROMPTS:
                for i in range(args.runs_per_cell):
                    tasks.append(("openai", model, pid, ptext, i))

    completed = load_completed_cells(args.output) if args.resume else set()
    if completed:
        before = len(tasks)
        tasks = [t for t in tasks if (t[1], t[2], t[4]) not in completed]
        print(f"Resume: skipping {before - len(tasks)} already-completed runs.", file=sys.stderr)

    total = len(tasks)
    print(f"Total runs to perform: {total}", file=sys.stderr)
    print(f"Models: {ANTHROPIC_MODELS if need_anthropic else []} "
          f"+ {OPENAI_MODELS if need_openai else []}", file=sys.stderr)
    print(f"Prompts: {len(PROMPTS)} | Runs/cell: {args.runs_per_cell} | "
          f"Temp: {TEMPERATURE} | Max tokens: {MAX_TOKENS}", file=sys.stderr)
    print(f"Output: {args.output.resolve()}", file=sys.stderr)
    print("-" * 60, file=sys.stderr)

    # Open output in append mode so resume + crash recovery work naturally.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_f = args.output.open("a", encoding="utf-8")

    error_count = 0
    try:
        with tqdm(total=total, unit="run", dynamic_ncols=True) as pbar:
            for provider, model, pid, ptext, iteration in tasks:
                pbar.set_description(f"{model[:20]:<20} {pid:<12}")
                rec = Record(
                    run_id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    provider=provider,
                    model=model,
                    prompt_id=pid,
                    prompt_text=ptext,
                    iteration=iteration,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                    response=None,
                    input_tokens=None,
                    output_tokens=None,
                    latency_ms=None,
                    error=None,
                )
                try:
                    if provider == "anthropic":
                        result = call_with_retry(call_anthropic, anthropic_client, model, ptext)
                    else:
                        result = call_with_retry(call_openai, openai_client, model, ptext)
                    rec.response = result["response"]
                    rec.input_tokens = result["input_tokens"]
                    rec.output_tokens = result["output_tokens"]
                    rec.latency_ms = result["latency_ms"]
                except Exception as e:  # noqa: BLE001
                    rec.error = f"{type(e).__name__}: {e}"
                    error_count += 1

                out_f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
                out_f.flush()  # so partial progress survives a crash
                pbar.update(1)
                pbar.set_postfix(errors=error_count)
    finally:
        out_f.close()

    print("-" * 60, file=sys.stderr)
    print(f"Done. {total - error_count} successes, {error_count} errors.", file=sys.stderr)
    print(f"Results written to: {args.output.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    main()
