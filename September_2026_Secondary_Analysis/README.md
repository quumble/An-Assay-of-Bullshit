# September 2026 Secondary Analysis

This directory contains the September 2026 secondary-analysis layer over the two frozen May 2026 Bullshit Assay studies.

## Status

The May studies remain frozen and unchanged:

- `Bullshit_Assay_1/` — May exploratory discovery study.
- `Bullshit_Assay_2/` — May prospectively preregistered poetry follow-up.
- Repository state immediately before the September layer: `2d122305dafab5c89f1fbfc9f567069fed0b8d8f`.

The September primary-analysis sequence is complete and frozen:

1. **Secondary-analysis plan locked:** `f91608d8d5990f1a0e9da8b9ce6a8af32d2612ac`
2. **Harmonization pipeline implemented:** `82f471ec1c7d589fb66e7940f8db9b1a1eb57f03`
3. **Parser validation sample locked:** `eb4bca99b8924bd182a19311c64bac2379589ca0`
4. **Parser validated and frozen:** `e7fb9a3ef38eecb44a4115470a0cf97cb8bc0bdd`
5. **Validated harmonized dataset frozen:** `c14f6b433d4c277a9dc0acc8d44c46ec8570c2cb`
6. **Primary P1-P5 analysis implementation frozen:** `8e96188c6f0fccc3fabcd4ff7d2e1bced6dadb36`
7. **Primary P1-P5 results frozen:** `f2f93897572b8b6e9f5f162dc4d51cb15fcd48ff`

The harmonized September dataset contains:

- Study 1: 540 records
- Study 2: 5,398 successful non-empty records
- Total: 5,938 records

The frozen primary results are under `results/primary_analysis/`.

No frozen May artifact, harmonized dataset, parser, primary-analysis script, or primary-result artifact should be modified in place.

## Evidentiary layers

The project now contains three analytically distinct layers.

### 1. May studies

The original studies retain their original evidentiary status:

- Study 1 is exploratory.
- Study 2 is the prospectively preregistered follow-up.

The September work does not retrospectively change those statuses.

### 2. September locked analyses

`SECONDARY_ANALYSIS_PLAN.md` was locked before the September harmonized outcome analyses were run.

Its P1-P5 analyses are now complete and frozen.

Its S1-S5 analyses remain **planned, pre-result secondary analyses** and have not yet been run.

### 3. Post-primary interpretability and access work

Inspection of P1-P5 raised additional questions about what the classifier is actually detecting and how strongly the observed transfer differences can be interpreted.

These questions are explicitly **outcome-informed and exploratory**. They are documented separately in `POST_PRIMARY_IA_PLAN.md`.

They are not amendments to P1-P5 and must not be represented as preregistered or prospectively specified before the primary results were known.

## Purpose

The May papers asked whether minimally prompted frontier language models display characteristic creative-writing defaults.

The September layer asks a narrower and more transferable question:

> Which model-specific stylistic signatures survive changes in prompt regime, genre, and study design, and which apparent signatures are local artifacts of prompting, task constraints, or preprocessing?

The broader methodological question emerging from the primary results is:

> When researchers attribute a behavioral property to a language model, under what changes of context does that attribution remain valid?

Model attribution is therefore treated as a measurement instrument for behavioral stability, not as the ultimate scientific objective.

## Primary analysis

The locked P1-P5 suite covers:

- cross-study six-way model transfer;
- cross-study provider-label transfer;
- cross-genre transfer within Study 1;
- prompt-phrasing and length-cap transfer within Study 2;
- cross-study replication of opening-token entropy.

Primary analyses use the harmonized body-only feature set. Titles and conversational/meta preambles are excluded from the primary classifier.

The complete machine-readable results, confusion matrices, and opening-entropy output are preserved under `results/primary_analysis/`.

## Planned secondary analyses

The pre-result `SECONDARY_ANALYSIS_PLAN.md` also specifies S1-S5:

- S1 — cross-study feature stability;
- S2 — surface-framing versus body-style attribution;
- S3 — corrected Study 2 descriptive effects;
- S4 — previously salient May signatures under harmonized preprocessing;
- S5 — Study 1 genre interactions.

These analyses should be implemented and reported separately from the post-primary exploratory diagnostics.

## Post-primary interpretability and access

`POST_PRIMARY_IA_PLAN.md` defines outcome-informed diagnostics intended to answer three immediate questions:

1. How much of the apparent P1-versus-P3 transfer difference is attributable to unequal training-set size?
2. Which feature families actually carry model-identifying information across contexts?
3. How can the observed transfer results be represented as a behavioral-stability map without overstating what the current experimental design identifies?

This layer is explicitly exploratory.

## Interpretation guardrails

The September analyses concern the six named model snapshots under the tested conditions.

They do not establish:

- universal provider-family differences;
- permanent model fingerprints;
- model personality or subjective traits;
- general authorship attribution for arbitrary AI-generated text;
- causal explanations in terms of training data, RLHF, system prompts, architecture, or provider policy;
- persistence across future model versions.

“Stylistic signature” should be preferred to “fingerprint” where possible. The current evidence supports partially transferable, context-dependent behavioral regularities rather than immutable identities.

## Repository structure

Key September materials include:

- `SECONDARY_ANALYSIS_PLAN.md` — locked pre-result analysis plan;
- `HARMONIZED_CODING_SPEC.md` — locked preprocessing and feature definitions;
- `PROVENANCE.md` — source anchors and lineage;
- `IMPLEMENTATION_NOTES.md` — pre-outcome harmonization implementation choices;
- `ANALYSIS_IMPLEMENTATION.md` — pre-result P1-P5 implementation choices;
- `PRE_RESULT_CODE_AUDIT.md` — audit of the frozen primary-analysis implementation;
- `POST_PRIMARY_IA_PLAN.md` — outcome-informed exploratory interpretability/access plan;
- `validation/` — parser-validation materials;
- `derived_data/` — frozen harmonized feature table;
- `scripts/` — harmonization, validation, and analysis code;
- `results/primary_analysis/` — frozen P1-P5 results;
- `results/` — other September provenance and future analysis outputs;
- `figures/` — future figures;
- `manuscript/` — future integrated journal manuscript.

The intended journal product remains a new synthesis integrating both May studies and the September analysis rather than a replacement version of either May preprint.
