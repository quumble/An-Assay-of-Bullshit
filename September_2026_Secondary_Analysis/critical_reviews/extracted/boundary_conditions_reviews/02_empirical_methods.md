# Review 2 — Skeptical empirical-methods referee

**Perspective:** Experimental design, estimands, statistical interpretation, and falsifiability.  
**Material reviewed:** The complete supplied working draft, including Methods, Results, and Discussion.  
**Scope:** This review assesses the reported completed analyses and separately evaluates the proposed prospective experiment. I did not inspect raw responses, analysis code, preregistrations, or the absent tables and figures, replicate experiments, or verify external references. Numerical observations below are consistency checks on the manuscript, not independent validation.

## Overall verdict

**Promising empirical paper; major revision of inferential scope and reporting before submission.** The positive finding is persuasive on the manuscript's own terms: a fixed, interpretable feature representation allows a classifier trained on BA2 poetry to identify generators in independently collected BA1 poetry substantially above balanced-class chance. The careful separation of primary, secondary, and outcome-informed exploratory analyses is a particular strength.

The negative finding needs more discipline. Poor transfer measures the failure of a particular trained decision rule, using particular features, across particular environments. It does not establish that model information disappeared or that a behavioral signature reached an intrinsic boundary. The paper sometimes maintains this distinction and sometimes crosses it. Establishing the difference between reduced target-domain separability and failed transport of a source-domain classifier would materially strengthen the central argument.

## What is already strong

- **Independent collection:** P1 evaluates on a separate study rather than simply a random held-out subset of the training study.
- **Shared processing:** Re-extracting features from frozen raw text addresses a real comparability problem. Training-only imputation and scaling avoid a common source of leakage.
- **Transparent evidence layers:** IA1–IA3 are clearly identified as outcome-informed. Retain this distinction in figures and captions as well as prose.
- **Appropriate population restraint:** The explicit prohibition on provider- or tier-level population inference is correct for one model per provider-by-tier position.
- **Useful specificity:** Classwise recall reveals that 48.9% aggregate accuracy masks considerable heterogeneity, including 10% recall for one model.

## Priority 1 — Define the assay's estimand and repair its asymmetric interpretation

**Locations:** Introduction, “Classification and transfer analyses,” Discussion: “Attribution as an assay rather than an endpoint.”

The estimand is approximately: *accuracy of a specified classifier trained under source environment A and evaluated on outputs under target environment B, for six fixed model labels and a specified feature representation*. That is narrower than persistence of “behavioral information” in general.

Successful transfer supports recognizable model-associated information in the measured features. Failed transfer has several explanations: weaker target-domain separation, changed feature-to-label relationships, insufficient source data, or an inadequate classifier. These alternatives are central to the proposed interpretation, not peripheral limitations.

**Concrete revision:** Add equal-budget within-environment baselines for every target, using held-out target examples and matched class balance. Present target-only accuracy beside transferred accuracy and chance. High within-target accuracy with low transfer would demonstrate failure of transport despite retained identifiability; low values for both would establish only limited identifiability under this assay. Any new analysis must be labeled exploratory. Replace “the change identified a boundary on the original signature” with “the change identified a boundary on transport of the measured signature using this classifier.”

Similarly, “There was no hidden set of simple punctuation or grammatical features” overstates what the fixed feature-family comparisons tested. Say that none of the tested representations yielded strong transfer with the chosen classifier.

## Priority 2 — Make the genre comparison commensurate

**Locations:** “Source studies,” IA1, Results: “Different environmental changes disrupted the signature to different degrees.”

IA1 addresses training-set size, but not all differences between P1 and P3. P1 tests BA1 poetry; pooled P3 tests poetry, story, and animal outputs. The cleanest same-target comparison is matched-budget BA2 poetry → BA1 poetry against BA1 story + animal → the same BA1 poetry set. That compares sources while holding the target examples fixed. It still does not isolate a causal effect of genre, because source study and source tasks also differ.

“Animal” is not sufficiently defined to establish that this is a genre manipulation. If it changes topic, task instructions, or expected response format, the experiment tests a bundled task-context shift. Exact prompts, requested length conditions, and allocation weights are indispensable here.

**Concrete revision:** Lead with the common poetry target comparison, report its uncertainty, and describe pooled P3 as a complementary summary. Include all prompt templates in an appendix. Soften “genre change was considerably more disruptive” to a statement about the tested cross-task/genre transfers unless the actual prompts justify the stronger label. IA1 supports “not explained by training-set size alone,” which is a defensible and useful conclusion.

## Priority 3 — Separate sources of uncertainty

**Locations:** P1 confidence interval, S1, IA1 percentile interval, P3/P4 pooled accuracies.

P1's test-response bootstrap and IA1's distribution across training subsamples quantify different uncertainties. The IA1 interval conditions on the same 180 test poems; it is not a confidence interval for the population-level P1–P3 difference. Its lower tail exceeding observed P3 values is descriptive, not a calibrated test of that contrast.

**Concrete revision:** Label every interval by its resampling unit and what remains fixed. For the common-target comparison, a paired test-example bootstrap can quantify conditional uncertainty in the accuracy difference; explicitly distinguish that from variation across training samples. Report intervals for P3/P4 and full-surface gains, including their shared-example structure. Do not treat repeated training subsets or overlapping folds as independent experiments.

Specify whether response bootstraps preserve model × prompt × length cells and whether calls share batches, sessions, or execution order. The appropriate resampling unit depends on the actual collection process. Explain pooled weighting and provide confusion matrices: balanced overall classes do not make aggregate accuracy representative of all six models.

## Priority 4 — Distinguish stable ordering from stable behavior

**Locations:** S1, Results: “The transferable signature was heterogeneous rather than unitary.”

Spearman correlations across six model means measure relative ordering, not agreement in absolute rates or persistence of particular between-model contrasts. Strong correlations can coexist with large common shifts or sharply changed effect magnitudes. Conversely, unstable rankings of near-identical means need not reflect substantively important reorganization.

**Concrete revision:** Plot paired per-model means with uncertainty and units for the central features. Show between-study changes and a small set of clearly justified model contrasts. Report the promised bootstrap intervals, not just selected large correlations. Provide all 22 results and identify tied ranks. With six fixed models, response-level resampling assesses precision for these snapshots, not generalization to a population of models.

For S5, define η² precisely: sums-of-squares type, denominator, fitted terms, and handling of requested length. A larger interaction η² than main-effect η² does not by itself demonstrate rank reversal. Display interactions for semicolons and em dashes so readers can distinguish magnitude changes from reversals.

## Priority 5 — Audit whether measurement choices create part of the signal

**Locations:** “Parser validation,” “Harmonized features,” “Response presentation carried additional model-associated information.”

The parser validation is encouraging, but the reported boundary agreements lack denominators. A .920 score over a small number of detected preambles means something different from .920 over all 180 responses. State how correctness was adjudicated, whether false negatives enter boundary evaluation, and whether one or multiple humans annotated the sample.

Specify the tokenizer/POS model and version, pronoun vocabulary, zero-pronoun handling, punctuation patterns, and stanza rules. Sparse punctuation rates on short outputs and pronoun shares with small denominators can be unstable. Missing-value patterns may themselves identify models; show their frequency by model and condition.

The shared 400-token cap deserves explicit treatment. Report termination reasons and truncation rates by condition and model, if available. A common cap does not imply common effective constraint severity, especially across tasks. A sensitivity analysis excluding cap-hit responses could reveal whether apparent style partly reflects incomplete generation; label it exploratory and discuss resulting selection.

Finally, the four added surface features demonstrate presentation information, but cannot exclude differential parser errors. An error breakdown by model and study would help. Describe S2 as adding presentation indicators, rather than “restoring titles and preambles,” since their text is not actually modeled.

## Prospective design and minimum revision package

The proposed fully crossed follow-up is an appropriate **future experiment**, not evidence already supplied. Add multiple independently sampled prompt instances per environment cell, repeated collection waves, randomized/interleaved call order, and reciprocal transfer. Preregister a primary transfer contrast and meaningful retention criterion. Crossing six labels with one wording per cell would otherwise preserve dependence on particular prompt realizations.

For the current paper, the highest-value revision package is: exact prompts and collection metadata; within-target baselines; the same-target matched-budget comparison; correctly labeled uncertainty; full feature-stability results and interaction plots; and reproducible specifications for features, parser, and classifier. Also link dated analysis plans and explain what September analysts already knew from May: “specified before harmonized outcomes” is valuable, but differs from being unaware of the underlying data's patterns.

With those changes, the paper can make a clear, credible claim: **these six models retained measurable attribution signal across several tested contexts, while the transportability of a specified stylistic assay varied substantially across contexts.** That is strong enough without claiming that failed attribution establishes the disappearance of model-associated behavior.
