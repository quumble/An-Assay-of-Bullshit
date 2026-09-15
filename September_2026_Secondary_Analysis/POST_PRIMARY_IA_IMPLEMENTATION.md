# Post-Primary I&A Implementation — September 2026

**Status:** implementation choices fixed before any I&A result is inspected  
**Plan:** `POST_PRIMARY_IA_PLAN.md`  
**Evidentiary status:** outcome-informed exploratory follow-up  
**Frozen primary-result boundary:** `f2f93897572b8b6e9f5f162dc4d51cb15fcd48ff`  
**Frozen S1-S5 result boundary present in repository before implementation:** `e845fd356a6c842d114ad04489de2b7f5ca663a2`

The S1-S5 results are not inputs to the I&A script. The I&A inputs are the frozen harmonized feature table and frozen P1-P5 result JSON.

## IA1 — training-size-matched cross-study transfer

The implementation follows the plan literally:

- 1,000 deterministic resamples;
- 360 BA2 training poems per resample;
- exactly 60 training poems per model;
- within each model, all nine BA2 prompt cells contribute six records, and six deterministically selected cells contribute one additional record;
- sampling is without replacement within each resample;
- the BA1 poetry test set is unchanged at 180 records / 30 per model;
- the classifier is the exact frozen P1 pipeline: median imputation, `StandardScaler`, and default `LogisticRegression()`;
- raw accuracy, balanced accuracy, and per-model recall are retained for every resample;
- summaries use median, mean, and 2.5th/97.5th percentiles;
- the frozen full-training P1 accuracy and three frozen P3 held-out-genre accuracies are copied as descriptive references only.

Deterministic RNG streams are derived from a NumPy `SeedSequence` containing the base seed (`20260915`), analysis identifier, resample index, and fixed model index.

## IA2 — fixed feature-family attribution

The five feature families are exactly those in `POST_PRIMARY_IA_PLAN.md`:

1. form/structure;
2. grammar/person;
3. punctuation;
4. nonstructural style = grammar/person + punctuation;
5. full body-only vector.

For every family, the script reruns:

- P1 cross-study poetry transfer;
- P3 leave-one-genre-out transfer, including pooled held-out predictions;
- P4 leave-one-phrasing-out transfer, including pooled held-out predictions;
- P4 leave-one-length-cap-out transfer, including pooled held-out predictions.

For each condition it stores accuracy, balanced accuracy, per-model recall, and the confusion matrix. Deltas are computed against the already-frozen full-body primary result for the corresponding condition.

### Full-body reproducibility gate

The `full_body` IA2 condition is also a fail-closed reproducibility check. Its confusion matrices must exactly reproduce the frozen P1/P3/P4 confusion matrices, and scalar metrics/per-model recalls must match within floating-point tolerance (`atol=1e-15`, `rtol=0`). A mismatch aborts the I&A run.

### Convergence handling

The classifier remains the frozen default `LogisticRegression()` specification. A scikit-learn `ConvergenceWarning` is promoted to an error so that a non-converged exploratory fit cannot silently enter the result bundle. If this occurs on the real run, stop before inspecting I&A outputs and document any permitted convergence correction before rerunning.

## IA3 — descriptive behavioral transfer map

The transfer map contains:

- frozen primary P1, P3 folds, and P4 folds using the full body vector;
- IA1 size-matched P1 as a median summary with the 2.5th/97.5th resample interval;
- IA2 restricted feature-family results for form/structure, grammar/person, punctuation, and nonstructural style.

The full-body IA2 rerun is not duplicated in the map because the frozen primary rows already represent that condition.

Each row retains:

- source layer;
- analysis / transfer family / holdout;
- training and testing environment labels;
- training and testing sample size;
- feature family;
- raw accuracy and balanced accuracy;
- six-way chance reference (1/6);
- chance-adjusted accuracy `(accuracy - 1/6) / (1 - 1/6)`;
- an accuracy interval where applicable (IA1 summary only).

The map is explicitly descriptive and non-reciprocal. It is not presented as a fully crossed invariance matrix.

## Accessibility outputs

The script writes:

- `IA1_size_matched_resamples.csv`
- `IA1_model_recall_resamples.csv`
- `IA1_model_recall_summary.csv`
- `IA2_feature_family_summary.csv`
- `IA2_feature_family_model_recalls.csv`
- `IA2_confusion_matrices.json`
- `IA3_transfer_map.csv`
- `IA_opening_entropy_reference.csv`
- `IA_ACCESS_SUMMARY.md`
- `post_primary_ia_results.json`

`IA_ACCESS_SUMMARY.md` is generated mechanically. It reports the matched-size result, headline feature-family decomposition, frozen full-body model heterogeneity, and the frozen P5 opening-entropy example. It does not assign a new evidentiary status or make an inferential claim.

## Boundaries

The I&A script does not modify or overwrite:

- the May studies;
- the harmonized dataset;
- the parser or validation materials;
- P1-P5 scripts/results;
- S1-S5 scripts/results.

All outputs are written under `results/post_primary_ia/`.
