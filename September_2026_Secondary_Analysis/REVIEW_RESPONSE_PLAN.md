# Critical Review Response Plan — Pre-Diagnostic Freeze

**Status:** written after critical review and before running any reviewer-motivated post-review diagnostics.

## Purpose

This note records the manuscript-level concerns raised during critical review and the decisions made before any D1/D2 diagnostic results are observed.

## Agreed manuscript revisions independent of D1/D2 outcomes

1. Replace broad causal language about “genre” with the exact operational contrast where appropriate. BA1 contains three creative-writing categories/tasks: story, animal-description, and poem. The preregistered analysis label P3 may remain “cross-genre” for provenance, but interpretive prose should prefer “cross-category,” “creative-writing task/form,” or similarly exact language.
2. Treat successful predictive transfer and failed predictive transfer asymmetrically. Successful transfer demonstrates portability of model-label information under the specified representation and fitted rule. Failed transfer does not by itself establish disappearance of the underlying model-associated signature.
3. Distinguish at least four concepts in the revised paper:
   - predictive transfer;
   - ordinal stability of a named feature;
   - magnitude stability of a named feature;
   - target-local separability.
4. IA1 rules out training-set size as an explanation for the observed P1/P3 contrast; it does not transform the two transfer designs into a causal experiment.
5. Narrow the empirical object from broad “language-model behavior” to model-associated stylistic/output behavior. Broader behavioral applications belong in implications and future work.
6. Replace “model snapshots” with “named model identifiers/endpoints tested in May 2026” unless immutability is established. Only the Haiku identifier is explicitly date-pinned in the archived BA2 materials.
7. Retain macrostructure, microstyle, and delivery as descriptive groupings only; do not imply independent latent or mechanistic factors.
8. Make explicit that the logistic-regression classifier is a fixed, interpretable assay rather than an attempt to maximize attribution performance.
9. Clarify that pooled P4 values combine held-out predictions from separate leave-one-group-out fits.
10. Tighten the manuscript by reducing repeated statements of the same boundary-condition thesis.

## Bounded post-review diagnostics authorized

Only two reviewer-motivated diagnostics are authorized before manuscript revision:

### D1 — BA1 poetry target-local separability
Purpose: determine whether weak story/animal -> poetry transfer reflects loss of target separability or failure of transport from the source categories.

Planned status: outcome-informed, post-review exploratory diagnostic.

### D2 — output-token ceiling audit
Purpose: determine whether the 400-token generation ceiling plausibly contaminates BA2 long-line conditions, especially the 20-line condition.

Planned status: outcome-informed, post-review exploratory diagnostic.

No other reviewer-suggested analysis is authorized at this stage. Surface-only attribution, within-provider conditional classification, expanded classifier comparisons, and broad new sensitivity analyses are deferred unless D1/D2 reveal a concrete need.

## Interpretation boundary

The post-review diagnostics may sharpen or narrow interpretation, but they do not retroactively change the evidentiary status of P1-P5, S1-S5, or IA1-IA3.

The pre-diagnostic manuscript state and the external review packet are archived alongside this note so that any subsequent changes can be traced to the reviewer concerns recorded here.
