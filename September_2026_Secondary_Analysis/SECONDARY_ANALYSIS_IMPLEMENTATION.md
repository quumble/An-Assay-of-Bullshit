# September 2026 Secondary S1-S5 Implementation

**Status:** Pre-S-result implementation clarification for the locked S1-S5 plan.  
**Locked plan:** `September_2026_Secondary_Analysis/SECONDARY_ANALYSIS_PLAN.md`  
**Primary-result boundary already known:** `f2f93897572b8b6e9f5f162dc4d51cb15fcd48ff`  
**Post-primary I&A work:** explicitly excluded from this implementation.

The S1-S5 questions were specified before the September harmonized outcome analyses. The implementation details below are fixed after P1-P5 were inspected but before any S1-S5 output is inspected. They are intended to resolve underspecified computational choices without changing the locked secondary questions.

## Global rules

- Input is the frozen 5,938-row harmonized feature table: BA1 = 540, BA2 = 5,398.
- Model order is the six-model order in the locked plan.
- The locked 22 body-only numeric features are used wherever the plan refers to harmonized body features.
- No random row-level cross-validation is introduced.
- No p-value battery is added. Secondary feature analyses emphasize effect sizes, rank stability, descriptive consistency, and transparent uncertainty.
- Base seed is `20260915`.
- The script writes only to `September_2026_Secondary_Analysis/results/secondary_analysis/`.
- The script reads the frozen P1-P5 JSON only to compute S2 full-surface-minus-body performance differences; it does not modify the primary results.

## S1 — Cross-study feature stability

For each of the 22 locked body features:

1. Restrict BA1 to poetry and use all BA2 rows.
2. Compute the six per-model means separately in each study.
3. Standardize those six model means within each study using population-SD z scores (`ddof=0`). Spearman correlation is rank-based, so the z transformation does not affect the rank correlation; it does make direction relative to the six-model study grand mean explicit.
4. Report Spearman rank correlation across the six models.
5. For each model, report whether its standardized mean is on the same side of zero in both studies.
6. Use 2,000 deterministic bootstrap resamples. Within each study, resample with replacement inside model × prompt-ID strata, preserving the observed prompt composition.
7. Report the percentile 95% interval for Spearman rho and the bootstrap probability of direction agreement for each model.

These are descriptive six-model stability summaries, not population-level inferential tests.

## S2 — Surface framing versus body style

Repeat P1-P4 using the locked full-surface additions:

- `preamble_present`
- `title_present`
- `preamble_token_count`
- `title_token_count`

Implementation:

- the 22 body features plus the two token-count features receive training-fitted median imputation and standardization;
- the two binary indicators receive training-fitted most-frequent imputation and are passed through without z-scoring;
- the classifier is scikit-learn default L2 `LogisticRegression`, matching the frozen primary classifier family;
- P1/P2 receive 10,000 deterministic stratified bootstrap resamples of the fixed BA1 predictions, preserving model × prompt-ID strata;
- P3 and P4 use the same held-out groups and pooled definitions as the frozen primary implementation;
- the frozen P1-P4 JSON is used to report full-surface minus body-only deltas without rerunning or altering the body-only primaries.

## S3 — Corrected Study 2 descriptive effects

For every locked body feature in BA2:

- report per-model `n`, mean, SD, and median;
- report global one-way model-effect eta squared (`eta_squared`);
- report global omega squared (`omega_squared`);
- report all 15 pairwise Hedges' g values in fixed model order, with sign defined as model A minus model B.

No feature is selected or suppressed based on its effect size. No response-level p-values are reported.

## S4 — Previously salient May signatures

Produce harmonized per-model summaries for three scopes:

- all BA1 records;
- BA1 poetry only;
- BA2.

The locked headline families are operationalized as:

- **em dash:** mean em-dash events per 100 words and prevalence of at least one em dash;
- **meta preamble:** response-level preamble rate;
- **title:** response-level title rate;
- **opening concentration/entropy:** first-token Shannon entropy in bits, modal first token, and modal-token share;
- **line/block formatting:** mean body word count, nonempty line count, stanza count, mean words per line, and within-response words-per-line SD;
- **pronoun/person tendencies:** mean first-singular, first-plural, second-person, and third-person pronoun shares.

For scalar headline summaries, also report the six-model Spearman rank correlation between BA1 poetry and BA2. The modal opening token itself is descriptive and is not rank-correlated.

## S5 — Study 1 genre interactions

All 22 locked features are evaluated; none are hidden based on results.

For each feature, exploit the balanced BA1 6-model × 3-genre design (30 records per cell) to decompose sums of squares into:

- model;
- genre;
- model × genre interaction;
- within-cell error.

Report:

- eta squared for model;
- eta squared for genre;
- eta squared for model × genre;
- partial eta squared for model × genre.

For the plan's phrase “features with substantial model separation,” use a fixed descriptive heuristic of `eta_squared_model >= 0.06`. This threshold is fixed before S results are inspected and is not a significance criterion. Model × genre cell means are exported for the flagged features; effect sizes for all 22 features remain available.

## Environment and reproducibility

The result JSON records Python, platform, NumPy, pandas, and scikit-learn versions plus SHA-256 hashes for both the harmonized input and frozen primary-results JSON.

A synthetic 5,938-row dry run matching the frozen study structure completed S1-S5 end to end. The dry run used synthetic features and reduced bootstrap counts for execution testing only; it contains no real S1-S5 outcomes.
