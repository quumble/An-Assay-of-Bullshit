# Post-Review Diagnostic Implementation — September 2026

**Status:** Implementation choices fixed before diagnostic results are inspected  
**Plan:** `POST_REVIEW_DIAGNOSTIC_PLAN.md`  
**Evidentiary status:** outcome-informed exploratory manuscript follow-up

## D1 — target-local separability

Implementation follows the plan literally:

- input: frozen September harmonized feature table;
- scope: BA1 poetry only;
- required structure: 180 rows in 18 model × prompt cells, exactly 10 rows per cell;
- resamples: 1,000;
- train/test split within each model × prompt cell: 5/5 without replacement;
- train n per resample: 90;
- test n per resample: 90;
- classifier: median imputation → `StandardScaler` → default `LogisticRegression()`;
- feature set: exact frozen 22 body features;
- convergence warnings promoted to errors;
- outputs: raw accuracy, balanced accuracy, and per-model recall for every resample plus percentile summaries.

The RNG seed is `20261215`. A single deterministic NumPy generator is used in fixed sorted model × prompt order.

This is deliberately a within-target separability diagnostic. Prompt conditions are represented on both sides of each split because the question is whether model labels are recoverable *inside the BA1-poetry environment*, not whether the local classifier transfers across prompt conditions.

## D2 — token-ceiling audit

The script reads the frozen raw BA1 and BA2 JSONL sources directly.

For successful non-empty responses it extracts:

- study;
- source line;
- run/output ID;
- provider;
- model;
- prompt ID/text;
- inferred requested line cap;
- iteration;
- `output_tokens`;
- `max_tokens` / `max_output_tokens`;
- Anthropic `raw_response.stop_reason` when available;
- OpenAI `raw_response.status` when available.

Fixed flags:

- `direct_cap_flag = (Anthropic stop_reason == "max_tokens") OR (OpenAI status == "incomplete")`;
- `at_or_above_cap = output_tokens >= max_tokens` when both values exist;
- `near_cap_95 = output_tokens / max_tokens >= 0.95` when both values exist.

The token-fraction flags are reported as usage diagnostics only. They are not treated as direct evidence of visible-text truncation.

The script exports record-level and grouped audit tables. BA2 grouping includes requested line cap, model × line cap, and prompt ID.

## Conditional D2 sensitivity

If and only if one or more analyzed BA2 rows is directly flagged:

1. collect those rows' source run IDs;
2. verify every flagged source run ID exists exactly once in the harmonized BA2 table;
3. remove those harmonized rows;
4. rerun the frozen P4 leave-one-length-cap-out body-only classifier;
5. write fold and pooled metrics beside the frozen original P4 length metrics.

No other P1-P5/S1-S5/I&A analysis is rerun.

## Fail-closed integrity checks

Production execution requires:

- harmonized SHA-256 = `cd6dfbb320e219241923a8a71a3f8cc2fb50d86c15226d73fb9c90653845750f`;
- primary-results SHA-256 = `95f549bc125d137972fa863386886775503f353ec8e5ff9e0097fb98e9e112bb`;
- harmonized counts BA1 = 540 and BA2 = 5,398;
- BA1-poetry D1 structure exactly 6 models × 3 prompt IDs × 10 records;
- model labels exactly match the frozen six-model list.

Any failure aborts before outcome output is written.

## Self-test

`run_post_review_diagnostics.py --self-test` runs a synthetic in-memory test of:

- D1 balanced 5/5 cell splitting with no within-split overlap;
- classifier fitting and metric production;
- D2 direct/proximity flag logic;
- line-cap inference.

The self-test does not read real study data and cannot expose diagnostic outcomes.

## Output location

All real outputs are written only to:

`September_2026_Secondary_Analysis/results/post_review_diagnostics/`

Expected outputs:

- `D1_local_separability_resamples.csv`
- `D1_local_separability_model_recalls.csv`
- `D1_local_separability_summary.json`
- `D2_token_cap_records.csv`
- `D2_token_cap_by_study.csv`
- `D2_token_cap_by_ba2_length.csv`
- `D2_token_cap_by_ba2_model_length.csv`
- `D2_token_cap_by_ba2_prompt.csv`
- `D2_conditional_length_sensitivity.json` (only if triggered)
- `post_review_diagnostics_results.json`
- `POST_REVIEW_DIAGNOSTIC_ACCESS_SUMMARY.md`

The script modifies no existing result file.
