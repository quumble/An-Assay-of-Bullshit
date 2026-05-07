# Provisional Results — Model Comparison Experiment

**Status:** Provisional draft. Single coding pass, no inferential statistics, n=10 per cell.
**Date:** 2026-05-07
**Author:** Bo Chesterton
**Provisional analysis assistance:** `claude-opus-4-7` (this is one of the six subjects of the experiment; see Section 0 for what that means and how to read what follows).

---

## 0. Author / analyst disclosure

This document was drafted in collaboration with `claude-opus-4-7`, which is one of the six models being compared. That is a real conflict and the reader should weight the writeup accordingly. Concretely:

- `structural_heuristics.py`, the second of the two heuristic coders, was authored by `claude-opus-4-7`. It is deterministic lexical/regex matching with no learned components, but the *choice* of which features to measure (em-dashes, smart quotes, title lines, single-block formatting, "Here is..." preambles) reflects the author's priors about what stylistic signals exist.
- The blind interpretive pass (Sections 3–5) was conducted by `claude-opus-4-7` against summary CSVs with model identities masked. The model went on record with one labeled mapping guess before unblinding ("Model B is in the Claude family, Model D is GPT") and **was wrong on both** — Model B is `gpt-5.4-nano`, Model D is `claude-sonnet-4-6`. The structural patterns described in Section 3 were committed to *before* unblinding, so they survive that error; the family-level interpretations were revised after.
- One of the more flattering structural readings ("Opus drops formal markers under tight constraint, format-adaptive") is `claude-opus-4-7` describing its own outputs in aggregate. Read with a grain of salt. The same model was also responsible for the highest truncation rate in the study (a defect, not a virtue).
- The complementary semantic coder (`semantic_heuristics.py`) was authored separately by `gpt-5.5-thinking`, which has a symmetric conflict in the other direction.

The methodology was designed in awareness of these conflicts — two independent coders with opposite biases, blinding during interpretation, deterministic lexical matching rather than LLM-as-judge. None of that fully neutralizes the conflict; it just bounds it. Findings that survive across both coders are more credible than findings from either alone.

## 1. What the experiment measured

Six models — `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano`, `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001` — were prompted with nine short, contextless creative-writing prompts (3 categories × 3 length conditions: story / animal / poem × `<5 sentences` / `<10 sentences` / open). Each (model, prompt) cell was sampled 10 times at `temperature=1.0`, `max_tokens=400`, no system prompt. Total: 540 calls. All 540 succeeded with non-null responses. See `README.md` and `PREREGISTRATION.md` for the full design.

Two heuristic coders processed the JSONL:

- `semantic_heuristics.py` codes content (setting, mood, plot arc, imagery, ending valence, named entities for animal prompts, sentence count, opening word/bigram, formulaicness).
- `structural_heuristics.py` codes form (punctuation features, sentence-length distribution, paragraph/stanza structure, title and preamble flags, repetition, hedging, closing-sentence properties).

Both coders independently blinded the model identities with seeded random labels. The interpretive pass below was conducted blind, with one explicit unblinding gate at the end.

## 2. Headline numbers

### 2.1 Compliance, refusal, truncation

Compliance is the rate at which length-constrained responses (60 per model, excluding the 30 open-length cells) had fewer sentences than the cap, using the semantic coder's sentence splitter.

| Model | Compliance (sem) | Compliance (struct) | Refusal-like | Truncation @ 400 |
|---|---|---|---|---|
| gpt-5.4 | 60/60 (100%) | 60/60 (100%) | 0% | 5.6% |
| gpt-5.4-mini | 60/60 (100%) | 60/60 (100%) | 0% | 8.9% |
| gpt-5.4-nano | 60/60 (100%) | 60/60 (100%) | 0% | 11.1% |
| claude-opus-4-7 | 58/60 (96.7%) | 58/60 (96.7%) | 2.2% | **22.2%** |
| claude-sonnet-4-6 | 59/60 (98.3%) | 59/60 (98.3%) | 0% | 0% |
| claude-haiku-4-5 | **54/60 (90.0%)** | 51/60 (85.0%) | 1.1% | 1.1% |

All 9 compliance failures by the semantic coder are from Claude models (Opus: 2, Sonnet: 1, Haiku: 6). All 12 failures by the structural coder are likewise from Claude (Opus: 2, Sonnet: 1, Haiku: 9). No GPT failed compliance once. **The two coders disagree on three Haiku `story_lt5` outputs** — those responses had exactly 5 sentences by the structural splitter (non-compliant) and 4 by the semantic splitter (compliant). See Section 4 for what this means.

### 2.2 Length

| Model | Median words | Mean words | Median sentences | Median TTR |
|---|---|---|---|---|
| gpt-5.4 | 81.5 | 109.7 | 5 | 0.806 |
| gpt-5.4-mini | 94.0 | 116.7 | 5 | 0.769 |
| gpt-5.4-nano | 96.0 | 119.4 | 4 | 0.804 |
| claude-opus-4-7 | 105.5 | 108.6 | 5 | 0.785 |
| claude-sonnet-4-6 | 109.0 | 112.2 | 4 | 0.747 |
| claude-haiku-4-5 | 112.0 | 119.1 | 5 | 0.754 |

Claude models cluster at higher median word counts; GPT models lower. TTR (within-response type-token ratio) is broadly similar; gpt-5.4 leads, claude-sonnet trails. n is too small to read much into the 0.06 spread.

### 2.3 Punctuation and format

| Model | Em-dash mean | Smart-quote share (median) | Title rate | Single-block rate | Preamble rate |
|---|---|---|---|---|---|
| gpt-5.4 | 0.36 | 0.00 | 2.2% | 64.4% | 0.0% |
| gpt-5.4-mini | 0.37 | 0.50 | 22.2% | 65.6% | 0.0% |
| **gpt-5.4-nano** | **1.62** | **1.00** | 5.6% | 66.7% | 0.0% |
| claude-opus-4-7 | 0.62 | 0.00 | 75.6% | 23.3% | 1.1% |
| **claude-sonnet-4-6** | 0.81 | 0.00 | 98.9% | 0.0% | **37.8%** |
| claude-haiku-4-5 | 0.69 | 0.00 | 100.0% | 0.0% | 0.0% |

Two cells in this table are doing most of the work for the most surprising findings in this study. `gpt-5.4-nano`'s em-dash and smart-quote habit, and `claude-sonnet-4-6`'s preamble rate. Both contradict popular folk-stereotypes about model families. See Section 3.

### 2.4 Cross-coder agreement

The two coders agree on **540/540 (100%)** of word counts and **435/540 (80.6%)** of exact sentence counts. The 19% disagreement on sentence count is concentrated at sentence-number boundaries — most are off-by-one, driven by how each splitter handles dialogue, ellipses, and abbreviations. The compliance disagreements (3 cases, all on Haiku `story_lt5`) sit at the 4-vs-5 boundary, where any splitter choice will swing the verdict.

## 3. Findings

### 3.1 Two folk-stereotypes did not survive

This is the most quotable result of the study, and the one the methodology was best positioned to surface.

**The em-dash is not a Claude tell here.** `gpt-5.4-nano` had a median of 1 em-dash per response and was the only model with a non-zero median smart-quote share. The three Claude models had em-dash medians of 0 and smart-quote shares of 0. Whatever folk-stereotype links em-dashes and curly quotes to Claude is not borne out on this prompt set with this set of models. Mean em-dashes per response: nano = 1.62, every other model ≤ 0.81. Mean smart-quote share for nano was elevated across the board, not just within quoted dialogue.

**The "Sure! Here is..." preamble is not a GPT tell here.** `claude-sonnet-4-6` had a 37.8% preamble rate; the three GPT models had 0.0%. Sonnet's preamble is also strongly conditional on the prompt: 100% of `poem_lt5` and `poem_lt10` cells, 100% of `story_lt5`, 40% of `story_lt10`, and 0% of all open-length cells and all animal cells. The pattern is "when given a length constraint on a poem or story, frame the output as a deliverable being handed over." It is not a Sonnet-wide habit, and it is not a GPT-wide habit either — in this experiment, `claude-sonnet-4-6` is the only model in any cell that does this.

These are findings about *folk-stereotypes failing to track*, not "GPT does X" or "Claude does Y." Generalization beyond this prompt set is not warranted; that's what the design caveats say. But the failures are stark enough at n=90 per model that they're worth registering, and are the kind of finding the prereg-and-blind methodology is genuinely good at producing.

### 3.2 Opening-word concentration tracks family

The Claude models open with "the" 60–62% of the time. The GPT models do not.

| Model | Opening-word entropy (bits) | Top opening word | Top word's share |
|---|---|---|---|
| gpt-5.4 | 3.02 | "at" | 26.7% |
| gpt-5.4-mini | 2.92 | "the" | 21.1% |
| gpt-5.4-nano | 2.87 | "mara" | 28.9% |
| claude-opus-4-7 | 1.52 | "the" | 66.7% |
| claude-sonnet-4-6 | 1.18 | "the" | 62.2% |
| claude-haiku-4-5 | 1.49 | "the" | 66.7% |

Claude opening-word distributions are substantially more concentrated than GPT distributions (entropy ~1.2–1.5 bits vs. ~2.9–3.0 bits). gpt-5.4-nano fixates on the proper noun "Mara" in 26 of 90 responses — a different kind of templating. This is the only finding in this study where a Claude-vs-GPT family signal is clear and crosses tier within each family.

### 3.3 Title-line and single-block formatting: a 2-2-2 split

A pre-unblinding analysis grouped the six models into three pairs based on how they respond to length constraints, by examining the title-line and single-block flags broken down by category × length condition:

- **Format-rigid (claude-sonnet-4-6, claude-haiku-4-5):** 99–100% title rate across every category and every length condition; 0% single-block. These two models impose the same scaffolding regardless of how short the requested output.
- **Format-adaptive (claude-opus-4-7, gpt-5.4-mini):** title under open prompts (Opus: 89% in stories/poems, mini: 30% in poems / 33% in animals), drop the title under tight `lt5` constraints. Same with single-block: multi-block under open conditions, fold to single-block when squeezed.
- **Format-minimal (gpt-5.4, gpt-5.4-nano):** rarely title in any condition (top rates 6.7% and 13.3%, both in animals). Multi-block under open prompts, single-block under constraint.

The split is real but does not correspond to provider, family, or scale. It corresponds to **how much the model lets the length cue override its default formatting habits.** The two smaller Claudes (Sonnet, Haiku) override the least; gpt-5.4 and nano override the most by virtue of having little default scaffolding in the first place; Opus and mini sit in between and adjust visibly.

The `claude-sonnet-4-6` preamble pattern (Section 3.1) is consistent with the format-rigid reading: when squeezed, Sonnet does not change format — instead it adds a preamble framing the constrained output as a delivery.

### 3.4 Truncation is an open-prompt phenomenon, dominated by Opus

The headline 22.2% truncation rate for `claude-opus-4-7` is misleading at the model level. Broken out by length condition:

| Model | open | lt10 | lt5 |
|---|---|---|---|
| gpt-5.4 | 16.7% | 0.0% | 0.0% |
| gpt-5.4-mini | 26.7% | 0.0% | 0.0% |
| gpt-5.4-nano | 33.3% | 0.0% | 0.0% |
| **claude-opus-4-7** | **66.7%** | 0.0% | 0.0% |
| claude-sonnet-4-6 | 0.0% | 0.0% | 0.0% |
| claude-haiku-4-5 | 3.3% | 0.0% | 0.0% |

All truncation, across all six models, occurs on open-length prompts. Two-thirds of `claude-opus-4-7`'s open-length completions hit the 400-token cap. `claude-sonnet-4-6` never truncates. Three of the six models have ≥25% truncation on open prompts; the `max_tokens=400` setting is a real constraint on this experiment's results. **Open-prompt outputs from gpt-5.4-mini, gpt-5.4-nano, and especially claude-opus-4-7 should be treated as length-clipped** for any downstream comparison.

This is the strongest argument in the data for raising `max_tokens` in any follow-up. It also means the within-model embedding-distance and lexical-diversity comparisons that include open-prompt cells are confounded by clipping.

### 3.5 Compliance failures are at the boundary, and they're all Claude

All 9–12 compliance failures (depending on splitter) come from the three Claude models. All Haiku failures cluster in `story_lt5`. The disagreement between coders is concentrated at the 4-vs-5 sentence boundary: Haiku writes `story_lt5` outputs that sit *exactly* on the edge of the rule. The structural splitter pushes 3 of those over; the semantic splitter does not.

A reasonable read is **not** "Haiku can't count to 5" but "Haiku writes story_lt5 outputs that are systematically as long as they can be while still claiming compliance." That is also a finding — it implies a different attitude toward the constraint than gpt-5.4 has — but it is a different finding from "fails to follow instructions." The gap between the two readings is exactly what the splitter ambiguity exposes.

The Opus failures (2 in `story_lt5`) and the Sonnet failure (1 in `story_lt10`) are similar in character: a single sentence over the limit, in the hardest cell. Compliance is not at risk in any other cell for any Claude.

## 4. What the methodology surfaced (and what it didn't)

### What worked

- **Prereg-then-blind-then-unblind protected against `claude-opus-4-7`'s most consequential prior errors.** The author of the structural coder labeled the em-dash signal and the preamble signal as Claude-and-GPT respectively *before* unblinding, was wrong on both, and was forced to update on the labeled record.
- **Two coders with opposite biases broadly agreed.** Word counts agree 100%, sentence counts agree 81%, compliance disagreements concentrate at a single splitter-boundary case. Findings reported above survive in both coders.
- **The deterministic, lexical nature of both coders is a real safeguard against LLM-prior contamination of the codes themselves.** The contamination shows up in interpretation, which is acknowledged here.

### What did not work, or worked partially

- The cross-coder join (`structural_heuristics.py --semantic-csv`) was not run as part of the original pipeline; the author had to retrofit it during interpretation. A clean follow-up should regenerate `cross_coder_join.csv` and ship it as a primary artifact.
- The semantic coder's lexicons largely failed to discriminate — every model's dominant mood was "serene" and dominant setting was "natural" because the lexicons are big enough to fire on essentially any creative-writing output. This is reported but not used to support any finding.
- The blinding had its intended effect on `claude-opus-4-7`'s human-interpretive pass *only because* the analyst announced labeled guesses early enough to lock them in before unblinding. Less disciplined interpretation would have reasoned in circles.
- The "format-rigid / format-adaptive / format-minimal" split is `claude-opus-4-7`'s reading of patterns that do exist in the data, but its specific framing is the part most vulnerable to the analyst's biases. A different analyst might describe the same data as a different 2-2-2 split. Treat the labels as suggestive, not definitive.

## 5. Caveats

Carrying forward from `PREREGISTRATION.md`, with a few additions:

- n=10 per (model, prompt) cell at temperature 1.0 is small. Findings here are hypotheses, not conclusions.
- Cold contextless prompts measure defaults, not behavior under typical use. The "Here is..." preamble result in particular may reflect a Sonnet behavior that disappears entirely with any system prompt; this experiment cannot tell.
- Length-constraint prompts conflate instruction-following with style. Section 3.5's read is one interpretation of the boundary cases; "Haiku is sloppier on counts" is another. The data supports both.
- `max_tokens=400` is an active constraint on three of the six models for open-length prompts (Section 3.4). Any embedding or lexical analysis on open-prompt cells should report this confound.
- The two coders are written by two of the six subjects. Even with deterministic matching, choice of features encodes priors. The structural coder's emphasis on em-dashes and titles reflects `claude-opus-4-7`'s priors about what tells exist.
- One of the prompts has a typo: `poem_lt5` reads "fewer **then** 5 lines." Models may or may not have parsed this as "than"; the typo is identical across all 540 calls so it does not differ across models, but it is an instruction-following hazard.
- Model snapshots: only `claude-haiku-4-5-20251001` is pinned to a dated snapshot. The other five model identifiers may point to mutable deployments; results may not reproduce on later dates.

## 6. Summary table

| Finding | Strength | Survives unblinding |
|---|---|---|
| Em-dashes are not a Claude tell here; they live at gpt-5.4-nano | High | Yes |
| "Here is..." preamble is not a GPT tell here; it lives at claude-sonnet-4-6, conditional on length constraint and category | High | Yes |
| Claude opening-word distributions are concentrated on "the"; GPT distributions are dispersed | High | Yes |
| 2-2-2 format split (rigid / adaptive / minimal); does not map to family or scale | Medium | Yes (descriptively); the framing is biased |
| Truncation is an open-prompt phenomenon, peaking at Opus 67% | High | Yes |
| All compliance failures are Claude; Haiku's cluster at the 4-vs-5 boundary | Medium | Yes |
| Within-model embedding-distance / lexical-diversity comparisons | Not yet computed | Pending |

## 7. Next steps

This is a provisional report. To finalize:

1. Run `structural_heuristics.py --semantic-csv ...` to generate the proper `cross_coder_join.csv`.
2. Run the embedding-distance analyses described in Section 6.5 of `PREREGISTRATION.md`. They are not in this report.
3. Resolve which preregistration is *the* preregistration — this repo currently has two semi-overlapping ones (`PREREGISTRATION.md` and `model_comparison_preregistration.md`) which will be confusing for any reader.
4. Decide on truncation handling: either re-run open-length cells at higher `max_tokens`, or restrict open-length analyses to the 50% of cells that did not truncate (with that caveat reported).
5. Manual review of the blind sample CSV by a human coder (not by either author of the heuristic coders), to validate the preamble-rate finding in particular, since that is the most surprising of the headline results.
