# Post-Review Diagnostic Plan — September 2026

**Project:** An Assay of Bullshit — manuscript critical-review follow-up  
**Date:** 2026-09-15  
**Status:** Outcome-informed exploratory diagnostics, specified before diagnostic results are inspected  
**Frozen primary boundary:** `f2f93897572b8b6e9f5f162dc4d51cb15fcd48ff`  
**Frozen secondary S1-S5 boundary:** `e845fd356a6c842d114ad04489de2b7f5ca663a2`  
**Frozen post-primary I&A boundary:** existing committed post-primary I&A results  

## 1. Purpose and evidentiary status

Critical review of the working manuscript identified two bounded questions that materially affect interpretation but do not require reopening the September analysis suite:

1. When cross-category transfer into BA1 poetry is weak, is BA1 poetry itself locally model-separable under the same 22 body features?
2. Could the common 400-output-token ceiling materially contaminate the long-output conditions, especially BA2's 20-line prompts?

Both diagnostics are explicitly **post-result and review-informed**. They are not amendments to P1-P5 or S1-S5 and must not be represented as preregistered or prospectively specified before the September findings were known.

The diagnostics are intentionally narrow. No new feature engineering, classifier search, hypothesis battery, or new model calls are permitted here.

## 2. D1 — BA1-poetry target-local separability

### Question

P3 showed weak transfer from the other BA1 creative-writing categories into BA1 poetry. Failed transfer does not by itself establish that model-associated signal disappeared in the target environment: the target may remain locally separable even if a source-trained decision rule does not transport.

D1 therefore asks:

> Using the exact frozen 22-feature body representation and classifier family, how separable are the six model labels **within BA1 poetry itself** under a leakage-safe local evaluation?

### Data

Use only the frozen September harmonized BA1 poetry rows:

- 180 total poems;
- six model identifiers;
- three BA1 poetry prompt conditions;
- 10 responses per model × prompt cell.

The script must verify this 6 × 3 × 10 structure before fitting any model.

### Resampling design

Run **1,000 deterministic balanced half-split resamples**.

Within every model × prompt-ID cell independently:

- randomly select 5 of the 10 rows for training;
- place the remaining 5 rows in testing;
- sample without replacement within each split.

Therefore every resample contains:

- training n = 90;
- testing n = 90;
- exactly 15 training and 15 testing poems per model;
- exactly balanced prompt composition within every model.

Rows may appear in different roles across different resamples, but no row may appear in both train and test within the same resample.

### Classifier

Use the exact frozen body-only classifier specification:

- 22 locked body features;
- training-fitted median imputation;
- training-fitted `StandardScaler`;
- scikit-learn default L2 `LogisticRegression()`;
- no hyperparameter tuning;
- no feature selection.

A `ConvergenceWarning` is promoted to an error. If convergence fails, stop before inspecting diagnostic outcomes and document any permitted implementation correction before rerunning.

### Outputs

For every resample retain:

- accuracy;
- balanced accuracy;
- per-model recall.

Summarize with:

- mean;
- median;
- 2.5th and 97.5th percentiles.

Also report the fixed six-way chance reference of 1/6.

### Interpretation rule

D1 measures **target-local separability**, not transfer.

- If BA1 poetry is locally separable while P3 transfer into poetry remains weak, that supports an interpretation in terms of limited portability of the source-trained assay into the poetry target environment.
- If BA1 poetry is itself only weakly separable, then the P3 failure cannot be cleanly attributed to transport failure; weak target signal is a competing explanation.

D1 does not establish an intrinsic or causal "genre effect."

## 3. D2 — 400-token ceiling audit

### Question

Both May studies used a 400-output-token ceiling. Critical review raised the possibility that the ceiling could interact with requested length, particularly BA2's 20-line poems, and thereby contribute to apparent model × length behavior.

D2 asks:

> Is there direct or proximal evidence that analyzed outputs reached the 400-token ceiling, and is any such evidence concentrated in particular studies, models, prompts, or BA2 length-cap conditions?

### Data

Audit the frozen raw JSONL inputs used by the September harmonizer:

- BA1: `Bullshit_Assay_1/Results and Heuristics/results.jsonl`
- BA2: `Bullshit_Assay_2/Results and Analysis/results_final_raw_5400.jsonl`

Restrict the main audit to successful, non-empty responses that were eligible for September text-feature analysis.

### Preserved termination evidence

The BA2 runner preserved:

- provider-reported `output_tokens`;
- requested `max_tokens` (= 400);
- Anthropic `raw_response.stop_reason`;
- OpenAI `raw_response.status`.

BA1 preserves provider-reported output-token counts and the 400-token ceiling but does not preserve equivalent provider termination metadata for every call.

### Fixed audit flags

For each successful record compute:

1. **direct_cap_flag**
   - Anthropic: `raw_response.stop_reason == "max_tokens"`;
   - OpenAI: `raw_response.status == "incomplete"`.

2. **at_or_above_cap**
   - provider-reported `output_tokens >= max_tokens`, where both are present.

3. **near_cap_95**
   - provider-reported `output_tokens / max_tokens >= 0.95`, where both are present.

`direct_cap_flag` is the principal truncation indicator. Token-count flags are proximity diagnostics and are not automatically interpreted as proof of visible-text truncation, especially where provider usage accounting may include non-visible output tokens.

### Summaries

Report counts and fractions of each flag:

- by study;
- in BA2 by requested line cap (5, 10, 20);
- in BA2 by model × requested line cap;
- in BA2 by prompt ID.

Also report output-token median, 95th percentile, and maximum for the same BA2 length-cap summaries.

### Conditional sensitivity rule

A sensitivity rerun is triggered **only if one or more BA2 analyzed responses has `direct_cap_flag = true`**.

If triggered:

- remove those directly flagged BA2 rows by `source_run_id` from the frozen harmonized table;
- rerun only the frozen P4 leave-one-length-cap-out body-only classifier;
- retain the same feature set, preprocessing, classifier, held-out groups, and pooling rule;
- report the original frozen P4 length result beside the exclusion sensitivity result.

If no BA2 `direct_cap_flag` is observed, no sensitivity classifier is run.

Near-cap token counts alone do not trigger exclusion because they are not direct termination evidence.

## 4. Interpretation boundaries

These diagnostics refine manuscript language; they do not create a new confirmatory layer.

In particular:

- D1 cannot show that the target environment contains a context-independent model trait.
- D1 cannot identify a causal effect of genre, category, or task form.
- D2 cannot infer truncation from provider token counts alone when direct termination metadata do not support it.
- A clean D2 audit does not prove that the 400-token ceiling had no behavioral effect below the ceiling; it addresses the narrower concern of ceiling contact/truncation.

## 5. Reproducibility commitments

The diagnostic script must:

- record SHA-256 hashes for all analyzed inputs;
- verify the frozen harmonized feature-table hash before D1;
- verify the frozen primary-result JSON hash before any conditional P4 comparison;
- record Python, NumPy, pandas, and scikit-learn versions;
- use fixed deterministic seeds;
- write only under `September_2026_Secondary_Analysis/results/post_review_diagnostics/`;
- modify no frozen May or September artifact.

No manuscript claim should be revised from these diagnostics until the plan and implementation are frozen in version control.
