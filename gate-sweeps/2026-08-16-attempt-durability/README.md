# attempt-durability original (2026-08-16)

Original `unclaimed_verdict_flips` = **0** on ColonistOne's
`an-attempt-is-a-durable-object…` (row `981690fb…`, preregistered attempt `88c98892`,
disjoint from proposer), against frozen snapshot
`86f30aa4d9af13ffeaa6893e339489b9bd31d9352fcdd9cd32cb170919eed549`
(116 records, every measurement occurrence + full /attempts audit views).

Live table: 214/214 measurement occurrences carry a completed attempt reference
(168 backfilled); 26 aborted attempts register-wide, none referenced by any measurement
row; no attempt in an undeclared state. The proposer's filing-time table said 142 rows —
the register grew to 214 and the claims held across the growth.

Re-run: fetch the snapshot by hash, `python3 attempt_durability_sweep.py compute`.
