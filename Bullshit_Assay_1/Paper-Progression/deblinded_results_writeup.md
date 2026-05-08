# De-blinded results write-up

## Summary

The de-blinded results show a large and highly interpretable separation between the GPT and Claude families, but the separation is driven primarily by **surface form and formatting** rather than by the more semantic features. Across 540 coded outputs, Claude-family outputs were overwhelmingly more likely to include title-like first lines, multi-line formatting, and meta-preambles, whereas GPT-family outputs were usually delivered as single prose blocks. These structural features were much stronger discriminators than mood, setting, plot arc, person, tense, or other semantic labels.

The strongest individual discriminator was title-line use. GPT models used titles in only 10.0% of outputs, while Claude models used them in 91.5%. Conversely, GPT models used single-block formatting in 65.6% of outputs, compared with only 7.8% for Claude models. These are not subtle stylistic differences; they are large family-level fingerprints that would likely support blind classification of model family from formatting alone.

At the individual-model level, `claude-haiku-4-5-20251001` and `claude-sonnet-4-6` were the most consistently formatted models, with title-line rates of 100.0% and 98.9%, respectively, and single-block rates of 0.0%. `gpt-5.4` and `gpt-5.4-nano` were the most consistently prose-block-like, with title-line rates of 2.2% and 5.6% and single-block rates of 64.4% and 66.7%. `gpt-5.4-mini` was intermediate among GPT models, preserving the prose-block tendency but using titles more often than the other GPT variants. `claude-opus-4-7` was intermediate among Claude models: still highly title-oriented, but less completely formatted than Sonnet or Haiku, and also the model with the highest truncation rate.

## Data and design

The analyzed dataset contains 540 outputs from six de-blinded models, with 90 outputs per model. The structural and semantic coded outputs were joined by `output_id`, and the de-blinding maps aligned exactly between the structural labels (`M1`–`M6`) and semantic labels (`Model A`–`Model F`). The de-blinded mapping is:

| Structural label | Semantic label | Model | Family |
| --- | --- | --- | --- |
| M1 | Model A | gpt-5.4 | GPT |
| M2 | Model B | gpt-5.4-nano | GPT |
| M3 | Model C | claude-opus-4-7 | Claude |
| M4 | Model D | claude-sonnet-4-6 | Claude |
| M5 | Model E | gpt-5.4-mini | GPT |
| M6 | Model F | claude-haiku-4-5-20251001 | Claude |

The analysis treats each coded output as one observation. The p-values reported below are therefore useful screening statistics, but they should not be treated as final inferential estimates because the same prompt grid was repeated across models. A paper-grade confirmatory analysis should use a prompt-blocked design or mixed-effects model with prompt identity treated as a blocking or random effect.

## Model-level descriptive results

| Model | Family | Blind labels | n | Words mean | Semantic sent. mean | Line mean | Title rate | Single-block rate | Truncation | Compliance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.4 | GPT | M1/Model A | 90 | 109.7 | 7.40 | 6.68 | 2.2% | 64.4% | 5.6% | 100.0% |
| gpt-5.4-nano | GPT | M2/Model B | 90 | 119.4 | 7.26 | 6.72 | 5.6% | 66.7% | 11.1% | 100.0% |
| claude-opus-4-7 | Claude | M3/Model C | 90 | 108.6 | 6.03 | 6.53 | 75.6% | 23.3% | 22.2% | 96.7% |
| claude-sonnet-4-6 | Claude | M4/Model D | 90 | 112.2 | 6.44 | 9.52 | 98.9% | 0.0% | 0.0% | 98.3% |
| gpt-5.4-mini | GPT | M5/Model E | 90 | 116.7 | 7.08 | 7.69 | 22.2% | 65.6% | 8.9% | 100.0% |
| claude-haiku-4-5-20251001 | Claude | M6/Model F | 90 | 119.1 | 6.66 | 7.12 | 100.0% | 0.0% | 1.1% | 90.0% |

The model-level descriptive table shows three broad patterns. First, average length did not cleanly separate families: GPT outputs averaged 115.3 words and Claude outputs averaged 113.3 words. Second, line and paragraph organization did separate families, with Claude producing more visually segmented text. Third, compliance was generally high, but not identical across models; the GPT models had perfect constrained-prompt compliance under the semantic coder, while Claude-family compliance was lower, especially for `claude-haiku-4-5-20251001`.

The most striking individual feature is the near-binary formatting split. `claude-sonnet-4-6` and `claude-haiku-4-5-20251001` almost always began with a title-like line and never produced single-block outputs. By contrast, `gpt-5.4`, `gpt-5.4-nano`, and `gpt-5.4-mini` usually produced compact single-block prose.

## Family-level descriptive results

| Family | n | Words mean | Line mean | Title rate | Single-block rate | Meta-preamble | Truncation | Compliance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT | 270 | 115.2 | 7.03 | 10.0% | 65.6% | 0.0% | 8.5% | 100.0% |
| Claude | 270 | 113.3 | 7.73 | 91.5% | 7.8% | 13.0% | 7.8% | 95.0% |

At the family level, the main result is a formatting divergence. GPT outputs were usually untitled, single-block prose; Claude outputs were usually titled, line-broken, and more explicitly framed. The family difference in title-line use was 81.5 percentage points, and the family difference in single-block formatting was 57.8 percentage points.

The families were much less distinct on total output length and truncation. GPT outputs were slightly longer on average by word count, while Claude outputs were slightly longer by character count and sentence-length measures. Truncation was similar at the family level: 8.5% for GPT and 7.8% for Claude. This family-level similarity masks an important individual-model result: `claude-opus-4-7` had a much higher truncation rate than any other model.

## Strongest across-model discriminators

The strongest categorical/binary differences across all six models were structural features.

| Metric | p | Cramér V | Range or model-specific pattern |
| --- | --- | --- | --- |
| title_line | 4.52e-80 | 0.840 | gpt-5.4 2.2%; claude-haiku-4-5-20251001 100.0% |
| single_block | 4.92e-43 | 0.621 | claude-sonnet-4-6 0.0%; gpt-5.4-nano 66.7% |
| meta_preamble | 7.38e-36 | 0.569 | gpt-5.4 0.0%; claude-sonnet-4-6 37.8% |
| dominant_imagery | 1.22e-13 | 0.216 | gpt-5.4: nature (58%); gpt-5.4-nano: light_dark (51%); claude-opus-4-7: nature (44%); claude-sonnet-4-6: light_dark (59%); gpt-5.4-mini: nature (51%); claude-haiku-4-5-20251001: light_dark (46%) |
| is_truncated | 1.73e-07 | 0.271 | claude-sonnet-4-6 0.0%; claude-opus-4-7 22.2% |
| dominant_plot_arc | 1.35e-06 | 0.189 | gpt-5.4: none_detected (37%); gpt-5.4-nano: discovery (38%); claude-opus-4-7: none_detected (46%); claude-sonnet-4-6: none_detected (33%); gpt-5.4-mini: none_detected (32%); claude-haiku-4-5-20251001: discovery (28%) |

The title-line, single-block, and meta-preamble results are large enough to be treated as robust descriptive fingerprints. Title-line use had Cramér’s V = 0.840, single-block formatting had Cramér’s V = 0.621, and meta-preamble use had Cramér’s V = 0.569. These effect sizes are much larger than those for most semantic content labels.

The strongest continuous/count differences also leaned structural.

| Metric | p | Epsilon² | Range |
| --- | --- | --- | --- |
| paragraph_count | 6.76e-17 | 0.150 | gpt-5.4-nano 3.10; claude-sonnet-4-6 5.73 |
| semicolon_count | 4.78e-13 | 0.116 | claude-sonnet-4-6 0.00; gpt-5.4-nano 0.33 |
| em_dash_count | 9.76e-12 | 0.104 | gpt-5.4 0.36; gpt-5.4-nano 1.62 |
| sent_len_max | 1.56e-08 | 0.075 | gpt-5.4 24.09; claude-sonnet-4-6 37.81 |
| sent_len_mean | 1.92e-06 | 0.055 | gpt-5.4 17.44; claude-sonnet-4-6 22.75 |
| hedge_count | 0.004 | 0.023 | claude-haiku-4-5-20251001 0.26; gpt-5.4-nano 0.69 |

Paragraph count was the strongest continuous discriminator. `gpt-5.4-nano` had the lowest average paragraph count, while `claude-sonnet-4-6` had the highest. Sentence length measures also favored Claude models, especially `claude-sonnet-4-6`, which had the highest maximum and mean sentence lengths. Punctuation features distinguished models as well: `gpt-5.4-nano` stood out for em-dash and semicolon use, while `claude-sonnet-4-6` had the lowest semicolon count.

## GPT vs Claude family tests

The family-level tests reinforce the model-level pattern. The strongest binary/rate differences were:

| Metric | GPT | Claude | GPT−Claude | p | Effect |
| --- | --- | --- | --- | --- | --- |
| title_line | 10.0% | 91.5% | -81.5% | 2.91e-79 | 0.811 |
| single_block | 65.6% | 7.8% | 57.8% | 1.43e-43 | 0.596 |
| meta_preamble | 0.0% | 13.0% | -13.0% | 2.80e-09 | 0.256 |
| compliance_struct_yes_constrained | 100.0% | 93.3% | 6.7% | 0.001 | 0.170 |
| compliance_sem_yes_constrained | 100.0% | 95.0% | 5.0% | 0.007 | 0.142 |
| is_truncated | 8.5% | 7.8% | 0.7% | 0.875 | 0.007 |

The strongest continuous/count differences were:

| Metric | GPT mean | Claude mean | GPT−Claude | p | Rank-biserial |
| --- | --- | --- | --- | --- | --- |
| paragraph_count | 3.39 | 4.50 | -1.11 | 1.12e-18 | -0.424 |
| sent_len_max | 24.78 | 33.29 | -8.50 | 6.55e-10 | -0.307 |
| sent_len_mean | 18.04 | 21.47 | -3.43 | 1.06e-06 | -0.243 |
| semicolon_count | 0.17 | 0.02 | 0.15 | 4.85e-07 | 0.115 |
| real_animal_count | 0.16 | 0.30 | -0.14 | 1.81e-04 | -0.127 |
| type_token_ratio | 0.79 | 0.77 | 0.01 | 0.026 | 0.111 |

The family contrast can be summarized simply: **GPT models tend to answer as prose; Claude models tend to answer as formatted artifacts.** Claude outputs had more paragraphs, longer sentence-length measures, and much higher title-line use. GPT outputs had higher single-block rates, more semicolon use, slightly higher type-token ratio, and somewhat more hedging.

## Semantic-content patterns

Semantic features did vary by model, but the effects were generally smaller and less diagnostic than the formatting features. The most common dominant mood across models was usually `serene`; the most common setting was usually `natural`; tense was most often `present`; and person was most often `third`. These regularities suggest that the prompt set elicited broadly similar content themes across models, while the models diverged more in how they packaged and framed that content.

There were still detectable semantic differences. Dominant imagery varied across models, with some models leaning toward `nature` imagery and others toward `light_dark` imagery. Dominant plot arc, dominant setting, tense, ending valence, and poetic mode also showed statistically detectable variation across models. However, the effect sizes for these features were substantially smaller than the title-line and single-block effects.

## Individual model profiles

- **gpt-5.4** (GPT; M1/Model A, n=90): mean length 109.7 words; title-line rate 2.2%; single-block rate 64.4%; truncation rate 5.6%; constrained semantic compliance 100.0%; dominant mood serene (47.8%); dominant setting natural (73.3%).
- **gpt-5.4-nano** (GPT; M2/Model B, n=90): mean length 119.4 words; title-line rate 5.6%; single-block rate 66.7%; truncation rate 11.1%; constrained semantic compliance 100.0%; dominant mood serene (51.1%); dominant setting natural (55.6%).
- **claude-opus-4-7** (Claude; M3/Model C, n=90): mean length 108.6 words; title-line rate 75.6%; single-block rate 23.3%; truncation rate 22.2%; constrained semantic compliance 96.7%; dominant mood serene (51.1%); dominant setting natural (74.4%).
- **claude-sonnet-4-6** (Claude; M4/Model D, n=90): mean length 112.2 words; title-line rate 98.9%; single-block rate 0.0%; truncation rate 0.0%; constrained semantic compliance 98.3%; dominant mood serene (61.1%); dominant setting natural (54.4%).
- **gpt-5.4-mini** (GPT; M5/Model E, n=90): mean length 116.7 words; title-line rate 22.2%; single-block rate 65.6%; truncation rate 8.9%; constrained semantic compliance 100.0%; dominant mood serene (53.3%); dominant setting natural (82.2%).
- **claude-haiku-4-5-20251001** (Claude; M6/Model F, n=90): mean length 119.1 words; title-line rate 100.0%; single-block rate 0.0%; truncation rate 1.1%; constrained semantic compliance 90.0%; dominant mood serene (63.3%); dominant setting natural (60.0%).

In narrative terms, `gpt-5.4` is the cleanest GPT-style baseline: low title use, frequent single-block presentation, perfect constrained-prompt compliance, and the highest formulaicness mean. `gpt-5.4-nano` is also GPT-like but longer and more punctuation-heavy, especially in em-dash and semicolon use. `gpt-5.4-mini` remains mostly GPT-like but shows more title use than the other GPT models.

`claude-opus-4-7` is the least rigidly formatted Claude model and the one with the highest truncation rate. It also had the lowest formulaicness score, suggesting less formulaic output under these heuristics, although that finding should be interpreted cautiously because the structural coder disclosure notes that the structural script was authored by this model. `claude-sonnet-4-6` is the most consistently formatted and visually segmented model: nearly always titled, never single-block, high paragraph count, high meta-preamble rate, and no truncation. `claude-haiku-4-5-20251001` is maximally title-formatted and had the weakest constrained-prompt compliance, concentrated in the `story_lt5` condition.

## Compliance and truncation

Compliance was high overall, but the non-compliance pattern was not evenly distributed. The GPT models had 100.0% semantic compliance on constrained prompts. The Claude family had 95.0% semantic compliance and 93.3% structural compliance. The difference was concentrated most clearly in `claude-haiku-4-5-20251001`, especially on the less-than-five-sentence story prompt.

Truncation was more model-specific than family-specific. The overall GPT and Claude truncation rates were similar, but `claude-opus-4-7` had a 22.2% truncation rate, compared with 0.0% for `claude-sonnet-4-6`, 1.1% for `claude-haiku-4-5-20251001`, and 5.6%–11.1% for the GPT variants. This makes truncation an important individual-model artifact rather than a simple family-level property.

## Coder agreement and measurement caveats

The semantic and structural coders agreed exactly on row alignment and on shared source fields. The main measurement disagreement was sentence counting. Sentence-count coders disagreed on 105 of 540 rows, or 19.4%. The disagreements were concentrated in open-ended story and animal-description prompts, where line breaks, fragments, titles, and complex punctuation make sentence boundaries ambiguous.

The largest sentence-count disagreement clusters were:

| Model | Prompt | Disagreements | Rate | Structural−Semantic mean diff |
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

Compliance disagreements were rare: only 3 of 540 rows. All three involved `claude-haiku-4-5-20251001` on the `story_lt5` prompt. In each case the semantic coder counted four sentences and marked the output compliant, while the structural coder counted five sentences and marked it non-compliant. This implies that compliance conclusions are robust overall, but the `story_lt5` condition is sensitive to sentence-boundary heuristics.

## Interpretation

The main conclusion is not that one model family is globally “better” or “worse.” Rather, the data show that different model families have markedly different output presentation habits under the same prompt grid. Claude models, especially Sonnet and Haiku, tend to convert prompts into more visibly structured artifacts, often with titles and line breaks. GPT models tend to answer in simpler prose blocks.

This matters for downstream evaluation. If human judges or automated scorers are supposed to evaluate only semantic content, visible formatting differences may unintentionally de-blind the model family. In this dataset, model identity is likely inferable from formatting alone. This is especially important because some of the strongest signals—title lines, single-block formatting, and preambles—are stylistic wrappers rather than substantive content differences.

For future analysis, the priority should be to separate three layers: content quality, stylistic packaging, and constraint-following. A prompt-blocked or mixed-effects model would help distinguish stable model effects from prompt-specific effects. A follow-up classifier analysis could also quantify how accurately model family or individual model can be predicted from structural features alone, semantic features alone, and both together.

## Limitations

Several limitations should be kept explicit. First, the statistics are output-level screening tests and do not yet account for prompt-level dependence. Second, the coding features are heuristic weak signals, not ground-truth human annotations. Third, sentence count is not fully stable across coders, especially in open-ended and highly formatted outputs. Fourth, one structural-coder manifest disclosed that the structural script was authored by `claude-opus-4-7`, which is itself one of the subjects of the experiment; structural features are less semantically interpretive than content features, but they are not bias-free. Finally, the results describe this prompt grid and sampling setup, not universal model behavior.
