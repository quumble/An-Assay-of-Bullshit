# By-hand arm: Claude app and ChatGPT app

Run by Bo Chesterton on 2026-11-16, after the API run and after the prediction file was written. Scored by Claude Fable 5.2 from replies pasted into a chat.

## Conditions, as reported by the human

- Claude app, one fresh incognito chat per reply, nothing else in the chat.
- Prompt, verbatim: `Tell me a joke.`
- Preferences and style at default.
- Thinking left at whatever the app defaulted to when the window opened. The app labelled it Medium for Haiku 5.5 and Sonnet 5.5 and High for Opus 5.5. The API runs had no thinking, so this differs.
- Replies were copied by selecting the rendered text, not with the app's copy button.

## Replies

| Model | n | Joke | Identical within model |
|---|---|---|---|
| Haiku 5.5 | 3 | atoms | 3/3 |
| Sonnet 5.5 | 3 | atoms | 3/3 |
| Opus 5.5 | 3 | skeletons | 3/3 |

The nine replies are in `hand_claude.txt` in the order above, three per model.

## Reading

- All nine replies come from the same three-joke canon as the published joke study and the API run in this folder. Each model repeated one joke.
- Prediction P9 (atoms in at most 3 of 10 by-hand Claude replies) missed: atoms appeared in 6 of 9.
- The claim this folder was built to test, that the published findings depend on the bare-API condition, is not supported by this arm either.
- Opus 5.5 told the skeleton joke, which was the modal gpt-5.4 joke in the API run. Three replies; an observation, not a finding.

## Limits

These apply to the Claude replies above. The ChatGPT section below has its own.

- n = 3 per model.
- These are current app models, not the May models. The arm tests today's product, not the paper's models under product conditions.
- Because the text was copied from the rendered page, markdown, and possibly punctuation style, is not preserved. The apostrophes arrived curly. "Identical" here means identical as pasted, and these strings cannot be compared character for character with the API strings.
- The pasted replies had no opener, emoji or bold. Emoji and an opener would have survived this copy method; bold would not.

## ChatGPT app (added after the Claude replies)

### Conditions, as reported by the human

- ChatGPT app, one fresh temporary chat per reply, same prompt.
- The picker offered only GPT-6 and GPT-5.6; both were run. The app labelled thinking Medium for both.
- Replies were copied with the app's copy function, not by selecting text. This differs from the Claude replies, so the two apps' strings are not copied the same way.
- Whether saved custom instructions were blank was not reported.

### Replies

| Model | n | Joke | Identical within model |
|---|---|---|---|
| GPT-5.6 Sol | 3 | scarecrow | 2/3 |
| GPT-6 | 3 | scarecrow | 2/3 |

The six replies are in `hand_chatgpt.txt`, GPT-5.6 Sol first. In each model, two replies end the punchline with an exclamation mark and one with a period; all six carry the same two emoji.

### Reading

- Six of six are the scarecrow joke, the third joke of the canon. Across both apps, all fifteen by-hand replies are atoms, skeletons or scarecrow.
- The two ChatGPT models returned the same three strings in the same order as pasted. That may be two models converging, the app routing both picker entries to one model, or a pasting slip. This note cannot tell which.

### Limits

- n = 3 per model.
- Current app models, not the May models.
- Copy method differs from the Claude replies (see above).
