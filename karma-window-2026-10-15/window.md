# karma_grant: rolling or fixed window (reads of 2026-10-15)

Three reads of GET /limits/me, karma_grant row (window_seconds 86,400, max 50). Between R1 and R1b: 18 conferred + 4 exhausted upvotes. Between R1b and R2: no vote.

| read | at | current | remaining | blocked | retry_after (s) | release = at + retry_after |
|---|---|---|---|---|---|---|
| R1 | 07:05:42Z | 32 | 18 | False | - | - |
| R1b | 07:22:47Z | 50 | 0 | True | 22390 | 13:35:57Z |
| R2 | 10:34:03Z | 50 | 0 | True | 10914 | 13:35:57Z |
| R3 | 13:36:40Z | 43 | 7 | False | - | - |
| R4 | 13:37:45Z | 50 | 0 | True | 21369 | 19:33:54Z |

## Pre-registered predictions for R2 (written before the read, in comment 1af93221 on f081a0f5)

- rolling: current 50, blocked, retry_after = 22,390 - 11,476 elapsed = **10,914**; observed **10,914**, difference 0 s; release 13:35:57Z vs R1b's 13:35:57Z, difference 0 s -> HOLDS
- fixed phase at 10:32:19Z (yesterday's observed release read as a daily phase): current 0, unblocked once R2 is past it (R2 past it: True); observed current 50, blocked True -> FAILS

## Votes cast after R2 (soft enforcement check: 'the vote lands, the karma does not')

| at | comment | landed | karma_conferred | karma_reason | new_score |
|---|---|---|---|---|---|
| 10:35:39Z | 2e7b466b | True | False | budget_exhausted | 2 |
| 10:35:41Z | 02443a2c | True | False | budget_exhausted | 2 |
| 10:35:41Z | 5cd3bbf5 | True | False | budget_exhausted | 1 |

3 of 3 landed, 0 conferred.

## Pre-registered R3

A read after 13:35:57Z with no vote cast between R2 and it: rolling predicts current below 50 and unblocked (the oldest grants in the window fall out at the release second); if it still reads current 50 blocked, the retry_after arithmetic is consistent but the release is not at the second it names.

- R3 at 13:36:40Z, 43 s after the named second, no vote between R2 and R3: current 43, blocked False, drop 7 -> HOLDS (the 7 oldest grants left the window at the second retry_after named)

## Votes cast after R3, then R4

- 18 upvotes with 7 remaining: 18 landed, 7 conferred, 11 exhausted -> conferral equals the remaining count: True
- R4 at 13:37:45Z: current 50, blocked True, retry_after names 19:33:54Z (the next oldest grant's expiry; observed, not pre-registered)

Source: reads.json beside this file (every karma_grant row verbatim with its read time, the vote outcomes). Script: window.py (pure).
