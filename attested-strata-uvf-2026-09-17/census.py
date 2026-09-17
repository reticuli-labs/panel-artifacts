"""Frozen-population census + per-form width replay + counterfactual-if-opted + uvf projection for
protocol row a-gpjvfpt63g2zq0cx (attested-strata-v1). Reads ONLY the frozen snapshot on disk."""
import json, glob, os, sys, hashlib, time, statistics
sys.path.insert(0, os.path.dirname(__file__))
from replay import check_row, contract_from_manifest
F = os.path.expanduser("~/.reticuli/work/aing-round-20260917e/freeze")
OUT = os.path.expanduser("~/.reticuli/work/aing-round-20260917e/census"); os.makedirs(OUT, exist_ok=True)
rows = {}
for fp in glob.glob(f"{F}/measurements/*.json"):
    m = json.load(open(fp)); rows[m["manifest_hash"]] = m
props = {}
for fp in glob.glob(f"{F}/proposals/*.json"):
    p = json.load(open(fp)); props[p["slug"]] = p
pop = json.load(open(f"{F}/population.json"))
print("rows", len(rows), "props", len(props), "pop", pop)
def g(d, *ks):
    for k in ks: d = d.get(k) if isinstance(d, dict) else None
    return d
# 1. applicability predicate
ident = [h for h, m in rows.items() if "settlement_analysis" in (m.get("manifest") or {})]
ident_v1 = [h for h in ident if rows[h]["manifest"].get("settlement_analysis") == "attested-strata-v1"]
keyed = []
for s, p in props.items():
    for pre in ((p.get("evidence_contract") or {}).get("prerequisites") or []):
        if isinstance(pre, dict) and "bound_reading" in pre: keyed.append((s, pre))
print("manifests with settlement_analysis:", len(ident), "== attested-strata-v1:", len(ident_v1), "| contracts with bound_reading:", len(keyed))
# 2. classes (09-16 blast.py logic)
reps = [m for m in rows.values() if m.get("is_replication")]
interval_pairs = [m for m in reps if g(m, "replication_comparison", "rule_applied") == "interval-overlap-commensurable-v1"]
strat_pairs = [m for m in reps if isinstance(g(m, "replication_comparison", "strata"), list) and g(m, "replication_comparison", "strata")]
cell_failed = [m for m in strat_pairs if g(m, "replication_comparison", "aggregate_reproduced_ok") is True and m.get("reproduced_ok") is False]
cell_pass = [m for m in strat_pairs if m.get("reproduced_ok") is True]
legacy_strata_pairs = [m for m in strat_pairs if g(m, "replication_comparison", "rule_applied") != "interval-overlap-commensurable-v1"]
attested = [m for m in rows.values() if m.get("interval_provenance_attestation")]
attested_strat = [m for m in attested if (m.get("manifest") or {}).get("settlement_strata")]
with_filer_bounds = [m for m in rows.values() if any(isinstance(s, dict) and (s.get("value_lo") is not None) for s in (m.get("stratum_results") or []))]
cad_atleast = []
for s, p in props.items():
    for pre in ((p.get("evidence_contract") or {}).get("prerequisites") or []):
        if isinstance(pre, dict) and pre.get("metric") == "comprehension_accuracy_delta" and "at_least" in pre: cad_atleast.append((s, pre))
interval_strat = [m for m in strat_pairs if g(m, "replication_comparison", "rule_applied") == "interval-overlap-commensurable-v1"]
classes = {"interval_rule_pairs": len(interval_pairs), "stratified_pairs_any_rule": len(strat_pairs), "interval_rule_stratified_pairs": len(interval_strat), "cell_failed_pairs": len(cell_failed), "cell_pass_pairs": len(cell_pass),
  "legacy_strata_pairs": len(legacy_strata_pairs), "attested_rows": len(attested), "attested_stratified_rows": len(attested_strat), "rows_with_filer_stratum_bounds": len(with_filer_bounds),
  "legacy_cad_at_least_contracts": len(cad_atleast), "cad_at_least_list": cad_atleast}
print(json.dumps(classes, indent=1, default=str)[:1500])
# 3. width replay over every attested row (positive control on all; strata where present)
widths = {}; control_fail = []
t0 = time.time()
CACHE = f"{OUT}/widths.json"
if os.path.exists(CACHE) and os.environ.get("REUSE_WIDTHS") == "1":
    widths = json.load(open(CACHE)); control_fail = [h for h, w in widths.items() if not w["pooled_match"]]; attested = [m for m in attested if m["manifest_hash"] not in widths]
    print("reusing cached widths for", len(widths), "rows; replaying", len(attested), "new")
for i, m in enumerate(attested):
    r = check_row(m)
    if not (r["pooled_match"] and r["accepted_match"]): control_fail.append(r["hash"])
    widths[m["manifest_hash"]] = {"pooled_match": r["pooled_match"], "accepted": r["accepted"], "strata": r["strata"],
        "n_items": len(m["interval_provenance_attestation"]["items"]), "arms_by_stratum": {s["id"]: s.get("arms") for s in (m.get("stratum_results") or [])}}
    if i % 20 == 0: print("replayed", i, "of", len(attested), f"{time.time()-t0:.0f}s", flush=True)
print("positive control failures:", control_fail)
json.dump(widths, open(f"{OUT}/widths.json", "w"), indent=1)
allw = [(h, sid, s["width"], s["accepted"]) for h, w in widths.items() if w["strata"] for sid, s in w["strata"].items()]
wv = [x[2] for x in allw]
per_items = {}
for h, w in widths.items():
    if not w["strata"]: continue
    m = rows[h]; n_by = {}
    for it in m["interval_provenance_attestation"]["items"]: n_by[it["stratum"]] = n_by.get(it["stratum"], 0) + 1
    for sid, s in w["strata"].items(): per_items.setdefault(n_by[sid], []).append(s["width"])
summary = {"stratum_intervals": len(wv), "width_median": statistics.median(wv) if wv else None, "width_q1": statistics.quantiles(wv, n=4)[0] if len(wv) > 3 else None, "width_q3": statistics.quantiles(wv, n=4)[2] if len(wv) > 3 else None,
  "width_min": min(wv) if wv else None, "width_max": max(wv) if wv else None, "zero_width": sum(1 for x in wv if x == 0),
  "by_items_per_stratum": {str(k): {"n": len(v), "median_width": statistics.median(v)} for k, v in sorted(per_items.items())}}
print(json.dumps(summary, indent=1))
# 4. counterfactual-if-opted for every stratified pair with attestation on both sides
cf = []
for m in interval_strat:
    o = rows.get(m.get("replicates_hash"))
    if not o: continue
    wo, wr = widths.get(o["manifest_hash"]), widths.get(m["manifest_hash"])
    if not (wo and wr and wo["strata"] and wr["strata"]):
        cf.append({"rep": m["manifest_hash"][:8], "orig": o["manifest_hash"][:8], "counterfactual": "hold_missing_bounds", "current_reproduced_ok": m.get("reproduced_ok")}); continue
    verdict = "agree"; degenerate = False; failing = []
    for sid, so in wo["strata"].items():
        sr = wr["strata"].get(sid)
        if sr is None: verdict = "hold_missing_bounds"; break
        if so["hi"] < sr["lo"] or sr["hi"] < so["lo"]: failing.append(sid)
        for side in (wo, wr):
            arms = side["arms_by_stratum"].get(sid) or {}
            if any(arms.get(a) in (0, 1, 0.0, 1.0) for a in ("english", "ainglish")): degenerate = True
    if verdict == "agree":
        if failing: verdict = "oppose"
        elif degenerate: verdict = "unresolved_degenerate_arm"
    cf.append({"rep": m["manifest_hash"][:8], "orig": o["manifest_hash"][:8], "counterfactual": verdict, "failing_strata": failing, "current_reproduced_ok": m.get("reproduced_ok"), "current_aggregate": g(m, "replication_comparison", "aggregate_reproduced_ok")})
from collections import Counter
print("counterfactual-if-opted:", Counter(x["counterfactual"] for x in cf))
print("  among currently cell-failed:", Counter(x["counterfactual"] for x in cf if x.get("current_aggregate") is True and x.get("current_reproduced_ok") is False))
json.dump(cf, open(f"{OUT}/counterfactual_if_opted.json", "w"), indent=1)
# 5. uvf projection: surfaces before; branch selection set S; after == before iff S empty and no keyed contract
surfaces = {}
for h, m in rows.items():
    surfaces[f"m:{h}"] = {k: m.get(k) for k in ("reproduced_ok", "confirmed", "settlement_state", "settlement_eligible", "evidence_state", "counts_toward_verdict", "resolution_bound")}
    surfaces[f"m:{h}:agg"] = g(m, "replication_comparison", "aggregate_reproduced_ok")
for s, p in props.items():
    surfaces[f"p:{s}"] = {"stage": p.get("stage"), "assessment": g(p, "verdict", "assessment"), "readiness_satisfied": g(p, "evidence_readiness", "satisfied"), "readiness_missing": g(p, "evidence_readiness", "missing_evidence"),
        "readiness_opposing": g(p, "evidence_readiness", "opposing_evidence"), "readiness_unresolved": g(p, "evidence_readiness", "unresolved_evidence"), "ballot_ready": g(p, "ratification", "readiness", "ready"), "verdict_class": p.get("verdict_class")}
canon = json.dumps(surfaces, sort_keys=True, separators=(",", ":"), default=str)
sd = hashlib.sha256(canon.encode()).hexdigest()
S = [m["manifest_hash"] for m in reps if rows.get(m.get("replicates_hash")) and (m.get("manifest") or {}).get("settlement_analysis") == "attested-strata-v1" and (rows[m["replicates_hash"]].get("manifest") or {}).get("settlement_analysis") == "attested-strata-v1"]
uvf = {"population_digest_newline": pop["digest_newline"], "computed_at": pop["computed_at"], "measurements": len(rows), "proposals": len(props),
  "verdict_surfaces_counted": len(surfaces), "surfaces_before_sha256": sd, "branch_selected_pairs": S, "keyed_contracts": keyed,
  "surfaces_after_sha256": sd if not S and not keyed else None, "unclaimed_verdict_flips": 0 if not S and not keyed else None,
  "note": "The proposed branch runs only for pairs whose BOTH manifests declare settlement_analysis: attested-strata-v1 and the keyed reading only for contracts carrying bound_reading. With both selection sets empty on this frozen population, every counted verdict surface is byte-identical before and after by construction of the branch predicate; the count is the size of the symmetric difference, 0. This is the applicability projection, not a run of the candidate code."}
json.dump({"classes": classes, "applicability": {"settlement_analysis_manifests": len(ident), "attested_strata_v1_manifests": len(ident_v1), "bound_reading_contracts": len(keyed)}, "width_summary": summary, "uvf": uvf}, open(f"{OUT}/census.json", "w"), indent=1, default=str)
json.dump(surfaces, open(f"{OUT}/surfaces_before.json", "w"), sort_keys=True, indent=0, default=str)
print(json.dumps(uvf, indent=1)[:1200]); print("CENSUS_DONE")
