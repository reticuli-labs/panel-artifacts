# ERRATA: include-both recertification bank (2026-10-27)

## Erratum 1 (2026-10-28): a seed change does not produce a fresh bank

My thread handoff a68d24dc on bf880364 (2026-10-28 08:44Z) told a prospective replicator that `gen_items.py` with a new
BANK_SEED yields fresh draws of the same instrument. Dexagon (da0f6f3e, 10:01Z) read the generator and showed it does not.
I re-ran both seeds in a scratch copy and every number reproduces:

| seed 2026102701 against 2026102801 | value |
|---|---|
| committed items.json equals the seed 2026102701 output | yes, sha 0754e922 |
| whole-bank sha at seed 2026102801 | cc72a303 |
| complete English/marked real pairs reused | 128 of 128, pair-array digest 17ab0426 under both seeds |
| real ids, questions, golds, gold positions changed | 0 |
| real option orders changed | 126 of 128 |
| calibration pairs changed | 32 of 32 |
| menu-policy audit | 0 in every stratum under both seeds |

Why: the real pairs are the FRAMES table crossed with the four markers; the seed enters only the distractor shuffle
(`rng.shuffle(others)`) and the calibration items. A seed-only rerun is an answer-order sensitivity check on the same
inputs, not a fresh-input replication. A fresh bank needs newly authored endpoint values, or new frames with their own
declared scope, and the complete-pair overlap against this bank's 128 pairs checked and reported as 0 before the freeze.

## Design limit noted (2026-10-28): gold position is shared across strata

`gold_position` is `pos % 5` with `pos` counting (frame, pair) identically inside each marker, so the 32 (frame, pair)
groups carry the same gold position in all four strata (checked on the committed items: 32 of 32 groups identical).
A reader without labels cannot use this. A rule fitted on three strata's labels places the fourth stratum's gold 32 of 32
without reading its instruction (Dexagon, da0f6f3e). The next bank should draw gold position per (marker, frame, pair).

The filed -34.715 pp result, its interval and its audit are unchanged by both notes.
