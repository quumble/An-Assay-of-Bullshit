# Pre-Test Coding Heuristic — Bullshit Assay 2

This document locks down measurement decisions **before any data is
collected**. It is a constraint on the analysis, not a description of it.
Any deviation from this document during analysis must be recorded in
`deviations.md` with a date and a reason.

## Purpose

Without a pre-specified coding scheme, there is freedom in how each feature
gets operationalized — and that freedom tends to flow toward whatever
operationalization makes the results look cleanest. This document removes
that freedom.

## Tools and versions (pin before run)

| Tool | Purpose | Version |
|---|---|---|
| spaCy | POS tagging, tokenization | `en_core_web_trf`, version pinned in `run_metadata.json` |
| pronouncing | Rhyme detection via CMU dict | latest at run start, pinned in metadata |
| Brysbaert et al. 2014 norms | Concreteness lookup | the 40k-word version |
| OpenAI text-embedding-3-large | Poem-level embeddings | snapshot logged at embedding time |
| scipy / scikit-learn | Statistical tests | versions pinned in metadata |

## Pre-processing

Every poem is the raw `response` field from `results.jsonl`. No
modifications before feature extraction:

- Do **not** strip leading/trailing whitespace (line breaks are data).
- Do **not** normalize unicode beyond what the API returned.
- Do **not** remove preambles like "Here's a poem:" — those are themselves a
  feature (logged separately, see "Preamble detection" below).
- Do **not** truncate non-compliant poems.

Errored runs (where `error` is non-null in the JSONL) are excluded from all
analyses. Attrition rate is reported per cell.

## Preamble detection

Some models prefix poems with conversational preambles ("Here's a poem for
you:", "Sure! Here goes:", etc.). These are not part of the poem and
distort structural metrics if included.

Decision rule, locked: a poem has a preamble if the response contains at
least one blank-line-separated block before any line that contains a verb,
noun, or adjective per the spaCy tagger. The preamble is everything up to
and including the first blank line; the poem is what follows. If no blank
line separates the preamble from the poem, the response is treated as
having no preamble (the whole thing is the poem).

A boolean `has_preamble` feature is computed per poem and reported as its
own analysis (does preamble rate vary by model?). All structural features
are computed on the post-preamble text.

## Structural features (deterministic)

Computed per poem:

- **`line_count`**: number of non-empty lines after preamble removal.
- **`stanza_count`**: number of blocks separated by ≥1 blank line.
- **`words_per_line_mean`**: mean word count across non-empty lines.
- **`words_per_line_sd`**: SD of word counts across non-empty lines.
- **`total_words`**: total word count (whitespace tokenization).
- **`mean_word_length`**: mean character length of words.

## Compliance

Length compliance is a feature and an analysis target.

- **`compliant`**: boolean, `line_count < N` where N is 5/10/20 from the
  prompt id.
- Per-cell compliance rate reported.
- Non-compliant poems are **included as-is** in all structural and
  semantic analyses. We do not truncate them. A sensitivity analysis
  re-runs primary analyses excluding non-compliant poems; if conclusions
  change, this is reported.

## POS features (spaCy `en_core_web_trf`)

The full post-preamble poem is tagged as a single document.

Per poem, computed as ratios over content tokens (excluding punctuation
and whitespace, as classified by spaCy):

- **`noun_ratio`** (NOUN + PROPN)
- **`verb_ratio`** (VERB + AUX)
- **`adj_ratio`** (ADJ)
- **`adv_ratio`** (ADV)
- **`pronoun_ratio`** (PRON)

Decision rule, locked: trust the tagger. No manual override of tagger
output, no custom rules for poetic constructions. The tagger's behavior
on poetry is itself something we are measuring against, and the manual
validation step (below) tells us how much to trust the per-feature
results.

## Person / voice (rule-based)

Pronoun lists, locked:

- 1st singular: `{i, me, my, mine, myself}`
- 1st plural: `{we, us, our, ours, ourselves}`
- 2nd: `{you, your, yours, yourself, yourselves}`
- 3rd: `{he, she, it, they, him, her, them, his, hers, its, their, theirs, himself, herself, itself, themselves}`

Matching is case-insensitive on whitespace-tokenized words after stripping
trailing punctuation.

Per-poem categorical feature **`person`**:

- `impersonal` if zero personal pronouns in any category.
- Otherwise the category with the largest pronoun count, with ties
  broken by precedence: 1st_singular > 1st_plural > 2nd > 3rd.
- `mixed` if the largest category has ≤ 50% of total personal pronouns.

## Concreteness

Lookup against Brysbaert et al. 2014 norms (40k-word version).

Per-poem feature **`concreteness_mean`**: mean concreteness rating across
content words present in the lexicon.

Decision rules, locked:

- Lookup is exact match, lowercased, no lemmatization.
- Words not in the lexicon are excluded from the mean (not treated as
  zero or as missing-data).
- Per-poem feature **`concreteness_coverage`**: fraction of content
  words that hit the lexicon. Reported alongside concreteness_mean
  because low coverage means low trust in the score.
- A poem with concreteness_coverage < 0.30 is flagged. Sensitivity
  analysis re-runs concreteness comparisons excluding flagged poems.

## Rhyme

Using `pronouncing` library / CMU dict.

Per line, extract the final word's terminal rhyming phonemes (CMU's
rhyming-part definition). Two lines rhyme if their terminal phonemes
match exactly.

Per-poem features:

- **`rhyme_participation_rate`**: fraction of lines that rhyme with at
  least one other line in the poem.
- **`rhyme_scheme`**: a string label using A/B/C/... where same letter
  means same rhyming-part. Lines whose final word is not in CMU dict
  get label `?`.
- **`rhyme_scheme_known_only`**: same as above but with `?` lines
  removed before labeling.

Decision rule, locked: words not in CMU dict are not guessed. They get
`?` and are not treated as either rhyming or not-rhyming.

## Embeddings

Embedder: OpenAI `text-embedding-3-large`. Each post-preamble poem
embedded as a single document. Snapshot date logged at embedding time.

Distance metric: cosine.

Pre-specified analyses (computed from the embedding matrix):

- **Within-model spread**: mean pairwise cosine distance among a
  model's poems, per (model, prompt) cell and pooled across prompts.
- **Between-model separation**: mean pairwise cosine distance between
  pairs of models, pooled across prompts.
- **Silhouette score** with three labelings:
  - model-as-label (6 labels)
  - family-as-label (Claude vs GPT, 2 labels)
  - tier-as-label (small/med/full, 3 labels collapsing across families)
- **Permutation null** for each silhouette: 1000 random permutations of
  the relevant label set, silhouette recomputed each time.

## Manual validation step (mandatory before any aggregate analysis)

Before any model-level results are computed, a 50-poem random sample is
hand-validated.

- Sample is drawn with stratification: ≥5 poems from each model, ≥5
  from each length cap. Seed logged.
- Two raters (or one rater twice with a 1-week gap if solo) hand-tag
  per sampled poem:
  - Does the spaCy POS look broadly correct? (yes / mostly / no)
  - Does the rhyme detector match the reader's ear? (yes / partial / no)
  - Does the person classifier agree with the reader's judgment? (yes / no)
  - Was the preamble correctly detected and split? (yes / no)
- Inter-rater (or test-retest) agreement target: ≥85% per feature.
- Decision rule, locked: any feature with <85% agreement is downgraded
  to "exploratory" status and removed from primary analyses. The
  feature still gets reported, but with a flag.
- This step happens before model identities are revealed in the
  validation interface. The validator sees poems and applies tags
  without knowing which model produced them.

## What is deliberately not measured

- **Tone / sentiment.** Dropped per design discussion. Sentiment tools
  are unreliable on poetry and "tone" has no single operationalization
  worth defending.
- **Quality / aesthetic judgment.** Out of scope. Series 2 measures
  defaults, not preferences.
- **Originality / training-data overlap.** Important question, separate
  study.

## Order of operations during analysis

1. Run `run_experiment.py` to completion.
2. Compute preamble detection on all responses; split preamble from poem.
3. Run manual validation step on 50-poem sample.
4. If any feature fails the 85% threshold, mark it exploratory in the
   analysis script before any aggregates are computed.
5. Compute all per-poem features.
6. Compute embeddings.
7. Run pre-specified primary analyses (see preregistration).
8. Run sensitivity analyses.
9. Run exploratory analyses, clearly labeled.
10. Write up. Any departure from this document goes in `deviations.md`.
