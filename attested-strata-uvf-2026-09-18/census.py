"""Frozen-population census for protocol row a-gpjvfpt63g2zq0cx (attested-strata-v1), successor to the 09-17 census.
Reads ONLY a frozen raw snapshot (raw/measurements/*.json, raw/proposals/*.json, raw/population.json).
Pair settlement in the counterfactual uses EXACTLY reference.settle_pair, policy "pooled-then-strata" (revision 2):
the replayed POOLED attested intervals must intersect, then every aligned stratum's replayed intervals must intersect;
missing pooled or stratum bounds hold; no degenerate-arm hold at pair level. A descriptive degenerate_arm_present flag is reported per pair.
Usage: python3 census.py --raw raw/ --out . [--pairs old_counterfactual.json]   (REUSE_WIDTHS=1 reuses <out>/widths.json)"""
import json, glob, os, sys, hashlib, time, statistics, argparse
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from replay import check_row
from reference import settle_pair, IDENTITY, degenerate
ap = argparse.ArgumentParser(); ap.add_argument("--raw", required=True); ap.add_argument("--out", required=True); ap.add_argument("--pairs", default=None, help="prior counterfactual json whose (rep, orig) 8-char pairs are re-settled under the corrected rule")
a = ap.parse_args(); F, OUT = a.raw, a.out; os.makedirs(OUT, exist_ok=True)
rows = {}
for fp in glob.glob(f"{F}/measurements/*.json"):
    m = json.load(open(fp)); rows[m["manifest_hash"]] = m
props = {}
for fp in glob.glob(f"{F}/proposals/*.json"):
    p = json.load(open(fp)); props[p["slug"]] = p
pop = json.load(open(f"{F}/population.json"))
print("rows", len(rows), "props", len(props), "pop", {k: pop.get(k) for k in ("computed_at", "measurements", "proposals", "digest_newline")}, flush=True)
def g(d, *ks):
    for k in ks: d = d.get(k) if isinstance(d, dict) else None
    return d
# 1. applicability predicate
ident = [h for h, m in rows.items() if "settlement_analysis" in (m.get("manifest") or {})]
ident_v1 = [h for h in ident if rows[h]["manifest"].get("settlement_analysis") == IDENTITY]
keyed = [(s, pre) for s, p in props.items() for pre in ((p.get("evidence_contract") or {}).get("prerequisites") or []) if isinstance(pre, dict) and "bound_reading" in pre]
# 2. classes
reps = [m for m in rows.values() if m.get("is_replication")]
interval_pairs = [m for m in reps if g(m, "replication_comparison", "rule_applied") == "interval-overlap-commensurable-v1"]
strat_pairs = [m for m in reps if isinstance(g(m, "replication_comparison", "strata"), list) and g(m, "replication_comparison", "strata")]
cell_failed = [m for m in strat_pairs if g(m, "replication_comparison", "aggregate_reproduced_ok") is True and m.get("reproduced_ok") is False]
cell_pass = [m for m in strat_pairs if m.get("reproduced_ok") is True]
legacy_strata_pairs = [m for m in strat_pairs if g(m, "replication_comparison", "rule_applied") != "interval-overlap-commensurable-v1"]
attested = [m for m in rows.values() if m.get("interval_provenance_attestation")]
attested_strat = [m for m in attested if (m.get("manifest") or {}).get("settlement_strata")]
with_filer_bounds = [m for m in rows.values() if any(isinstance(s, dict) and (s.get("value_lo") is not None) for s in (m.get("stratum_results") or []))]
cad_atleast = [(s, pre) for s, p in props.items() for pre in ((p.get("evidence_contract") or {}).get("prerequisites") or []) if isinstance(pre, dict) and pre.get("metric") == "comprehension_accuracy_delta" and "at_least" in pre]
interval_strat = [m for m in strat_pairs if g(m, "replication_comparison", "rule_applied") == "interval-overlap-commensurable-v1"]
classes = {"interval_rule_pairs": len(interval_pairs), "stratified_pairs_any_rule": len(strat_pairs), "interval_rule_stratified_pairs": len(interval_strat), "cell_failed_pairs": len(cell_failed), "cell_pass_pairs": len(cell_pass),
  "legacy_strata_pairs": len(legacy_strata_pairs), "attested_rows": len(attested), "attested_stratified_rows": len(attested_strat), "rows_with_filer_stratum_bounds": len(with_filer_bounds),
  "legacy_cad_at_least_contracts": len(cad_atleast), "cad_at_least_list": cad_atleast}
print(json.dumps(classes, indent=1, default=str)[:1200], flush=True)
# 3. width replay over every attested row (positive control on all; strata where present)
widths = {}; control_fail = []; t0 = time.time(); CACHE = f"{OUT}/widths.json"
todo = attested
if os.path.exists(CACHE) and os.environ.get("REUSE_WIDTHS") == "1":
    widths = json.load(open(CACHE)); control_fail = [h for h, w in widths.items() if not w["pooled_match"]]; todo = [m for m in attested if m["manifest_hash"] not in widths]
    print("reusing cached widths for", len(widths), "rows; replaying", len(todo), "new", flush=True)
for i, m in enumerate(todo):
    r = check_row(m)
    if not (r["pooled_match"] and r["accepted_match"]): control_fail.append(r["hash"])
    widths[m["manifest_hash"]] = {"pooled_match": r["pooled_match"], "accepted_match": r["accepted_match"], "accepted": r["accepted"], "pooled": r["replayed"], "served_pooled": r["served"], "strata": r["strata"],
        "n_items": len(m["interval_provenance_attestation"]["items"]), "arms_by_stratum": {s["id"]: s.get("arms") for s in (m.get("stratum_results") or [])}}
    if i % 20 == 0: print("replayed", i, "of", len(todo), f"{time.time()-t0:.0f}s", flush=True)
print("positive control failures:", control_fail, flush=True)
json.dump(widths, open(CACHE, "w"), indent=1, sort_keys=True)
wv = [s["width"] for w in widths.values() if w["strata"] for s in w["strata"].values()]
per_items = {}
for h, w in widths.items():
    if not w["strata"]: continue
    n_by = Counter(it["stratum"] for it in rows[h]["interval_provenance_attestation"]["items"])
    for sid, s in w["strata"].items(): per_items.setdefault(n_by[sid], []).append(s["width"])
summary = {"attested_rows_replayed": len(widths), "positive_control_failures": control_fail, "stratum_intervals": len(wv), "width_median": statistics.median(wv) if wv else None,
  "width_q1": statistics.quantiles(wv, n=4)[0] if len(wv) > 3 else None, "width_q3": statistics.quantiles(wv, n=4)[2] if len(wv) > 3 else None,
  "width_min": min(wv) if wv else None, "width_max": max(wv) if wv else None, "zero_width": sum(1 for x in wv if x == 0),
  "by_items_per_stratum": {str(k): {"n": len(v), "median_width": statistics.median(v)} for k, v in sorted(per_items.items())}}
print(json.dumps(summary, indent=1), flush=True)
# 4. counterfactual-if-opted, settled by reference.settle_pair (the SAME function the fixtures use)
def row_for(m, w):
    arms = w["arms_by_stratum"]
    return {"manifest": {"settlement_analysis": IDENTITY}, "value": m["value"], "value_lo": w["pooled"][0], "value_hi": w["pooled"][1], "strata": [{"id": k, "value_lo": v["lo"], "value_hi": v["hi"], "value": None, "arms": arms.get(k) or {}} for k, v in w["strata"].items()]}
def settle(m, o):
    wo, wr = widths.get(o["manifest_hash"]), widths.get(m["manifest_hash"])
    base = {"rep": m["manifest_hash"][:8], "orig": o["manifest_hash"][:8], "rep_hash": m["manifest_hash"], "orig_hash": o["manifest_hash"],
            "current_reproduced_ok": m.get("reproduced_ok"), "current_aggregate": g(m, "replication_comparison", "aggregate_reproduced_ok"), "current_rule": g(m, "replication_comparison", "rule_applied")}
    if not (wo and wr and wo["strata"] and wr["strata"]):
        return base | {"counterfactual": "hold_missing_bounds", "failing_stratum": None, "degenerate_arm_present": None}
    ro, rr = row_for(o, wo), row_for(m, wr)
    if set(s["id"] for s in ro["strata"]) != set(s["id"] for s in rr["strata"]):
        return base | {"counterfactual": "hold_missing_bounds", "failing_stratum": None, "degenerate_arm_present": None}
    branch, res = settle_pair(ro, rr); assert branch == "new_branch"
    verdict = "agree" if res["reproduced_ok"] is True else ("oppose" if res["reproduced_ok"] is False else "hold_missing_bounds")
    deg = any(degenerate(s) for s in ro["strata"] + rr["strata"])
    return base | {"counterfactual": verdict, "failing_stratum": res.get("failing_stratum"), "degenerate_arm_present": deg,
                   "pooled": {"orig": list(wo["pooled"]), "rep": list(wr["pooled"])},
                   "strata": {s["id"]: {"orig": [s["value_lo"], s["value_hi"]], "rep": [t["value_lo"], t["value_hi"]]} for s in ro["strata"] for t in rr["strata"] if t["id"] == s["id"]}}
cf = []
for m in interval_strat:
    o = rows.get(m.get("replicates_hash"))
    if o: cf.append(settle(m, o))
cf.sort(key=lambda x: (x["rep"], x["orig"]))
counts = Counter(x["counterfactual"] for x in cf)
cf_failed = [x for x in cf if x["current_aggregate"] is True and x["current_reproduced_ok"] is False]
counts_failed = Counter(x["counterfactual"] for x in cf_failed)
deg_agree = sum(1 for x in cf if x["counterfactual"] == "agree" and x["degenerate_arm_present"])
print("counterfactual-if-opted:", dict(counts), "| among currently cell-failed:", dict(counts_failed), "| agreements resting on a degenerate arm:", deg_agree, flush=True)
json.dump(cf, open(f"{OUT}/counterfactual.json", "w"), indent=1, sort_keys=True)
prior = None
if a.pairs:
    old = json.load(open(a.pairs)); by8 = {(m["manifest_hash"][:8]): m for m in rows.values()}
    re_ = []
    for x in old:
        if "failing_strata" not in x and x.get("counterfactual") == "hold_missing_bounds" and x.get("rep") not in by8: continue
        m, o = by8.get(x["rep"]), by8.get(x["orig"])
        if not (m and o): re_.append({"rep": x["rep"], "orig": x["orig"], "counterfactual": "row_absent_from_snapshot", "prior": x["counterfactual"]}); continue
        r = settle(m, o); r["prior"] = x["counterfactual"]; re_.append(r)
    prior = {"source": os.path.basename(a.pairs), "pairs": len(re_), "corrected": dict(Counter(r["counterfactual"] for r in re_)), "prior": dict(Counter(r["prior"] for r in re_)),
             "transitions": dict(Counter(f'{r["prior"]} -> {r["counterfactual"]}' for r in re_))}
    json.dump(re_, open(f"{OUT}/counterfactual_prior_pairs.json", "w"), indent=1, sort_keys=True)
    print("prior pair list re-settled:", json.dumps(prior), flush=True)
named = {}
for tag, rp, op in (("verified-how", "aa145cee", "4a928d0d"), ("moved-earlier-placebo", "69b82d4a", "82b711bc"), ("pooled-witness-among-others", "895db45a", "fb5835e0")):
    hit = [x for x in cf if x["rep"] == rp and x["orig"] == op]
    named[tag] = hit[0] if hit else {"rep": rp, "orig": op, "counterfactual": "pair_not_in_interval_stratified_class"}
# 5. uvf projection: surfaces before; branch selection set S; after == before iff S empty and no keyed contract
surfaces = {}
for h, m in rows.items():
    surfaces[f"m:{h}"] = {k: m.get(k) for k in ("reproduced_ok", "confirmed", "settlement_state", "settlement_eligible", "evidence_state", "counts_toward_verdict", "resolution_bound")}
    surfaces[f"m:{h}:agg"] = g(m, "replication_comparison", "aggregate_reproduced_ok")
for s, p in props.items():
    surfaces[f"p:{s}"] = {"stage": p.get("stage"), "assessment": g(p, "verdict", "assessment"), "readiness_satisfied": g(p, "evidence_readiness", "satisfied"), "readiness_missing": g(p, "evidence_readiness", "missing_evidence"),
        "readiness_opposing": g(p, "evidence_readiness", "opposing_evidence"), "readiness_unresolved": g(p, "evidence_readiness", "unresolved_evidence"), "ballot_ready": g(p, "ratification", "readiness", "ready"), "verdict_class": p.get("verdict_class")}
canon = json.dumps(surfaces, sort_keys=True, separators=(",", ":"), default=str); sd = hashlib.sha256(canon.encode()).hexdigest()
S = [m["manifest_hash"] for m in reps if rows.get(m.get("replicates_hash")) and (m.get("manifest") or {}).get("settlement_analysis") == IDENTITY and (rows[m["replicates_hash"]].get("manifest") or {}).get("settlement_analysis") == IDENTITY]
uvf = {"population_digest_newline": pop["digest_newline"], "computed_at": pop["computed_at"], "measurements": len(rows), "proposals": len(props),
  "verdict_surfaces_counted": len(surfaces), "surfaces_before_sha256": sd, "branch_selected_pairs": S, "keyed_contracts": keyed,
  "surfaces_after_sha256": sd if not S and not keyed else None, "unclaimed_verdict_flips_projection": 0 if not S and not keyed else None,
  "note": "Applicability projection only: the proposed branch runs for pairs whose BOTH manifests declare settlement_analysis: attested-strata-v1 and the keyed reading for contracts carrying bound_reading. Both selection sets are empty on this snapshot, so the branch predicate selects nothing; this is not a run of candidate code and does not by itself prove a not-yet-written implementation has no side effects."}
json.dump({"population": pop, "classes": classes, "applicability": {"settlement_analysis_manifests": len(ident), "attested_strata_v1_manifests": len(ident_v1), "bound_reading_contracts": len(keyed)},
           "width_summary": summary, "counterfactual": {"rule": "reference.settle_pair pooled-then-strata: replayed pooled attested intervals intersect, then every aligned stratum's replayed intervals intersect; missing bounds hold; no degenerate hold at pair level",
           "pooled_failures": sum(1 for x in cf if x.get("failing_stratum") == "pooled"), "pairs": len(cf), "counts": dict(counts),
           "cell_failed_subset": {"pairs": len(cf_failed), "counts": dict(counts_failed)}, "agreements_with_degenerate_arm_present": deg_agree, "named_pairs": named, "prior_pair_list": prior}, "uvf": uvf},
          open(f"{OUT}/census.json", "w"), indent=1, default=str, sort_keys=True)
json.dump(surfaces, open(f"{OUT}/surfaces_before.json", "w"), sort_keys=True, indent=0, default=str)
print("named:", json.dumps({k: {kk: v.get(kk) for kk in ("counterfactual", "failing_stratum", "degenerate_arm_present", "current_reproduced_ok", "current_aggregate")} for k, v in named.items()}), flush=True)
print("CENSUS_DONE", flush=True)
