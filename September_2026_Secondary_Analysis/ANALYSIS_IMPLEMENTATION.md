# September 2026 Primary Analysis Implementation

**Status:** Pre-result implementation clarification for the locked P1-P5 plan.
**Source dataset boundary:** `c14f6b433d4c277a9dc0acc8d44c46ec8570c2cb`

This file does not add hypotheses or alter the locked primary analyses. It fixes implementation details needed to make P1-P5 deterministic before outcome inspection.

## Fixed implementation choices

1. **Primary feature vector.** Exactly the locked body-only harmonized numeric features from `HARMONIZED_CODING_SPEC.md`: six length/line features, five POS ratios, four pronoun shares, and seven punctuation rates. Raw counts, opening-token strings, title/preamble indicators, and response text are excluded from P1-P4.
2. **Classifier pipeline.** `SimpleImputer(strategy="median")` -> `StandardScaler()` -> `LogisticRegression()` with scikit-learn library defaults. Imputation and standardization are fitted on training data only. No test-set fitting or feature selection occurs.
3. **Label order.** Confusion matrices use the six model identifiers in the exact order listed in the locked analysis plan. Provider confusion matrices use `anthropic`, `openai` when those are the observed labels; otherwise observed provider labels are sorted and recorded.
4. **P1/P2 confidence intervals.** 10,000 deterministic stratified bootstrap resamples of the fixed BA1 poetry test predictions. Resampling occurs with replacement within `model x prompt_id` strata. Percentile 95% intervals are reported for accuracy and balanced accuracy. Base seed: `20260915`.
5. **P3 pooled result.** Each BA1 record is predicted only in the fold where its genre is held out. The three held-out prediction sets are concatenated once and pooled metrics are computed on that union.
6. **P4 pooled results.** Phrasing-transfer and length-cap-transfer are pooled separately. Each BA2 record is predicted once within each transfer family, in the fold corresponding to its held-out group. The two transfer families are never pooled together.
7. **P5 entropy.** Shannon entropy uses log base 2 and is reported in bits. For each model, each Study 2 rarefaction draws 30 poems **without replacement**, repeated 10,000 times. Deterministic model-specific RNG streams are derived from seed `20260915`. The 2.5th and 97.5th percentiles form the rarefaction interval.
8. **Output discipline.** The script writes JSON summaries plus CSV confusion matrices and rarefaction summaries. It does not modify the harmonized dataset or any frozen May artifact.
9. **Environment record.** The analysis output records Python, NumPy, pandas, and scikit-learn versions plus the source-data SHA-256 hash.

These choices are intended as implementation clarifications, not deviations from the locked scientific plan.
