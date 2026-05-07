# Preregistration: Exploratory Model Comparison of Creative-Writing Defaults

**Project title:** Model Comparison Experiment: Creative-Writing Defaults Across Claude and OpenAI Model Tiers\
**Registration date:** 2026-05-07\
**Registration status:** In-progress preregistration / study already underway\
**Study type:** Exploratory computational study\
**Primary investigator:** Bo Chesterton

**Analyst model**: GPT 5.5 Thinking

## 1. Transparency statement

This preregistration is being written while the study is currently running. It should therefore be treated as an **in-progress preregistration for the record**, not as a fully prospective preregistration completed before any data collection.

At the time this preregistration is finalized, the investigator should record the following:

- Whether any model outputs have already been inspected: `[yes/no; describe if yes]`
- Whether any aggregate metrics have already been computed: `[yes/no; describe if yes]`
- Whether any exclusion, cleaning, or analysis decisions have already been made based on observed results: `[yes/no; describe if yes]`
- Whether the full planned set of API calls has completed: `[yes/no]`

Any results or patterns observed before this preregistration was finalized should be disclosed in the final report.

## 2. Purpose and rationale

This study explores how different Claude and OpenAI model tiers respond by default to short, contextless creative-writing prompts. The goal is to compare stylistic and instruction-following tendencies across models when prompts are intentionally minimal and no system prompt is provided.

The study is exploratory. Findings will be interpreted as descriptive evidence about model defaults under this particular setup, not as general claims about overall model quality, creativity, intelligence, or real-world usefulness.

## 3. Research questions

The study will address the following exploratory research questions:

1. **Length compliance:** How often does each model comply with sentence-count constraints in short creative-writing prompts?
2. **Opening patterns:** Do models differ in their first words or opening bigrams under cold creative-writing prompts?
3. **Lexical diversity:** Do models differ in lexical diversity across prompt types and length constraints?
4. **Named-entity behavior:** For animal prompts, do models differ in their tendency to produce real, invented, or hybrid animal names/entities?
5. **Within- vs. between-model variation:** Are responses from the same model more similar to one another than responses from different models?
6. **Cross-model structure:** Do response embeddings reveal clustering by provider, model tier, prompt category, or length constraint?

## 4. Confirmatory hypotheses

No confirmatory hypotheses are preregistered. All analyses are exploratory and descriptive.

If inferential statistics are reported, they will be clearly labeled as exploratory and will not be treated as confirmatory hypothesis tests.

## 5. Experimental design

### 5.1 Models

The study compares six models:

1. `claude-haiku-4-5-20251001`
2. `claude-sonnet-4-6`
3. `claude-opus-4-7`
4. `gpt-5.4-nano`
5. `gpt-5.4-mini`
6. `gpt-5.4`

### 5.2 Prompt categories

There are three prompt categories:

1. Story
2. Animal
3. Poem

Each category is crossed with three length conditions:

1. Fewer than 5 sentences
2. Fewer than 10 sentences
3. Open length / no explicit sentence constraint

This yields 9 prompt conditions total.

### 5.3 Repetitions

Each model-prompt cell will be sampled 10 times.

Total planned calls:

`6 models × 9 prompt conditions × 10 runs = 540 calls`

### 5.4 Generation settings

All calls will use:

- `temperature = 1.0`
- `max_tokens = 400`
- no system prompt

The absence of a system prompt is a deliberate part of the design, intended to measure model behavior under cold, contextless prompting.

## 6. Data collection procedure

The experiment will be run using `run_experiment.py`.

The runner writes one JSONL record per model call. Each record contains:

- `run_id`
- `timestamp`
- `provider`
- `model`
- `prompt_id`
- `prompt_text`
- `iteration`
- `temperature`
- `max_tokens`
- `response`
- `input_tokens`
- `output_tokens`
- `latency_ms`
- `error`

Failed calls will be written with `response: null` and an error string. Failed calls are not marked complete for resume purposes and may be retried using the runner’s `--resume` option.

## 7. Inclusion and exclusion criteria

### 7.1 Included records

A record will be included in text-based analyses if:

- `error` is `null`
- `response` is non-null
- the response is parseable as text
- the record corresponds to one of the preregistered model-prompt-iteration cells

### 7.2 Excluded records

A record may be excluded from text-based analyses if:

- the API call failed and no response text was returned
- the response is empty or whitespace only
- the response is a refusal or non-answer unrelated to the prompt
- the record is a duplicate caused by rerun/resume behavior
- the record does not match the intended model, prompt, or iteration schema

All exclusions will be reported, including counts by model and prompt condition.

### 7.3 Error handling

For the main descriptive analyses, failed calls will not be treated as zero-quality creative outputs. They will be reported separately as API or generation failures.

If failed calls are retried successfully through the resume mechanism, the successful response will be used. If multiple successful responses exist for the same model-prompt-iteration cell because of rerun artifacts, the earliest successful record by timestamp will be retained unless there is a documented reason to prefer another record.

## 8. Planned measures

### 8.1 Sentence-count compliance

For story and animal prompts with explicit sentence constraints, sentence-count compliance will be measured as whether the response contains fewer than the requested number of sentences.

For prompts requesting fewer than 5 sentences:

- compliant if sentence count `< 5`

For prompts requesting fewer than 10 sentences:

- compliant if sentence count `< 10`

Sentence counts will be estimated using a documented sentence segmentation method. The chosen method will be reported. Known ambiguity in sentence segmentation, abbreviations, fragments, dialogue, and stylized punctuation will be acknowledged.

Poems will be analyzed primarily using line-based metrics rather than sentence-count compliance, because sentence segmentation is less reliable for poetry.

### 8.2 Line-count metrics for poems

For poem prompts, planned descriptive metrics include:

- number of non-empty lines
- number of stanzas, if separable by blank lines
- total word count
- whether the poem appears to follow the requested length constraint when sentence-count prompts are used

### 8.3 Opening-word and opening-bigram frequency

For each response, the first word and first two-word sequence will be extracted after basic normalization.

Planned summaries:

- most common opening words by model
- most common opening bigrams by model
- entropy or concentration of opening patterns by model
- examples of repeated openings, if notable

### 8.4 Lexical diversity

Lexical diversity will be measured using MTLD or a comparable documented metric.

Planned summaries:

- lexical diversity by model
- lexical diversity by provider
- lexical diversity by prompt category
- lexical diversity by length condition

If responses are too short for stable MTLD estimates, the analysis will note this limitation and may supplement with simpler measures such as type-token ratio, moving-average type-token ratio, or unique-token proportion.

### 8.5 Named entity inventory for animal prompts

For animal prompts, named entities and animal names will be categorized as:

1. Real animals/species
2. Invented animals/species
3. Hybrid or ambiguous entities
4. Non-animal named entities

The classification procedure will be described. If manual coding is used, the final report will disclose coding rules and whether coding was blind to model identity. If automated coding is used, the tool or model used for classification will be reported.

### 8.6 Embedding-distance analyses

Responses will be embedded using a documented embedding model. The embedding model, preprocessing choices, and distance metric will be reported.

Planned analyses:

- within-model response distances
- between-model response distances
- nearest-neighbor relationships across responses
- clustering or visualization by provider, model, prompt category, and length condition

Embedding analyses will be treated as exploratory and sensitive to embedding-model choice.

## 9. Preprocessing plan

The following preprocessing steps may be applied before analysis:

1. Strip leading and trailing whitespace.
2. Normalize line endings.
3. Preserve original casing for archival records.
4. Use lowercased versions only for token-frequency, opening-word, and n-gram analyses.
5. Remove or normalize surrounding quotation marks only when they are clearly formatting artifacts.
6. Preserve punctuation for sentence-count analyses.
7. Preserve line breaks for poem analyses.

Any additional preprocessing steps will be documented in the final report.

## 10. Planned statistical and descriptive reporting

Because this is an exploratory study with a small number of runs per cell, the primary reporting will be descriptive.

Planned outputs include:

- tables of compliance rates by model and prompt condition
- mean, median, and range of sentence counts by model and prompt condition
- line-count summaries for poem prompts
- opening-word and opening-bigram frequency tables
- lexical diversity summaries
- named-entity category counts for animal prompts
- embedding-distance summaries and visualizations
- nearest-neighbor examples across models

Inferential statistics, if used, will be secondary and exploratory. The final report will avoid strong claims from p-values or significance tests due to the small sample size and high dependence on prompt selection.

## 11. Robustness and sensitivity analyses

Where feasible, the following sensitivity checks may be conducted:

1. Repeat sentence-count analyses using an alternative sentence segmentation method.
2. Report results with and without obvious refusals or malformed responses.
3. Compare lexical diversity metrics across at least two tokenization approaches.
4. Repeat embedding-distance analyses with one alternative embedding model, if practical.
5. Check whether conclusions change when grouping by provider rather than individual model.

## 12. Deviations from preregistration

Any deviations from this preregistration will be listed in the final report under a dedicated “Deviations” section.

Potential deviations include:

- changes to model names or model availability
- changes to prompt wording
- additional retries beyond the planned resume behavior
- changes to analysis metrics
- changes to exclusion criteria
- unplanned manual coding decisions

## 13. Limitations

The study has several known limitations:

1. The sample size is small: 10 runs per model-prompt cell.
2. The high temperature setting increases output variability.
3. Contextless prompts may not reflect normal user interactions.
4. Sentence-count constraints partly measure instruction-following rather than creative style alone.
5. Poetry is difficult to analyze with sentence-based metrics.
6. Model behavior may change if model identifiers point to mutable or non-dated deployments.
7. API settings, hidden provider-side defaults, and safety behavior may differ across providers.
8. Results are specific to the exact prompt set and generation settings.

## 14. Reproducibility plan

The final report should include:

- the exact model identifiers used
- the exact prompt texts
- the runner code version or commit hash, if available
- the date and time range of data collection
- the full JSONL output or an archival link to it, if shareable
- package versions for analysis code, where relevant
- any failed-call counts and retry behavior

Where possible, model identifiers should be pinned to dated snapshots to improve long-term reproducibility.

## 15. Data and materials

Planned files:

- `run_experiment.py` — experiment runner
- `results.jsonl` — raw output, one record per call
- analysis scripts or notebooks — to be added
- final report — to be added

The raw JSONL file should be preserved before any cleaning or filtering.

## 16. Reporting commitments

The final write-up will distinguish clearly between:

- planned analyses listed in this preregistration
- analyses added after inspecting results
- deviations from the original plan
- speculative interpretations

The final report will avoid ranking models globally unless the ranking is explicitly tied to a narrow metric, such as sentence-count compliance under the tested prompts.

## 17. Registration checklist before finalizing

Before submitting or archiving this preregistration, complete the following:

-

