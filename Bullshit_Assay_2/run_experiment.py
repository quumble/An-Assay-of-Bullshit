"""
Bullshit Assay 2 — Poetry defaults experiment runner.

Runs 9 length-constrained poetry prompts against 6 Claude and OpenAI models,
100 iterations per cell, at temperature=1.0, no system prompt, max 400 output
tokens. Calls are interleaved across models/prompts via a shuffled task list
(seed logged) so any time-correlated provider drift does not align with model.
Results stream to JSONL; partial progress survives crashes.

Setup:
    pip install anthropic openai tqdm
    export ANTHROPIC_API_KEY=...
    export OPENAI_API_KEY=...

Run:
    python run_experiment.py                   # full run, default seed
    python run_experiment.py --runs-per-cell 1 # smoke test, 54 calls
    python run_experiment.py --resume          # skip cells already in output
    python run_experiment.py --dry-run         # estimate cost, no API calls
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import anthropic as anthropic_pkg
    import openai as openai_pkg
    from anthropic import Anthropic
    from openai import OpenAI
    from tqdm import tqdm
except ImportError as e:
    sys.exit(f"Missing dependency: {e}. Run: pip install anthropic openai tqdm")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROMPTS = [
    ("poem_write_5",     "write a poem in fewer than 5 lines."),
    ("poem_write_10",    "write a poem in fewer than 10 lines."),
    ("poem_write_20",    "write a poem in fewer than 20 lines."),
    ("poem_compose_5",   "compose a poem in fewer than 5 lines."),
    ("poem_compose_10",  "compose a poem in fewer than 10 lines."),
    ("poem_compose_20",  "compose a poem in fewer than 20 lines."),
    ("poem_gimme_5",     "gimme a poem in fewer than 5 lines."),
    ("poem_gimme_10",    "gimme a poem in fewer than 10 lines."),
    ("poem_gimme_20",    "gimme a poem in fewer than 20 lines."),
]

# Model identifiers match series 1 exactly. Only Haiku is pinned to a dated
# snapshot; the others use unpinned aliases as in series 1, so cross-series
# comparison is at parity. The exact strings used at run time are recorded
# in run_metadata.json for reproducibility.
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
DEFAULT_RUNS_PER_CELL = 100


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
    iteration: int
    temperature: float
    max_tokens: int
    response: Optional[str]
    raw_response: Optional[dict]
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
    raw = {
        "id": msg.id,
        "model": msg.model,
        "stop_reason": msg.stop_reason,
        "content": [
            {"type": getattr(b, "type", None), "text": getattr(b, "text", None)}
            for b in msg.content
        ],
    }
    return {
        "response": text,
        "raw_response": raw,
        "input_tokens": msg.usage.input_tokens,
        "output_tokens": msg.usage.output_tokens,
        "latency_ms": latency_ms,
    }


def call_openai(client: OpenAI, model: str, prompt: str) -> dict:
    t0 = time.perf_counter()
    resp = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    text = getattr(resp, "output_text", None) or ""
    usage = getattr(resp, "usage", None)
    raw = {
        "id": getattr(resp, "id", None),
        "model": getattr(resp, "model", None),
        "status": getattr(resp, "status", None),
        "output_text": text,
    }
    return {
        "response": text,
        "raw_response": raw,
        "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
        "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
        "latency_ms": latency_ms,
    }


def call_with_retry(fn, *args, retries: int = 3, backoff: float = 2.0):
    last_err = None
    for attempt in range(retries):
        try:
            return fn(*args)
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(backoff ** attempt)
    raise last_err


# ---------------------------------------------------------------------------
# Resume support
# ---------------------------------------------------------------------------

def load_completed_cells(path: Path) -> set[tuple[str, str, int]]:
    """Return set of (model, prompt_id, iteration) already present in output
    with no error. Errored runs are NOT counted complete and will be retried."""
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
                continue
            completed.add((rec["model"], rec["prompt_id"], rec["iteration"]))
    return completed


# ---------------------------------------------------------------------------
# Run metadata
# ---------------------------------------------------------------------------

def get_git_commit() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return None


def write_metadata(path: Path, args, seed: int, tasks_count: int) -> None:
    metadata = {
        "experiment": "Bullshit Assay 2 — poetry defaults",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "git_commit": get_git_commit(),
        "anthropic_models": ANTHROPIC_MODELS,
        "openai_models": OPENAI_MODELS,
        "prompts": [{"id": pid, "text": ptext} for pid, ptext in PROMPTS],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "runs_per_cell": args.runs_per_cell,
        "total_planned_calls": tasks_count,
        "package_versions": {
            "anthropic": getattr(anthropic_pkg, "__version__", "unknown"),
            "openai": getattr(openai_pkg, "__version__", "unknown"),
            "python": platform.python_version(),
        },
        "args": {
            "runs_per_cell": args.runs_per_cell,
            "output": str(args.output),
            "resume": args.resume,
            "anthropic_only": args.anthropic_only,
            "openai_only": args.openai_only,
            "seed_arg": args.seed,
        },
        "prompt_list_hash": hashlib.sha256(
            json.dumps([list(p) for p in PROMPTS], sort_keys=True).encode()
        ).hexdigest(),
    }
    path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-per-cell", type=int, default=DEFAULT_RUNS_PER_CELL,
                        help=f"Iterations per (model, prompt) cell. Default: {DEFAULT_RUNS_PER_CELL}")
    parser.add_argument("--output", type=Path, default=Path("results.jsonl"),
                        help="JSONL output path. Default: results.jsonl")
    parser.add_argument("--metadata", type=Path, default=Path("run_metadata.json"),
                        help="Run metadata path. Default: run_metadata.json")
    parser.add_argument("--resume", action="store_true",
                        help="Skip (model, prompt, iteration) cells already in output.")
    parser.add_argument("--anthropic-only", action="store_true")
    parser.add_argument("--openai-only", action="store_true")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for task shuffle. Default: random, logged in metadata.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print task plan and exit without making API calls.")
    args = parser.parse_args()

    if args.anthropic_only and args.openai_only:
        sys.exit("Cannot pass both --anthropic-only and --openai-only.")

    seed = args.seed if args.seed is not None else random.randrange(2**31)
    rng = random.Random(seed)

    need_anthropic = not args.openai_only
    need_openai = not args.anthropic_only
    if not args.dry_run:
        if need_anthropic and not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY not set.")
        if need_openai and not os.environ.get("OPENAI_API_KEY"):
            sys.exit("OPENAI_API_KEY not set.")

    anthropic_client = Anthropic() if (need_anthropic and not args.dry_run) else None
    openai_client = OpenAI() if (need_openai and not args.dry_run) else None

    tasks: list[tuple[str, str, str, str, int]] = []
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

    rng.shuffle(tasks)

    completed = load_completed_cells(args.output) if args.resume else set()
    if completed:
        before = len(tasks)
        tasks = [t for t in tasks if (t[1], t[2], t[4]) not in completed]
        print(f"Resume: skipping {before - len(tasks)} already-completed runs.",
              file=sys.stderr)

    total = len(tasks)
    print(f"Seed: {seed}", file=sys.stderr)
    print(f"Total runs to perform: {total}", file=sys.stderr)
    print(f"Models: {ANTHROPIC_MODELS if need_anthropic else []} "
          f"+ {OPENAI_MODELS if need_openai else []}", file=sys.stderr)
    print(f"Prompts: {len(PROMPTS)} | Runs/cell: {args.runs_per_cell} | "
          f"Temp: {TEMPERATURE} | Max tokens: {MAX_TOKENS}", file=sys.stderr)
    print(f"Output: {args.output.resolve()}", file=sys.stderr)
    print(f"Metadata: {args.metadata.resolve()}", file=sys.stderr)

    if args.dry_run:
        per_model_count: dict[str, int] = {}
        for _, model, _, _, _ in tasks:
            per_model_count[model] = per_model_count.get(model, 0) + 1
        print("\nDry run — no API calls made.", file=sys.stderr)
        print("Per-model call counts:", file=sys.stderr)
        for model, count in sorted(per_model_count.items()):
            print(f"  {model:<35} {count}", file=sys.stderr)
        print("\nEstimate per-call cost externally before kicking off the real run.",
              file=sys.stderr)
        return

    print("-" * 60, file=sys.stderr)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_metadata(args.metadata, args, seed, total)
    out_f = args.output.open("a", encoding="utf-8")

    error_count = 0
    per_model_done: dict[str, int] = {m: 0 for m in ANTHROPIC_MODELS + OPENAI_MODELS}

    try:
        with tqdm(total=total, unit="run", dynamic_ncols=True) as pbar:
            for provider, model, pid, ptext, iteration in tasks:
                pbar.set_description(f"{model[:25]:<25} {pid:<18}")
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
                    raw_response=None,
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
                    rec.raw_response = result["raw_response"]
                    rec.input_tokens = result["input_tokens"]
                    rec.output_tokens = result["output_tokens"]
                    rec.latency_ms = result["latency_ms"]
                    per_model_done[model] = per_model_done.get(model, 0) + 1
                except Exception as e:
                    rec.error = f"{type(e).__name__}: {e}"
                    error_count += 1

                out_f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
                out_f.flush()
                pbar.update(1)
                pbar.set_postfix(errors=error_count)
    finally:
        out_f.close()

    print("-" * 60, file=sys.stderr)
    print(f"Done. {total - error_count} successes, {error_count} errors.", file=sys.stderr)
    print("Per-model successful calls:", file=sys.stderr)
    for model, count in sorted(per_model_done.items()):
        print(f"  {model:<35} {count}", file=sys.stderr)
    print(f"Results written to: {args.output.resolve()}", file=sys.stderr)
    print(f"Metadata written to: {args.metadata.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    main()
