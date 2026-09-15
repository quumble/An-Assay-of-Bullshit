# Draft Manuscript Tables

## Table 1. Source-study design and role in the September analysis

| Characteristic | Bullshit Assay 1 (BA1) | Bullshit Assay 2 (BA2) |
|---|---|---|
| Original study status | Exploratory discovery study | Prospectively preregistered follow-up |
| Successful responses used in September | 540 | 5,398 |
| Models | Same six named model snapshots | Same six named model snapshots |
| Primary content | Creative writing across three genres | Poetry |
| Genre conditions | Story, animal, poem | Poem only |
| Prompt/constraint structure | Three requested length conditions | Three phrasings (`write`, `compose`, `gimme`) × three line caps (5, 10, 20) |
| Repetitions | 10 per model-prompt cell | 100 per model × phrasing × line-cap cell |
| Temperature | 1.0 | 1.0 |
| System message | None | None |
| Output cap | 400 tokens | 400 tokens |
| Principal September role | Cross-genre transfer; independent poetry test set | Cross-study training; phrasing and length-cap transfer |
| Poetry observations per model | 30 | Approximately 900 |
| Total harmonized September records | - | 5,938 across BA1 + BA2 |

**Note.** BA2 planned 5,400 calls. The frozen raw file contained 5,398 successful non-empty responses and two API errors. One successful response had been omitted from the historical May feature table; September inclusion was re-derived from frozen raw responses.

## Table 2A. Core six-way model-transfer results

| Analysis | Environmental shift | Train n | Test n | Accuracy | Balanced accuracy | Evidentiary status |
|---|---|---:|---:|---:|---:|---|
| P1 | BA2 poetry → independent BA1 poetry | 5,398 | 180 | .489 | .489 | Primary |
| IA1 | BA2 poetry → BA1 poetry, training size matched to P3 | 360 | 180 | .461 median | .461 median | Outcome-informed exploratory |
| P3 | Story + animal → poem | 360 | 180 | .178 | .178 | Primary |
| P3 | Story + poem → animal | 360 | 180 | .250 | .250 | Primary |
| P3 | Animal + poem → story | 360 | 180 | .244 | .244 | Primary |
| P3 pooled | Leave-one-genre-out | — | 540 | .224 | .224 | Primary |
| P4 pooled | Leave-one-phrasing-out | — | 5,398 | .619 | .619 | Primary |
| P4 pooled | Leave-one-length-cap-out | — | 5,398 | .484 | .484 | Primary |

**IA1 interval:** across 1,000 matched-size resamples, median accuracy was .461 with a 2.5th–97.5th percentile interval of **.406–.522**.

### Table 2B. Model-level recall under selected transfer regimes

| Model | P1 cross-study | P3 cross-genre pooled | P4 phrasing pooled | P4 length pooled |
|---|---:|---:|---:|---:|
| Claude Haiku 4.5 | .733 | .222 | .423 | .314 |
| Claude Sonnet 4.6 | .433 | .344 | .668 | .470 |
| Claude Opus 4.7 | .100 | .189 | .673 | .420 |
| GPT-5.4 nano | .633 | .144 | .830 | .626 |
| GPT-5.4 mini | .567 | .167 | .623 | .659 |
| GPT-5.4 | .467 | .278 | .498 | .416 |

**Note.** Six-way balanced-class chance accuracy is 1/6 (.167). P1 95% stratified-bootstrap accuracy interval: .428–.550.

## Table 3. Six-way attribution accuracy by behavioral feature family

| Feature family | P1 cross-study | P3 cross-genre pooled | P4 phrasing pooled | P4 length pooled |
|---|---:|---:|---:|---:|
| Form / structure | .344 | .235 | .310 | .274 |
| Grammar / person | .317 | .183 | .453 | .401 |
| Punctuation | .339 | .239 | .409 | .358 |
| Nonstructural style | .433 | .204 | .558 | .496 |
| Full body | .489 | .224 | .619 | .484 |

**Feature definitions.** Form/structure contains six length and structural measurements. Grammar/person contains five part-of-speech ratios and four pronoun/person shares. Punctuation contains seven punctuation-rate measures. Nonstructural style combines grammar/person and punctuation. Full body contains all 22 body-only features.

**Interpretation.** Nonstructural style retains most of the cross-study and prompt-transfer signal and approximately matches the full body representation under held-out length constraints. No feature family produces strong cross-genre transfer.
