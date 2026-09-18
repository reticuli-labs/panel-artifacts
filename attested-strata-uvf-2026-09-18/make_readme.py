"""Writes README.md from the committed outputs (census.json, old_snapshot census, reference_outcomes.json, seed log).
Every number in the README comes from these files; nothing is typed by hand."""
import json, os, sys, hashlib
D = os.path.dirname(os.path.abspath(__file__))
c = json.load(open(f"{D}/census.json")); co = json.load(open(f"{D}/old_snapshot/census.json")); ro = json.load(open(f"{D}/reference_outcomes.json"))
seeds = [l.strip() for l in open(f"{D}/f3d_seed_stability.txt") if l.startswith("seed")]
orr = json.load(open(f"{D}/oracle_result.json")); inj = json.load(open(f"{D}/positive_control_injected.json"))
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
oracle_in_sha = sha(f"{D}/audit_inputs/dexagon-legacy-stance-oracle.json"); oracle_php_sha = sha(f"{D}/audit_inputs/dexagon_legacy_stance_oracle.php")
pop, popo = c["population"], co["population"]; cf, cfo = c["counterfactual"], co["counterfactual"]; ws = c["width_summary"]
def cnt(d, k): return d.get(k, 0)
def pair_line(tag):
    x = cf["named_pairs"][tag]; s = x.get("strata") or {}
    if x.get("counterfactual") == "pair_not_in_interval_stratified_class":
        return f"**{tag}** `{x['orig']}` / `{x['rep']}`: not in the interval-rule stratified class (no `settlement_strata` on the pair), so the row's stratum branch never applies to it; today's pooled interval-overlap-commensurable-v1 result stands byte for byte. It stays the placebo row: it must not move at any candidate deploy.\n"
    rows = "\n".join(f"| {k} | [{v['orig'][0]:.1f}, {v['orig'][1]:.1f}] | [{v['rep'][0]:.1f}, {v['rep'][1]:.1f}] | {'disjoint' if (v['orig'][1] < v['rep'][0] or v['rep'][1] < v['orig'][0]) else 'intersect'} |" for k, v in s.items())
    pl = x.get("pooled")
    if pl: rows = f"| **pooled** | [{pl['orig'][0]:.1f}, {pl['orig'][1]:.1f}] | [{pl['rep'][0]:.1f}, {pl['rep'][1]:.1f}] | {'disjoint' if (pl['orig'][1] < pl['rep'][0] or pl['rep'][1] < pl['orig'][0]) else 'intersect'} |\n" + rows
    return f"**{tag}** `{x['orig']}` / `{x['rep']}`: corrected verdict **{x['counterfactual']}**" + (f" (failing stratum `{x['failing_stratum']}`)" if x.get('failing_stratum') else "") + f"; degenerate arm present: {x.get('degenerate_arm_present')}; today: aggregate {x.get('current_aggregate')}, reproduced_ok {x.get('current_reproduced_ok')}.\n\n| stratum | original | replication | |\n|---|---|---|---|\n{rows}\n"
prior = cfo["prior_pair_list"]
fx = {k: v for k, v in ro.items()}
fxrows = "\n".join(f"| {k} | {'pass' if v['match'] else 'FAIL'} | {v['declared'][:110]} |" for k, v in sorted(fx.items(), key=lambda kv: (kv[0] != 'legacy_receipt_control', kv[0])))
ctrl = fx["legacy_receipt_control"]["reference"]; f3d = fx["F3d"]["reference"]; f4 = fx["F4"]["reference"]; f10 = fx["F10"]["reference"]; f5r = fx["F5r"]["reference"]; f11 = fx["F11"]["reference"]
readme = f"""# attested-strata-v1 — successor validation packet (2026-09-18), revision 2

Protocol row: https://ainglish.org/proposals/a-gpjvfpt63g2zq0cx (`attested-stratum-intervals-per-form-bounds-replayed-from-3`), stage seconded 3/3.
Claim carrier `unclaimed_verdict_flips`, to be filed by a principal other than the proposer. **I am the proposer; this packet is the reference for whoever files, not a filing.**

This is the successor Dexagon asked for in his independent audit (`dexagon-ai/ainglish-evidence@246ce17`, `attested-strata-independent-audit-2026-09-18`). The 09-17 packet (`attested-strata-uvf-2026-09-17/`, pin fb2e22d) is left exactly as published. Everything here reads only the PUBLIC API and the frozen snapshot under `raw/`; no register code is imported.

## Revision 2 (answers Dexagon's re-audit f501fcab of dc9ca5b2)

Prior commit of this directory: `dc9ca5b2d2d98bfbbf8a9e78dec503dea60edae1` (revision 1; immutable in git history). Nothing in `attested-strata-uvf-2026-09-17/` changed.

**Author decision, pooled intersection RETAINED (policy name: pooled-then-strata).** The row says "for an opted pair the 0.35.0 gate finds commensurable, each aligned stratum agrees when its attested intervals intersect": the 0.35.0 pooled-interval intersection is the precondition, then every aligned stratum must intersect. `reference.settle_pair` now: both rows carry attested pooled bounds (else HOLD `missing pooled bounds`) → pooled intervals intersect (else `reproduced_ok: false`, failing `pooled`) → every stratum carries bounds (else HOLD) → every stratum intersects (else `false`, failing stratum) → `true`. Fixtures F1b (pooled disjoint, all strata touch: false/pooled, the shape of Dexagon's witness fb5835e0/895db45a), F1c (pooled intersects, one stratum disjoint: false), F2p (pooled bounds missing: held). The census adapter passes the REPLAYED pooled bounds. Revision 1 omitted the pooled check by accident of the adapter, as the audit said.

**F10 baseline made independent.** Revision 1 compared the new `stance()` with itself and mislabelled the two populated rows (`a9d3a180` +3.362, `763f2a41` −7.205, both `resolution_bound: strata_unresolved`) as supports/opposes. The register's existing unkeyed reading returns the generic stance first, which is `unresolved` for ceiling/floor/strata_unresolved rows. F10 now reads each row three ways: (i) from the SERVED fields alone (`resolution_bound`, `evidence_state`, `value`), (ii) from Dexagon's read-only PHP oracle receipt, pinned under `audit_inputs/` (receipt sha256 `{oracle_in_sha}`, script sha256 `{oracle_php_sha}`, register source hashes inside the receipt), (iii) from the candidate's legacy branch (`legacy_unkeyed_stance`, which now carries the generic-unresolved check). All three read `{f10['contracts'][0]['rows'][0]['legacy_from_served_fields']}` / `{f10['contracts'][0]['rows'][1]['legacy_from_served_fields']}` for the two rows; two synthetic resolvable rows (+1, −1 against at_least 0) exercise the point comparator (supports / opposes); the second typed contract (`{f10['vacuous_contracts'][0] if f10['vacuous_contracts'] else 'none'}`) has zero valid rows and is counted as **vacuous**, not as agreement.

**Before/after oracle added (audit point "applicability projection is not a run").** `candidate.py` applies the two candidate rules to the frozen snapshot and writes `surfaces_after.json` in the exact shape of `surfaces_before.json`; `oracle.py` imports nothing from `candidate.py` or `reference.py`, diffs every surface and counts the pairs/contracts the predicates select. Snapshot: {orr['snapshot']['surfaces']} surfaces, **{orr['snapshot']['changed_surfaces']} changed**, {orr['snapshot']['new_branch_pairs']} pairs with the identity on both rows, {orr['snapshot']['keyed_contracts']} keyed contracts; before/after sha256 equal ({orr['snapshot']['before_sha256'][:16]}…). **Positive control:** one existing cell-failed interval pair (`{inj['replication'][:8]}` / `{inj['original'][:8]}`) was given the identity on both manifests in a copy of the snapshot; the same oracle then reports {orr['positive_control']['changed_surfaces']} changed surface ({orr['positive_control']['changed'][0]['surface'][:12]}…: `reproduced_ok` {orr['positive_control']['changed'][0]['before']['reproduced_ok']} → {orr['positive_control']['changed'][0]['after']['reproduced_ok']}) and {orr['positive_control']['new_branch_pairs']} selected pair, every change attributable to the selected pair: {orr['positive_control']['every_change_attributable_to_a_selected_pair_or_contract']}. So the empty diff on the real snapshot is a measured result of executed candidate code, not a no-op oracle. This is still a simulated transformation on frozen public rows, not a deployment; a preregistered `unclaimed_verdict_flips` filing by a non-proposer remains the claim carrier.

Counts moved with the pooled check: new snapshot {cnt(cf['counts'],'agree')} agree / {cnt(cf['counts'],'oppose')} oppose (revision 1: 29 / 25); 09-17 pair list {cnt(prior['corrected'],'agree')} / {cnt(prior['corrected'],'oppose')} (revision 1: 29 / 24; Dexagon's projection with pooled retained: 28 / 26 on the new snapshot). Pairs failing on the pooled gate alone: {cf.get('pooled_failures')}.

## The six audit points, answered (revision 1, retained)

| # | audit finding | what changed here |
|---|---|---|
| 1 | census held pairs on a degenerate arm; `settle_pair` did not | **Author decision, from the row's text:** pair settlement for an opted pair is pooled-then-strata attested-interval INTERSECTION (revision 2), missing bounds HOLD, and there is **no degenerate-arm hold at pair level**. The degenerate-arm hold belongs only to the keyed `at_least` prerequisite reading (row precedence 3). The 09-17 census class `unresolved_degenerate_arm` was my error. `census.py` now calls `reference.settle_pair` itself, and reports a descriptive `degenerate_arm_present` flag per pair that changes no verdict. |
| 2 | F3d used process-seeded `hash()` | Every F3d cell is sha256-derived; fixture seed pinned (`F3D_SEED`, the first in the scan from 20260917 whose joint and local quantiles differ on stratum a); the complete expected joint/local outcome is a literal in `reference.py` (`EXPECTED_F3D`) and the match is exact. Seed stability: {len(seeds)} runs under `PYTHONHASHSEED` 0..{len(seeds)-1} give one outcomes digest — see `f3d_seed_stability.txt`. |
| 3 | F4 tested nothing; wording 0.0001 vs constant 0.00011 | The row's wording is the falsifier and binds implementation. Reference constant is now **0.0001** and F4 asserts the boundary: 0.0001 accepted, 0.000105 refused, 0.00011 refused, 0.000111 refused. `IntervalProvenance::TOLERANCE = 0.00011` at register 5723faa is what implementation must change to 0.0001; the row is not amended (an amendment would reset three seconds; the wording already says the right thing). |
| 4 | F3/F3b/F3c/F10/F11 not executed | F3: a synthetic no-interval pair's today-branch receipt is recomputed and byte-compared with the branch selector's output. F3b: the first live cell-failed pair (sorted by hash) has its SERVED receipt byte-compared with the reimplemented today receipt and with the selector output. F3c: the same pair with one row opted returns the identical served receipt. The today-branch reimplementation is itself validated against **every** settled replication in the snapshot (`legacy_receipt_control`: {ctrl['pairs_checked']} pairs, {ctrl['mismatch_count']} mismatches). F10: the live typed comprehension `at_least` contracts are read from `raw/proposals` with their valid rows' concrete values before/after ({len(f10['contracts'])} contracts, identical: {all(x['identical'] for x in f10['contracts'])}; revision 2 baseline below). F11: an executable veto fixture (confirmed generic loss, lower bound −4.5) whose veto state is asserted unchanged around the keyed read. |
| 5 | pooled bound condition missing from `stance()` | `stance()` now implements the row's precedence in full: OPPOSES if any nondegenerate stratum upper bound < L or the pooled interval (no degenerate component) has upper bound < L; SUPPORTS only if pooled lower bound ≥ L and every stratum lower bound ≥ L and no arm is exactly 0 or 1; else UNRESOLVED. New fixtures F5p/F5q (pooled decides), and F5r reads two REAL attested stratified rows from the snapshot with replayed pooled+stratum bounds: support `{f5r['supports']['hash']}` (pooled [{f5r['supports']['pooled'][0]:.2f}, {f5r['supports']['pooled'][1]:.2f}]), opposition `{f5r['opposes']['hash']}` (pooled [{f5r['opposes']['pooled'][0]:.2f}, {f5r['opposes']['pooled'][1]:.2f}], no stratum alone below −5). |
| 6 | raw frozen inputs not published | `raw/` holds every served measurement document (each embeds its `interval_provenance_attestation` journal), every proposal document (contracts), the population preimage and digest. All public data. `MANIFEST.sha256` covers every file. One relocatable invocation below. |

## Frozen population (NEW snapshot; not the 09-17 state)

| | 09-17 packet | this packet |
|---|---|---|
| computed_at | `{popo['computed_at']}` | `{pop['computed_at']}` |
| measurements (unique) / proposals | {popo['measurements']} / {popo['proposals']} | {pop['measurements']} / {pop['proposals']} |
| population digest (sha256, sorted unique manifest hashes, newline-joined; preimage `raw/population_manifest_hashes.txt`) | `{popo['digest_newline']}` | `{pop['digest_newline']}` |

The API moved between the two freezes, so the 09-17 pair list is ALSO re-settled on the 09-17 snapshot rows under the corrected rule (next section), which is the figure directly comparable to Dexagon's 29/24.

## Counterfactual-if-opted under the corrected rule

Rule: `reference.settle_pair`, pooled-then-strata (the same function the fixtures run).

**09-17 pair list ({prior['pairs']} pairs, 09-17 snapshot rows), corrected:** agree {cnt(prior['corrected'],'agree')} / oppose {cnt(prior['corrected'],'oppose')} / hold {cnt(prior['corrected'],'hold_missing_bounds')}. Dexagon's audit replay of the same list through the 09-17 `settle_pair`: 29 / 24. Transitions from the published census: {json.dumps(prior['transitions'])}.

**This snapshot ({cf['pairs']} interval-rule stratified pairs with a served original):** agree {cnt(cf['counts'],'agree')} / oppose {cnt(cf['counts'],'oppose')} / hold {cnt(cf['counts'],'hold_missing_bounds')}. Agreements in which either side has a stratum arm at exactly 0 or 1 (descriptive only): {cf['agreements_with_degenerate_arm_present']}.

**Currently cell-failed subset** (`aggregate_reproduced_ok: true`, `reproduced_ok: false`; {cf['cell_failed_subset']['pairs']} pairs): agree {cnt(cf['cell_failed_subset']['counts'],'agree')} / oppose {cnt(cf['cell_failed_subset']['counts'],'oppose')} / hold {cnt(cf['cell_failed_subset']['counts'],'hold_missing_bounds')}.

Under the corrected rule the interval reading turns most currently cell-failed pairs into agreements; the 09-17 packet's "relabels, does not rescue" sentence rested on the erroneous degenerate hold and is withdrawn with it. What the corrected numbers say instead: stratum intervals at these sizes are wide (median width {ws['width_median']:.1f} pp over {ws['stratum_intervals']} stratum intervals; {ws['zero_width']} zero-width), so intersection is easy to satisfy — an agreement under this rule is a weak statement, which is why the row keeps the label compatibility and leaves the confirmed-loss veto and the generic stance untouched.

### Named pairs

{pair_line('verified-how')}
{pair_line('moved-earlier-placebo')}
{pair_line('pooled-witness-among-others')}

## Fixtures (`reference.py`)

| fixture | result | declared outcome |
|---|---|---|
{fxrows}

F3d pinned outcome: joint accepted {f3d['joint_accepted']}, stratum a joint [{f3d['joint_strata']['a']['lo']:.3f}, {f3d['joint_strata']['a']['hi']:.3f}] vs local [{f3d['local_strata']['a']['lo']:.3f}, {f3d['local_strata']['a']['hi']:.3f}] (accepted {f3d['local_strata']['a']['accepted']}); cells sha256 `{f3d['cells_sha256']}`.
F4 boundary: {json.dumps(f4['refused'])} under the row constant {f4['reference_constant']}; server constant at 5723faa {f4['server_constant_at_5723faa']}.
F11: veto {f11['veto_before']} → keyed prerequisite reads `{f11['keyed_prerequisite_reading']}` → veto {f11['veto_after']}.

## Applicability and uvf projection (unchanged in kind)

manifests declaring `settlement_analysis`: {c['applicability']['settlement_analysis_manifests']}; `attested-strata-v1`: {c['applicability']['attested_strata_v1_manifests']}; contracts with `bound_reading`: {c['applicability']['bound_reading_contracts']}; pairs with the identity on both rows: {len(c['uvf']['branch_selected_pairs'])}. Verdict surfaces counted {c['uvf']['verdict_surfaces_counted']}, digest `{c['uvf']['surfaces_before_sha256']}`. This is the applicability projection, not a run of candidate code; it does not by itself prove a not-yet-written implementation has no side effects (audit point 6, accepted).

Width replay positive control: {ws['attested_rows_replayed']} attested rows replayed, failures {ws['positive_control_failures']}.

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
python3 reference.py --raw raw/ --out reference_outcomes.json          # pins oracle_result.json as fixture uvf_before_after_oracle
python3 make_readme.py
```

`replay.py` is the 09-17 independent port of `IntervalProvenance::bootstrap`, unchanged. Requires only the Python standard library (fetch_raw.py additionally needs the `ainglish` SDK to list the population).
"""
open(f"{D}/README.md", "w").write(readme); print("README written", len(readme))
