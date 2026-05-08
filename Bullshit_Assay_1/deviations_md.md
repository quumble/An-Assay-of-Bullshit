# DEVIATIONS.md

This file records deviations, clarifications, and live-methods decisions for the model comparison experiment.

The study is exploratory. Entries here are intended to preserve a public record of methodological decisions made while the experiment and analysis pipeline were developing.

## 2026-05-07 — Preregistration timing clarification

The preregistration was added to the repository while the experiment was already underway. It should therefore be interpreted as an **in-progress exploratory preregistration / methods lock-in for the record**, not as a fully prospective preregistration completed before any data collection began.

At the time of this clarification, the core design was already specified:

* six models
* nine prompt conditions
* ten runs per model-prompt cell
* `temperature = 1.0`
* `max\_tokens = 400`
* no system prompt
* JSONL output, one record per call

The final report will disclose whether any raw outputs, aggregate metrics, or model-specific patterns had been inspected before the preregistration and this clarification were committed.

## 2026-05-07 — Public running log

The study is being developed and documented publicly as it proceeds. This means that some methodological choices, analysis ideas, and interpretive questions are being recorded in the repository before the full analysis is complete.

This public-running-log approach increases transparency but means the project should not be represented as a conventional sealed preregistration. The appropriate framing is:

> exploratory computational study with public, time-stamped methods development.

## 2026-05-07 — Semantic coding added as exploratory follow-up

The preregistration emphasized structural and lexical measures such as sentence-count compliance, line counts, opening words/bigrams, lexical diversity, named-entity inventory, and embedding geometry.

During data collection, an additional qualitative/semantic analysis direction was identified: coding story and poem outputs for themes such as mood, setting, tense, grammatical person, plot arc, imagery, emotional valence, and formulaicness.

This is an exploratory extension, not a replacement for the preregistered analyses.

Planned semantic variables may include:

* mood or affective mode
* setting type
* tense
* grammatical person
* plot arc or poetic mode
* imagery domain
* ending valence
* formulaicness or cliché markers
* originality/weirdness notes

These semantic analyses should be reported as exploratory unless a later experiment preregisters them prospectively.

## 2026-05-07 — Heuristic coding pipelines

A deterministic semantic-heuristic script was drafted with GPT-5.5 Thinking before final inspection of the complete dataset. A second blind heuristic pipeline is being drafted independently with Claude Opus 4.7.

The purpose of using two independently authored heuristic pipelines is not to eliminate bias, but to test whether descriptive patterns survive different operationalizations.

Agreement between the two heuristic pipelines will be treated as stronger evidence that a pattern is robust to coding choices. Disagreement will be treated as evidence that the construct is sensitive to operationalization.

The heuristic pipelines should be archived with the repository, including the date created and the analyst/model that helped author each pipeline.

## 2026-05-07 — Blinding clarification

Model-label blinding may help reduce human expectancy effects during manual review. However, because this study concerns stylistic defaults, model outputs may themselves contain provider/model fingerprints.

For LLM-assisted interpretation, blinding should not be treated as a complete solution. LLM analysts may infer model identity from style, formatting, phrasing, or other surface cues. Therefore:

* deterministic metrics and heuristics should be treated as primary for quantitative summaries;
* human coding may be blinded where useful, but the scope of that blinding should be stated;
* LLM-assisted qualitative interpretation should be described as non-independent, exploratory, and potentially affected by analyst-model priors;
* no LLM-coded semantic label should be treated as ground truth without validation or sensitivity checks.

## 2026-05-07 — Analyst-position note

Some analysis planning and interpretation involved LLM assistance, including models from the same broad families being compared in the study. This creates a potential analyst-position issue: the tools helping interpret the results may have priors about, or stylistic relationships to, the systems under comparison.

The final write-up should distinguish among:

1. deterministic or rule-based measures;
2. human-coded qualitative observations;
3. LLM-assisted qualitative observations;
4. post hoc interpretations developed after inspecting results.

LLM-generated analysis suggestions should be treated as hypothesis-generating unless independently validated.

## 2026-05-07 — How deviations will be reported

The final report should include a dedicated section summarizing:

* deviations from the original preregistration;
* clarifications to ambiguous preregistered procedures;
* exploratory analyses added after the preregistration;
* any data inspection that occurred before analysis choices were finalized;
* any disagreements between independently authored heuristic pipelines;
* any known limitations caused by live public documentation of the study.

## Running table

|Date|Type|Entry|Status|
|-|-|-|-|
|2026-05-07|Clarification|Preregistration was posted while the experiment was already underway.|To disclose in final report|
|2026-05-07|Exploratory addition|Semantic coding of mood, setting, tense, person, imagery, plot/poetic mode, and valence added as exploratory follow-up.|Added to analysis plan|
|2026-05-07|Methods addition|GPT-authored deterministic heuristic pipeline drafted.|Archive script|
|2026-05-07|Methods addition|Claude-authored second heuristic pipeline planned/drafted independently.|Compare against GPT pipeline|
|2026-05-07|Clarification|Blinding is useful for human expectancy effects but not sufficient for LLM-assisted interpretation.|To disclose in final report|

## Template for future entries

```md
## YYYY-MM-DD — Short title

\*\*Type:\*\* Deviation / clarification / exploratory addition / implementation note / correction

\*\*What changed:\*\*  
Describe the change plainly.

\*\*Why it changed:\*\*  
Describe the reason without overexplaining.

\*\*Effect on interpretation:\*\*  
Explain whether this affects confirmatory claims, exploratory analyses, comparability, or reproducibility.

\*\*Status:\*\*  
Planned / implemented / superseded / reported in final write-up.
```

