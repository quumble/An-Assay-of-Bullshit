# Product gap quick run: analyst preregistration (Claude Fable 5.2)

Committed 2026-11-16, after collection finished and before the analyst saw any output of `product_gap.py`.

## Provenance

- Analyst: Claude Fable 5.2, in a memoried chat with Bo Chesterton. Prior-informed, not naive.
- What the analyst had seen: the PhilArchive abstracts for "Why Don't Scientist Trust Atoms?", "The Average Bullshittings of Machines" and "Six Ways to Write a Synthetic Poem"; the Series 1 repo, including `results.jsonl`, which was run through the coder for an equivalence check but never tabulated by model.
- What the analyst had not seen: any response, count or summary from this run.
- The human had the results on screen when this was written. He did not share them.
- The analyst wrote the runner and the scorer. The predictions are about quantities the scorer prints.

## Design being predicted

Six models (claude-haiku-4-5-20251001, claude-sonnet-4-6, claude-opus-4-7, gpt-5.4-nano, gpt-5.4-mini, gpt-5.4), three prompts (joke, poem_lt5, story_lt5), two arms (bare, chatapp), n = 20 per cell, temperature 1.0, 400 output tokens.

## Predictions

Confidence is the analyst's stated probability that the prediction holds.

| # | Prediction | Confidence |
|---|---|---|
| P1 | Sonnet 4.6, bare, joke: atoms in at least 19/20, and at least 18/20 character-identical. | 85% |
| P2 | All three Claude models, bare, joke: atoms in at least 55/60 combined. | 80% |
| P3 | Sonnet 4.6, chatapp, joke: atoms still in at least 14/20. | 65% |
| P4 | Sonnet 4.6, joke: the identical-string count is lower in chatapp than in bare. | 60% |
| P5 | At least two of the three GPT models, bare, joke: atoms in fewer than 10/20. | 60% |
| P6 | Sonnet 4.6, poem_lt5: preamble rate in chatapp is not more than 5/20 below bare. | 65% |
| P7 | Em-dash per 100 words, bare, pooled over poem and story: the highest model is a GPT model. Same in chatapp. | 60% |
| P8 | In the bare-vs-chatapp table, at most 4 cells are starred (p < .01). | 60% |
| P9 | If the by-hand arm is run: Claude app, atoms in at most 3/10. | 65% |

## Headline bet

The one-line system prompt moves little. The atoms joke survives it as content, and only the exact wrapper loosens.

## What each outcome would mean

- If P3 and P8 hold, this arm does not support the claim that the published results are artifacts of the bare-API condition. That claim would then rest on the by-hand arm and the published-prompt arm, which test a different and much larger intervention.
- If P3 fails badly (atoms at 5/20 or fewer in chatapp), the 200/200 result is a property of the empty-context condition, and the analyst's headline bet was wrong.
- If P1 fails, the bare condition did not replicate, and nothing else in the run can be compared to the published numbers until that is explained.

## Not predicted

Whether all six models are still served. Opus 4.7 and the GPT-5.4 family under any condition other than those named above.
