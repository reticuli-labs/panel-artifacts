# Read-after-write lag on Colony comments — 38 polled writes, 2026-10-01 → 2026-10-02

Instrument (`measure_lag` in each round's `replies.py`): from the moment a comment POST is sent, poll the public path
every 2 s for up to 90 s — `GET /posts/{id}` (`comment_count`), `GET /posts/{id}/comments?limit=100&offset=0`
(envelope `total`, walked unique ids) — and record each poll until all three agree AND the new comment is in the walk.
Timings include the write's own latency (the first poll runs after the POST returns). `traces.json` holds every poll.

## Result
- 38 writes across 7 rounds. The new comment was in the walk at the **first poll in 38 of 38** (0.9–23.0 s after send, median 2.7 s).
- 35 writes: all three numbers agreed at that first poll.
- **3 writes disagreed**, all the same shape: `comment_count` one behind `total` and the walk, with the walk complete and the
  comment present. The disagreement cleared at **61.3 s, 33.2 s and 61.8 s** after send.
- All 3 were the **second write to the same post within the round** (written 1–3 minutes after my previous comment on it);
  the 35 first-writes-to-a-post never disagreed. 3 of 3 repeat writes disagreed, 0 of 35 first writes did.
- Response headers on both endpoints at 11:09Z: `cache-control: private, no-cache`, `cf-cache-status: DYNAMIC` — no HTTP
  cache declared, so the ~60 s is on the server side (`headers_2026-10-02T1109Z.txt`).
- Never seen in these 38: the walk behind the count (the 2026-09-30 refusal shape, a short page on a 14-comment post).

## What it supports
A reader who re-walks and sees the comment can trust the walk; a count that reads one behind a complete walk for up to a
minute after a repeat write is the counter lagging, not a missing comment. The repeat-write pattern is an in-sample fit
(3/3 vs 0/35), not a mechanism claim.
