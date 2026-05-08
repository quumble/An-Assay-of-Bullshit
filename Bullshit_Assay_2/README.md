# Bullshit Assay 2 — Poetry Defaults

Series 2 of an exploratory study comparing creative-writing defaults
across model families and tiers, narrowed to length-constrained poetry.

## What this is

Six models (3 Claude tiers, 3 OpenAI tiers) are prompted to produce
poems under three line caps (5, 10, 20) crossed with three phrasings
("write" / "compose" / "gimme"). 100 iterations per cell, 5,400 calls
total. Cold contextless prompts at temperature 1.0, no system prompt,
max 400 output tokens per call.

The goal is to measure model-default poetic style and structure with
enough per-cell n to support semantic and structural analysis: POS
ratios, person/voice classification, rhyme detection, concreteness,
length-constraint compliance, and embedding-based clustering.

## What this is not

- Not a quality or aesthetic comparison.
- Not a measurement of behavior in real use — cold contextless prompts
  measure defaults, not what models do when given context.
- Not generalizable beyond poetry. Series 1 covered story, animal, and
  poem; series 2 narrows to poetry to enable deeper analysis.

## Design

- **Models (6):** Claude Haiku 4.5, Sonnet 4.6, Opus 4.7; GPT-5.4 nano,
  mini, full. Model identifiers match series 1; exact strings logged in
  `run_metadata.json`.
- **Prompts (9):** 3 length caps × 3 phrasings.
- **Runs/cell:** 100.
- **Total calls:** 5,400.
- **Settings:** temperature 1.0, max_tokens 400, no system prompt.
- **Output:** JSONL, one record per call.

Full prompt list:

| ID | Prompt |
|---|---|
| poem_write_5 | write a poem in fewer than 5 lines. |
| poem_write_10 | write a poem in fewer than 10 lines. |
| poem_write_20 | write a poem in fewer than 20 lines. |
| poem_compose_5 | compose a poem in fewer than 5 lines. |
| poem_compose_10 | compose a poem in fewer than 10 lines. |
| poem_compose_20 | compose a poem in fewer than 20 lines. |
| poem_gimme_5 | gimme a poem in fewer than 5 lines. |
| poem_gimme_10 | gimme a poem in fewer than 10 lines. |
| poem_gimme_20 | gimme a poem in fewer than 20 lines. |

## Preregistration

This study is preregistered. Design, hypotheses, primary analyses, and
decision rules are locked in `preregistration.md` before any data is
collected. The measurement plan (how each feature is computed) is
locked in `coding_heuristic.md`. Any deviation from either document
during analysis is recorded in `deviations.md` with a date and a
reason.

## Setup

For running the experiment:

```
pip install anthropic openai tqdm
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
```

For running the analysis pipeline:

```
pip install spacy pronouncing scipy scikit-learn statsmodels pandas openpyxl numpy
```

The spaCy model and Brysbaert concreteness norms auto-download to
`~/.cache/bullshit_assay_2/` on first use.

Model identifiers match series 1 exactly. Haiku is pinned to a dated
snapshot; the others use unpinned aliases as in series 1, for parity in
cross-series comparison. The exact strings used at run time are
recorded in `run_metadata.json` for reproducibility.

## Run

```
# Dry run — print task plan and per-model counts, no API calls
python run_experiment.py --dry-run

# Smoke test — 1 iteration per cell, 54 calls total
python run_experiment.py --runs-per-cell 1

# Full run
python run_experiment.py

# Resume after a crash or interrupt
python run_experiment.py --resume

# Single provider
python run_experiment.py --anthropic-only
python run_experiment.py --openai-only
```

The full task list is shuffled with a logged random seed before
execution, so any time-correlated provider effects (rate-limit
backoff, intermittent outages, intra-day model drift) do not align
with model identity. The seed is written to `run_metadata.json`.

Output flushes after every call. Resume detects already-completed
(model, prompt, iteration) cells and skips them; errored runs are not
counted complete and will be retried on resume.

## Output

`results.jsonl` — one record per call:

```json
{
  "run_id": "uuid",
  "timestamp": "2026-...",
  "provider": "anthropic",
  "model": "claude-opus-4-7",
  "prompt_id": "poem_compose_10",
  "prompt_text": "compose a poem in fewer than 10 lines.",
  "iteration": 0,
  "temperature": 1.0,
  "max_tokens": 400,
  "response": "...",
  "raw_response": { ... },
  "input_tokens": 12,
  "output_tokens": 187,
  "latency_ms": 2340,
  "error": null
}
```

`run_metadata.json` — single document with seed, model snapshot
identifiers, package versions, git commit, prompt list hash, and run
arguments.

Failed calls are written with `response: null` and an `error` string;
they are retried on `--resume`.

## Analysis plan

See `preregistration.md` for primary analyses and decision rules, and
`coding_heuristic.md` for the per-feature measurement specification.

In brief, primary analyses cover:

1. Embedding clustering by model, family, and tier (silhouette score
   with permutation null).
2. Pre-specified feature battery comparison across models (one-way
   ANOVA, Bonferroni-corrected, effect sizes ranked).
3. Phrasing-by-model interaction (2-way ANOVA on each feature).
4. Compliance regression (model × length cap × phrasing).

A mandatory 50-poem manual validation step runs before any aggregate
analysis. Features failing an 85% agreement threshold are downgraded
to exploratory.

## Files

- `run_experiment.py` — runner.
- `run_analysis.py` — single entrypoint for the analysis pipeline.
- `analysis/` — analysis package:
    - `features.py` — per-poem feature extraction (structural, POS, person, concreteness, rhyme).
    - `embed.py` — poem embedding via OpenAI text-embedding-3-large.
    - `analyze.py` — primary statistical analyses (Q1–Q4 from preregistration).
    - `validate.py` — stratified-sample drawing and human-tag scoring.
    - `validation_tool.html` — single-file blinded HTML tagging tool, opens in any browser.
    - `tests/` — unit tests with hand-crafted poem fixtures.
- `preregistration.md` — locked study design and analysis plan.
- `coding_heuristic.md` — locked measurement specification.
- `deviations.md` — log of any departures from the preregistration
  during analysis.
- `results.jsonl` — experiment output (created on first run).
- `run_metadata.json` — experiment output (written at run start).

## Analysis pipeline

The full pipeline runs in five steps. All commands are PowerShell-friendly
and run from the repo root.

```
# 1. Extract features from every poem
python run_analysis.py features --input results.jsonl --output features.jsonl

# 2. Compute embeddings (~$2 OpenAI cost for 5,400 poems)
python run_analysis.py embed --input features.jsonl --output embeddings.jsonl

# 3. Draw a stratified blinded sample for human validation
python run_analysis.py validate --draw --n 200 --seed 42

# 4. Open analysis/validation_tool.html in your browser, load the sample,
#    tag everything (keyboard shortcuts: 1/2/3 for POS+rhyme, Y/N for
#    person+preamble, arrow keys to navigate, Tab for next untagged).
#    Click "Export results" when done.

# 5. Score the human tags against the automated extractors
python run_analysis.py validate --score --input validation_results.json

# 6. Run the primary statistical analyses
python run_analysis.py analyze
```

Run unit tests on the feature extractors at any time:

```
python run_analysis.py test
```

## Validation gate

Per `coding_heuristic.md`, the validation step is **mandatory before any
aggregate analysis is computed**. Features that fail the 85% agreement
threshold are downgraded to exploratory before primary analyses run.
The HTML tool tags poems blinded — model identity is hidden, only the
length cap is shown — to protect against unconscious bias.

The Q1 embedding analysis requires `embeddings.jsonl`. If you skip the
embedding step, Q1 reports as "no embeddings provided" and the other
three primary analyses still run.

## Caveats

- Cold contextless prompts measure defaults, not real-world behavior.
- "Fewer than N lines" is partly an instruction-following test;
  compliance is treated as its own measurement target rather than a
  confound.
- Single-snapshot model versions; results may not generalize to other
  snapshots of the same models. Snapshot identifiers are logged.
- POS taggers are imperfect on poetry; the manual validation step is
  designed to catch this. Features that fail validation are flagged.
- n=100/cell is enough for medium-effect detection but small effects
  may not reach Bonferroni-corrected significance.

## Series 1

The prior round (`Bullshit_Assay_1/` in the parent repo) covered three
categories (story, animal, poem) at n=10/cell. Findings from that round
informed the narrower focus and deeper sampling here. Series 2 does not
attempt direct prompt-level replication of series 1; the prompt
phrasings have been cleaned ("fewer than" rather than "fewer then") and
the category set has been narrowed.

## License

Apache-2.0.
