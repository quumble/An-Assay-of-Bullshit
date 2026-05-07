# Preregistration: Model Comparison Experiment

**Status:** Exploratory study. This document locks the design and the planned analyses *before* data collection. Analytic flexibility is preserved (see "Deviations and exploratory analyses" below); this is not a confirmatory hypothesis test.

**Date locked:** *05/07/26 14:00 EST*
**Author:** *Bo Chesterton*
**Companion file:** `README.md`

\---

## 1\. Background and motivation

LLMs from different providers and tiers exhibit recognizable stylistic "defaults" when given short, contextless prompts. This study probes those defaults by sampling many completions per (model, prompt) cell at temperature 1.0 and comparing them on simple structural and lexical metrics.

The goal is **descriptive**: to characterize and compare default behavior, generate hypotheses for follow-up work, and produce a public artifact (the JSONL) that supports re-analysis.

This is not a study of in-context behavior, capability, or quality. Findings should be read as facts about cold-prompt defaults under the specific settings below.

## 2\. Research questions

All questions are exploratory. None is preregistered as a confirmatory test with a decision rule.

1. **Constraint compliance.** How often does each model satisfy the explicit length constraint (`<5`, `<10` sentences)? Does compliance vary systematically by provider, tier, or category?
2. **Opening-token concentration.** How concentrated are opening words and opening bigrams within a model? Are some models more "templated" at the start of completions than others?
3. **Lexical diversity.** Within-model lexical diversity (MTLD) on completions, by category and length condition.
4. **Named entity defaults.** For animal prompts in particular: do models default to real species, invented species, or hybrids? What are the most frequent named entities by model?
5. **Embedding geometry.** Intra-model vs. inter-model embedding distance (mean pairwise cosine within model vs. between models). Cross-model nearest-neighbor structure: does any model's outputs sit unusually close to another's?

## 3\. Design (locked)

Reproduced from `README.md` and locked here:

* **Models (6):** `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `claude-opus-4-7`, `gpt-5.4-nano`, `gpt-5.4-mini`, `gpt-5.4`
* **Prompts (9):** 3 categories × 3 length conditions

  * Categories: story, animal, poem
  * Length conditions: `<5 sentences`, `<10 sentences`, open (no length constraint)
* **Cells:** 6 × 9 = 54
* **Runs per cell:** 10
* **Total calls:** 540
* **Sampling settings:** `temperature = 1.0`, `max\_tokens = 400`, no system prompt
* **Output:** JSONL, one record per call (schema in `README.md`)

The exact prompt strings and the prompt → `prompt\_id` mapping are fixed in `run\_experiment.py` at the time this prereg is locked. Any change to prompts, models, or cell sizes after lock-in counts as a deviation (Section 7).

## 4\. Data collection procedure

* Calls are issued by `run\_experiment.py` with `--resume` semantics: failed calls (any non-null `error`) are not marked complete and are retried on rerun.
* A run is considered "complete" when every (model, prompt\_id, iteration) cell up to `runs\_per\_cell` has at least one record with `error == null`.
* Smoke test (`--runs-per-cell 1`) is run first; smoke data is **excluded** from the main analysis dataset.
* The frozen analysis dataset is the first 10 successful (`error == null`) records per cell, ordered by `timestamp`. Any additional successful records (e.g., from over-collection during retries) are excluded from primary analyses but retained in the JSONL.

## 5\. Exclusions and missing data

* **Hard errors** (API failures, refusals returning `null` content, truncations at exactly `max\_tokens` with no terminal punctuation): these are reported as a per-cell completion rate. Cells with fewer than 10 successful records after retries are flagged and analyzed with the available n; no imputation.
* **Refusals** (model returns a refusal-style completion rather than attempting the task): kept in the dataset, flagged via a post-hoc binary code, and reported separately. They are excluded from compliance, opening-token, MTLD, and embedding analyses but counted in the refusal rate.
* **Truncation at `max\_tokens`:** records where `output\_tokens >= 400` are flagged. They are kept in primary analyses but the truncation rate is reported per cell, since it can confound length-compliance and embedding analyses.
* No outlier removal beyond the above. Distributions are reported with medians and IQRs alongside means.

## 6\. Planned analyses

Each analysis is described at a level that locks the *measure* but not every plotting choice.

### 6.1 Constraint compliance

* **Measure:** sentence count per completion, computed with a single, pre-chosen tokenizer (planned: spaCy `en\_core\_web\_sm` sentence segmentation; if unavailable, NLTK Punkt). The tokenizer is chosen and recorded *before* analysis.
* **Compliance rule:** for `<5` cells, completion is compliant iff sentence count ≤ 4; for `<10`, ≤ 9; open cells are not scored for compliance.
* **Reporting:** per-cell compliance rate with Wilson 95% CIs; aggregated by model and by provider.
* **Note:** poems are scored both by sentence count (for parity) and by line count (more meaningful), and both are reported.

### 6.2 Opening-token concentration

* **Measure:** for each (model, category) pair, the empirical distribution of the first word and first bigram across all 30 completions in that pair (3 length conditions × 10).
* **Statistics reported:** top-5 most frequent openings, share of completions starting with the most-frequent opening, and Shannon entropy of the opening distribution.
* **Tokenization:** lowercase, strip leading punctuation, split on whitespace.

### 6.3 Lexical diversity

* **Measure:** MTLD per completion, computed with a fixed implementation (planned: `lexical-diversity` PyPI package; version recorded). Threshold: default 0.72.
* **Reporting:** per-(model, category, length condition) median and IQR; visual comparison across models.

### 6.4 Named entity inventory

* **Measure:** spaCy NER on each completion; entity types of interest are PERSON, ORG, GPE, LOC, and a custom regex-based pass for animal names against a fixed reference list (compiled before analysis from a public taxonomy source; source recorded).
* **Categories:** real species (in reference list), invented species (capitalized noun phrases not in reference list and not matching common-English wordlist), hybrids (compound forms like "fire-lynx").
* **Reporting:** per-model entity inventories for animal prompts; counts of real / invented / hybrid.

### 6.5 Embedding geometry

* **Embedding model:** a single embedding model fixed before analysis (planned: `text-embedding-3-large`; locked at analysis time, recorded in the analysis script).
* **Measures:**

  * Mean pairwise cosine distance within each (model, prompt\_id) cell.
  * Mean pairwise cosine distance between models, holding prompt\_id fixed.
  * For each completion, the model whose other completions (same prompt\_id) are closest in mean cosine — i.e., a nearest-neighbor confusion matrix at the model level.
* **Reporting:** within-vs-between distance ratio per model, and the confusion matrix as a heatmap.

### 6.6 Reporting conventions

* All comparisons are reported with effect sizes and 95% CIs (bootstrap, 10,000 resamples) where applicable.
* No p-value thresholds are used to declare findings. The framing is descriptive throughout.

## 7\. Deviations and exploratory analyses

This prereg is lightweight by design. The following are explicitly *allowed* without counting as deviations, provided they are flagged in the writeup:

* Additional descriptive plots and summaries beyond those listed.
* Replacing a tool (e.g., a different sentence segmenter) if the original is broken or unavailable, provided the substitution is recorded and a sensitivity check against the original tool is shown when feasible.
* Sub-analyses suggested by the data (e.g., looking at a specific model's behavior more closely).

The following *do* count as deviations and must be disclosed:

* Changes to the model list, prompt set, runs-per-cell, or sampling settings after lock-in.
* Changes to compliance rules in Section 6.1 or to the n=10 frozen-dataset rule in Section 4.
* Switching from "exploratory/descriptive" framing to confirmatory claims.

Deviations are recorded in a `DEVIATIONS.md` file added to the repo when they occur, with date and rationale.

## 8\. Caveats (carried forward from README)

* n=10 per cell at temperature 1.0 is small; all findings are hypotheses, not conclusions.
* Cold contextless prompts measure defaults, not behavior in real use.
* Length-constraint prompts partly test instruction-following, not just style.
* Poems are awkward to score by sentence count; line-based metrics are reported alongside.
* Model snapshots may shift; the dated snapshot for Haiku is pinned, others should be pinned at lock-in for full reproducibility.

## 9\. Artifacts

On completion, the following will be made available:

* `results.jsonl` — raw output (one record per call).
* The frozen analysis dataset (first 10 successes per cell) as `analysis\_dataset.jsonl`.
* Analysis scripts, with the embedding model, segmenter, and reference lists pinned by version.
* `DEVIATIONS.md` if applicable.

