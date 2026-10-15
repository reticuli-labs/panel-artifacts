# Manifest retention boundary (read 2026-10-15T07:11:09+00:00)

Rows 1535; with an attempt and a created_at 1535; retained (attempt.manifest.url + sha256 served) 1201; not retained 334.

| has_attempt | retained | backfilled | rows |
|---|---|---|---|
| True | False | False | 128 |
| True | False | True | 206 |
| True | True | False | 961 |
| True | True | True | 240 |

| retained | manifest_storage | rows |
|---|---|---|
| False | commitment_only | 334 |
| True | stored_at_filing | 240 |
| True | stored_at_mint | 961 |

First retained attempt created_at: 2026-08-23T22:03:34+00:00
Last non-retained attempt created_at: 2026-08-23T21:29:08+00:00
Non-retained rows created after the first retained one: 0 (by backfilled: {})
Retained rows created before the last non-retained one: 0
Earliest non-backfilled retained: 2026-08-23T22:03:34+00:00; latest backfilled non-retained: 2026-08-23T07:20:05+00:00; latest backfilled retained: 2026-09-22T02:52:28+00:00
Non-backfilled, non-retained rows after the first retained one (retention gaps, not boundary): 0
