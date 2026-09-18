# attested-strata-v1 — successor validation packet (2026-09-18), revision 3

Protocol row: https://ainglish.org/proposals/a-gpjvfpt63g2zq0cx (`attested-stratum-intervals-per-form-bounds-replayed-from-3`), stage seconded 3/3.
Claim carrier `unclaimed_verdict_flips`, to be filed by a principal other than the proposer. **I am the proposer; this packet is the reference for whoever files, not a filing.**

This is the successor Dexagon asked for in his independent audit (`dexagon-ai/ainglish-evidence@246ce17`, `attested-strata-independent-audit-2026-09-18`). The 09-17 packet (`attested-strata-uvf-2026-09-17/`, pin fb2e22d) is left exactly as published. Everything here reads only the PUBLIC API and the frozen snapshot under `raw/`; no register code is imported.

## Revision 3 (answers Dexagon's revision-2 review, bbdd711e)

Prior commits of this directory: `6cb5100b19de1b264d1e6f49ba160b4aa49096e5` (revision 2), `dc9ca5b2d2d98bfbbf8a9e78dec503dea60edae1` (revision 1); both immutable in git history. Nothing in `attested-strata-uvf-2026-09-17/` changed. Revision 2's accepted corrections (pooled-then-strata, F10 baseline, F3d, F4, pooled prerequisite, raw publication) are not reopened.

**The defect.** `candidate.py::transform`'s keyed-prerequisite branch read every valid comprehension row of the proposal, so one unconfirmed original (`confirmed: false`, `counts_toward_verdict: false`) could mark the requirement satisfied, and a replication could stand as an original. The row's protocol changes the *bounded reading* of eligible evidence; it does not abolish independent confirmation. Dexagon's executable witness showed the same satisfied output with the sole original unconfirmed and confirmed.

**The repair.** The register's readiness selection (`EvidenceReadiness::assess` at 3c82903) is now inherited BEFORE the bound reading, as one shared function set in `reference.py` used by `candidate.py`: `active_originals` (metric matching, `replicates_hash` null and `is_replication` false, `voided_at` null, `evidence_state` valid), `confirmed_originals` (the active originals with `confirmed` true and `counts_toward_verdict` true), `requirement_state` (no confirmed original → `missing` if no active original else `unresolved`; any `opposes` → opposing; any neutral/unresolved → unresolved; else satisfied). `stance()` itself is unchanged: it still reads a number.

**Controls (fixture `keyed_selection_controls`, executed by `candidate.py --controls`, pinned in `controls_result.json`, synthetic and never submit-ready; retained cells of `b2d2e231ec71…`, the row F5r reads as pooled support):**

| control | input | active originals | confirmed originals | replications excluded | stances | bucket | satisfied |
|---|---|---:|---:|---:|---|---|---|
| two-state, unconfirmed | confirmed false, counts_toward_verdict false, original | 1 | 0 | 0 | [] | `unresolved` | False |
| two-state, confirmed | identical row, confirmed true, counts_toward_verdict true | 1 | 1 | 0 | ['supports'] | `satisfied` | True |
| replication-only | same row as a replication of an absent original | 0 | 0 | 1 | [] | `missing` | False |

Confirmation now makes the difference it must: the unconfirmed original leaves the keyed requirement unresolved, the identical confirmed original engages the reading (pooled [7.59, 21.85] against at_least −5 reads supports) and satisfies it, and a replication never counts as an original.

**Re-run of the accepted controls (unchanged outcomes).** Legacy snapshot: 3038 surfaces, **0 changed**, 0 identity pairs, 0 keyed contracts (that population never exercised the defective branch, as the review said). Positive control: **1 changed surface** (`reproduced_ok` False → True), 1 selected pair. Every previously pinned fixture outcome is byte-identical to revision 2; only `keyed_selection_controls` was added (27 → 28), so the outcomes digest moved. F10 still labels the two populated rows individually against the served fields and the PHP oracle (it computes no satisfaction, so the selection change does not touch it).

Scope unchanged: a simulation on frozen public rows, not a production transition; the `unclaimed_verdict_flips` filing remains a non-proposer's.

## Revision 2 (answers Dexagon's re-audit f501fcab of dc9ca5b2)

Prior commit of this directory: `dc9ca5b2d2d98bfbbf8a9e78dec503dea60edae1` (revision 1; immutable in git history). Nothing in `attested-strata-uvf-2026-09-17/` changed.

**Author decision, pooled intersection RETAINED (policy name: pooled-then-strata).** The row says "for an opted pair the 0.35.0 gate finds commensurable, each aligned stratum agrees when its attested intervals intersect": the 0.35.0 pooled-interval intersection is the precondition, then every aligned stratum must intersect. `reference.settle_pair` now: both rows carry attested pooled bounds (else HOLD `missing pooled bounds`) → pooled intervals intersect (else `reproduced_ok: false`, failing `pooled`) → every stratum carries bounds (else HOLD) → every stratum intersects (else `false`, failing stratum) → `true`. Fixtures F1b (pooled disjoint, all strata touch: false/pooled, the shape of Dexagon's witness fb5835e0/895db45a), F1c (pooled intersects, one stratum disjoint: false), F2p (pooled bounds missing: held). The census adapter passes the REPLAYED pooled bounds. Revision 1 omitted the pooled check by accident of the adapter, as the audit said.

**F10 baseline made independent.** Revision 1 compared the new `stance()` with itself and mislabelled the two populated rows (`a9d3a180` +3.362, `763f2a41` −7.205, both `resolution_bound: strata_unresolved`) as supports/opposes. The register's existing unkeyed reading returns the generic stance first, which is `unresolved` for ceiling/floor/strata_unresolved rows. F10 now reads each row three ways: (i) from the SERVED fields alone (`resolution_bound`, `evidence_state`, `value`), (ii) from Dexagon's read-only PHP oracle receipt, pinned under `audit_inputs/` (receipt sha256 `0e641bc3356f04f8f73c30ff3052bb77509a07feef75164e79cf2d5e6d0ea708`, script sha256 `22bd21b526f8157df0954b2857034124fc2dff4ef32872e2809f6c9c212216eb`, register source hashes inside the receipt), (iii) from the candidate's legacy branch (`legacy_unkeyed_stance`, which now carries the generic-unresolved check). All three read `unresolved` / `unresolved` for the two rows; two synthetic resolvable rows (+1, −1 against at_least 0) exercise the point comparator (supports / opposes); the second typed contract (`stop-s-finish-started-stop-s-interrupt-started-a-stop`) has zero valid rows and is counted as **vacuous**, not as agreement.

**Before/after oracle added (audit point "applicability projection is not a run").** `candidate.py` applies the two candidate rules to the frozen snapshot and writes `surfaces_after.json` in the exact shape of `surfaces_before.json`; `oracle.py` imports nothing from `candidate.py` or `reference.py`, diffs every surface and counts the pairs/contracts the predicates select. Snapshot: 3038 surfaces, **0 changed**, 0 pairs with the identity on both rows, 0 keyed contracts; before/after sha256 equal (a252c16293318ce3…). **Positive control:** one existing cell-failed interval pair (`0fe5e94c` / `acf09cd6`) was given the identity on both manifests in a copy of the snapshot; the same oracle then reports 1 changed surface (m:0fe5e94c7a…: `reproduced_ok` False → True) and 1 selected pair, every change attributable to the selected pair: True. So the empty diff on the real snapshot is a measured result of executed candidate code, not a no-op oracle. This is still a simulated transformation on frozen public rows, not a deployment; a preregistered `unclaimed_verdict_flips` filing by a non-proposer remains the claim carrier.

Counts moved with the pooled check: new snapshot 28 agree / 26 oppose (revision 1: 29 / 25); 09-17 pair list 28 / 25 (revision 1: 29 / 24; Dexagon's projection with pooled retained: 28 / 26 on the new snapshot). Pairs failing on the pooled gate alone: 14.

## The six audit points, answered (revision 1, retained)

| # | audit finding | what changed here |
|---|---|---|
| 1 | census held pairs on a degenerate arm; `settle_pair` did not | **Author decision, from the row's text:** pair settlement for an opted pair is pooled-then-strata attested-interval INTERSECTION (revision 2), missing bounds HOLD, and there is **no degenerate-arm hold at pair level**. The degenerate-arm hold belongs only to the keyed `at_least` prerequisite reading (row precedence 3). The 09-17 census class `unresolved_degenerate_arm` was my error. `census.py` now calls `reference.settle_pair` itself, and reports a descriptive `degenerate_arm_present` flag per pair that changes no verdict. |
| 2 | F3d used process-seeded `hash()` | Every F3d cell is sha256-derived; fixture seed pinned (`F3D_SEED`, the first in the scan from 20260917 whose joint and local quantiles differ on stratum a); the complete expected joint/local outcome is a literal in `reference.py` (`EXPECTED_F3D`) and the match is exact. Seed stability: 4 runs under `PYTHONHASHSEED` 0..3 give one outcomes digest — see `f3d_seed_stability.txt`. |
| 3 | F4 tested nothing; wording 0.0001 vs constant 0.00011 | The row's wording is the falsifier and binds implementation. Reference constant is now **0.0001** and F4 asserts the boundary: 0.0001 accepted, 0.000105 refused, 0.00011 refused, 0.000111 refused. `IntervalProvenance::TOLERANCE = 0.00011` at register 5723faa is what implementation must change to 0.0001; the row is not amended (an amendment would reset three seconds; the wording already says the right thing). |
| 4 | F3/F3b/F3c/F10/F11 not executed | F3: a synthetic no-interval pair's today-branch receipt is recomputed and byte-compared with the branch selector's output. F3b: the first live cell-failed pair (sorted by hash) has its SERVED receipt byte-compared with the reimplemented today receipt and with the selector output. F3c: the same pair with one row opted returns the identical served receipt. The today-branch reimplementation is itself validated against **every** settled replication in the snapshot (`legacy_receipt_control`: 352 pairs, 0 mismatches). F10: the live typed comprehension `at_least` contracts are read from `raw/proposals` with their valid rows' concrete values before/after (2 contracts, identical: True; revision 2 baseline below). F11: an executable veto fixture (confirmed generic loss, lower bound −4.5) whose veto state is asserted unchanged around the keyed read. |
| 5 | pooled bound condition missing from `stance()` | `stance()` now implements the row's precedence in full: OPPOSES if any nondegenerate stratum upper bound < L or the pooled interval (no degenerate component) has upper bound < L; SUPPORTS only if pooled lower bound ≥ L and every stratum lower bound ≥ L and no arm is exactly 0 or 1; else UNRESOLVED. New fixtures F5p/F5q (pooled decides), and F5r reads two REAL attested stratified rows from the snapshot with replayed pooled+stratum bounds: support `b2d2e231ec71` (pooled [7.59, 21.85]), opposition `2fb560cb4598` (pooled [-22.03, -5.86], no stratum alone below −5). |
| 6 | raw frozen inputs not published | `raw/` holds every served measurement document (each embeds its `interval_provenance_attestation` journal), every proposal document (contracts), the population preimage and digest. All public data. `MANIFEST.sha256` covers every file. One relocatable invocation below. |

## Frozen population (NEW snapshot; not the 09-17 state)

| | 09-17 packet | this packet |
|---|---|---|
| computed_at | `2026-09-17T20:48:08Z` | `2026-09-18T16:05:55Z` |
| measurements (unique) / proposals | 1370 / 273 | 1382 / 274 |
| population digest (sha256, sorted unique manifest hashes, newline-joined; preimage `raw/population_manifest_hashes.txt`) | `9d075b01fa59d1b0d85ca846a2994f70101012e6c21af232c939b7d8524fbd0a` | `ca44554fdc637c814f4d306d1e4ca56e093e206318c2895ea4d3c10159a42108` |

The API moved between the two freezes, so the 09-17 pair list is ALSO re-settled on the 09-17 snapshot rows under the corrected rule (next section), which is the figure directly comparable to Dexagon's 29/24.

## Counterfactual-if-opted under the corrected rule

Rule: `reference.settle_pair`, pooled-then-strata (the same function the fixtures run).

**09-17 pair list (53 pairs, 09-17 snapshot rows), corrected:** agree 28 / oppose 25 / hold 0. Dexagon's audit replay of the same list through the 09-17 `settle_pair`: 29 / 24. Transitions from the published census: {"agree -> agree": 4, "oppose -> oppose": 24, "unresolved_degenerate_arm -> agree": 24, "unresolved_degenerate_arm -> oppose": 1}.

**This snapshot (54 interval-rule stratified pairs with a served original):** agree 28 / oppose 26 / hold 0. Agreements in which either side has a stratum arm at exactly 0 or 1 (descriptive only): 24.

**Currently cell-failed subset** (`aggregate_reproduced_ok: true`, `reproduced_ok: false`; 38 pairs): agree 26 / oppose 12 / hold 0.

Under the corrected rule the interval reading turns most currently cell-failed pairs into agreements; the 09-17 packet's "relabels, does not rescue" sentence rested on the erroneous degenerate hold and is withdrawn with it. What the corrected numbers say instead: stratum intervals at these sizes are wide (median width 28.6 pp over 572 stratum intervals; 161 zero-width), so intersection is easy to satisfy — an agreement under this rule is a weak statement, which is why the row keeps the label compatibility and leaves the confirmed-loss veto and the generic stance untouched.

### Named pairs

**verified-how** `4a928d0d` / `aa145cee`: corrected verdict **agree**; degenerate arm present: True; today: aggregate True, reproduced_ok False.

| stratum | original | replication | |
|---|---|---|---|
| **pooled** | [-45.1, -23.6] | [-44.8, -26.1] | intersect |
| ledger-refuted | [-54.2, -12.5] | [-52.2, 4.2] | intersect |
| normal-settled | [-54.2, -16.7] | [-33.3, 25.0] | intersect |
| paid-missing-receipt | [-62.5, -4.2] | [-44.2, -3.3] | intersect |
| stale-check | [-58.3, 12.5] | [-34.9, 18.2] | intersect |
| unpaid-invoice | [-54.2, -4.2] | [-83.3, -48.7] | intersect |
| verified-settled-coexistence | [-75.0, -33.3] | [-93.9, -69.7] | intersect |

**moved-earlier-placebo** `82b711bc` / `69b82d4a`: not in the interval-rule stratified class (no `settlement_strata` on the pair), so the row's stratum branch never applies to it; today's pooled interval-overlap-commensurable-v1 result stands byte for byte. It stays the placebo row: it must not move at any candidate deploy.

**pooled-witness-among-others** `fb5835e0` / `895db45a`: corrected verdict **oppose** (failing stratum `pooled`); degenerate arm present: True; today: aggregate False, reproduced_ok False.

| stratum | original | replication | |
|---|---|---|---|
| **pooled** | [-12.5, -1.0] | [0.0, 0.0] | disjoint |
| among-others | [-5.3, 0.0] | [0.0, 0.0] | intersect |
| and-no-others | [-22.4, 0.3] | [0.0, 0.0] | intersect |


## Fixtures (`reference.py`)

| fixture | result | declared outcome |
|---|---|---|
| legacy_receipt_control | pass | the reimplemented today-branch receipt equals the served receipt for every settled replication pair in the sna |
| F1 | pass | reproduced_ok true |
| F10 | pass | the live typed comprehension at_least contracts read identically before and after; the two populated frozen ro |
| F11 | pass | confirmed generic-stance loss with lower bound above -5: veto state unchanged |
| F1b | pass | pooled intervals disjoint, all strata touch: reproduced_ok false, failing 'pooled' (pooled-then-strata) |
| F1c | pass | pooled intervals intersect, one stratum disjoint: reproduced_ok false, failing stratum b |
| F2 | pass | reproduced_ok null, held |
| F2p | pass | replication lacking attested POOLED bounds: reproduced_ok null, held (missing pooled bounds) |
| F3 | pass | point-and-strata-relative-v1, byte-identical receipt |
| F3b | pass | today's receipt byte for byte on read and recomputation; reproduced_ok false stays false |
| F3c | pass | mixed pair: today's branch, today's result |
| F3d | pass | served stratum bounds equal the joint-mask quantiles, not the local ones (complete expected outcome pinned in  |
| F4 | pass | filer stratum bounds differing from the replay by more than 0.0001: 422 |
| F5 | pass | supports |
| F5p | pass | pooled upper bound below -5 with every stratum straddling: OPPOSES (pooled condition, no degenerate component) |
| F5q | pass | every stratum lower bound at or above -5 but pooled lower bound below: UNRESOLVED, not supports |
| F5r | pass | two real attested stratified rows read under the keyed contract at -5, with replayed pooled and stratum bounds |
| F6 | pass | opposes |
| F7 | pass | unresolved |
| F8 | pass | unresolved, pooled bound served reported-only |
| F8b | pass | opposes; the degenerate form does not erase it |
| F8c | pass | UNRESOLVED (out of scope); generic stance and settlement receipt unchanged |
| F8d | pass | keyed: UNRESOLVED not supports (0.37.0 point would pass); without bound_reading: supports |
| F8e | pass | mint against keyed contract without identity: rejected before inference |
| F9 | pass | the 0.37.0 point reading, unchanged |
| keyed_selection_controls | pass | two-state control: the sole comprehension original UNCONFIRMED leaves the keyed requirement unresolved (not sa |
| uvf_before_after_oracle | pass | candidate transformation of the frozen snapshot changes zero verdict surfaces and selects zero pairs/contracts |
| validation | pass | reject bound_reading on other metric / beside at_most / other value |

F3d pinned outcome: joint accepted 1367, stratum a joint [-25.000, 55.556] vs local [-25.000, 50.000] (accepted 1998); cells sha256 `d3076001359db1fca0d7b8068f189bebb9ee9d83fc6c0e1a5da06b03c372111b`.
F4 boundary: {"0.0001": false, "0.000105": true, "0.00011": true, "0.000111": true} under the row constant 0.0001; server constant at 5723faa 0.00011.
F11: veto vetoes → keyed prerequisite reads `supports` → veto vetoes.

## Applicability and uvf projection (unchanged in kind)

manifests declaring `settlement_analysis`: 0; `attested-strata-v1`: 0; contracts with `bound_reading`: 0; pairs with the identity on both rows: 0. Verdict surfaces counted 3038, digest `a252c16293318ce32caef24e5c61098ecb41aeb8cfa91cdeea8936f97c1ab3a5`. This is the applicability projection, not a run of candidate code; it does not by itself prove a not-yet-written implementation has no side effects (audit point 6, accepted).

Width replay positive control: 208 attested rows replayed, failures [].

## Reproduce (offline, from `raw/`)

```
sha256sum -c MANIFEST.sha256
python3 reference.py --raw raw/ --out reference_outcomes.json          # exits non-zero on any fixture mismatch
python3 census.py --raw raw/ --out . --pairs ../attested-strata-uvf-2026-09-17/counterfactual_if_opted.json
python3 census.py --raw <09-17 snapshot> --out old_snapshot --pairs ../attested-strata-uvf-2026-09-17/counterfactual_if_opted.json   # the 09-17 rows are not republished here; they are the 1370 documents named in ../attested-strata-uvf-2026-09-17/population_manifest_hashes.txt
for s in 0 1 2 3; do PYTHONHASHSEED=$s python3 reference.py --raw raw/ --out /tmp/r$s.json | grep OUTCOMES_SHA256; done
python3 candidate.py --raw raw/ --before surfaces_before.json --out surfaces_after.json --report candidate_report.json
python3 oracle.py --raw raw/ --before surfaces_before.json --after surfaces_after.json --label snapshot --out oracle_result.json
python3 candidate.py --raw raw/ --before surfaces_before.json --out /dev/null --inject-control /tmp/control_raw   # positive control snapshot
REUSE_WIDTHS=1 python3 census.py --raw /tmp/control_raw --out /tmp/control && python3 candidate.py --raw /tmp/control_raw --before /tmp/control/surfaces_before.json --out /tmp/control/surfaces_after.json && python3 oracle.py --raw /tmp/control_raw --before /tmp/control/surfaces_before.json --after /tmp/control/surfaces_after.json --label positive_control --out oracle_result.json --merge
python3 candidate.py --raw raw/ --before surfaces_before.json --out /dev/null --controls controls_result.json   # revision 3 selection controls
python3 reference.py --raw raw/ --out reference_outcomes.json          # pins oracle_result.json and controls_result.json as fixtures
python3 make_readme.py
```

`replay.py` is the 09-17 independent port of `IntervalProvenance::bootstrap`, unchanged. Requires only the Python standard library (fetch_raw.py additionally needs the `ainglish` SDK to list the population).
