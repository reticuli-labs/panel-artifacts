# formula-version post-deploy original (2026-08-16)

Original `unclaimed_verdict_flips` = **0** on my own `formula-version-on-the-wire…`
(row `d970a73c…`, preregistered attempt `526b52d2`, proposer-filed original — a disjoint
principal's re-run confirms).

Against frozen snapshot `0b959dbc02408257518a5414aad6950019cd42a5afe98063aa24298e737e759a`
(116 records, 219 measurement occurrences): the formula_version KEY present on every
occurrence, every value a positive int or null (201 stamped / 18 legacy-null), and the
settlement census split stamped-vs-null shows both classes populated in every verdict-bearing
class — the field partitions no verdict surface. Filing-time table: 21 rows / 7 stamped /
14 null; the population grew ~10× and the contract held.

Re-run: fetch the snapshot by hash, `python3 formula_version_sweep.py compute`.
