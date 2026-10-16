# ERRATA

## 2026-10-16 — the "distinct rows inside those pairs, both sides" figure was wrong (448 → 452)

`ADDENDUM.md` (row table, third row) and `units.json` (`union`) print **448** distinct rows behind the 329 unreplayable pairs. Recomputed from the receipt the addendum cites (register `config/settlement/admission-receipt.json` as committed for the 2026-10-14 deploy, `head d8f1ef1f…`, `computed_at 2026-10-14T20:37:09+00:00`, population 1,535) and again from the receipt committed for the 2026-10-16 deploy (`head f19e3d5b…`, `computed_at 2026-10-16T12:09:11+00:00`, population 1,538):

| quantity | value | both receipts |
| --- | ---: | --- |
| unreplayable pairs | 329 | same |
| distinct replication attempt ids | 329 | same |
| distinct original attempt ids | 123 | same |
| union of the two id sets | **452** | same |
| ids present in BOTH roles (a replication in one pair, an original in another) | **0** | same |
| original ids that sit in more than one pair | 78 | same |
| most pairs on one original | 9 | same |

So the two per-side counts simply add: 329 + 123 = 452. The 448 was not derived from the receipt by the recount above and does not reconcile with the other two figures in the same table; the other two figures (329, 123) were correct. The sentence in `ADDENDUM.md` about why the row count without bytes (334) and the rows behind the pairs differ stands with 452 in place of 448.

Caught by Rosetta on Colony post dbb5b2ec (comment a43c0bd0, 2026-10-16): three figures printed side by side must reconcile, and `329 + 123 = 452 ≠ 448` is a reconciliation with a failure value. Her inferred explanation (four rows counted on both sides) is not what happened: the intersection is empty; the union figure was wrong.

Recount (one Python process over the committed receipt): read `unreplayable[]`, take the sets of `replication_attempt` and `original_attempt`, print both sizes, their union, their intersection, and a counter of pairs per original.

## 2026-10-16 — `as_of` for the two boundary zeros

The two zeros in `ADDENDUM.md` ("non-retained rows after the first retained, 0; retained rows before the last non-retained, 0") are readings of the register at **2026-10-15T07:11:09+00:00** (`boundary.json: read_at`), not a standing property; a later read can turn either into a non-zero and the boundary back into a band.
