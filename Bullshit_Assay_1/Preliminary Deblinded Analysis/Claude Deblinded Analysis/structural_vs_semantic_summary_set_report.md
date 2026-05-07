# Structural vs Semantic Summary-Set Difference Report

## Executive summary

- The four newly uploaded summary files are byte-for-byte duplicates of the previously uploaded summary files with the same base names. The analysis below therefore confirms and extends the earlier comparison rather than changing it.
- The two summary sets describe the same 54 model × prompt × length cells and the same 6 model-level rows. Structural blind labels `M1`–`M6` map exactly to semantic labels `Model A`–`Model F` by `n`, `word_count_mean`, and `word_count_median`.
- The directly comparable summary metrics match exactly for `n`, `word_count_mean`, `word_count_median`, `line_count_nonempty_mean`, and `line_count_nonempty_median` at both model and prompt levels.
- The only recurring numeric difference in common-ish metrics is sentence counting: structural uses `sentence_count_alt_*`, semantic uses `sentence_count_heuristic_*`. Differences are largest in open-ended animal and story prompts.
- Compliance summaries are almost identical except for `M6 / Model F`, especially the `story_lt5` cell. Semantic reports a 5/5 no/yes split for that cell, while structural top-share implies 8/10 no.

## File inventory and duplicate check

| Label | File | Rows | Cols | MD5 | Duplicate of earlier upload? |
| --- | --- | --- | --- | --- | --- |
| semantic_prompt | summary_by_blind_model_prompt_semantic(1).csv | 54 | 63 | ccff50ac547a89a9c045c471abe04693 | True |
| semantic_model | summary_by_blind_model_semantic(1).csv | 6 | 61 | 72dd374bbe7dee5010fb1aba078125d6 | True |
| structural_prompt | summary_by_blind_model_prompt_structural(1).csv | 54 | 74 | 6d7648c28cd081da9e2a77ad37e201f1 | True |
| structural_model | summary_by_blind_model_structural(1).csv | 6 | 72 | 042bcfe12b3bb61d0c2193b6d366bc9a | True |

## Model label mapping

| Structural label | Semantic label |
| --- | --- |
| M1 | Model A |
| M2 | Model B |
| M3 | Model C |
| M4 | Model D |
| M5 | Model E |
| M6 | Model F |

## Directly comparable metrics

These fields match exactly after applying the label map:

- `n`
- `word_count_mean` / `word_count_median`
- `line_count_nonempty_alt_mean` / `line_count_nonempty_mean`
- `line_count_nonempty_alt_median` / `line_count_nonempty_median`

Model-level mismatches across these directly comparable fields: **0**.
Prompt-level mismatches across these directly comparable fields: **0**.

## Sentence-count differences

Model-level sentence means:

| Structural | Semantic | Structural sentence mean | Semantic sentence mean | Signed delta |
| --- | --- | --- | --- | --- |
| M1 | Model A | 7.7667 | 7.4 | 0.3667 |
| M5 | Model E | 7.4222 | 7.0778 | 0.3444 |
| M3 | Model C | 5.7444 | 6.0333 | -0.2889 |
| M2 | Model B | 7.0556 | 7.2556 | -0.2 |
| M6 | Model F | 6.4556 | 6.6556 | -0.2 |
| M4 | Model D | 6.3556 | 6.4444 | -0.0888 |

Largest prompt-level sentence-count divergences:

| Structural | Semantic | Prompt | Length | Structural mean | Semantic mean | Signed delta | Word count mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | Model A | story | open | 30.3 | 27.3 | 3 | 309.6 |
| M6 | Model F | animal | open | 5.4 | 8.2 | -2.8 | 186.1 |
| M5 | Model E | story | open | 28 | 25.4 | 2.6 | 320.4 |
| M2 | Model B | animal | open | 7.9 | 10.4 | -2.5 | 204.9 |
| M3 | Model C | animal | open | 5.3 | 7 | -1.7 | 157.5 |
| M3 | Model C | story | open | 13.7 | 14.7 | -1 | 215.1 |
| M2 | Model B | story | lt10 | 7.7 | 7.2 | 0.5 | 149.2 |
| M6 | Model F | story | lt5 | 4.8 | 4.3 | 0.5 | 108.5 |
| M5 | Model E | story | lt5 | 3.9 | 3.5 | 0.4 | 82.1 |
| M4 | Model D | story | open | 19.8 | 20.2 | -0.4 | 206.7 |
| M6 | Model F | story | lt10 | 6.9 | 6.6 | 0.3 | 147.2 |
| M4 | Model D | animal | open | 5.2 | 5.4 | -0.2 | 188.3 |
| M2 | Model B | story | lt5 | 3.9 | 3.7 | 0.2 | 76.1 |
| M5 | Model E | story | lt10 | 7.1 | 6.9 | 0.2 | 148 |
| M6 | Model F | story | open | 23.1 | 23 | 0.1 | 251.1 |

Sentence-count differences summarized by prompt group:

| Prompt | Length | Cells with diff | Sum abs delta | Mean signed delta |
| --- | --- | --- | --- | --- |
| animal | open | 6 | 7.4 | -1.2 |
| story | open | 5 | 7.1 | 0.86 |
| story | lt10 | 6 | 1.3 | 0.15 |
| story | lt5 | 5 | 1.3 | 0.26 |
| animal | lt10 | 2 | 0.2 | 0.1 |
| poem | open | 1 | 0.1 | -0.1 |

## Compliance-summary differences

Model-level compliance top-share comparison:

| Structural | Semantic | Structural top/share | Semantic top/share | Share delta | Semantic counts |
| --- | --- | --- | --- | --- | --- |
| M6 | Model F | yes / 0.5667 | yes / 0.6000 | -0.0333 | {"yes": 54, "not_applicable": 30, "no": 6} |
| M1 | Model A | yes / 0.6667 | yes / 0.6667 | 0 | {"yes": 60, "not_applicable": 30} |
| M2 | Model B | yes / 0.6667 | yes / 0.6667 | 0 | {"yes": 60, "not_applicable": 30} |
| M3 | Model C | yes / 0.6444 | yes / 0.6444 | 0 | {"yes": 58, "not_applicable": 30, "no": 2} |
| M4 | Model D | yes / 0.6556 | yes / 0.6556 | 0 | {"yes": 59, "not_applicable": 30, "no": 1} |
| M5 | Model E | yes / 0.6667 | yes / 0.6667 | 0 | {"yes": 60, "not_applicable": 30} |

Prompt-level compliance cells with any top/share difference:

| Structural | Semantic | Prompt | Length | Structural top/share | Semantic top/share | Semantic counts |
| --- | --- | --- | --- | --- | --- | --- |
| M6 | Model F | story | lt5 | no / 0.8000 | no / 0.5000 | {"no": 5, "yes": 5} |

## What each set uniquely adds

### Semantic set
Semantic fields add content/style heuristics such as mood, imagery, setting, plot arc, valence, person/tense, formulaicness, entity counts, and type-token ratio.

| Semantic model | Mood | Imagery | Setting | Plot arc | Valence | Formulaicness mean | TTR mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Model A | serene (0.48) | nature (0.58) | natural (0.73) | none_detected (0.37) | neutral_or_unclear (0.38) | 1.6889 | 0.7922 |
| Model B | serene (0.51) | light_dark (0.51) | natural (0.56) | discovery (0.38) | neutral_or_unclear (0.37) | 1.3889 | 0.7877 |
| Model C | serene (0.51) | nature (0.44) | natural (0.74) | none_detected (0.46) | neutral_or_unclear (0.54) | 0.9444 | 0.7939 |
| Model D | serene (0.61) | light_dark (0.59) | natural (0.54) | none_detected (0.33) | neutral_or_unclear (0.32) | 1.4444 | 0.7506 |
| Model E | serene (0.53) | nature (0.51) | natural (0.82) | none_detected (0.32) | neutral_or_unclear (0.33) | 1.3667 | 0.7778 |
| Model F | serene (0.63) | light_dark (0.46) | natural (0.60) | discovery (0.28) | neutral_or_unclear (0.36) | 1.5 | 0.7779 |

### Structural set
Structural fields add surface-form heuristics such as single-block layout, title lines, meta preambles, punctuation counts, sentence-length distribution, anaphora, closers, pivots, and quote style.

| Structural | Semantic | Single block top/share | Title line top/share | Meta preamble top/share | Colon mean | Em dash mean | Semicolon mean | Sentence length mean | Very short share | Very long share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | Model A | True (0.64) | False (0.98) | False (1.00) | 0.3778 | 0.3556 | 0.0556 | 17.4392 | 0.041 | 0.1316 |
| M2 | Model B | True (0.67) | False (0.94) | False (1.00) | 0.8556 | 1.6222 | 0.3333 | 18.9409 | 0.0184 | 0.1631 |
| M3 | Model C | False (0.77) | True (0.76) | False (0.99) | 0.3889 | 0.6222 | 0.0556 | 19.3956 | 0.0187 | 0.1677 |
| M4 | Model D | False (1.00) | True (0.99) | False (0.62) | 0.9667 | 0.8111 | 0 | 22.7479 | 0.0326 | 0.2523 |
| M5 | Model E | True (0.66) | False (0.78) | False (1.00) | 0.7889 | 0.3667 | 0.1333 | 17.7417 | 0.02 | 0.1137 |
| M6 | Model F | False (1.00) | True (1.00) | False (1.00) | 0.8333 | 0.6889 | 0.0111 | 22.2711 | 0.0159 | 0.2663 |

## Interpretation

The summary sets are compatible and should be joined on the three prompt-level keys plus the blind-label map, or on model label after remapping at model level. The most important caution is that `sentence_count_alt_*` and `sentence_count_heuristic_*` are not interchangeable. They agree directionally, but open-ended prose exposes different boundary rules. Compliance is also mostly aligned, with a localized Model F/M6 discrepancy in the under-5-sentence story condition.