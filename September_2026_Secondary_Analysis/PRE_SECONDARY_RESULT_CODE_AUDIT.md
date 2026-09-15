# Pre-secondary-result code audit — locked S1-S5

**Audit basis:** `SECONDARY_ANALYSIS_PLAN.md`, `HARMONIZED_CODING_SPEC.md`, and the frozen P1-P5 implementation/results boundary.  
**Result:** **PASS for pre-S-result implementation.** No change to the locked S1-S5 scientific questions was identified.

## S1

- Uses BA1 poetry versus BA2, as specified.
- Computes per-model means for every locked numeric body feature.
- Standardizes the six model means within each study.
- Reports six-model Spearman rank stability.
- Reports model-level direction agreement relative to the within-study six-model mean.
- Adds deterministic stratified bootstrap uncertainty while preserving model × prompt-ID composition.

## S2

- Adds exactly the four full-surface features permitted by the locked harmonized specification.
- Repeats P1-P4 only; P5 is not converted into a classifier analysis.
- Preserves grouped cross-study, cross-genre, phrasing, and length-cap transfer definitions.
- Preserves training-only preprocessing.
- Leaves binary preamble/title indicators unstandardized.
- Reports deltas from the already frozen body-only P1-P4 results rather than altering or replacing them.

## S3

- Recomputes BA2 descriptive model differences from the harmonized body parser.
- Covers all 22 locked body features.
- Uses global eta squared and omega squared plus all pairwise Hedges' g values as effect-size summaries.
- Does not add mass response-level significance testing.

## S4

- Re-expresses every headline family explicitly named in the locked plan: em dash, meta preamble, title, opening concentration/entropy, line/block formatting, and pronoun/person tendencies.
- Reports BA1-all, BA1-poetry, and BA2 per-model summaries.
- Uses BA1-poetry versus BA2 rank stability as the direct same-genre cross-study comparison.

## S5

- Evaluates all 22 locked features in the balanced BA1 model × genre design.
- Reports model, genre, and interaction effect sizes.
- Uses a fixed eta-squared model-separation heuristic (`>= 0.06`) solely to flag features for expanded cell-mean reporting.
- Retains effect-size output for every feature, preventing selective disappearance of non-headline results.

## Guardrails

- Frozen-count checks require BA1 = 540 and BA2 = 5,398.
- BA1 model × genre cells must each contain exactly 30 records.
- Unexpected model identifiers fail closed.
- Numeric feature infinities fail closed.
- Frozen P1-P5 outputs are read-only inputs for S2 comparison.
- Post-primary `POST_PRIMARY_IA_PLAN.md` analyses are not implemented here.
- Outputs are isolated under `results/secondary_analysis/`.

## Dry run

A synthetic 5,938-row dataset matching the six-model BA1/BA2 structure, BA1 genre balance, BA2 phrasing/length design, surface fields, and required feature schema completed S1-S5 end to end. Bootstrap repetition counts were reduced only for the synthetic execution test. No real S1-S5 outcomes were loaded or inspected.
