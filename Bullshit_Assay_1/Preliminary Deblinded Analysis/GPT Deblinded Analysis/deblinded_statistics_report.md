# De-blinded coded-output statistics

Source files analyzed: `coded_outputs_semantic(2).csv`, `coded_outputs_structural(2).csv`, `blind_model_map_PRIVATE_semantic.json`, and `blind_model_map_PRIVATE_structural.json`.

## Caveats

- These are output-level heuristic statistics. P-values below treat the 540 rows as independent observations. Because prompts are repeated across models, read them as screening evidence rather than a fully specified mixed-effects model.
- Semantic and structural coder fields are joined by `output_id`. Hidden placeholder columns were not used.

## De-blinded label map

| structural | semantic | model | family |
| --- | --- | --- | --- |
| M1 | Model A | gpt-5.4 | GPT |
| M2 | Model B | gpt-5.4-nano | GPT |
| M3 | Model C | claude-opus-4-7 | Claude |
| M4 | Model D | claude-sonnet-4-6 | Claude |
| M5 | Model E | gpt-5.4-mini | GPT |
| M6 | Model F | claude-haiku-4-5-20251001 | Claude |

## Model-level descriptive summary

| model | family | n | word_mean | sent_sem_mean | line_mean | title_rate | single_block_rate | truncation_rate | compliance_sem_rate_constrained | formulaicness_mean | type_token_ratio_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.4 | GPT | 90 | 109.67 | 7.40 | 6.68 | 2.2% | 64.4% | 5.6% | 100.0% | 1.69 | 0.79 |
| gpt-5.4-nano | GPT | 90 | 119.41 | 7.26 | 6.72 | 5.6% | 66.7% | 11.1% | 100.0% | 1.39 | 0.79 |
| claude-opus-4-7 | Claude | 90 | 108.63 | 6.03 | 6.53 | 75.6% | 23.3% | 22.2% | 96.7% | 0.94 | 0.79 |
| claude-sonnet-4-6 | Claude | 90 | 112.23 | 6.44 | 9.52 | 98.9% | 0.0% | 0.0% | 98.3% | 1.44 | 0.75 |
| gpt-5.4-mini | GPT | 90 | 116.67 | 7.08 | 7.69 | 22.2% | 65.6% | 8.9% | 100.0% | 1.37 | 0.78 |
| claude-haiku-4-5-20251001 | Claude | 90 | 119.06 | 6.66 | 7.12 | 100.0% | 0.0% | 1.1% | 90.0% | 1.50 | 0.78 |

## Family-level summary

| family | n | word_mean | line_mean | title_rate | single_block_rate | truncation_rate | compliance_sem_rate_constrained | formulaicness_mean | type_token_ratio_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT | 270 | 115.25 | 7.03 | 10.0% | 65.6% | 8.5% | 100.0% | 1.48 | 0.79 |
| Claude | 270 | 113.31 | 7.73 | 91.5% | 7.8% | 7.8% | 95.0% | 1.30 | 0.77 |

## Most discriminating continuous metrics across models

| metric | test | p | effect_epsilon2 | min_model | min_mean | max_model | max_mean | range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| paragraph_count | Kruskal-Wallis | 6.76e-17 | 0.150 | gpt-5.4-nano | 3.100 | claude-sonnet-4-6 | 5.733 | 2.633 |
| semicolon_count | Kruskal-Wallis | 4.78e-13 | 0.116 | claude-sonnet-4-6 | 0.000 | gpt-5.4-nano | 0.333 | 0.333 |
| em_dash_count | Kruskal-Wallis | 9.76e-12 | 0.104 | gpt-5.4 | 0.356 | gpt-5.4-nano | 1.622 | 1.267 |
| sent_len_max | Kruskal-Wallis | 1.56e-08 | 0.075 | gpt-5.4 | 24.089 | claude-sonnet-4-6 | 37.811 | 13.722 |
| sent_len_mean | Kruskal-Wallis | 1.92e-06 | 0.055 | gpt-5.4 | 17.439 | claude-sonnet-4-6 | 22.748 | 5.309 |
| hedge_count | Kruskal-Wallis | 0.00408 | 0.023 | claude-haiku-4-5-20251001 | 0.256 | gpt-5.4-nano | 0.689 | 0.433 |
| real_animal_count | Kruskal-Wallis | 0.00485 | 0.022 | gpt-5.4-mini | 0.100 | claude-sonnet-4-6 | 0.344 | 0.244 |
| repeated_bigram_types | Kruskal-Wallis | 0.00536 | 0.022 | claude-haiku-4-5-20251001 | 2.156 | gpt-5.4-mini | 2.856 | 0.700 |
| colon_count | Kruskal-Wallis | 0.00704 | 0.020 | gpt-5.4 | 0.378 | claude-sonnet-4-6 | 0.967 | 0.589 |
| type_token_ratio | Kruskal-Wallis | 0.00744 | 0.020 | claude-sonnet-4-6 | 0.751 | claude-opus-4-7 | 0.794 | 0.043 |
| present_tense_score | Kruskal-Wallis | 0.015 | 0.017 | gpt-5.4-mini | 11.867 | claude-haiku-4-5-20251001 | 15.333 | 3.467 |
| formulaicness | Kruskal-Wallis | 0.068 | 0.00984 | claude-opus-4-7 | 0.944 | gpt-5.4 | 1.689 | 0.744 |
| first_person_pronouns | Kruskal-Wallis | 0.079 | 0.00912 | gpt-5.4 | 0.378 | claude-opus-4-7 | 1.333 | 0.956 |
| intensifier_count | Kruskal-Wallis | 0.171 | 0.00515 | gpt-5.4-nano | 0.000 | claude-sonnet-4-6 | 0.089 | 0.089 |
| future_tense_score | Kruskal-Wallis | 0.218 | 0.0038 | gpt-5.4-nano | 0.144 | claude-haiku-4-5-20251001 | 0.311 | 0.167 |

## Most discriminating categorical/binary metrics across models

| metric | test | p | effect_cramers_v | min_model | min_rate | max_model | max_rate | top_by_model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| title_line | Chi-square | 4.52e-80 | 0.840 | gpt-5.4 | 2.2% | claude-haiku-4-5-20251001 | 100.0% |  |
| single_block | Chi-square | 4.92e-43 | 0.621 | claude-sonnet-4-6 | 0.0% | gpt-5.4-nano | 66.7% |  |
| meta_preamble | Chi-square | 7.38e-36 | 0.569 | gpt-5.4 | 0.0% | claude-sonnet-4-6 | 37.8% |  |
| dominant_imagery | Chi-square | 1.22e-13 | 0.216 |  |  |  |  | gpt-5.4: nature (58%); gpt-5.4-nano: light_dark (51%); claude-opus-4-7: nature (44%); claude-sonnet-4-6: light_dark (59%); gpt-5.4-mini: nature (51%); claude-haiku-4-5-20251001: light_dark (46%) |
| is_truncated | Chi-square | 1.73e-07 | 0.271 | claude-sonnet-4-6 | 0.0% | claude-opus-4-7 | 22.2% |  |
| dominant_plot_arc | Chi-square | 1.35e-06 | 0.189 |  |  |  |  | gpt-5.4: none_detected (37%); gpt-5.4-nano: discovery (38%); claude-opus-4-7: none_detected (46%); claude-sonnet-4-6: none_detected (33%); gpt-5.4-mini: none_detected (32%); claude-haiku-4-5-20251001: discovery (28%) |
| dominant_setting | Chi-square | 1.22e-05 | 0.157 |  |  |  |  | gpt-5.4: natural (73%); gpt-5.4-nano: natural (56%); claude-opus-4-7: natural (74%); claude-sonnet-4-6: natural (54%); gpt-5.4-mini: natural (82%); claude-haiku-4-5-20251001: natural (60%) |
| tense | Chi-square | 4.5e-05 | 0.187 |  |  |  |  | gpt-5.4: present (66%); gpt-5.4-nano: present (67%); claude-opus-4-7: present (67%); claude-sonnet-4-6: present (67%); gpt-5.4-mini: present (67%); claude-haiku-4-5-20251001: present (67%) |
| ending_valence | Chi-square | 0.000118 | 0.149 |  |  |  |  | gpt-5.4: neutral_or_unclear (38%); gpt-5.4-nano: neutral_or_unclear (37%); claude-opus-4-7: neutral_or_unclear (54%); claude-sonnet-4-6: neutral_or_unclear (32%); gpt-5.4-mini: neutral_or_unclear (33%); claude-haiku-4-5-20251001: neutral_or_unclear (36%) |
| dominant_mood | Chi-square | 0.00359 | 0.159 |  |  |  |  | gpt-5.4: serene (48%); gpt-5.4-nano: serene (51%); claude-opus-4-7: serene (51%); claude-sonnet-4-6: serene (61%); gpt-5.4-mini: serene (53%); claude-haiku-4-5-20251001: serene (63%) |
| poetic_mode | Chi-square | 0.00617 | 0.141 |  |  |  |  | gpt-5.4: free_verse_or_narrative (44%); gpt-5.4-nano: free_verse_or_narrative (33%); claude-opus-4-7: not_poem_like (36%); claude-sonnet-4-6: not_poem_like (39%); gpt-5.4-mini: free_verse_or_narrative (34%); claude-haiku-4-5-20251001: not_poem_like (44%) |
| person | Chi-square | 0.025 | 0.126 |  |  |  |  | gpt-5.4: third (77%); gpt-5.4-nano: third (71%); claude-opus-4-7: third (79%); claude-sonnet-4-6: third (70%); gpt-5.4-mini: third (77%); claude-haiku-4-5-20251001: third (70%) |
| closer_ends_question | Chi-square | 0.175 | 0.119 | gpt-5.4-nano | 0.0% | claude-opus-4-7 | 3.3% |  |
| ending_pivot_present_struct | Chi-square | 0.791 | 0.067 | claude-sonnet-4-6 | 46.7% | gpt-5.4 | 54.4% |  |

## Strongest GPT-vs-Claude family differences

Binary/rate features:

| metric | test | p | GPT rate | Claude rate | GPT−Claude | phi |
| --- | --- | --- | --- | --- | --- | --- |
| title_line | Chi-square 2x2 | 2.91e-79 | 10.0% | 91.5% | -81.5% | 0.811 |
| single_block | Chi-square 2x2 | 1.43e-43 | 65.6% | 7.8% | 57.8% | 0.596 |
| meta_preamble | Chi-square 2x2 | 2.80e-09 | 0.0% | 13.0% | -13.0% | 0.256 |
| compliance_struct_yes_constrained | Chi-square 2x2 | 0.00124 | 100.0% | 93.3% | 6.7% | 0.170 |
| compliance_sem_yes_constrained | Chi-square 2x2 | 0.00692 | 100.0% | 95.0% | 5.0% | 0.142 |
| ending_pivot_present_struct | Chi-square 2x2 | 0.344 | 53.3% | 48.9% | 4.4% | 0.041 |
| closer_ends_question | Chi-square 2x2 | 0.447 | 0.7% | 1.9% | -1.1% | 0.033 |
| is_truncated | Chi-square 2x2 | 0.875 | 8.5% | 7.8% | 0.7% | 0.00677 |

Continuous/count features:

| metric | test | p | GPT mean | Claude mean | GPT−Claude mean | rank-biserial |
| --- | --- | --- | --- | --- | --- | --- |
| paragraph_count | Mann-Whitney U | 1.12e-18 | 3.385 | 4.500 | -1.115 | -0.424 |
| sent_len_max | Mann-Whitney U | 6.55e-10 | 24.781 | 33.285 | -8.504 | -0.307 |
| semicolon_count | Mann-Whitney U | 4.85e-07 | 0.174 | 0.022 | 0.152 | 0.115 |
| sent_len_mean | Mann-Whitney U | 1.06e-06 | 18.041 | 21.472 | -3.431 | -0.243 |
| real_animal_count | Mann-Whitney U | 1.81e-04 | 0.159 | 0.300 | -0.141 | -0.127 |
| repeated_bigram_types | Mann-Whitney U | 0.00393 | 2.452 | 2.270 | 0.181 | -0.138 |
| present_tense_score | Mann-Whitney U | 0.00468 | 12.274 | 13.733 | -1.459 | -0.141 |
| future_tense_score | Mann-Whitney U | 0.014 | 0.185 | 0.285 | -0.100 | -0.082 |
| type_token_ratio | Mann-Whitney U | 0.026 | 0.786 | 0.774 | 0.012 | 0.111 |
| hedge_count | Mann-Whitney U | 0.028 | 0.593 | 0.374 | 0.219 | 0.089 |
| first_person_pronouns | Mann-Whitney U | 0.050 | 0.537 | 1.107 | -0.570 | -0.080 |
| char_count | Mann-Whitney U | 0.050 | 662.107 | 682.378 | -20.270 | -0.097 |

## Sentence-count coder disagreement clusters

Sentence-count coders disagreed on 105 / 540 rows (19.4%). Compliance coders disagreed on 3 / 540 rows (0.6%).
| model | prompt_id | n_disagree | rate | mean_diff_struct_minus_sem |
| --- | --- | --- | --- | --- |
| claude-haiku-4-5-20251001 | animal_open | 10 | 100.0% | -2.80 |
| claude-sonnet-4-6 | story_open | 10 | 100.0% | -0.40 |
| gpt-5.4 | story_open | 9 | 90.0% | 3.33 |
| claude-opus-4-7 | animal_open | 9 | 90.0% | -1.89 |
| claude-opus-4-7 | story_open | 9 | 90.0% | -1.11 |
| gpt-5.4-mini | story_open | 8 | 80.0% | 3.25 |
| gpt-5.4-nano | animal_open | 7 | 70.0% | -3.57 |
| claude-haiku-4-5-20251001 | story_lt5 | 5 | 50.0% | 1.00 |
| gpt-5.4-nano | story_lt10 | 5 | 50.0% | 1.00 |
| claude-haiku-4-5-20251001 | story_open | 5 | 50.0% | 0.20 |
| gpt-5.4-mini | story_lt5 | 4 | 40.0% | 1.00 |
| gpt-5.4 | story_lt10 | 3 | 30.0% | 0.33 |
| gpt-5.4-nano | story_open | 3 | 30.0% | 0.00 |
| claude-haiku-4-5-20251001 | story_lt10 | 2 | 20.0% | 1.50 |
| claude-sonnet-4-6 | animal_open | 2 | 20.0% | -1.00 |
| gpt-5.4-mini | story_lt10 | 2 | 20.0% | 1.00 |
| gpt-5.4-nano | story_lt5 | 2 | 20.0% | 1.00 |
| gpt-5.4-mini | animal_open | 2 | 20.0% | -0.50 |
| claude-haiku-4-5-20251001 | animal_lt10 | 1 | 10.0% | 1.00 |
| claude-opus-4-7 | animal_lt10 | 1 | 10.0% | 1.00 |

## Compliance disagreements

| output_id | actual_model | prompt_id | word_count | compliance_sem | compliance_struct | sentence_sem | sentence_struct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0dd08ac8f8eb | claude-haiku-4-5-20251001 | story_lt5 | 127.00 | yes | no | 4.00 | 5.00 |
| 108355196aa1 | claude-haiku-4-5-20251001 | story_lt5 | 114.00 | yes | no | 4.00 | 5.00 |
| 9895e976224a | claude-haiku-4-5-20251001 | story_lt5 | 95.00 | yes | no | 4.00 | 5.00 |

## Files generated

- `deblinded_model_summary.csv`
- `deblinded_family_summary.csv`
- `deblinded_prompt_model_summary.csv`
- `deblinded_model_tests_continuous.csv`
- `deblinded_model_tests_categorical.csv`
- `deblinded_family_tests.csv`
- `deblinded_pairwise_selected_tests.csv`
- `deblinded_sentence_disagreement_by_prompt.csv`
- `deblinded_compliance_disagreements.csv`
