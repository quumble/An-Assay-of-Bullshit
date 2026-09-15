# Harmonized Coding Specification — September 2026

**Status:** Locked before September outcome analysis  
**Date:** 2026-09-15  
**Applies to:** raw response text from Bullshit Assay 1 and Bullshit Assay 2

## 1. Goal

The September pipeline must measure the same textual objects in both studies. The core correction is to separate three layers that were not always distinguished consistently in May:

1. **meta preamble** — assistant/delivery framing outside the requested creative work;
2. **title** — a title belonging to the creative work;
3. **creative body** — the text to be used for body-level stylistic features.

All body-level features are computed only after removing any detected preamble and title.

## 2. Text normalization

For each successful response:

1. normalize CRLF/CR line endings to `\n`;
2. strip leading and trailing whitespace from the whole response;
3. preserve internal blank lines;
4. preserve case and punctuation in the archival normalized text;
5. do not silently correct spelling, grammar, markdown, or the original prompt text.

The normalized full response remains available alongside all derived fields.

## 3. Meta-preamble detection

A **meta preamble** is leading assistant/delivery language that frames the requested creative work rather than constituting the work itself.

### 3.1 Candidate region

Only leading material before the first blank-line boundary is eligible for automatic preamble removal.

### 3.2 Positive framing patterns

The leading block is coded as a preamble when it is 30 whitespace-delimited tokens or fewer and begins, case-insensitively, with one of the following families of markers:

- `here is`
- `here's`
- `here you go`
- `sure`
- `certainly`
- `of course`
- `absolutely`
- `below is`
- `a short poem`
- `a poem`
- `poem:`
- `story:`

Minor punctuation or markdown before/after the marker does not prevent a match.

### 3.3 Exclusions

A leading block is not removed as preamble solely because it is short, title-cased, or followed by a blank line. A block matching a title rule but not a framing marker proceeds to title detection.

A line or block already classified as preamble is never simultaneously classified as title.

### 3.4 Output fields

Record:

- `preamble_present`
- `preamble_text`
- `text_after_preamble`

## 4. Title detection

Title detection runs **after** any preamble has been removed.

Only the first non-empty line/block after preamble removal may be classified as title.

A title is detected if any of the following is true.

### 4.1 Explicit markdown heading

The first non-empty line matches a markdown heading pattern such as `# Title`, `## Title`, etc.

### 4.2 Explicit standalone markdown emphasis

The first non-empty line is wholly wrapped in a single markdown emphasis pair (`**...**`, `__...__`, `*...*`, or `_..._`), contains no more than 12 whitespace-delimited tokens, and is followed by a blank-line boundary before subsequent body text.

### 4.3 Plain standalone title

The first non-empty line:

- contains 1–12 whitespace-delimited tokens;
- is followed by a blank-line boundary before subsequent body text;
- does not end in `.`, `!`, or `?`;
- is not a preamble/framing marker;
- has at least half of its alphabetic tokens beginning with uppercase letters, ignoring short function words (`a`, `an`, `the`, `of`, `and`, `or`, `in`, `on`, `to`, `for`).

A trailing colon is permitted for an actual title only if the line does not match a preamble/framing marker.

### 4.4 Output fields

Record:

- `title_present`
- `title_text`
- `creative_body`

The title itself is excluded from all body-level line, stanza, word, POS, punctuation-rate, and opening-token calculations.

## 5. Creative body

`creative_body` is the normalized response after removing the detected preamble and detected title, while preserving all remaining line breaks, markdown, punctuation, and casing.

If neither preamble nor title is detected, `creative_body` equals the normalized full response.

If parsing would produce an empty creative body, the parser must retain the last removed candidate as body text and flag `parse_empty_fallback = true` rather than silently emitting an empty body.

## 6. Locked body-only feature set

The following features define the primary classifier input unless marked not applicable by genre.

### 6.1 Length and line structure

- `body_word_count`
- `body_line_count_nonempty`
- `body_stanza_count`
- `words_per_line_mean`
- `words_per_line_sd`
- `mean_word_length`

For prose/story/animal responses, line-based features remain mechanically defined from literal line breaks; they are not interpreted as poetic form.

### 6.2 Part-of-speech ratios

Using one documented spaCy English model consistently across both studies, compute ratios over non-punctuation/non-space/non-symbol tokens:

- `pos_noun_ratio` = NOUN + PROPN
- `pos_verb_ratio` = VERB + AUX
- `pos_adj_ratio`
- `pos_adv_ratio`
- `pos_pronoun_ratio`

The exact spaCy model and version must be written to the September environment manifest.

### 6.3 Person/pronoun ratios

Using deterministic lexical sets, count first-singular, first-plural, second-person, and third-person pronouns. Report each as a proportion of all recognized pronouns, with zero for all four ratios when no recognized pronoun occurs:

- `pronoun_1s_share`
- `pronoun_1p_share`
- `pronoun_2_share`
- `pronoun_3_share`

Also retain raw counts.

### 6.4 Punctuation rates

Count the following in the creative body and express each as events per 100 body words (zero when body word count is zero):

- em dash (`—`)
- semicolon
- colon
- comma
- exclamation mark
- question mark
- ellipsis (`…` or three-or-more periods)

Raw counts are retained alongside rates.

### 6.5 Opening features

Extract after removal of leading markdown punctuation:

- `first_lexical_token`
- `opening_bigram` when at least two lexical tokens are available.

Lexical tokens are lowercased for entropy/frequency summaries but the original text is preserved.

## 7. Full-surface secondary feature set

Secondary attribution analyses may add the following response-level features to the body-only set:

- `preamble_present`
- `title_present`
- `preamble_token_count`
- `title_token_count`

These are intentionally excluded from the primary body-only classifier so that assistant-style delivery conventions do not automatically count as creative-body style.

## 8. Features not primary in the harmonized transfer model

The following may be computed and reported secondarily but are not part of the locked primary classifier feature set:

- rhyme participation/rhyme scheme;
- concreteness ratings;
- semantic topic labels;
- mood/plot/formulaicness judgments;
- embeddings;
- named-entity categories;
- lexical-diversity measures sensitive to short-text length.

If any of these become central to a later analysis, that analysis must be labeled exploratory or added via a dated pre-result deviation/amendment.

## 9. Prompt/study metadata

Each harmonized row must retain:

- study (`BA1` or `BA2`);
- provider;
- exact model identifier;
- prompt ID;
- exact prompt text;
- iteration;
- temperature;
- max-token setting;
- timestamp when present;
- original run ID/output ID when present;
- genre (`story`, `animal`, `poem`);
- length condition/cap;
- phrasing condition when applicable.

Model identity is retained in the final harmonized table, but the human parser-validation interface must hide it.

## 10. Validation and revision rule

The parser is validated according to `SECONDARY_ANALYSIS_PLAN.md` before primary outcome analysis.

If validation falls below threshold, parser rules may be revised. Any revision must:

1. be documented in a September deviations log;
2. preserve the frozen raw inputs;
3. rerun validation on the same locked sample;
4. occur before primary transfer/classification results are inspected where feasible.

The final manuscript must distinguish the frozen May pipelines from this September harmonized pipeline.
