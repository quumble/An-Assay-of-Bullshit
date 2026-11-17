# Product gap, quick run

Scored 2026-11-16 18:23. Settings: temperature 1.0, max 400 output tokens. Coder: the published structural heuristics (preamble, title line, em-dash).

## `Tell me a joke.`

| model | arm | n | preamble | title line | any em-dash | em-dash /100w | atoms | identical | distinct | top first word |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5-20251001 | bare | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 20/20 | 16/20 | 2 | why (20) |
| claude-haiku-4-5-20251001 | chatapp | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 20/20 | 20/20 | 1 | why (20) |
| claude-sonnet-4-6 | bare | 20 | 20/20 | 20/20 | 0/20 | 0.00 | 20/20 | 20/20 | 1 | here's (20) |
| claude-sonnet-4-6 | chatapp | 20 | 20/20 | 20/20 | 0/20 | 0.00 | 20/20 | 18/20 | 2 | here's (20) |
| claude-opus-4-7 | bare | 20 | 15/20 | 15/20 | 0/20 | 0.00 | 20/20 | 13/20 | 4 | here's (13) |
| claude-opus-4-7 | chatapp | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 19/20 | 17/20 | 3 | why (20) |
| gpt-5.4-nano | bare | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 9/20 | 6/20 | 5 | why (20) |
| gpt-5.4-nano | chatapp | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 7/20 | 5/20 | 11 | why (20) |
| gpt-5.4-mini | bare | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 2/20 | 9/20 | 4 | why (20) |
| gpt-5.4-mini | chatapp | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 7/20 | 7/20 | 5 | why (20) |
| gpt-5.4 | bare | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 0/20 | 19/20 | 2 | why (20) |
| gpt-5.4 | chatapp | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 0/20 | 20/20 | 1 | why (20) |

## `create a poem in fewer then 5 lines.`

| model | arm | n | preamble | title line | any em-dash | em-dash /100w | atoms | identical | distinct | top first word |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5-20251001 | bare | 20 | 0/20 | 20/20 | 4/20 | 0.95 | 0/20 | 1/20 | 20 | whisper (16) |
| claude-haiku-4-5-20251001 | chatapp | 20 | 1/20 | 20/20 | 11/20 | 2.24 | 0/20 | 1/20 | 20 | november (9) |
| claude-sonnet-4-6 | bare | 20 | 20/20 | 20/20 | 0/20 | 0.00 | 0/20 | 3/20 | 16 | here (16) |
| claude-sonnet-4-6 | chatapp | 20 | 20/20 | 20/20 | 0/20 | 0.00 | 0/20 | 1/20 | 20 | here's (20) |
| claude-opus-4-7 | bare | 20 | 0/20 | 0/20 | 1/20 | 0.24 | 0/20 | 1/20 | 20 | moonlight (16) |
| claude-opus-4-7 | chatapp | 20 | 2/20 | 2/20 | 13/20 | 3.00 | 0/20 | 1/20 | 20 | moonlight (9) |
| gpt-5.4-nano | bare | 20 | 0/20 | 0/20 | 17/20 | 3.33 | 0/20 | 1/20 | 20 | beneath (11) |
| gpt-5.4-nano | chatapp | 20 | 0/20 | 0/20 | 18/20 | 3.52 | 0/20 | 1/20 | 20 | in (6) |
| gpt-5.4-mini | bare | 20 | 0/20 | 0/20 | 0/20 | 0.00 | 0/20 | 1/20 | 20 | moonlight (20) |
| gpt-5.4-mini | chatapp | 20 | 0/20 | 0/20 | 1/20 | 0.21 | 0/20 | 1/20 | 20 | moonlight (20) |
| gpt-5.4 | bare | 20 | 0/20 | 0/20 | 2/20 | 0.39 | 0/20 | 1/20 | 20 | dawn (13) |
| gpt-5.4 | chatapp | 20 | 0/20 | 0/20 | 2/20 | 0.38 | 0/20 | 1/20 | 20 | morning (15) |

## `create a short story in fewer than 5 sentences.`

| model | arm | n | preamble | title line | any em-dash | em-dash /100w | atoms | identical | distinct | top first word |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5-20251001 | bare | 20 | 0/20 | 20/20 | 14/20 | 0.77 | 0/20 | 1/20 | 20 | the (20) |
| claude-haiku-4-5-20251001 | chatapp | 20 | 0/20 | 20/20 | 16/20 | 0.96 | 0/20 | 1/20 | 20 | the (20) |
| claude-sonnet-4-6 | bare | 20 | 20/20 | 20/20 | 6/20 | 0.39 | 0/20 | 1/20 | 20 | here (20) |
| claude-sonnet-4-6 | chatapp | 20 | 20/20 | 20/20 | 12/20 | 0.70 | 0/20 | 1/20 | 20 | here (19) |
| claude-opus-4-7 | bare | 20 | 0/20 | 0/20 | 3/20 | 0.21 | 0/20 | 1/20 | 20 | the (20) |
| claude-opus-4-7 | chatapp | 20 | 0/20 | 0/20 | 3/20 | 0.21 | 0/20 | 1/20 | 20 | the (20) |
| gpt-5.4-nano | bare | 20 | 0/20 | 0/20 | 11/20 | 0.93 | 0/20 | 1/20 | 20 | mara (17) |
| gpt-5.4-nano | chatapp | 20 | 0/20 | 0/20 | 15/20 | 1.09 | 0/20 | 1/20 | 20 | mara (19) |
| gpt-5.4-mini | bare | 20 | 0/20 | 0/20 | 1/20 | 0.06 | 0/20 | 1/20 | 20 | at (15) |
| gpt-5.4-mini | chatapp | 20 | 0/20 | 0/20 | 2/20 | 0.18 | 0/20 | 1/20 | 20 | at (10) |
| gpt-5.4 | bare | 20 | 0/20 | 0/20 | 6/20 | 0.45 | 0/20 | 1/20 | 20 | at (17) |
| gpt-5.4 | chatapp | 20 | 0/20 | 0/20 | 3/20 | 0.24 | 0/20 | 1/20 | 20 | at (15) |

## Does the system prompt move anything? (bare vs each other arm)

Fisher exact p, two-sided, uncorrected. With six models, three prompts and four features, expect a few small p-values by chance; look for patterns, not single cells.

| model | prompt | vs arm | feature | bare | other | p |
|---|---|---|---|---|---|---|
| claude-haiku-4-5-20251001 | joke | chatapp | atoms | 20/20 | 20/20 | 1.0000 |
| claude-haiku-4-5-20251001 | poem_lt5 | chatapp | preamble | 0/20 | 1/20 | 1.0000 |
| claude-haiku-4-5-20251001 | poem_lt5 | chatapp | title line | 20/20 | 20/20 | 1.0000 |
| claude-haiku-4-5-20251001 | poem_lt5 | chatapp | any em-dash | 4/20 | 11/20 | 0.0484 |
| claude-haiku-4-5-20251001 | story_lt5 | chatapp | title line | 20/20 | 20/20 | 1.0000 |
| claude-haiku-4-5-20251001 | story_lt5 | chatapp | any em-dash | 14/20 | 16/20 | 0.7164 |
| claude-sonnet-4-6 | joke | chatapp | preamble | 20/20 | 20/20 | 1.0000 |
| claude-sonnet-4-6 | joke | chatapp | title line | 20/20 | 20/20 | 1.0000 |
| claude-sonnet-4-6 | joke | chatapp | atoms | 20/20 | 20/20 | 1.0000 |
| claude-sonnet-4-6 | poem_lt5 | chatapp | preamble | 20/20 | 20/20 | 1.0000 |
| claude-sonnet-4-6 | poem_lt5 | chatapp | title line | 20/20 | 20/20 | 1.0000 |
| claude-sonnet-4-6 | story_lt5 | chatapp | preamble | 20/20 | 20/20 | 1.0000 |
| claude-sonnet-4-6 | story_lt5 | chatapp | title line | 20/20 | 20/20 | 1.0000 |
| claude-sonnet-4-6 | story_lt5 | chatapp | any em-dash | 6/20 | 12/20 | 0.1110 |
| claude-opus-4-7 | joke | chatapp | preamble | 15/20 | 0/20 | 0.0000 * |
| claude-opus-4-7 | joke | chatapp | title line | 15/20 | 0/20 | 0.0000 * |
| claude-opus-4-7 | joke | chatapp | atoms | 20/20 | 19/20 | 1.0000 |
| claude-opus-4-7 | poem_lt5 | chatapp | preamble | 0/20 | 2/20 | 0.4872 |
| claude-opus-4-7 | poem_lt5 | chatapp | title line | 0/20 | 2/20 | 0.4872 |
| claude-opus-4-7 | poem_lt5 | chatapp | any em-dash | 1/20 | 13/20 | 0.0001 * |
| claude-opus-4-7 | story_lt5 | chatapp | any em-dash | 3/20 | 3/20 | 1.0000 |
| gpt-5.4-nano | joke | chatapp | atoms | 9/20 | 7/20 | 0.7475 |
| gpt-5.4-nano | poem_lt5 | chatapp | any em-dash | 17/20 | 18/20 | 1.0000 |
| gpt-5.4-nano | story_lt5 | chatapp | any em-dash | 11/20 | 15/20 | 0.3203 |
| gpt-5.4-mini | joke | chatapp | atoms | 2/20 | 7/20 | 0.1274 |
| gpt-5.4-mini | poem_lt5 | chatapp | any em-dash | 0/20 | 1/20 | 1.0000 |
| gpt-5.4-mini | story_lt5 | chatapp | any em-dash | 1/20 | 2/20 | 1.0000 |
| gpt-5.4 | poem_lt5 | chatapp | any em-dash | 2/20 | 2/20 | 1.0000 |
| gpt-5.4 | story_lt5 | chatapp | any em-dash | 6/20 | 3/20 | 0.4506 |
