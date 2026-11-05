# The sampling band, re-derived from committed bytes (2026-11-05)

The register's `SamplingBand` rule (`unconfirmable-by-tolerance-v1`, z = 2, refuse-only; issues 582 and 645) refuses to call a point-rule disagreement a disagreement when the two means differ by less than 2 standard errors of their difference, computed from exact integer moments of the per-pair token deltas on each row's headline encoding (and, for a stratified headline, per declared stratum with the committed shares). It needs those moments on BOTH rows, so every replication filed before the server retained them keeps its point-rule label.

This directory re-derives the band for every standing token_delta disagreement on the register by recounting both rows' committed pairs with tiktoken 0.14.0, taking the same moments, and applying the same rule. Nothing here changes a stored label; it is a reading of what the rule would say if it could reach those rows.

Read at 2026-11-05T13:38:21Z through the SDK's complete iterators (`iter_measurements()`, `iter_proposals()`), 1559 measurement rows, 1021 of them token_delta.

| population | count |
|---|---|
| standing token disagreements (replication, reproduced_ok false, settlement_eligible true, evidence valid, not retracted or voided) | 210 |
| distinct originals they target | 106 |
| token rows carrying server-recounted dispersion | 8 |
| rows the register's band has assessed | 1 |
| rows the register labels unconfirmable | 1 |

| outcome under the band, re-derived | rows |
|---|---|
| unconfirmable: difference inside z=2 SE on the headline encoding and every declared stratum | 75 |
| disagreement stands: difference outside the band | 48 |
| not reachable | 87 |
| reachable, exact recount of both filed headline values | 96 |
| reachable, recount within the 3-decimal filing rounding of legacy rows | 27 |
| reachable and stratified (committed shares, per-stratum re-test) | 38 |
| reachable with the point tolerance narrower than the band | 111 of 123 |

| why a row is not reachable | rows |
|---|---|
| the filed value is not reproduced by recounting the manifest (the filed-vs-derived class; see `dl/diag.json`) | 43 |
| a single pair on a headline encoding: no sample variance exists | 19 |
| test_set is not an inline list of pairs | 14 |
| a tokenizer not available locally (google/gemma-4-31b-it) | 8 |
| a non-string arm | 2 |
| no inline manifest on one row | 1 |

Tolerance over band on the 120 reachable rows with a non-zero band: quartiles 0.093, 0.202, 0.327; below 1 on 111. Among the standing disagreements the difference is 1.67 bands at the median; among the unconfirmable rows 0.39.

| the 106 originals | count |
|---|---|
| every standing disagreement inside the band | 27 |
| at least one inside the band | 45 |
| every disagreement reachable | 63 |
| no disagreement reachable | 42 |

What the stored counters would say if the band's reading were promoted to the label (a separate, receipted act the register reserves; `ReplicationSettlement::status` with MIN_AGREEMENTS 1): disputed to awaiting 13, confirmed_contested to confirmed 13, disputed to confirmed_contested 3, disputed to confirmed 1; 55 stay disputed and 21 stay contested. 30 of 106 originals would move.

The register's own shadow reading (`SamplingBand::shadowForOriginal`, served on the dispute queue) covers 19 token originals in the queue; it could derive 0 of their rows and labels 0 unconfirmable. This recount reaches 49 rows on the same originals and finds 34 inside the band.

The 19 single-pair rows, under the resolution hold proposed in a-22spx2ghcwt7ms0d (hold iff tolerance < s and |gap| <= s with s = 1 token for one pair): held 0; the smallest gap is 5.25 tokens.

Calibration: the port reproduces the served sampling-band block on 42d2addb vs 130bcdcf exactly: variances 5.85 and 4.8667, standard error 0.8184, band 1.6368.

## Files

- `census.py`: the re-derivation. Reads `dl/measurements_slim.json` (every field it uses, from `iter_measurements()` at read_at), `dl/manifests/<hash>.json` (each row's inline manifest from `/api/v1/measurements/<hash>`), `dl/queue_shadow.json` (the register's shadow from the authenticated queue read of 12:39Z); writes `dl/census.json` (every row with its band, outcome and reason; every original with its counts and counterfactual state).
- `diag.py`: why the unreachable rows are unreachable; writes `dl/diag.json`.
- `facts.py`: binds the numbers above into `dl/facts.json` and asserts them.
- `dl/orig_to_proposal.json`: original manifest hash (8) to proposal public id, slug and title.

Run `python3 census.py && python3 diag.py && python3 facts.py` in this directory with tiktoken 0.14.0 installed; the outputs are byte-for-byte what is committed.
