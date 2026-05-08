"""
Poem embedding via OpenAI text-embedding-3-large.

Reads features.jsonl (or results.jsonl), embeds the poem_body field,
writes embeddings to a separate JSONL keyed by run_id. Resumable —
rerunning skips already-embedded run_ids.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Iterable

EMBEDDING_MODEL = "text-embedding-3-large"
BATCH_SIZE = 100  # OpenAI accepts up to 2048 inputs per request


def load_already_embedded(out_path: Path) -> set[str]:
    done: set[str] = set()
    if not out_path.exists():
        return done
    with out_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                done.add(rec["run_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    return done


def iter_input_records(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def embed_batch(client, texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [d.embedding for d in response.data]


def run_embed(features_path: Path, out_path: Path) -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY not set.")
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai not installed. Run: pip install openai")

    client = OpenAI()
    already = load_already_embedded(out_path)
    if already:
        print(f"Resume: {len(already)} embeddings already present, skipping those.",
              file=sys.stderr)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_f = out_path.open("a", encoding="utf-8")

    pending: list[tuple[str, str, str, str, int]] = []  # (run_id, text, model, prompt_id, iteration)
    total_done = 0
    total_errors = 0

    def flush() -> None:
        nonlocal total_done, total_errors
        if not pending:
            return
        texts = [p[1] for p in pending]
        try:
            embeddings = embed_batch(client, texts)
        except Exception as e:
            print(f"Embedding batch failed ({type(e).__name__}: {e}); "
                  f"writing error records.", file=sys.stderr)
            for run_id, _, model, pid, it in pending:
                out_f.write(json.dumps({
                    "run_id": run_id, "model": model, "prompt_id": pid,
                    "iteration": it, "embedding": None,
                    "error": f"{type(e).__name__}: {e}",
                }) + "\n")
                total_errors += 1
            out_f.flush()
            pending.clear()
            return
        for (run_id, _, model, pid, it), emb in zip(pending, embeddings):
            out_f.write(json.dumps({
                "run_id": run_id, "model": model, "prompt_id": pid,
                "iteration": it, "embedding": emb, "error": None,
            }) + "\n")
            total_done += 1
        out_f.flush()
        pending.clear()

    try:
        for rec in iter_input_records(features_path):
            run_id = rec["run_id"]
            if run_id in already:
                continue
            body = rec.get("poem_body")
            if not body:
                # No poem body — write a null embedding
                out_f.write(json.dumps({
                    "run_id": run_id,
                    "model": rec.get("model"),
                    "prompt_id": rec.get("prompt_id"),
                    "iteration": rec.get("iteration"),
                    "embedding": None,
                    "error": "empty_poem_body",
                }) + "\n")
                total_errors += 1
                continue
            pending.append((run_id, body, rec["model"], rec["prompt_id"], rec["iteration"]))
            if len(pending) >= BATCH_SIZE:
                flush()
                # Light pacing to be friendly to rate limits
                time.sleep(0.05)
        flush()
    finally:
        out_f.close()

    print(f"Embeddings written: {total_done} new, {total_errors} errors", file=sys.stderr)
    print(f"Output: {out_path.resolve()}", file=sys.stderr)
