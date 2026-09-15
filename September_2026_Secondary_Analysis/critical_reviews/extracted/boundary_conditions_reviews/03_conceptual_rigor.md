# Review 3 — Conceptual rigor and interpretation

**Perspective:** A theory-oriented referee evaluating the logic of the claims, the meaning of the measurements, and the scope of the proposed contribution.

**Scope:** I read the complete working draft. This is an independent review of its argument and reported findings; I have not audited the underlying data, code, cited papers, or historical analysis records. Novelty comments concern the contribution as the draft frames it, not a verified literature-priority claim.

## Overall assessment

The draft has a worthwhile methodological thesis: a behavioral difference attributed to a model is more informative when accompanied by evidence about the environments over which it generalizes. The empirical synthesis is well suited to illustrating that thesis. Its strongest result is the conjunction of substantial cross-study poetry attribution, heterogeneous feature stability, and weak cross-genre transfer under the selected representation and classifier.

The main conceptual revision should make **successful and unsuccessful transfer explicitly asymmetric evidence**. Successful transfer demonstrates predictive information accessible to this assay. Unsuccessful transfer does not establish that model-associated information disappeared, that a particular behavioral tendency reversed, or that the environment itself caused the difference in transfer performance. Several passages currently move too quickly among these interpretations.

**Verdict:** Major conceptual revision, with a promising contribution. Much can be resolved through sharper definitions and calibrated wording; a few targeted analyses would materially strengthen the central interpretation.

## What works particularly well

1. **The distinction between association and invariance is useful.** “A model effect is not the same as a context-invariant property” is the clearest discussion subsection. A feature can distinguish models locally while expressing those differences differently elsewhere. The semicolon example makes this concrete.
2. **The draft avoids several tempting overclaims.** It explicitly limits provider/tier inference, labels outcome-informed analyses, and acknowledges that the design is not fully crossed. These are substantive strengths.
3. **The decomposition supports a more informative account than one attribution score.** Body versus response presentation, and structural versus grammatical/punctuation representations, expose different ways models can remain distinguishable.
4. **The prospective proposal follows naturally.** A balanced, reciprocal transfer design is a credible next experiment. It should remain clearly separated from what the present synthesis has already established.

## Priority 1 — Define precisely what the attribution assay detects

**Relevant sections:** Introduction; “Attribution as an assay rather than an endpoint”; “Summary of the transfer pattern.”

The sentence “When transfer deteriorated, the change identified a boundary on the original signature” needs qualification. Consider a counterexample: two models retain sharply distinct punctuation rates in a new genre, but their relative ordering reverses. A classifier trained on the first genre could systematically fail while model identity remains fully recoverable in the second. Alternatively, both models could undergo a common shift that moves observations across the old decision boundary while preserving separation. A linear classifier can also fail to recover an existing nonlinear relationship.

These possibilities are compatible with low cross-genre performance. Accordingly, failure identifies a limit to **transporting the fitted decision rule**, not necessarily a limit to the existence of a signature. The introduction already uses the more careful “may have been”; maintain that restraint throughout.

A useful definition would be:

> We define transferability operationally as the ability of a source-trained classifier, using a fixed representation, to predict model identity in a specified target environment. Transfer failure does not by itself distinguish information loss from changes in encoding or limitations of the classifier.

Correspondingly, replace “There was no hidden set of simple punctuation or grammatical features that behaved as a context-free model identity” with “None of the prespecified feature families supported strong cross-genre transfer with the fitted linear classifier.” The latter is the actual tested claim.

## Priority 2 — Separate four different meanings of persistence

**Relevant sections:** Feature-stability results; “A model effect…”; prospective design.

The manuscript alternates among preserved attribution accuracy, preserved model rankings, preserved feature magnitudes, and preserved model effects. These are related but non-equivalent outcomes.

For example, a high Spearman correlation across six model means preserves ordering while permitting substantial changes in absolute values. Conversely, a sizable interaction can reflect amplification of stable ordering rather than a reversal. A composite classifier may transfer even when individual feature relationships change, because its remaining predictors compensate.

Introduce a compact operational framework:

- **Predictive transfer:** Does a fixed source-trained rule identify models in the target?
- **Ordinal stability:** Do models retain their relative ordering on a named measurement?
- **Magnitude stability:** Do named differences remain similar in size?
- **Target separability:** Are models distinguishable when the classifier is trained within the target?

The current study directly addresses the first two and reports evidence relevant to contextual modulation. It does not establish all four. In particular, the interaction results support context dependence but do not alone demonstrate reordered models. Show model-by-genre feature profiles before describing particular features as “reorganized.”

## Priority 3 — Calibrate the ranking of environmental disruptions

**Relevant sections:** “Different environmental changes disrupted the signature to different degrees”; Conclusion.

The matched-size analysis usefully addresses one concrete alternative explanation. It does not isolate the effect of genre from all other differences between the comparisons. Source composition, source-target similarity, prompt content, label separability, and collection conditions remain bundled differently. The within-BA2 phrasing and line-cap holdouts are likewise distinct tasks, not calibrated doses of environmental change.

Also, “animal” is not self-evidently a genre. If it denotes a topical instruction while “story” denotes a textual form, the genre axis mixes constructs. Supply exact prompts and explain the task taxonomy before assigning conceptual significance to genre as such.

A defensible formulation is: “Cross-genre transfer was weaker than the other tested transfers in this design; equalizing sample count did not remove that contrast.” Avoid implying a general ordering of genre, constraints, and wording as sources of disruption.

The most informative additional analysis would estimate within-environment performance using comparable training budgets. Weak transfer into a target with strong local attribution suggests a portability problem. Weak target-local attribution instead suggests limited distinguishability under that environment or representation. These are different scientific findings.

## Priority 4 — Distinguish six-label prediction from six-model individuality

**Relevant sections:** Models; primary transfer results; response presentation results.

The descriptive provider caveat appropriately blocks population-level provider inference. A separate issue remains: six-way accuracy above 16.7% need not imply fine-grained discrimination among all six snapshots. If an assay perfectly separated the two providers and guessed uniformly among each provider’s three models, expected six-way accuracy would already be 33.3%.

The 48.9% body result suggests additional discrimination overall, but uneven recalls—including 10% for Opus—make “the six tested snapshots exhibited…signatures” too uniform if interpreted individually. The packaging improvement could also reflect different levels of identity resolution.

Report the confusion matrix and, if feasible, conditional within-provider classification. Describe the primary result as recoverable model-label information **across this six-model set**, with uneven recognizability. This preserves the result without implying six equally portable individual signatures.

## Priority 5 — Make “style,” “structure,” and “delivery” explicitly operational

**Relevant sections:** Harmonized features; heterogeneous-signature results; “Different layers…”

The three-layer taxonomy is useful but not cleanly separable. Punctuation rates per 100 words can still depend on length and syntax; pronoun shares can reflect prompt content or narrative perspective; title detection partly operationalizes presentation. Removing length variables does not eliminate all structural influence. Mean word length also needs a clear conceptual placement within the feature-family definitions.

Replace “not primarily exploiting coarse structural differences” with the narrower finding that substantial predictive performance remained without the designated structural variables. That is evidence against dependence on those explicit predictors, not a causal decomposition of the signature into independent sources.

Include the exact family membership and distinguish all punctuation “rates” from response-level “prevalence.” This will make the taxonomy inspectable rather than suggest a mechanistic account the draft properly disavows.

## Contribution and revision priorities

The most defensible contribution is an interpretable secondary case study showing that different operational notions of behavioral persistence can diverge. “Boundary conditions” is valuable framing, but the current design samples specific transfers rather than locating a complete boundary of validity. Call these **tested limits of transfer** where precision matters.

I would prioritize: (1) defining the assay and its asymmetric evidential logic; (2) separating persistence outcomes; (3) calibrating environmental comparisons and clarifying “animal”; (4) adding target-local baselines and confusion analysis if feasible; and (5) tightening the feature taxonomy. None requires abandoning the paper’s central thesis. They would make the concluding claim—that the scope of a model-level description is itself an empirical question—substantially harder to misread.
