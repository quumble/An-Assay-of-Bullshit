# Post-Primary Interpretability & Access Plan — September 2026

**Project:** An Assay of Bullshit — September secondary analysis  
**Date:** 2026-09-15  
**Status:** Outcome-informed exploratory follow-up  
**Primary-result boundary:** `f2f93897572b8b6e9f5f162dc4d51cb15fcd48ff`  
**Locked pre-result analysis plan:** `f91608d8d5990f1a0e9da8b9ce6a8af32d2612ac`

## 1. Evidentiary status

This document was written **after inspection of the frozen P1-P5 primary results**.

Everything specified here is therefore outcome-informed and exploratory.

Nothing in this document:

- modifies P1-P5;
- changes the frozen harmonized dataset;
- changes the parser or feature definitions;
- changes the evidentiary status of S1-S5 in `SECONDARY_ANALYSIS_PLAN.md`;
- should be described as preregistered or prospectively specified before the primary results were known.

The purpose of this layer is interpretation: to determine what the primary transfer results can reasonably be said to measure and to make the findings intelligible without overstating them.

## 2. Why this follow-up is needed

The primary analyses established that model identity is recoverable from the locked body-only feature set under some forms of distribution shift, but that transfer varies substantially by condition and model.

Three interpretive problems became apparent after inspecting P1-P5.

### 2.1 Training-size confounding

P1 trained on 5,398 Study 2 poems and tested on 180 Study 1 poems, producing six-way accuracy of approximately 0.489.

Each P3 cross-genre fold trained on only 360 Study 1 records. P3 pooled held-out accuracy was approximately 0.224.

The difference is potentially meaningful, but the approximately fifteen-fold difference in training-set size prevents a strong inference that genre shift itself explains the P1-versus-P3 contrast.

### 2.2 Style versus response structure

The primary classifier combines several kinds of observable behavior:

- output length and line/stanza structure;
- word-length tendencies;
- part-of-speech composition;
- pronoun/person tendencies;
- punctuation rates.

These measures need not represent a single construct.

Some may reflect conventional writing style. Others may reflect instruction compliance, formatting behavior, or model-specific reactions to output constraints.

The P4 length-transfer results make this distinction especially important.

### 2.3 Attribution as instrument rather than endpoint

The scientific importance of P1-P4 is not primarily forensic authorship attribution.

Classification performance is useful because it provides an operational measure of how much model-associated behavior survives a change in environment.

The interpretive target is therefore **behavioral invariance under distribution shift**, not the existence of an immutable model “fingerprint.”

## 3. Terminology and interpretation rules

The following conventions apply to this exploratory layer.

### 3.1 Signature, not fingerprint

Prefer:

- `stylistic signature`;
- `model-associated behavioral signature`;
- `behavioral regularity`;
- `transferable signal`.

Avoid treating `fingerprint` as a technical conclusion. A fingerprint metaphor suggests uniqueness, permanence, and context invariance that the current results do not establish.

### 3.2 No personality inference

A repeatable statistical pattern is not evidence that a model has a personality, subjective trait, or stable internal persona.

Where trait language is useful as an analogy, it must remain explicitly statistical.

### 3.3 Provider results remain descriptive

Claude/GPT or Anthropic/OpenAI comparisons concern only the six named model snapshots tested.

There is no independent replication of provider family or model tier sufficient for population-level causal inference.

### 3.4 Separate style from task response

Where possible, interpretation should distinguish:

- stylistic composition;
- formatting/structural response;
- instruction compliance;
- interaction between model and production constraint.

A feature that predicts model identity is not automatically a stable stylistic trait.

## 4. IA1 — Training-size-matched cross-study transfer

### Question

How much of the difference between P1 cross-study poetry transfer and P3 cross-genre transfer remains when the P1 classifier is trained on the same number of observations as a P3 fold?

### Design

The frozen P1 test set remains unchanged:

- Study 1 poetry;
- 180 records;
- 30 records per model.

For each exploratory resample:

1. Start from the frozen Study 2 poetry training pool.
2. Draw exactly 360 training records without replacement.
3. Draw exactly 60 records per model.
4. Within each model, distribute the 60 records across the nine Study 2 prompt cells as evenly as possible:
   - six records from every prompt cell = 54;
   - six of the nine prompt cells contribute one additional record;
   - the six cells receiving the additional record are selected deterministically from the resample RNG.
5. Fit the exact frozen P1 classifier:
   - median imputation;
   - standardization fitted on the sampled training data only;
   - default L2 logistic regression;
   - identical 22-feature body-only vector.
6. Predict the unchanged 180-record Study 1 poetry test set.

Repeat for **1,000 deterministic resamples**.

Base seed: `20260915`.

Independent deterministic RNG streams should be derived from the base seed and resample index.

### Outputs

Report:

- accuracy for every resample;
- balanced accuracy for every resample;
- median accuracy and balanced accuracy;
- 2.5th and 97.5th percentiles;
- per-model recall distributions;
- the original full-training P1 result as a fixed reference;
- the three observed P3 held-out-genre accuracies as fixed descriptive references.

No null-hypothesis significance test is required.

The purpose is to determine whether the large P1-versus-P3 contrast remains visibly large after equalizing the training-data budget.

### Interpretation

If size-matched P1 remains substantially above P3, the interpretation that genre shift disrupts model-associated signatures becomes more credible.

If size-matched P1 approaches the P3 range, the original P1/P3 contrast should be interpreted primarily as confounded by training-set size.

Intermediate overlap should be reported as such rather than forced into a binary conclusion.

## 5. IA2 — Feature-family attribution

### Question

What kind of observable behavior carries model-identifying information across changes in study, genre, prompt wording, and length constraint?

### Fixed feature families

No feature family will be defined after inspecting its result.

#### A. Form and structure

- `body_word_count`
- `body_line_count_nonempty`
- `body_stanza_count`
- `words_per_line_mean`
- `words_per_line_sd`
- `mean_word_length`

#### B. Grammar and person

- `pos_noun_ratio`
- `pos_verb_ratio`
- `pos_adj_ratio`
- `pos_adv_ratio`
- `pos_pronoun_ratio`
- `pronoun_1s_share`
- `pronoun_1p_share`
- `pronoun_2_share`
- `pronoun_3_share`

#### C. Punctuation

- `em_dash_per_100_words`
- `semicolon_per_100_words`
- `colon_per_100_words`
- `comma_per_100_words`
- `exclamation_per_100_words`
- `question_per_100_words`
- `ellipsis_per_100_words`

#### D. Nonstructural style

Combination of B + C.

#### E. Full body-only vector

The original 22-feature P1-P4 feature set.

### Analyses

For each fixed feature family, rerun the same six-way classifier specification for:

- P1 cross-study poetry transfer;
- P3 leave-one-genre-out transfer;
- P4 leave-one-phrasing-out transfer;
- P4 leave-one-length-cap-out transfer.

P2 is excluded because the immediate interpretive target is named-model identity rather than provider classification.

P5 is excluded because opening-token entropy is a separate interpretable statistic rather than part of the primary classifier vector.

### Outputs

For every feature family and transfer condition, report:

- accuracy;
- balanced accuracy;
- per-model recall;
- confusion matrix.

Also report the difference between each restricted feature-family result and the frozen full-feature result.

No hyperparameter tuning, feature selection, or test-outcome-driven regrouping is permitted.

### Interpretation

The intended distinction is not “which feature set wins.”

The purpose is construct interpretation.

For example:

- strong form/structure performance with weak nonstructural performance would suggest that much of model attribution reflects formatting, length, or instruction-response behavior;
- substantial grammar/person or punctuation transfer would support a broader conventional-stylometric interpretation;
- substantial performance in multiple families would suggest that model identity is distributed across several observable behavioral dimensions;
- strong changes in the responsible feature family across environments would support a model × task interaction account.

## 6. IA3 — Behavioral transfer map

### Question

How can the primary and exploratory transfer results be represented as a coherent map of behavioral stability without pretending the current studies provide a fully crossed experimental design?

### Immediate analysis

Construct a descriptive transfer map using:

- frozen P1 cross-study transfer;
- frozen P3 genre-transfer folds;
- frozen P4 phrasing-transfer folds;
- frozen P4 length-transfer folds;
- IA1 size-matched P1 distribution;
- IA2 feature-family decompositions.

For each transfer condition, retain:

- training environment;
- testing environment;
- training sample size;
- testing sample size;
- feature family;
- accuracy;
- balanced accuracy;
- chance reference;
- per-model recall where applicable.

Because all six-way primary model-attribution analyses use the same 1/6 balanced-class chance reference, raw accuracy remains directly interpretable.

A chance-adjusted summary may additionally be reported as:

`(accuracy - 1/6) / (1 - 1/6)`

but it must not replace raw accuracy.

### What this is not

The current studies do **not** provide a clean, equally powered, reciprocal train-environment × test-environment matrix.

Study 1 and Study 2 differ sharply in cell sizes and experimental structure.

Accordingly, this exploratory layer will not manufacture a fully crossed “behavioral invariance matrix” whose cells imply comparability the data do not support.

A genuinely crossed transfer matrix should be treated as a design target for a future prospective study.

## 7. Accessibility outputs

The I&A layer should produce human-readable outputs in addition to machine-readable tables.

At minimum:

1. **Transfer overview**
   - raw six-way accuracy by transfer condition;
   - 1/6 chance reference shown explicitly;
   - training sample size displayed alongside performance.

2. **Feature-family decomposition**
   - form/structure;
   - grammar/person;
   - punctuation;
   - nonstructural style;
   - full body-only vector.

3. **Model heterogeneity**
   - per-model recall rather than aggregate accuracy alone.

4. **Concrete behavioral example**
   - opening-token entropy from P5 as an intuitive example of a directly interpretable repeatable tendency.

The prose explanation should distinguish clearly between:

- “the classifier can recognize the model”;
- “a particular measurable behavior is stable”;
- “the model has a context-independent trait.”

These are not equivalent claims.

## 8. Relationship to S1-S5

The analyses in this document must remain separate from the pre-result S1-S5 suite.

S1-S5 retain their status as analyses specified before the primary September outcomes were inspected.

The post-primary I&A diagnostics were motivated by the actual P1-P5 results and must be labeled accordingly in code, results, figures, and manuscript text.

Recommended output separation:

- `scripts/run_secondary_analysis.py` — planned S1-S5;
- `results/secondary_analysis/` — planned S1-S5 outputs;
- `scripts/run_post_primary_ia.py` — analyses in this document;
- `results/post_primary_ia/` — outcome-informed exploratory outputs;
- `figures/post_primary_ia/` — accessibility/interpretation figures.

## 9. Frozen boundaries

The following remain closed unless an actual contradiction or reproducibility failure is discovered:

- May raw data and analyses;
- September parser;
- parser-validation judgments;
- harmonized feature table;
- BA2 5,397/5,398 reconciliation;
- P1-P5 implementation;
- P1-P5 frozen outputs.

Post-primary diagnostics must operate downstream of these artifacts.

They may explain or qualify the primary results.

They may not rewrite them.

## 10. Scientific target

The broader question motivating this layer is:

> When researchers attribute a behavioral property to a language model, under what changes of context does that attribution remain valid?

The Bullshit Assay uses model attribution as an instrument for this question.

The goal is therefore not merely to show that six models can be distinguished from their writing.

The goal is to characterize **which model-associated behaviors persist, which are task-contingent, and how confidently model-level behavioral claims can travel across contexts**.
