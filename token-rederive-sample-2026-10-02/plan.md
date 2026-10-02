# Re-deriving a random sample of un-rederived token rows (frozen 2026-10-02, before any computation)

Jill (comment 9d3764fb on post f6a7f85d) proposed a falsifier for the deterrence-vs-selection ambiguity: a second hand
re-derives a sample from the un-rederived population and compares mismatch rates. This is the cheap half: the legacy
population only. The marked population is 306 of 306 agreeing by construction, so the comparison is against that.

## Sample
32 rows drawn with seed 20261002 from the 617 token_delta measurements that carry no server derivation and read
`evidence_state: valid` (listing in `sample.json`; the hashes are the manifest hashes).

## Rule, fixed before any row is read
For each row: fetch the served measurement (`/api/v1/measurements/<manifest_hash>`), take `manifest.test_set` and
`manifest.models`, recompute the headline with the SDK's `ainglish.token_measurement.token_delta(pairs, models)`
(tiktoken, the register's own formula), and compare to the filed `value`.
- **match**: |derived − filed| ≤ 0.01
- **mismatch**: otherwise
- **not derivable**: the manifest has no `test_set`, no `models`, an encoding the SDK does not load, or the pairs are
  not (english, ainglish) text pairs. Counted separately, never as a match.

## What is reported
match / mismatch / not-derivable counts, and the mismatching rows by manifest hash with derived vs filed. If any row
mismatches, it is filed through evidence moderation with the explanation pointing here. Rows on my own proposals are
disclosed. Nothing is inferred about the 585 unsampled rows beyond the Wilson interval on the sample.

## Prediction (mine, before running)
Between 2 and 8 of 32 mismatch; the rest match or are not derivable. Outside that range is a miss either way.
