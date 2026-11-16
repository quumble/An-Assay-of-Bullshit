# By-hand arm: Claude app

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

- n = 3 per model.
- These are current app models, not the May models. The arm tests today's product, not the paper's models under product conditions.
- Because the text was copied from the rendered page, markdown, and possibly punctuation style, is not preserved. The apostrophes arrived curly. "Identical" here means identical as pasted, and these strings cannot be compared character for character with the API strings.
- The pasted replies had no opener, emoji or bold. Emoji and an opener would have survived this copy method; bold would not.
- No ChatGPT replies had been collected when this was filed.
