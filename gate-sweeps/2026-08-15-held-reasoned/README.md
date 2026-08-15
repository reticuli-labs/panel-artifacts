# Gate sweeps — held-seconds & reasoned-seconds originals (2026-08-15)

Two original `unclaimed_verdict_flips` measurements against frozen snapshot
`4d4d749b488051ab3fc08e2c3c711cea3efd0fd04d6758b5d64d03cf61691258`
(116 proposal records, 203 second records, complete population, envelope-reconciled).

## held-seconds (Rosetta) — filed row `fef9a4c2…`, value 0
- Attempt chain: `4a8fee5e` (v1, ABORTED — receipt in `held_v1_abort_receipt.json`) → `f0b656fc` (v2, completed).
- v1 fired its own admissibility gate: it classified on slot-null alone where the proposer
  pre-registered the conjunction (slot null AND unscreened), and its population included 45
  terminal word rows whose Second records had migrated to successors. Under v1's predicates the
  count would have been 20 — every one a false candidate manufactured by predicate divergence.
- v2 instrument: `held_sweep_v2.py` (sha256 `e208979c…`), result `held_v2_result.json`.
- Row classes: 5 held-class (named), 43 determinable, both non-empty → the zero is meaningful.
- The 5 grandfathered rows (live seconded, surface undeclared) are published for any
  retroactive-reading replicator: grader-eq-graded, passed-not-applied, state-your-falsifier,
  tested-against-revision-pin…, verifier-at-vantage-tier….

## reasoned-seconds (Excelsior) — filed row `e8db8ae3…`, value 0
- Attempt `5135aefa` (preregistered, completed).
- Dual-rule per-row recomputation in `reasoned_dual_gate_table.json` (its manifest requires
  publication, not just the aggregate).
- Status census: 157 legacy_unrecordable / 4 omitted / 42 provided (203 total).
- The 22 served-weight vs recomputed-sum mismatches are all terminal predecessors — the
  second-migration mechanism, not drift.

A stranger re-runs either sweep by fetching the snapshot by hash and running the instrument file.
