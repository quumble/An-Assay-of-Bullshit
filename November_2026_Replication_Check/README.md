# November 2026 Replication Check

A quick run made on 2026-11-16, six months after the May studies. It is a check-in, not a study. No paper is planned from it and it makes no new claims.

The May studies and the September secondary analysis are unchanged by this folder.

## What it is

Two things in one run of 720 calls:

1. **A same-snapshot replication.** The `bare` arm repeats the published condition (no system prompt, temperature 1.0, 400 output tokens) on the six original model IDs, for three prompts.
2. **An exploratory system-prompt arm.** The `chatapp` arm adds one sentence telling the model its name, its maker, that it is in a chat app, and the date. Everything else is the same.

Design: 6 models x 3 prompts x 2 arms x 20 calls. All calls ran in one shuffled batch before anything was scored. 720 of 720 returned, with no errors, no empty replies and no token-cap hits.

Prompts, verbatim:

- `Tell me a joke.` (the baseline probe from "Why Don't Scientist Trust Atoms?")
- `create a poem in fewer then 5 lines.` (Bullshit Assay 1, typo kept)
- `create a short story in fewer than 5 sentences.` (Bullshit Assay 1)

## Files

| File | What it is |
|---|---|
| `product_gap.py` | Runner and scorer in one file, standard library only. Written by Claude Fable 5.2. |
| `results.jsonl` | Every call as it ran, including the system prompt sent. |
| `summary.md`, `summary.csv` | Scorer output, as generated on the collection machine. |
| `PREREG_FABLE.md` | The analyst's predictions. See the provenance note below before relying on it. |
| `HAND_ARM.md`, `hand_claude.txt`, `hand_chatgpt.txt` | The by-hand arm from both apps: conditions, tables, and the fifteen replies. |

Scoring uses the preamble, title-line, em-dash and word-count rules copied from `Bullshit_Assay_1/Results and Heuristics/structural_heuristics.py`. The copy reproduces the published coded outputs on all 540 Series 1 rows for those four features.

## Provenance, stated plainly

- **Why it was run.** Claude Fable 5.2 was asked to find weak spots in the published work and argued that the findings might depend on the bare-API condition. This run was the cheap test of that claim.
- **The prediction file is not a frozen-before-collection preregistration.** It was written after collection finished, in a chat, before the analyst had seen any output. The human had the results on screen at the time and did not share them. Its timing rests on that chat record, not on a commit that predates the data.
- **The analyst wrote the runner and the scorer**, and is one of the model families under test.
- **Commits in this folder were made by the analyst** and are not founder-signed.

## What came back

Replication (`bare` arm):

- Claude Sonnet 4.6 returned one character-identical atoms joke in 20 of 20 calls. All 60 Claude joke replies were the atoms joke.
- All 240 joke replies, both arms, were one of three jokes: atoms, skeletons, scarecrow.
- Em-dashes again concentrated in gpt-5.4-nano (17 of 20 poems). Preambles again sat in Claude Sonnet 4.6 (20 of 20 on every prompt). Claude Haiku 4.5 again put a title on 20 of 20 poems and stories.

System-prompt arm:

- Mostly no change. Claude Sonnet 4.6 did not move on any measure. The claim that the published findings depend on the empty-context condition is not supported by this arm.
- Claude Opus 4.7 dropped its joke opener ("Here's one for you:") from 15 of 20 to 0 of 20.
- Any-em-dash rose or held in all six Claude poem and story cells and fell in none (Opus poems 1 to 13 of 20, Haiku poems 4 to 11, Sonnet stories 6 to 12). Exploratory and not predicted.

Predictions: P1 to P8 held. P9, about the by-hand arm, missed. See `HAND_ARM.md`.

## Limits

- n = 20 per cell.
- One sentence is a stand-in for a consumer app, not the app. Only the by-hand arm touches a real product, at n = 3 per model.
- **The date in the system prompt leaks into content.** Claude Haiku 4.5 mentions November or the season in 19 of 20 `chatapp` poems against 6 of 20 `bare`. The sentence changes four things at once (a system prompt exists, a name, an app, a date), so no effect in this arm can be assigned to any one of them. The em-dash rise in particular may come from different poems, not from the name.
- Fisher p-values in `summary.md` are uncorrected.
- The joke probe ran at 400 output tokens here; the original joke study's cap was not checked against this.

## By-hand arm

Added later the same day: nine replies from the Claude app and six from the ChatGPT app, each in a fresh incognito or temporary chat. All fifteen are from the same three-joke canon. Conditions, tables and limits are in `HAND_ARM.md`; the replies are in `hand_claude.txt` and `hand_chatgpt.txt`.

`summary.md` and `summary.csv` are the scorer output from the collection machine and predate this arm, so they do not include it. Running `python product_gap.py score` here would add a pooled by-hand row.
