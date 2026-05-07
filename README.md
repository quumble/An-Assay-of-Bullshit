# Model Comparison Experiment

Exploratory study comparing creative-writing defaults across Claude and OpenAI model tiers under cold, contextless prompts.

## Design

- **Models (6):** `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `claude-opus-4-7`, `gpt-5.4-nano`, `gpt-5.4-mini`, `gpt-5.4`
- **Prompts (9):** 3 categories (story, animal, poem) × 3 length constraints (`<5`, `<10`, open)
- **Runs/cell:** 10
- **Total calls:** 540
- **Settings:** `temperature=1.0`, `max_tokens=400`, no system prompt
- **Output:** JSONL, one record per call

## Setup

```bash
pip install anthropic openai tqdm
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
```

## Run

```bash
# Smoke test first (54 calls, ~cents)
python run_experiment.py --runs-per-cell 1

# Full run
python run_experiment.py

# Resume after a crash / interrupt
python run_experiment.py --resume

# Single provider
python run_experiment.py --anthropic-only
python run_experiment.py --openai-only
```

Progress bar shows current model/prompt and running error count. Output flushes after every call, so partial progress survives crashes.

## Output schema

Each line of `results.jsonl` is one call:

```json
{
  "run_id": "uuid",
  "timestamp": "2026-05-07T...",
  "provider": "anthropic",
  "model": "claude-opus-4-7",
  "prompt_id": "story_lt5",
  "prompt_text": "create a short story in fewer than 5 sentences.",
  "iteration": 0,
  "temperature": 1.0,
  "max_tokens": 400,
  "response": "...",
  "input_tokens": 12,
  "output_tokens": 87,
  "latency_ms": 2340,
  "error": null
}
```

Failed calls are written with `response: null` and an `error` string. They are *not* marked complete on resume, so re-running with `--resume` retries them.

## Caveats

- n=10 at temp=1.0 is small; treat findings as hypotheses, not conclusions.
- Cold contextless prompts measure model *defaults*, not behavior in real use.
- "Fewer than N sentences" partly tests instruction-following, not just style.
- Poems are messy to analyze by sentence count — line-based metrics work better.
- Pin to dated model snapshots if you want long-term reproducibility.

## Planned analyses

- Sentence/line-count compliance vs. constraint
- Opening-word and opening-bigram frequency by model
- Lexical diversity (MTLD)
- Named entity inventory (especially for animal prompts: real / invented / hybrid)
- Intra-model vs. inter-model embedding distance
- Cross-model nearest-neighbor structure

## Files

- `run_experiment.py` — runner
- `results.jsonl` — output (created on first run)
