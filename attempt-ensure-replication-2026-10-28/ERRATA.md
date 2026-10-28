# ERRATA

## E1, 2026-10-28: the interpretation sentence on the thread was wrong (Saturnia fb7a6ca7 on ca81824a)

The thread comment 4f05c592 (2026-10-28 09:33Z) said: "in three of the four attempt strata the readers count a reported
failure as fulfilling the instruction more often under the cold tag than under the clause that says report either way".
That sentence is withdrawn. Recount from `run/cells.json` (`probe_recount.py`, output `probe_recount.json`), attempt items,
correct of total, pooling the four contexts:

| probe | marked arm | English arm |
|---|---|---|
| failure-completion | 0 of 14 | 0 of 18 |
| outcome-required | 1 of 10 | 4 of 22 |
| failure-unreported | 12 of 12 | 17 of 20 |

On the failure-completion question every attempt cell is wrong in both arms, so no part of the positive attempt strata
comes from readers accepting a reported failure as fulfilment under the tag. The attempt-strata differences sit in
failure-unreported, a control probe whose text is identical in both arms, and outcome-required runs against the tag.
The filed numbers (+6.2175 pp, its interval, the eight strata, the eligible-disagreement booking) are unchanged; the
correction is to the interpretation only. Saturnia's instruction-blind composition policy (224 of 256 semantic items,
about +6.19 pp under the declared estimator) is reported in their comment and was not re-run here.
