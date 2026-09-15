# Pre-result code audit — locked P1-P5

**Audit basis:** `SECONDARY_ANALYSIS_PLAN.md` and `HARMONIZED_CODING_SPEC.md` at frozen dataset commit `c14f6b433d4c277a9dc0acc8d44c46ec8570c2cb`.

## Result

**PASS for pre-result implementation.** No scientific deviation was identified.

## P1

- Trains six-way L2 logistic regression on all harmonized BA2 poetry rows.
- Tests without retraining on BA1 poetry.
- Uses only locked body-only features.
- Reports accuracy, balanced accuracy, six-way confusion matrix, per-model recall.
- Reports deterministic 10,000-resample 95% stratified bootstrap intervals, preserving model x prompt-ID strata.

## P2

- Uses the same body-only pipeline for provider labels.
- Trains on BA2 and tests on BA1 poetry.
- Reports requested metrics, confusion matrix, and stratified bootstrap intervals.
- Interpretation must remain restricted to the six named models.

## P3

- Implements all three leave-one-genre-out folds in BA1.
- Preprocessing is fitted on training folds only.
- Reports each fold and pooled held-out metrics/confusion matrices.

## P4

- Implements leave-one-phrasing-out for write/compose/gimme.
- Implements leave-one-length-cap-out for 5/10/20.
- Pools predictions separately within the phrasing and length transfer families.
- Reports fold and pooled metrics/confusion matrices/per-model recall.

## P5

- Uses harmonized first lexical token on poems only.
- Requires exactly 30 BA1 poems/model and non-empty opening tokens.
- Computes Shannon entropy in bits.
- Rarefies BA2 to 30 poems/model without replacement for 10,000 deterministic resamples.
- Reports 95% rarefaction intervals and whether BA1 falls inside.
- Reports cross-model rankings and descriptive named-provider mean/gap summaries.

## Guardrails

- Input must contain exactly 540 BA1 + 5,398 BA2 rows = 5,938 total.
- Unexpected model identifiers fail closed.
- Frozen source SHA-256 and analysis package versions are recorded.
- The script writes only to the September primary-analysis results directory.
- No parser, harmonizer, raw May file, or frozen harmonized table is modified.

## Dry run

A synthetic 5,938-row dataset matching the frozen study counts, six-model structure, BA1 genre design, BA2 phrasing/length design, and required schema completed P1-P5 end-to-end successfully. This dry run contains no real study outcomes.
