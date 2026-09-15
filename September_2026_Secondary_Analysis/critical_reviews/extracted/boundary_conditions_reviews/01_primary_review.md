# Primary review: contribution, inference, and revision priorities

**Reviewer:** Primary assistant  
**Manuscript:** *From Fingerprints to Boundary Conditions: Model-Associated Style Under Distribution Shift*  
**Basis:** The full supplied working draft. This is a manuscript review, not a replication or an external literature audit. Raw data, scripts, preregistrations, referenced papers, and the missing tables and figures were not supplied for inspection. Numerical results are assessed as reported.

## Overall assessment

This is a promising empirical paper with a clear central question and a coherent argument. Its strongest contribution is the combination of interpretable features, independently collected poetry data, several kinds of transfer, and an explicit distinction between planned and outcome-informed analyses. The body-versus-presentation comparison is particularly useful: it makes the object of attribution more concrete than a generic claim that models have a recognizable “style.”

My recommendation is **major revision before submission**, primarily to tighten the inferential claims and complete the reproducibility account. I would preserve the central framing. I would narrow what the classifier is said to establish, give readers the necessary reference conditions, and let the empirical results occupy more space than repeated statements of the thesis.

The paper can support an interesting conclusion without establishing a general hierarchy of environmental disruptions or proving that weak transfer reflects disappearance of model information.

## 1. Separate persistence of a fitted decision rule from persistence of a behavior

**Locations:** Introduction, “Attribution as an assay rather than an endpoint,” and Conclusion.

The positive-transfer interpretation is reasonably strong: when the fixed pipeline predicts model labels in a new sample above a suitable baseline, the measured representation contains information usable across those environments. The negative-transfer interpretation is weaker. A classifier can fail because the representation changes scale, its decision boundary stops working, the fitted classifier is inadequate, or useful information moves into unmeasured features. None requires model-associated behavior to disappear.

The draft acknowledges the sparse representation in Limitations, but some main-text language goes further. “When transfer deteriorated, the change identified a boundary on the original signature” can be read as a boundary in the behavior itself. Likewise, “There was no hidden set of simple punctuation or grammatical features” is stronger than the reported fixed feature-family analyses establish. Those analyses do not search every subset, interaction, or decision rule.

**Revision:** Define the central object as transferability of a specified representation-and-classifier assay. Use a formulation such as:

> Reduced transfer identifies a limit on the portability of this fitted attribution assay; feature-level analyses help assess whether that limit also reflects changes in particular model-associated tendencies.

Then distinguish three outcomes throughout: preserved classification, preserved model ordering on a measurement, and preserved absolute behavior. They are related but not interchangeable. A classifier can retain accuracy while the particular feature behind “Model X tends to do Y” reverses.

## 2. Make the comparison across environmental changes interpretable

**Locations:** Classification and transfer analyses; “Different environmental changes disrupted the signature to different degrees.”

The 61.9%, 48.4%, and 22.4% pooled accuracies are informative descriptions of these protocols. They do not, by themselves, place phrasing, length constraint, and genre on one common scale of disruption. Their training distributions, target distributions, sample sizes, and potentially baseline separability differ.

IA1 addresses a real objection, but only one: the training-size imbalance between P1 and P3. It does not remove the difference between training on poetry and training on two other task categories. Nor does it equalize the difficulty of every target set. The most direct existing contrast is matched-size BA2-to-BA1-poetry transfer against BA1-story-plus-animal-to-BA1-poetry transfer, because both use the same 180 target poems.

**Revision:** Lead with that shared-target comparison. Describe the broader ordering as a pattern in the tested protocols. Add leakage-safe within-environment reference accuracies with comparable budgets if the data permit; label these new analyses exploratory. Readers need to know whether low cross-genre accuracy represents a drop from strong within-genre discrimination or a difficult target even without transfer.

Avoid saying IA1 establishes that training size is irrelevant. It shows that reducing P1 to the P3 training budget does not eliminate the observed contrast.

## 3. Explain what was manipulated, especially “genre”

**Locations:** Source studies; Table 1 placeholder.

“Story,” “animal,” and “poem” do not tell the reader whether BA1 manipulated genre, topic, task, or several at once. “Animal” particularly needs its actual prompt and intended response form. The paper's strongest comparative interpretation depends on this distinction.

**Revision:** Supply all prompt templates verbatim, including each BA1 length request. Show which dimensions are shared across studies and which change together. If animal is a topic or task category rather than a genre, use “task/genre condition” where appropriate. Explicitly document whether cross-study poetry prompts are identical, overlapping, or materially different.

A fixed 400-token output cap also deserves direct attention. Report available termination reasons and truncation frequencies by model and condition. The requested 20-line condition may interact with that cap. Truncation could influence structure, punctuation, parsing, and attribution; its relevance cannot be inferred from the cap alone.

## 4. Give uncertainty statements their correct scope

**Locations:** Parser validation; IA1; Results on feature stability and presentation.

The paper commendably labels IA1's interval as percentiles of repeated training-sample outcomes. Keep that distinction prominent: those percentiles condition on the same BA1 test set and are not a confidence interval for a population-level transfer contrast. The statement about the “lower tail” exceeding P3 is descriptive, not an uncertainty-adjusted comparison between experiments.

For classification intervals, specify the resampling unit and strata, and whether the classifier remains fixed. For feature-stability bootstraps, specify whether responses are resampled within model and prompt cells. Six model means offer limited resolution, and the dependence induced by prompt conditions matters to the interpretation.

Report the promised S1 intervals, alongside scatterplots or the six means themselves. Rank preservation alone conceals effect magnitude, ties, and nearly indistinguishable model means. Define the eta-squared denominator and factorial decomposition, including the role of BA1 length conditions.

The presentation-feature gains are substantial enough to be a major result. Provide paired uncertainty for the accuracy differences where feasible, using the same held-out responses. A surface-only comparison would clarify how much identification resides in presentation versus its combination with the body. It would be an additional exploratory diagnostic, not a prerequisite for reporting the joint gain already observed.

## 5. Complete the methods that make the findings auditable

**Locations:** Models; Harmonization; Harmonized features; Reproducibility.

Several essential details are deferred to artifacts that are mentioned but not linked. Include a supplement or repository with the exact parsing rules, feature definitions, software and tagger versions, logistic-regression settings, missingness handling, seeds, and analysis specifications.

Especially clarify zero-pronoun responses: the person-share features have no natural denominator there. Explain whether such values are zero, missing, or otherwise encoded, and whether that convention itself carries structural information. Define punctuation-event detection and the membership of every IA2 feature family; mean word length is currently grouped with structural measures despite being a different kind of measurement.

For parser validation, report numerators and denominators for each field, the annotation procedure, and the definition of “agreement.” Boundary accuracy presumably applies to a smaller subset than all 180 responses. Explain whether the locked sample covered the BA1 categories adequately and whether any parser changes followed validation.

Finally, distinguish dated immutable model versions from API identifiers whose underlying version was not independently verified. Report collection dates, endpoint metadata available in the records, and generation options. “Same named model identifiers” and “same model snapshots” should not be treated as equivalent without supporting provenance.

## 6. Keep the argument, reduce the repetition

The Introduction, Results summary, opening Discussion, several Discussion subsections, and Conclusion repeatedly make the same context-dependence argument. That repetition currently displaces the empirical detail needed to evaluate it.

Retain one clear statement of the thesis in the Introduction and one developed interpretation in the Discussion. Use the recovered space for a transfer-protocol table, a complete confusion matrix, feature-stability plots, and practical examples of how a model-level claim changes when its tested domain is stated. The weak Opus recall is worth interpreting: average transfer should not imply comparable persistence for every tested model.

Complete the bibliography and replace all figure/table placeholders before submission. Correct the nonsequential figure callouts. The contribution should be framed as a specific empirical demonstration and useful way of reporting scope; the draft alone cannot establish that the general conceptual distinction is novel.

## Recommended revision sequence

1. Narrow the assay and negative-transfer claims; define the three kinds of persistence.
2. Add exact prompts, model provenance, feature definitions, and linked analysis records.
3. Center the shared-poetry-target comparison and clarify uncertainty throughout.
4. Add the missing exhibits and a small set of targeted diagnostics, clearly marked exploratory.
5. Compress the repeated thesis statements and finish with the strongest supported empirical claim.

My preferred final claim is that these six tested model configurations exhibit measurable, feature-dependent transfer under the specified creative-writing protocols, with particularly limited cross-task/genre portability for the present assay. That is already a substantive result; it does not need the stronger suggestion that failed classification locates the full boundary of model-associated behavior.
