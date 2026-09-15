# Secondary Analysis Plan — September 2026

**Project:** An Assay of Bullshit — cross-study secondary analysis  
**Date locked:** 2026-09-15  
**Status:** Prospective with respect to the September harmonized analyses; post hoc with respect to the frozen May datasets  
**Frozen source anchor:** `2d122305dafab5c89f1fbfc9f567069fed0b8d8f`

## 1. Scope and evidentiary status

This project re-analyzes two completed May 2026 studies without collecting new model outputs.

### Study 1 — Bullshit Assay 1

Study 1 contains 540 outputs from six models across three creative-writing categories (story, animal, poem) and three length conditions, sampled 10 times per model-prompt cell at temperature 1.0, no system message, and a 400-token output cap.

Study 1 is treated here as an **exploratory discovery study**. Data collection had begun before the repository preregistration record was committed, and the contemporaneous registration material itself describes the study as exploratory/in progress.

### Study 2 — Bullshit Assay 2

Study 2 planned 5,400 poetry calls from the same six model positions across three prompt phrasings (`write`, `compose`, `gimme`) and three line caps (5, 10, 20), with 100 iterations per cell, temperature 1.0, no system message, and a 400-token output cap. The frozen May analysis contains 5,397 analyzable records.

Study 2 is treated here as a **prospectively preregistered follow-up**. Its final pre-test files were committed before the run start recorded in `run_metadata.json`.

### September layer

The September work is a new secondary-analysis layer. It does not convert either original study into something more confirmatory than it was. The point of locking this document is narrower: the cross-study questions below are being specified before the harmonized September pipeline is run.

## 2. Central research question

> Which model-specific stylistic signatures survive changes in prompt regime, genre, and study design, and which apparent signatures are local to a particular prompt set, formatting convention, or preprocessing rule?

The project focuses on **stylistic defaults under minimally specified creative-writing prompts**, not model quality, intelligence, creativity in general, or stable traits outside the tested conditions.

## 3. Models

The six model identifiers are:

- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-6`
- `claude-opus-4-7`
- `gpt-5.4-nano`
- `gpt-5.4-mini`
- `gpt-5.4`

Provider-family (`Claude`/`GPT`) and tier (`small`/`medium`/`full`) labels may be reported descriptively, but **no population-level causal or inferential claim about family or tier will be made**. There is only one named model at each family-by-tier cell, so family and tier are not independently replicated factors at the model level.

## 4. Why a harmonized re-analysis is required

The two May studies used different feature pipelines, and later review identified preprocessing issues that matter for cross-study comparison.

At minimum, the September pipeline must correct the distinction among:

1. conversational/meta preamble;
2. title;
3. creative body.

The frozen May artifacts remain unchanged. September outputs are newly derived from the raw response text according to `HARMONIZED_CODING_SPEC.md`.

## 5. Primary analyses

The primary analyses are predictive/generalization tests because they directly address whether stylistic signatures survive distribution shift.

### P1. Cross-study six-way model transfer

Train a regularized multinomial logistic-regression classifier on Study 2 and evaluate it, without retraining, on the 180 Study 1 poetry outputs.

Primary feature set: the locked **body-only** harmonized feature set in `HARMONIZED_CODING_SPEC.md`.

Report:

- accuracy;
- balanced accuracy;
- six-by-six confusion matrix;
- per-model recall;
- 95% stratified bootstrap confidence intervals for accuracy and balanced accuracy.

The Study 1 test bootstrap will resample within model × prompt-condition strata so that the observed prompt balance is preserved.

Chance reference for six-way balanced classes is 1/6. No claim of a universal model fingerprint will be made from significance alone; the magnitude and confusion structure are the substantive outcomes.

### P2. Cross-study provider-family transfer

Using the same body-only harmonized features, train a binary regularized logistic-regression classifier on Study 2 provider labels and test it on Study 1 poetry.

Report accuracy, balanced accuracy, confusion matrix, and stratified-bootstrap confidence intervals.

Chance reference is 1/2. Interpretation is restricted to these six named models; this is not a population-level test of Anthropic versus OpenAI as organizations or model families in general.

### P3. Cross-genre transfer within Study 1

Run leave-one-genre-out six-way classification using the harmonized body-only feature set:

- train on story + animal, test on poem;
- train on story + poem, test on animal;
- train on animal + poem, test on story.

Standardization and classifier fitting occur using training data only. Report each held-out-genre confusion matrix and the pooled held-out accuracy/balanced accuracy.

This analysis tests whether model signatures discovered in one set of creative forms remain detectable in another.

### P4. Prompt-perturbation transfer within Study 2

Run two grouped transfer families:

1. leave-one-phrasing-out (`write`, `compose`, `gimme`);
2. leave-one-length-cap-out (5, 10, 20).

For each held-out group, fit the same six-way body-only classifier on the other two groups and test on the held-out group. Report per-fold and pooled accuracy, balanced accuracy, confusion matrices, and per-model recall.

This tests robustness to small wording changes and output-length constraints without relying on random record-level cross-validation.

### P5. Opening-token entropy replication

The first lexical token of the harmonized creative body will be extracted for every poem.

For each model:

- compute Shannon entropy of first-token distributions in Study 1 poetry;
- repeatedly rarefy Study 2 to 30 poems per model (matching Study 1 poetry n per model) using 10,000 deterministic-seed resamples;
- obtain a Study 2 rarefaction distribution and 95% interval for each model's opening-token entropy;
- report whether the Study 1 value falls inside that interval.

The cross-model ordering and the observed Claude/GPT descriptive gap will also be reported, but family interpretation remains descriptive because there are only three named models per provider.

## 6. Secondary analyses

Secondary analyses are planned but are not primary success criteria.

### S1. Cross-study feature stability

For each harmonized numeric feature, estimate per-model means separately in Study 1 poetry and Study 2. Standardize the six model means within each study, then report:

- Spearman rank correlation across the six models;
- direction agreement for each model relative to the study grand mean;
- bootstrap uncertainty where practical.

Because there are only six model points per feature, these statistics are descriptive stability summaries, not broad inferential tests.

### S2. Surface-framing versus body-style attribution

Repeat P1-P4 using a **full-surface** feature set that adds title and preamble indicators to the body-only features.

The difference between body-only and full-surface performance will be reported as an estimate of how much attribution depends on assistant-style framing versus the creative body itself.

### S3. Corrected Study 2 descriptive effects

Recompute Study 2 descriptive model differences using the harmonized body parser, including effect sizes for the locked body features. This replaces neither the frozen May preregistered record nor the public v3-1 paper; it is a September sensitivity/reanalysis layer.

### S4. Previously salient May signatures

Revisit, descriptively, the May headline signals under the harmonized pipeline, including:

- em-dash use;
- meta-preamble rate;
- title rate;
- opening concentration/entropy;
- line/block formatting;
- pronoun/person tendencies.

The purpose is to determine which survive corrected preprocessing and independent prompt regimes.

### S5. Study 1 genre interactions

For harmonized features with substantial model separation, report model × genre interactions descriptively and with effect sizes. These analyses ask whether a feature behaves like a model signature or a genre-specific habit.

## 7. Primary classifier specification

The primary classifier for P1, P3, and P4 is multinomial logistic regression with L2 regularization.

Rules:

- no feature selection based on test-set outcomes;
- missing feature values are handled using a training-set-fitted imputation rule, documented in code;
- continuous features are standardized using training-set means and standard deviations only;
- categorical/binary features, if used in secondary full-surface models, are not z-scored unless the implementation requires it;
- hyperparameters are fixed at library defaults unless a documented convergence issue requires change; any change is logged before looking at held-out predictions where feasible;
- no random record-level split will be presented as the main generalization result.

If a different classifier is explored (e.g. linear SVM, random forest), it is exploratory unless added to a dated deviation before its result is inspected.

## 8. Validation gate for the harmonized parser

Before outcome analysis, a stratified human validation sample of 180 responses will be drawn with seed `20260915`:

- 90 from Study 1;
- 90 from Study 2;
- 15 per model per study;
- distributed across available prompt conditions as evenly as possible.

The validator will be blinded to model identity and will code:

- preamble present: yes/no;
- title present: yes/no;
- preamble boundary correct: yes/no/not-applicable;
- title boundary correct: yes/no/not-applicable;
- creative-body start correct: yes/no.

Target agreement is at least 0.90 for each applicable field. If a field falls below 0.90, the parser may be revised **before primary outcome analysis**. Any revision, reason, and before/after validation score must be logged in a September deviations file. The validation sample remains fixed.

## 9. Error handling and inclusion

### Study 1

Use the frozen raw JSONL. Include every successful non-empty response corresponding to the planned 540 cells. Any duplicate or malformed record discovered in September must be documented rather than silently dropped.

### Study 2

Start from the frozen raw 5,400-call JSONL and reproduce the analyzable-record count. Records with failed or empty responses are excluded from text-feature analyses and enumerated by model/prompt cell. The September pipeline must not simply trust the old `features_final_5397.jsonl`; it should derive features again from raw response text.

## 10. Multiple comparisons and inferential posture

The paper's primary evidence is out-of-distribution predictive transfer and transparent effect-size/stability reporting, not a large battery of p-values.

Feature-level secondary analyses will emphasize:

- effect sizes;
- confidence intervals or bootstrap intervals where practical;
- consistency across studies/conditions;
- explicit labeling of exploratory findings.

The manuscript will avoid interpreting tiny p-values from thousands of response-level observations as evidence that a provider family or tier generalizes beyond the specific named models tested.

## 11. Interpretation rules

The following claims are out of scope unless new evidence specifically supports them:

- model quality ranking;
- creativity ranking;
- intelligence ranking;
- stable personality/persona outside these cold creative-writing conditions;
- causal attribution to pretraining, post-training, RLHF, system prompts, or provider policy;
- universal Claude-versus-GPT stylistic laws;
- claims that a style signature persists across model updates or future snapshots.

The strongest permissible conclusion, if supported, is that some stylistic signals transfer across the tested prompt regimes and two independently collected May datasets for these six model identifiers.

## 12. Manuscript relationship to existing preprints

The intended journal manuscript is a new synthesis, not `v4` of either May paper.

It will disclose and cite the two public antecedent papers:

- *The Average Bullshittings of Machines* — Study 1 historical report;
- *Six Ways to Write a Synthetic Poem* — Study 2 historical report.

The journal paper may reuse the frozen datasets but must clearly identify what is newly contributed by the September layer, especially:

- harmonized preprocessing;
- corrected title/preamble/body separation;
- cross-study transfer analysis;
- cross-genre and cross-prompt generalization tests;
- integrated interpretation in the stylometry/digital-humanities literature.

## 13. Reproducibility commitments

The September layer will preserve:

- exact source commit and blob identifiers;
- analysis environment/package versions;
- random seeds;
- harmonized feature table;
- validation sample and adjudication record;
- all scripts used to derive results;
- machine-readable result tables;
- a deviations log for any change from this plan.

No frozen May file will be overwritten in place.
