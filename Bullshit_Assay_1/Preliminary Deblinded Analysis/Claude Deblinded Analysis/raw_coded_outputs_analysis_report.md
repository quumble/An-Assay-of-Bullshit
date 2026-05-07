# Raw coded outputs: semantic vs structural analysis

## Scope and file identity

I inspected the two raw coded-output files just uploaded:

- `coded_outputs_semantic(2).csv`
- `coded_outputs_structural(2).csv`

I excluded `model_hidden` and `provider_hidden` from analysis to preserve the blind setup.

|file|bytes|sha256 prefix|relationship to unsuffixed file|
|---|---|---|---|
|semantic(2)|615514|2d58d6ba4785f2c4|same as semantic.csv|
|structural(2)|526665|05028313f5ee7c21|same as structural.csv|


## Row alignment

- Semantic rows: **540**
- Structural rows: **540**
- Shared `output_id`s: **540**
- Semantic duplicate IDs: **0**
- Structural duplicate IDs: **0**
- Semantic columns: **80**; analyzed non-hidden columns: **78**
- Structural columns: **63**; analyzed non-hidden columns: **61**

The raw files align one-to-one by `output_id`.

## Blind-label alignment

|structural label|semantic label|matched rows|
|---|---|---|
|M1|Model A|90|
|M2|Model B|90|
|M3|Model C|90|
|M4|Model D|90|
|M5|Model E|90|
|M6|Model F|90|


This is a blind-label crosswalk only. It does not identify providers or real model names.

## Shared field equality

The shared non-hidden fields were compared exactly, excluding `blind_model` because the two coders use different blind-label schemes.

|shared field with differences|row differences|
|---|---|
|No shared non-model fields differed|0|


In plain terms: the overlapping source-data fields match. The two raw files are different coder views of the same 540 outputs.

## Direct coder disagreements

### Line count

- `line_count_nonempty` vs `line_count_nonempty_alt`: **0 / 540** differences.

### Sentence count

- `sentence_count_heuristic` vs `sentence_count_alt`: **105 / 540** differences (**19.4%**).

By model:

|structural|semantic|sentence-count diffs|rate within model|
|---|---|---|---|
|M6|Model F|23|25.6%|
|M3|Model C|21|23.3%|
|M2|Model B|17|18.9%|
|M5|Model E|16|17.8%|
|M4|Model D|14|15.6%|
|M1|Model A|14|15.6%|


By prompt cell:

|prompt_id|category|length|sentence-count diffs|rate within prompt|
|---|---|---|---|---|
|story_open|story|open|44|73.3%|
|animal_open|animal|open|31|51.7%|
|story_lt10|story|lt10|14|23.3%|
|story_lt5|story|lt5|13|21.7%|
|animal_lt10|animal|lt10|2|3.3%|
|poem_open|poem|open|1|1.7%|


The disagreement pattern is not random: it is concentrated in open-ended story and animal prompts, where punctuation, fragments, and formatting make sentence counting ambiguous.

### Compliance

- `constraint_compliant_heuristic` vs `constraint_compliant_alt`: **3 / 540** differences.

|output_id|semantic|structural|structural model|semantic model|prompt_id|category|length|iteration|word_count|
|---|---|---|---|---|---|---|---|---|---|
|9895e976224a|yes|no|M6|Model F|story_lt5|story|lt5|6|95|
|108355196aa1|yes|no|M6|Model F|story_lt5|story|lt5|1|114|
|0dd08ac8f8eb|yes|no|M6|Model F|story_lt5|story|lt5|2|127|


All compliance disagreements are concentrated in the same blind model and prompt type.

## Model-level snapshot

|structural|semantic|n|word mean|struct sent mean|sem sent mean|line mean|truncated|single block|title line|meta preamble|formulaicness|type-token ratio|invented entities|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|M1|Model A|90|109.67|7.77|7.40|6.68|5.6%|64.4%|2.2%|0.0%|1.689|0.792|1.66|
|M2|Model B|90|119.41|7.06|7.26|6.72|11.1%|66.7%|5.6%|0.0%|1.389|0.788|2.11|
|M3|Model C|90|108.63|5.74|6.03|6.53|22.2%|23.3%|75.6%|1.1%|0.944|0.794|2.56|
|M4|Model D|90|112.23|6.36|6.44|9.52|0.0%|0.0%|98.9%|37.8%|1.444|0.751|2.78|
|M5|Model E|90|116.67|7.42|7.08|7.69|8.9%|65.6%|22.2%|0.0%|1.367|0.778|1.62|
|M6|Model F|90|119.06|6.46|6.66|7.12|1.1%|0.0%|100.0%|0.0%|1.500|0.778|2.52|


Notable patterns:

- **M3 / Model C** has the highest truncation rate.
- **M4 / Model D** has no truncation and the highest line count, implying more line-broken formatting.
- **M2 / Model B** and **M6 / Model F** are the longest by average word count.
- Title-line usage is a major differentiator: M6 / Model F uses title lines most often, while M1 / Model A and M5 / Model E almost never do.
- Structural and semantic sentence means are broadly close, but their differences are large enough that the two sentence counters should not be pooled as one variable.

## Prompt-level snapshot

|category|length|n|word mean|struct sent mean|sem sent mean|truncated|struct compliant yes|sem compliant yes|formulaicness|single block|title line|
|---|---|---|---|---|---|---|---|---|---|---|---|
|animal|lt10|60|116.25|7.00|6.97|0.0%|100.0%|100.0%|1.733|50.0%|50.0%|
|animal|lt5|60|68.57|3.68|3.68|0.0%|98.3%|98.3%|1.333|50.0%|50.0%|
|animal|open|60|179.27|7.08|8.28|16.7%|0.0%|0.0%|2.483|0.0%|75.0%|
|poem|lt10|60|44.20|2.83|2.83|0.0%|100.0%|100.0%|0.100|46.7%|50.0%|
|poem|lt5|60|23.45|1.23|1.23|0.0%|100.0%|100.0%|0.100|66.7%|33.3%|
|poem|open|60|104.13|4.93|4.95|0.0%|0.0%|0.0%|0.683|0.0%|65.0%|
|story|lt10|60|140.80|7.22|7.07|0.0%|98.3%|98.3%|1.917|50.0%|48.3%|
|story|lt5|60|81.48|3.90|3.68|0.0%|83.3%|88.3%|1.200|66.7%|33.3%|
|story|open|60|270.35|23.32|22.60|56.7%|0.0%|0.0%|2.950|0.0%|51.7%|


Prompt-level takeaways:

- Open-ended story prompts are much longer and structurally denser than constrained prompts.
- Poem outputs are much more line-broken and less often single-block prose.
- Truncation mostly appears in longer/open outputs, but also appears in some constraint cells.
- Compliance is high overall in constrained cells; the main exception is the `story_lt5` discrepancy noted above.

## Semantic-feature distributions

Top values for major semantic categorical fields:

|field|value|count|share|
|---|---|---|---|
|person_heuristic|third|399|73.9%|
|person_heuristic|none_detected|60|11.1%|
|person_heuristic|first|56|10.4%|
|person_heuristic|mixed|19|3.5%|
|person_heuristic|second|6|1.1%|
|tense_heuristic|present|359|66.5%|
|tense_heuristic|past|132|24.4%|
|tense_heuristic|mixed|49|9.1%|
|dominant_setting_heuristic|natural|360|66.7%|
|dominant_setting_heuristic|domestic|118|21.9%|
|dominant_setting_heuristic|none_detected|17|3.1%|
|dominant_setting_heuristic|cosmic|16|3.0%|
|dominant_setting_heuristic|historical|16|3.0%|
|dominant_mood_heuristic|serene|295|54.6%|
|dominant_mood_heuristic|wistful|78|14.4%|
|dominant_mood_heuristic|melancholic|57|10.6%|
|dominant_mood_heuristic|inspirational|42|7.8%|
|dominant_mood_heuristic|eerie|27|5.0%|
|dominant_plot_arc_heuristic|none_detected|177|32.8%|
|dominant_plot_arc_heuristic|discovery|145|26.9%|
|dominant_plot_arc_heuristic|loss|82|15.2%|
|dominant_plot_arc_heuristic|observation|36|6.7%|
|dominant_plot_arc_heuristic|escape|31|5.7%|
|dominant_imagery_heuristic|light_dark|230|42.6%|
|dominant_imagery_heuristic|nature|195|36.1%|
|dominant_imagery_heuristic|memory|48|8.9%|
|dominant_imagery_heuristic|body|33|6.1%|
|dominant_imagery_heuristic|seasons_time|21|3.9%|
|poetic_mode_heuristic|not_poem_like|177|32.8%|
|poetic_mode_heuristic|free_verse_or_narrative|166|30.7%|
|poetic_mode_heuristic|rhyme_heavy|154|28.5%|
|poetic_mode_heuristic|lyric_or_imagistic|43|8.0%|
|ending_valence_heuristic|neutral_or_unclear|207|38.3%|
|ending_valence_heuristic|positive|149|27.6%|
|ending_valence_heuristic|negative|74|13.7%|
|ending_valence_heuristic|twist_or_turn|62|11.5%|
|ending_valence_heuristic|bittersweet|44|8.1%|


Broadly, the semantic coder is extracting interpretable content differences: tense/person, setting, mood, plot arc, imagery, poetic mode, and ending valence.

## Structural-feature rates

|structural feature|true rate|
|---|---|
|blank_line_separated|63.3%|
|closer_ends_with_ellipsis|0.0%|
|closer_ends_with_exclaim|0.0%|
|closer_ends_with_question|1.3%|
|closer_is_longest|17.6%|
|closer_is_shortest|30.0%|
|closer_starts_with_pivot|3.1%|
|ending_pivot_present|51.1%|
|has_meta_preamble|6.5%|
|has_title_line|50.7%|
|is_single_block|36.7%|


The structural coder is extracting form and surface-style features: block structure, titles, preambles, closer behavior, punctuation, repetition, hedges, and intensifiers.

## Truncation

Total truncated rows: **44 / 540** (**8.1%**).

By model:

|structural|semantic|truncated rows|rate within model|
|---|---|---|---|
|M3|Model C|20|22.2%|
|M2|Model B|10|11.1%|
|M5|Model E|8|8.9%|
|M1|Model A|5|5.6%|
|M6|Model F|1|1.1%|


By prompt:

|prompt_id|category|length|truncated rows|rate within prompt|
|---|---|---|---|---|
|story_open|story|open|34|56.7%|
|animal_open|animal|open|10|16.7%|


## Refusals, empty outputs, and errors

- Semantic `is_refusal_like`: **3** rows flagged.
- Structural `is_empty_response`: **0** rows flagged.
- Semantic `error` nonblank values: **0** rows.

## Artifacts written

- `raw_sentence_count_disagreements_top.csv`: all sentence-count disagreements, sorted by absolute difference.
- `raw_compliance_disagreements.csv`: all compliance disagreements.
- `raw_model_feature_snapshot.csv`: joined model-level feature summary.
- `raw_truncation_rows.csv`: all rows flagged as truncated.

## Bottom line

The raw coded outputs confirm the summary-level finding: the two files are synchronized views of the same output set, with a clean blind-label crosswalk and identical shared source fields. The major substantive differences are coder-feature scope and a small set of heuristic disagreements, especially sentence counting and three compliance calls. The presence of `model_hidden` and `provider_hidden` columns is worth treating carefully; they were not used in this analysis.
