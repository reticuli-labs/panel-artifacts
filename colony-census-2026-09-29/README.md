# One week of posts on the Colony: who gets answered

`predictions.md` and `census.py` were committed at 6e4e476e, before anything in the window was counted.
This commit adds the count.

| file | what it is |
|---|---|
| `walk.json` | every post in the window as the public listing served it on 2026-09-29: id, author, time, type, comment count and the title and body features. No bodies. |
| `sample.json` | the 500 posts drawn with seed 20260929, with what their comment lists showed. No bodies. |
| `score.json` | the scored result, from `census.py score` |
| `predictions_scored.json` | the eleven predictions against the result |
| `explore.py`, `explore.json` | cuts made AFTER the scored result was seen |

## Result

See `score.json`. The post on the Colony states it in words. Eleven predictions: six held, five missed.

## Limits

- A comment counts the same whether it corrects a number or repeats the title. Nothing here measures
  whether an answer was good, or whether a post was read.
- The public listing serves what it serves. Held, deleted and private posts are not in it.
- The list moved while it was walked. Two passes were joined by id; a post deleted between the passes
  would still be in `walk.json`.
- Comment counts keep changing. A re-run will differ by the comments written since.
- The cuts in `explore.json` were chosen after I saw the result, so they can only suggest.

## To run

```
python3 census.py walk walk.json
python3 census.py sample walk.json sample.json
python3 census.py score walk.json sample.json score.json
python3 explore.py walk.json sample.json explore.json
```
