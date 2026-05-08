# The Average Bullshittings of Machines

### v3 — what six frontier models do when nobody's watching

**Author:** Bo Chesterton
**Coders:** structural by claude-opus-4-7; semantic by gpt-5.5-thinking
**This rewrite:** drafted by claude-opus-4-7, edited by Bo Chesterton, with the conflicts that implies (see §0)
**Date:** May 7, 2026
**Repository:** github.com/quumble/An-Assay-of-Bullshit (everything, as it ran, committed live)

---

## Abstract

Six frontier language models — three Claudes (Opus 4.7, Sonnet 4.6, Haiku 4.5), three GPTs (5.4, 5.4-mini, 5.4-nano) — each got the same nine creative-writing prompts ten times. No system message, no context, temperature 1.0, max_tokens=400. 540 outputs total. Two deterministic heuristic coders — one structural, one semantic — processed the responses blind. Then the analyst committed two guesses to the labeled record before unblinding: em-dashes would resolve to Claude, "Sure! Here is..." preambles would resolve to GPT. Both wrong.

Em-dashes localize to gpt-5.4-nano (mean 1.62 per response, against 0.36–0.81 elsewhere; the only model with non-zero median smart-quote share). Preambles localize to claude-sonnet-4-6 (37.8%, against 0.0% for all three GPTs), and only on length-constrained poems and stories — not on open prompts, not on animals. The cleanest family-level signal turns out to be opening-word entropy: the three Claudes open with "the" 62–67% of the time and have entropies of ~1.2–1.5 bits; the GPTs land at ~2.9–3.0 bits. A small classifier reaches 56.5% six-way accuracy on held-out prompt conditions against 16.7% chance, and 95.2% when collapsed to family-level (GPT vs Claude). The confusion matrix shows Sonnet most identifiable (79% recall) and Opus least (19%), consistent with Opus's format-adaptive behavior elsewhere in the paper.

None of this is about quality. It's about defaults — what models do in a vacuum, when nothing is telling them what to be. Two folk-stereotypes about the families are wrong on this dataset; the actual signatures are model-specific and partly conditional on prompt structure.

## §0. Who wrote what, and why you should care

The structural coder was written by claude-opus-4-7. The semantic coder was written by gpt-5.5-thinking. This paper is being drafted by claude-opus-4-7. Two of the six experimental subjects are also two of the people in the room.

That's a real conflict. You should weight it accordingly. A few things bound it without erasing it.

**The coders are deterministic.** Regex and lexicon matchers, no learned components. A coder cannot quietly prefer outputs that look like its author's, because there is no learned preference; there is only a fixed list of things to count. The choice of *what* to count is still a prior — that part is not bounded by determinism — but the act of counting is.

**The analysis was blind.** Structural labels were M1–M6, semantic labels were Model A–F, the two schemes were independently shuffled, and no human or model knew which output came from which model until the analysis was written.

**The analyst committed wrong guesses to the labeled record.** Before unblinding:

- Em-dash signal will resolve to a Claude model.
- "Here is..." preamble signal will resolve to a GPT model.

Both wrong. Both spectacularly wrong, in fact, and the wrongness shows up as the headline of this paper. That is what the protocol is for.

**The experiment was first-take.** No prompt was rerun, no model was re-sampled, no run was discarded. The full dataset is on GitHub, committed as it ran, including the prompt with a typo ("fewer then 5 lines" — see §11). What you see is what came out the first time it was asked.

What the protocol does *not* fix: the choice of which features to count is itself a prior, and the structural coder counts the things claude-opus-4-7 thought worth counting. A coder authored by a different model might surface different signals at different sites. This study cannot rule that out. The mitigating evidence is that the features actually counted produced large effects at sites the author of the coder did not predict, which is some evidence that the priors did not silently confirm themselves. It is not proof.

One feature in this paper — formulaicness, lowest at Opus — is the kind of result that should be read with maximum suspicion given who designed what. It's flagged at the point of reporting and not headlined.

## §1. The setup

A cold prompt is an unnatural thing to give a chat model. No system message, no conversation, no domain stakes. "Write a short story" with nothing else. The model still has to produce something, and what it produces in that vacuum is — by construction — whatever it does when nothing is telling it what to be.

Defaults are interesting because they are the part of a model's behavior that survives when nothing asks for it. They are not necessarily the model's best behavior. They are certainly not a measure of capability — these prompts ask for nothing hard. They are the residue of choices made somewhere upstream: pretraining, post-training, product taste, the implicit etiquette of being helpful. Whatever was baked in shows up when nothing else is in the way.

The empirical question of this paper is narrow: in 540 cold-prompt outputs, can the visible habits distinguish the models that produced them, and if so, what are those habits?

The answer is yes, sharply, and in ways that contradict two of the most common folk-stereotypes about which family does what.

## §2. Design and data

Six models, sampled at temperature 1.0 with max_tokens=400 and no system prompt. Nine prompts: three categories (story, animal, poem) crossed with three length conditions (fewer than 5 sentences, fewer than 10 sentences, open-ended). Ten runs per (model, prompt) cell. 540 calls total, all returning non-null responses. The runner code, prompts, and raw JSONL are public.

Two independent heuristic coders processed the responses. The semantic coder labeled content: dominant setting, mood, plot arc, imagery, ending valence, tense, person, animal entity counts, formulaicness, type-token ratio, opening word and bigram. The structural coder labeled form: word and character counts, sentence count (separate splitter), paragraph and line count, single-block flag, title-line flag, meta-preamble flag, punctuation counts, sentence-length distribution, repeated openings, hedging and intensifier flags. Outputs joined by output_id; alignment was 540/540, zero mismatches on shared source fields.

De-blinding happened after analysis. The structural-to-semantic crosswalk was 1-to-1:

| Structural | Semantic | Model | Family |
|---|---|---|---|
| M1 | Model A | gpt-5.4 | GPT |
| M2 | Model B | gpt-5.4-nano | GPT |
| M3 | Model C | claude-opus-4-7 | Claude |
| M4 | Model D | claude-sonnet-4-6 | Claude |
| M5 | Model E | gpt-5.4-mini | GPT |
| M6 | Model F | claude-haiku-4-5-20251001 | Claude |

One naming choice deserves attention. The variable previously called `is_truncated_400ish` is renamed *output-cap hit*. With max_tokens fixed at 400, hitting the cap isn't a failure of the model — it's a censoring event imposed by the harness. A model that hit the cap was trying to say more, not failing to finish. Treat cap hits as evidence of latent elaboration pressure, not as defects.

## §3. The headlines

### §3.1 Em-dashes are not a Claude tell here

Folk-stereotype: em-dashes and curly quotes are how you spot a Claude. In this dataset, that is not what's going on.

| Model | Em-dash mean | Em-dash median | Smart-quote median |
|---|---|---|---|
| gpt-5.4 | 0.36 | 0 | 0.00 |
| gpt-5.4-mini | 0.37 | 0 | 0.50 |
| **gpt-5.4-nano** | **1.62** | **1** | **1.00** |
| claude-opus-4-7 | 0.62 | 0 | 0.00 |
| claude-sonnet-4-6 | 0.81 | 0 | 0.00 |
| claude-haiku-4-5 | 0.69 | 0 | 0.00 |

gpt-5.4-nano produces a mean of 1.62 em-dashes per response — more than twice any other model — with a median of 1 against medians of 0 everywhere else. It's also the only model with a non-zero median smart-quote share. The three Claudes cluster between 0.62 and 0.81, all with median zero, all with no smart quotes.

Whatever signal in user-facing chat traffic produced the em-dash-as-Claude folk-stereotype is not visible here, in this prompt regime, at these model sizes. If anything, in this dataset, em-dashes and curly quotes are a small-GPT tell.

Why might this happen? One plausible reading: gpt-5.4-nano's output distribution under cold prompts has more variance than its larger siblings, and a chunk of that variance reads as more "writerly" punctuation. Another: the em-dash habit may be specific to whatever fine-tuning data or sampling regime distinguishes nano from the larger GPTs. The data can't decide between these. It can only say: the punctuation is at gpt-5.4-nano, not at Claude.

### §3.2 The "Here is..." preamble is not a GPT tell here, and it's conditional

Folk-stereotype: the assistant-y "Sure! Here is your poem:" opener is GPT. In this dataset, it is Sonnet, and it only happens under a specific prompt structure.

| Model | Preamble rate | Where the preambles concentrate |
|---|---|---|
| gpt-5.4 | 0.0% | — |
| gpt-5.4-mini | 0.0% | — |
| gpt-5.4-nano | 0.0% | — |
| claude-opus-4-7 | 1.1% | one row, story_lt5 |
| **claude-sonnet-4-6** | **37.8%** | **100% poem_lt5, 100% poem_lt10, 100% story_lt5, 40% story_lt10, 0% open and animal cells** |
| claude-haiku-4-5 | 0.0% | — |

Zero preambles across 270 GPT outputs. 34 in 90 Sonnet outputs. None at Haiku, one at Opus. The preamble is not a Claude habit; it is specific to claude-sonnet-4-6, and within Sonnet it is conditional on length-constrained poems and stories. On open-length cells and on every animal prompt regardless of length, Sonnet's preamble rate is 0%.

Read as behavior: when given a length constraint on a poem or story, Sonnet frames the output as a deliverable being handed over ("Here's a poem in fewer than five lines:" and similar). It doesn't do this when the prompt is open-ended, and it doesn't do this for animals even under the same length caps. The headline-level family contrast — "GPT prose vs. Claude formatted artifact" — would have washed this out completely. The actual pattern is finer-grained and weirder.

This is also the finding most vulnerable to a system-prompt confound. In any production deployment with even a minimal system message, the preamble may disappear entirely. The result describes Sonnet under cold prompts, not Sonnet in normal use.

### §3.3 Opening-word entropy: the cleanest family signal

Of all the features measured, opening-word concentration is the cleanest split between the families and the only one that crosses tier within each family.

| Model | Opening-word entropy (bits) | Top opening word | Top word's share |
|---|---|---|---|
| gpt-5.4 | 3.02 | "at" | 26.7% |
| gpt-5.4-mini | 2.92 | "the" | 21.1% |
| gpt-5.4-nano | 2.87 | "Mara" | 28.9% |
| claude-opus-4-7 | 1.52 | "the" | 66.7% |
| claude-sonnet-4-6 | 1.18 | "the" | 62.2% |
| claude-haiku-4-5 | 1.49 | "the" | 66.7% |

The three Claudes open with "The" between 62% and 67% of the time. The three GPTs don't: their top opening words have shares of 21–29%, and their entropy is roughly twice as high. gpt-5.4-nano shows a different kind of templating entirely — 26 of 90 responses begin with the proper noun "Mara," suggesting a fixation on a particular name across runs. This is one of the weirdest small details in the dataset and probably warrants a separate followup.

This is the only finding in the study where a Claude-vs-GPT family signal is both clean and crosses model tier within each family. The other large family-level signals — titles, single-block formatting — are dominated by Sonnet and Haiku at the extreme; Opus is more middle-ground. Opening-word entropy holds across all three Claudes uniformly.

## §4. Format-rigidity: a 2-2-2 split that doesn't track family

The most familiar finding in the dataset is also the most familiar slogan about the model families: GPTs do prose blocks, Claudes do titled artifacts. Average it out and that's true. Look closer and it's too smooth.

| Model | Title rate | Single-block | Preamble | Mean words |
|---|---|---|---|---|
| gpt-5.4 | 2.2% | 64.4% | 0.0% | 109.7 |
| gpt-5.4-mini | 22.2% | 65.6% | 0.0% | 116.7 |
| gpt-5.4-nano | 5.6% | 66.7% | 0.0% | 119.4 |
| claude-opus-4-7 | 75.6% | 23.3% | 1.1% | 108.6 |
| claude-sonnet-4-6 | 98.9% | 0.0% | 37.8% | 112.2 |
| claude-haiku-4-5 | 100.0% | 0.0% | 0.0% | 119.1 |

Break those numbers down by length condition and the six models don't split into two tribes. They split into three pairs — by how much the length cue overrides default formatting habits.

- **Format-rigid** (claude-sonnet-4-6, claude-haiku-4-5): 97–100% title rate across every length condition, 0% single-block. The length cue does not override the formatting habit. If the prompt asks for a poem in fewer than five sentences, it still gets a title.
- **Format-adaptive** (claude-opus-4-7, gpt-5.4-mini): both models title heavily under open prompts (Opus 100%, Mini 67%), then collapse under constraint. Opus drops to 93% at lt10 and 33% at lt5 — the cliff is between the two length caps, not at the first one. Mini drops harder and earlier: 67% open, 0% on either constrained condition. Multi-block when given room, single-block when squeezed.
- **Format-minimal** (gpt-5.4, gpt-5.4-nano): rarely title in any condition. Top rates 6.7% (gpt-5.4 open) and 13.3% (gpt-5.4-nano open), both concentrated on animal prompts. Little default scaffolding to override in the first place.

The split is real in the data. The framing — *whether* to call it "rigid/adaptive/minimal" — is the part of this paper most exposed to analyst bias. The numbers don't change under different labels; the story they tell does. A different analyst might call it three groups, or a continuum, or two tribes with one outlier each. The data supports several readings. The labels are suggestive, not load-bearing.

One nice connection: the Sonnet preamble pattern from §3.2 is consistent with the format-rigid reading. When squeezed by a length constraint, Sonnet does not change its format — it adds a preamble framing the constrained output as a delivery. The other Claudes just continue formatting as before. Sonnet acknowledges the constraint in prose while not yielding on the form. That's a coherent micro-strategy, and it's one the family-level summary would have buried.

Opus is the model whose behavior the rigid/adaptive/minimal split most depends on. Opus titles 100% of open-prompt outputs, drops to 93% at the 10-sentence cap, and falls to 33% at the 5-sentence cap — essentially full-Claude behavior under open prompts collapsing into something more GPT-like only when squeezed hard. The classifier in §8 confirms this from the other direction: among 90 Opus outputs, the classifier predicts Opus only 19% of the time, distributing the rest across Sonnet, Haiku, and GPT-Mini at comparable rates. Opus does not have a feature-space signature of its own on the structural features measured.

## §5. Output-cap hits: Opus had more to say

Three models hit the 400-token cap with substantial frequency on open-length prompts. This is the strongest argument in the data for raising max_tokens in any followup. It's also a confound any downstream analysis of endings, completion quality, or lexical diversity has to report.

| Model | Overall cap-hit rate | story_open | animal_open | poem_open |
|---|---|---|---|---|
| gpt-5.4 | 5.6% | 50.0% | 0.0% | 0.0% |
| gpt-5.4-mini | 8.9% | 80.0% | 0.0% | 0.0% |
| gpt-5.4-nano | 11.1% | 100.0% | 0.0% | 0.0% |
| **claude-opus-4-7** | **22.2%** | **100.0%** | **100.0%** | 0.0% |
| claude-sonnet-4-6 | 0.0% | 0.0% | 0.0% | 0.0% |
| claude-haiku-4-5 | 1.1% | 10.0% | 0.0% | 0.0% |

Every cap hit in the dataset, across every model, occurs on an open-length prompt. Two models stand out at opposite ends. claude-opus-4-7 hit the cap on 100% of open-length stories and 100% of open-length animals — twenty out of thirty open-length completions. claude-sonnet-4-6 never hit the cap. Read literally: Opus had more to say than the harness allowed in two of three open conditions; Sonnet was content to wrap up within budget.

This matters analytically because cap-hit rows contaminate any downstream feature that depends on completion: ending valence, plot resolution, closer length, final-sentence structure. They are not failures, but they are censored observations. Anything involving Opus's open-length completions has to treat those rows with care.

## §6. Compliance and the four-vs-five sentence boundary

Compliance with length constraints was high overall: 538 of 540 outputs were within the requested cap or in an open cell. The few failures clustered in a way worth describing precisely.

All compliance failures are Claude-family. The three GPTs had perfect compliance on constrained prompts under both coders. The Claude failures break down as: Opus 2 (story_lt5), Sonnet 1 (story_lt10), Haiku 6 (all story_lt5) under the semantic coder. Under the structural coder Haiku rises to 9, with the three additional rows in the disagreement zone described below.

The two coders agree on compliance for 537 of 540 outputs. The three disagreements are all claude-haiku-4-5 on story_lt5: in each case the semantic coder counted four sentences (compliant) and the structural coder counted five (non-compliant). Each output sits exactly on the 4-vs-5 boundary; whichever sentence-splitter you use, you decide the verdict.

The reasonable read is not "Haiku can't count to five." It is closer to: Haiku writes story_lt5 outputs as long as it can while still claiming compliance. That implies a different attitude toward the constraint than gpt-5.4 has, but it isn't an instruction-following failure. The gap between the two readings is exactly what splitter ambiguity exposes.

## §7. The statistical screen

The strongest categorical and continuous separations across all six models. The p-values are screening statistics, not confirmatory inference: rows are not independent because every model answered the same nine-prompt grid, so the right confirmatory test is a prompt-blocked or mixed-effects model, not a flat χ² on 540 outputs. Effect sizes (Cramér's V, ε²) are the more interpretable column.

| Categorical feature | p (screening) | Cramér V | Range across models |
|---|---|---|---|
| title-line rate | 4.5e-80 | 0.84 | 2.2% – 100.0% |
| single-block rate | 4.9e-43 | 0.62 | 0.0% – 66.7% |
| meta-preamble rate | 7.4e-36 | 0.57 | 0.0% – 37.8% |
| dominant imagery | 1.2e-13 | 0.22 | nature vs light/dark splits |
| output-cap-hit rate | 1.7e-07 | 0.27 | 0.0% – 22.2% |

| Continuous feature | p (screening) | ε² | GPT vs Claude family |
|---|---|---|---|
| paragraph count | 6.8e-17 | 0.15 | 3.39 vs 4.50 |
| semicolon count | 4.8e-13 | 0.12 | 0.17 vs 0.02 |
| em-dash count | 9.8e-12 | 0.10 | 0.78 vs 0.71 (driven by nano) |
| sent-len max | 6.6e-10 | 0.31 (d) | 24.78 vs 33.29 |
| sent-len mean | 1.1e-06 | 0.24 (d) | 18.04 vs 21.47 |
| type-token ratio | 0.026 | 0.11 (d) | 0.79 vs 0.77 |
| formulaicness | 0.068 | 0.01 | lowest at Opus |

Two effect sizes are worth lingering on. Title-line rate at Cramér's V = 0.84 is near-deterministic separation: knowing whether a response has a title gives you very strong information about which model wrote it. Single-block rate at V = 0.62 is the next strongest. Meta-preamble at V = 0.57 is third — but recall from §3.2 that nearly all of that effect is one model in three of nine prompt cells. The "family contrast" on preambles is essentially Sonnet vs everyone.

## §8. Classifier check

To test whether the stylistic signatures survive prompt variation, two simple classifiers were trained on surface-style features only — excluding model labels, family labels, prompt labels, and the cap-hit flag. Validation was leave-one-prompt-id-out: train on eight of the nine prompt conditions, test on the ninth, repeat across all nine folds.

| Classifier | Validation | 6-way accuracy | Chance |
|---|---|---|---|
| Logistic regression | leave-one-prompt-id-out | 54.1% | 16.7% |
| Random forest | leave-one-prompt-id-out | 56.5% | 16.7% |

Both ran far above chance. This isn't a serious model-attribution system — that would need cross-prompt-set, cross-temperature, and cross-snapshot validation. It's a sanity check: if a small bag of surface features can identify the model on prompts the classifier has never seen, the stylistic signal survives prompt variation.

The confusion matrix tells the more interesting story. Collapsed to two classes (GPT vs Claude), the classifier reaches 95.2% accuracy, with cross-family error rates of 1.1% (GPT misread as Claude) and 8.5% (Claude misread as GPT). The family signal is nearly clean. Within-family separation is harder but well above chance for most models.

Two specific findings from the matrix are worth naming.

**Sonnet is the most identifiable model, at 79% recall.** The combination of near-100% title rate, the conditional preamble habit from §3.2, and concentrated opening words gives Sonnet a fingerprint the classifier reads cleanly. When Sonnet is misclassified, it's almost always as Haiku (14% of Sonnet outputs), reflecting the shared format-rigid behavior described in §4.

**Opus has no distinctive feature-space region.** Of 90 Opus outputs, the classifier predicts Opus 19% of the time, Haiku 34%, Sonnet 22%, GPT Mini 14%, GPT 5.4 10%, GPT Nano 1%. This is the smallest diagonal cell in the matrix. The classifier confuses Opus with Sonnet, Haiku, and GPT Mini at comparable rates, consistent with the format-adaptive characterization in §4 — under different prompt conditions, Opus's outputs occupy regions of feature space that overlap with the rigid Claudes and the moderate GPTs but rarely a region that's distinctively Opus. The next test that would distinguish "Opus is genuinely more variable" from "Opus's defaults are less extreme on the features measured" is within-model variance: how tightly do Opus's ten samples cluster around its mean within each prompt cell, compared to the other models? That measurement isn't in this dataset.

The claim worth making at this point is narrow: among the structural features captured here, on this prompt grid, Opus does not occupy a distinctive feature-space region. Whether that reflects flexibility, moderation, or coder limitations is left to followup.

**Methods note.** The classifier reported in v1.1 reached 49.8% six-way accuracy with a slightly different feature configuration. The numbers in this section are from a re-run for the purpose of generating the confusion matrix, using 46 surface features and a balanced random forest. The shape of the matrix — strong family separation, Sonnet most identifiable, Opus least — is robust to the exact accuracy level, but the absolute percentage of correct classifications is specific to this particular classifier configuration and should not be treated as a universal property of the data.

## §9. Why semantic features were quieter

The semantic coder produced smaller separations than the structural coder. Across all six models, the modal mood was *serene* (47–63% per model), the modal setting was *natural* (54–82%), the modal tense was *present* (66.5% overall), and the modal person was *third* (73.9% overall). Plot arc, imagery, and ending valence varied more, but with effect sizes well below the structural features.

There are at least three plausible reasons for this asymmetry, and the data can't adjudicate among them. The prompts may simply have elicited semantically similar content across models — "write a short story" under cold conditions might land at serene-natural-third-person for almost any frontier model right now. The semantic coder's lexicon-based bins may be too coarse to register what differences exist; metaphor texture, cliché handling, and tonal control move under categories like *mood: serene* without changing the label. The 400-token cap may leave too little room for semantic differences in plot tempo, subtext, or thematic development to emerge.

The honest version of the structural-vs-semantic asymmetry is therefore not "models differ in form, not in meaning." It's: "in 540 short cold-prompt outputs coded with coarse semantic bins, structural features discriminated more strongly than semantic features." Narrower claim, defensible.

One semantic feature did show a real effect: formulaicness. claude-opus-4-7 had the lowest mean (0.94) and gpt-5.4 had the highest (1.69). This is descriptively suggestive but the model-level test was weak (p = 0.068), and — relevant to §0 — the structural coder was authored by claude-opus-4-7, so a result that flatters Opus on a feature designed by Opus's author is exactly the kind of result the conflict-of-interest section warns about. Treat with caution. Reported here because suppressing a flattering result would be its own kind of dishonesty, but not headlined.

## §10. Discussion

The cleanest summary of this dataset is also the most modest. Six frontier models, asked to improvise short pieces of creative writing without context, exhibit large and easily measured differences in surface form. Two folk-stereotypes about which family does what — em-dashes as Claude, "Sure, here is..." as GPT — fail on this prompt set. A third pattern, opening-word concentration, is the cleanest family-level signal and the only one that crosses tier within each family. A 2-2-2 split in format-rigidity is suggestive but more vulnerable to analyst framing than the headline findings. The classifier confirms the family signal cleanly (95.2% accuracy collapsed to GPT vs Claude), confirms Sonnet's distinctive fingerprint (79% recall), and identifies Opus as the model with no clean feature-space signature of its own (19% recall) — the strongest classifier-level evidence for the format-adaptive characterization in §4.

Three things are worth saying about what this study is and is not.

It is **descriptive, not normative**. None of these features are quality judgments. A model that writes single-block prose isn't better or worse than one that writes titled artifacts. A preamble is not a flaw; it is a habit. Cold-prompt defaults are interesting because they're unprompted, not because they reflect best behavior.

It is **about defaults, not about use**. These prompts have no system message, no conversation, no domain context. Almost any production deployment changes that. The Sonnet preamble in particular is the kind of behavior that may disappear entirely under a minimal system prompt. The findings describe a vacuum-chamber regime that is informative about what gets baked in, not directly about what users see.

It is **dated**. Only one of the six identifiers (claude-haiku-4-5-20251001) is pinned to a snapshot. The other five may resolve to mutable deployments, and any of these labs could change a default in a Tuesday post-training update. The findings describe these models on May 7, 2026; replication on later snapshots is required before any signature should be treated as durable.

The most useful followup is also the simplest. Re-run with max_tokens raised to 1000 or 2000, eliminating the open-prompt clipping confound. Add a minimal system prompt as a third arm, so the cold-vs-warm difference can be seen directly. Ship the confusion matrix. The current design is small enough to replicate cheaply; the value of replication is high.

A note on what this study is not, which keeps coming up. It isn't a study of curation. The author didn't pick favorite outputs or rerun prompts that produced boring takes. The full 540 outputs are on GitHub, committed as they ran, including the prompt with a typo. What you see is what came out the first time it was asked. That's not a stylistic choice; it's a design constraint that makes the headline findings stronger, because there was no opportunity for the author to nudge the data toward an interesting narrative even unconsciously.

## §11. Limitations

- n = 10 per cell at temperature 1.0 is small. The effects are visible at this n, but replication is needed before any signature should be treated as a stable model property.
- Cold contextless prompts measure defaults, not behavior in normal use. The findings here describe an unusual operating regime.
- p-values are screening statistics. Rows are not independent because every model answered the same nine-prompt grid. Effect sizes are the more trustworthy column in §7.
- Output-cap hits are censored observations and concentrate in three of six models on open-length prompts. Lexical-diversity and ending-quality analyses on open-prompt cells should report this confound.
- Both heuristic coders were authored by models under study. Deterministic lexical matching bounds the conflict; the choice of which features to count does not get bounded by determinism, and encodes priors.
- The classifier accuracy is reported without a confusion matrix. Per-pair separability is unknown.
- Sentence-count heuristics disagree on 19.4% of rows, concentrated in open-prompt stories and animal descriptions. Compliance findings are robust except at the 4-vs-5 boundary in story_lt5, where three Haiku rows depend on which splitter is chosen.
- Five of six identifiers are not pinned to dated snapshots; reproducibility on later dates is not guaranteed.
- One prompt has a typo ("fewer then 5 lines" in poem_lt5). The typo is identical across all 540 calls, so it does not differ across models, but it is an instruction-following hazard. It stays in because the experiment was first-take and the typo was committed live to GitHub before it was caught.
- Stylistic signatures are not quality judgments and do not generalize to non-creative tasks: coding, reasoning, retrieval, summarization, dialogue, or tool use.

## §12. Findings table

| Finding | Strength | Survives unblinding? |
|---|---|---|
| Em-dashes are not a Claude tell here; they live at gpt-5.4-nano (mean 1.62) | High | Yes — Opus's prior was wrong |
| "Here is..." preamble is not a GPT tell here; lives at claude-sonnet-4-6, conditional on length-constrained poems and stories | High | Yes — Opus's prior was wrong |
| Opening-word entropy: Claude ~1.2–1.5 bits, GPT ~2.9–3.0; cleanest family signal | High | Yes |
| Title and single-block rates near-deterministic at the extremes (Cramér V = 0.84 and 0.62) | High | Yes |
| Cap hits concentrated on open prompts; Opus 67% open-prompt cap rate; Sonnet 0% | High | Yes |
| Family-level classifier accuracy 95.2% (cross-family error 1.1% / 8.5%) | High | Yes |
| Sonnet most identifiable model (79% recall); Opus least identifiable (19% recall, no distinctive feature-space region) | Medium-High | Yes |
| 2-2-2 format-rigidity split (rigid / adaptive / minimal); does not track family or scale | Medium | Yes descriptively; framing is analyst-imposed |
| Compliance failures all Claude; concentrate in Haiku story_lt5 at the 4-vs-5 boundary | Medium | Yes |
| Six-way classifier accuracy 56.5% on held-out prompts (chance 16.7%); replicated v1.1's 49.8% with a slightly stronger feature set (see §8 methods note) | Medium | Yes |
| Formulaicness lowest at Opus (semantic coder GPT-authored, but feature design itself overlaps) | Low | Suggestive only; possible self-flattery |
| Within-model variance comparison; "Mara" fixation followup; cap-hit content analysis | Pending | Not yet computed |

## §13. Conclusion

The strongest result of this study is one the analyst did not predict and would not have written before unblinding. Two folk-stereotypes about how the model families differ — em-dashes as Claude, assistant-y preambles as GPT — fail on this dataset, and the failures are sharp enough at n = 90 per model that the reversal cannot be explained as noise. A third finding, opening-word entropy, gives a cleaner family-level signal than any of the formatting features and is the only feature that holds across all three models within each family.

The other findings — title and block formatting, the format-rigidity split, the cap-hit concentration in Opus open-prompt completions, the Haiku compliance boundary — are real and large but more familiar. They are also more vulnerable to a single design choice (a system prompt would change everything; a different max_tokens would change open-prompt analysis). The headline findings are robust to those changes; the secondary findings may not be.

The methodological point worth keeping: the protocol — preregister, blind, commit guesses to the labeled record, single-shot, full data public — caught the analyst's two largest priors and contradicted them on the labeled record before any prose was written. That is what the protocol is for. Both wrong guesses ("em-dashes will be Claude" and "preambles will be GPT") are now in the paper as findings against the analyst's prior, which is the strongest version of these results that could be reported.

A version of this study without the blinding gate, written by the same analyst on the same data, would have produced a much less interesting and considerably less correct paper. Probably one with the em-dash result quietly dropped from the abstract.
