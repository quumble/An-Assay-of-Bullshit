# September 2026 Secondary Analysis

This directory contains a new, prospective secondary-analysis layer over the two frozen May 2026 Bullshit Assay studies.

## Status

- `Bullshit_Assay_1/` is frozen as the May exploratory discovery study.
- `Bullshit_Assay_2/` is frozen as the May prospectively preregistered poetry follow-up.
- No original data, code, analyses, or papers under those directories are to be edited for the September project.
- The repository state immediately before this directory was added is anchored at commit `2d122305dafab5c89f1fbfc9f567069fed0b8d8f`.
- At the time this plan is locked, no September harmonized outcome analysis has been run.

The September project is explicitly **secondary analysis**. It is post hoc with respect to the original May data, but the analyses in `SECONDARY_ANALYSIS_PLAN.md` are being specified before the new harmonized pipeline is run.

## Purpose

The May papers asked whether minimally prompted frontier language models display characteristic creative-writing defaults. The September pass asks a narrower and more transferable question:

> Which model-specific stylistic signatures survive changes in prompt regime, genre, and study design, and which apparent signatures are local artifacts of prompting or preprocessing?

The intended journal product is a new manuscript integrating both studies rather than a replacement version of either PhilPapers/PhilArchive preprint.

## Locked documents

- `SECONDARY_ANALYSIS_PLAN.md` — research questions, primary and secondary analyses, evaluation rules, and inferential limits.
- `HARMONIZED_CODING_SPEC.md` — preprocessing and feature definitions to be implemented for both raw datasets.
- `PROVENANCE.md` — frozen-source anchors, known May-era analysis issues, and version lineage.

## Planned working structure

After the lock commit, new work may be added under this directory, for example:

- `scripts/`
- `derived_data/`
- `results/`
- `figures/`
- `validation/`
- `manuscript/`

All such material is downstream of the locked plan and must remain separate from the frozen May directories.
