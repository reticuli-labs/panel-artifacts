"""Register-wide: for every comprehension original with a served item-bootstrap interval, express the point rule's tolerance max(0.02, 0.1|v|) in units of the original's own sampling sd ((hi-lo)/3.92, normal approx) and derive the probability that a faithful replication (true value = observed, same n) lands inside tolerance on the aggregate: P = 2*Phi(tol/sd) - 1. Where strata carry intervals, multiply in each stratum's P (independence approx) since settlement requires every stratum (required_all). Reads all_measurements.json only. Writes analysis.json."""
import json, math, statistics, collections
D = json.load(open("all_measurements.json")); rows = D["rows"]; read_at = D["read_at"]
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
tol = lambda v: max(0.02, 0.1 * abs(v))
def p_in(v, lo, hi, k=1.0):
    """P(|X - v| <= tol(v)) for X ~ N(v, (k*sd)^2), sd = (hi-lo)/3.92; None if the interval is degenerate or missing"""
    if lo is None or hi is None or hi <= lo: return None
    sd = (hi - lo) / 3.92; return 2 * Phi(tol(v) / (k * sd)) - 1
comp = [r for r in rows if r.get("metric") == "comprehension_accuracy_delta"]
orig = [r for r in comp if not r.get("is_replication")]; reps = [r for r in comp if r.get("is_replication")]
by_hash = {r["manifest_hash"]: r for r in rows}
out = {"read_at": read_at, "rows_total": D.get("full_pull_rows", len(rows)), "comprehension_rows": len(comp), "originals": len(orig), "replications": len(reps), "classes": collections.Counter(), "originals_table": []}
for r in orig:
    v, lo, hi = r.get("value"), r.get("value_lo"), r.get("value_hi"); retracted = bool(r.get("retraction")); ev = r.get("evidence_state")
    if retracted: out["classes"]["retracted"] += 1; continue
    if ev != "valid": out["classes"][f"evidence_state_{ev}"] += 1; continue
    if lo is None or hi is None: out["classes"]["no_interval"] += 1; continue
    if hi <= lo: out["classes"]["degenerate_interval"] += 1; continue
    out["classes"]["usable"] += 1
    sd = (hi - lo) / 3.92; t = tol(v); pa = p_in(v, lo, hi); pa2 = p_in(v, lo, hi, math.sqrt(2))
    strata = r.get("stratum_results") or []; ps = []; s_na = 0
    for s in strata:
        q = p_in(s.get("value"), s.get("value_lo"), s.get("value_hi"))
        if q is None: s_na += 1
        else: ps.append(q)
    p_all = pa * math.prod(ps) if ps else None
    rc = r.get("replication_count"); dc = r.get("disagreement_count"); ip = r.get("interval_provenance") or {}; att = r.get("attempt") or {}
    prop = (att.get("pin") or {}).get("proposal_revision")
    out["originals_table"].append({"hash": r["manifest_hash"][:12], "proposal": prop, "items": ip.get("items"), "readers": ip.get("readers"), "cells": ip.get("cells"), "interval_kind": ip.get("kind"), "submitter": (r.get("submitter") or {}).get("name"), "value": v, "lo": lo, "hi": hi, "sd": round(sd, 3), "tolerance": round(t, 3), "tol_over_sd": round(t / sd, 3), "p_aggregate": round(pa, 4), "p_aggregate_sqrt2": round(pa2, 4), "strata": len(strata), "strata_with_interval": len(ps), "strata_without_interval": s_na, "p_all_strata_and_aggregate": (round(p_all, 6) if p_all is not None else None), "replication_count": rc, "disagreement_count": dc, "settlement_state": r.get("settlement_state"), "resolution_bound": r.get("resolution_bound"), "created": (r.get("at") or "")[:10]})
T = out["originals_table"]; P = [x["p_aggregate"] for x in T]
out["summary"] = {"usable_originals": len(T), "p_aggregate_median": round(statistics.median(P), 4), "p_aggregate_quartiles": [round(q, 4) for q in statistics.quantiles(P, n=4)], "tol_over_sd_median": round(statistics.median([x["tol_over_sd"] for x in T]), 3),
    "p_below_0.05": sum(1 for p in P if p < 0.05), "p_below_0.10": sum(1 for p in P if p < 0.10), "p_below_0.25": sum(1 for p in P if p < 0.25), "p_below_0.50": sum(1 for p in P if p < 0.50), "p_at_least_0.50": sum(1 for p in P if p >= 0.50), "p_at_least_0.90": sum(1 for p in P if p >= 0.90),
    "tol_below_one_sd": sum(1 for x in T if x["tol_over_sd"] < 1), "tol_below_half_sd": sum(1 for x in T if x["tol_over_sd"] < 0.5),
    "with_stratum_intervals": sum(1 for x in T if x["strata_with_interval"] > 0), "p_all_median_where_available": (round(statistics.median([x["p_all_strata_and_aggregate"] for x in T if x["p_all_strata_and_aggregate"] is not None]), 6) if any(x["p_all_strata_and_aggregate"] is not None for x in T) else None),
    "p_all_below_0.05_where_available": sum(1 for x in T if x["p_all_strata_and_aggregate"] is not None and x["p_all_strata_and_aggregate"] < 0.05)}
# booked disagreements against usable originals, from the replication rows' own receipts
usable = {x["hash"] for x in T}; booked = collections.Counter(); booked_by_class = collections.Counter()
for r in reps:
    comp_r = r.get("replication_comparison") or {}; src = (r.get("replicates_hash") or "")[:12]
    if src not in usable or comp_r.get("reproduced_ok") is None: continue
    ok = comp_r.get("reproduced_ok"); booked["agree" if ok else "disagree"] += 1
    p = next(x["p_aggregate"] for x in T if x["hash"] == src); cls = "p<0.10" if p < 0.10 else ("p<0.50" if p < 0.5 else "p>=0.50")
    booked_by_class[(cls, "agree" if ok else "disagree")] += 1
out["booked_against_usable"] = dict(booked); out["booked_by_class"] = {f"{k[0]} {k[1]}": v for k, v in sorted(booked_by_class.items())}
# the settlement_state field as served on usable originals
out["settlement_states_usable"] = dict(collections.Counter(x["settlement_state"] for x in T))
# expected agreements under the faithful model, over the comparisons actually booked, versus observed
exp_sum = 0.0; exp_sum2 = 0.0; n_booked = 0
for r in reps:
    comp_r = r.get("replication_comparison") or {}; src = (r.get("replicates_hash") or "")[:12]
    if src not in usable or comp_r.get("reproduced_ok") is None: continue
    x = next(x for x in T if x["hash"] == src); exp_sum += x["p_aggregate"]; exp_sum2 += x["p_aggregate_sqrt2"]; n_booked += 1
out["model_check"] = {"booked_comparisons": n_booked, "observed_agreements": booked["agree"], "expected_agreements_faithful_sd1": round(exp_sum, 2), "expected_agreements_faithful_sd_sqrt2": round(exp_sum2, 2), "note": "expected = sum over booked comparisons of the source's p_aggregate; the model ignores strata (required_all) so it is an upper bound on booked agreements"}
rules = collections.Counter(); rules_agree = collections.Counter()
for r in reps:
    comp_r = r.get("replication_comparison") or {}; src = (r.get("replicates_hash") or "")[:12]
    if src not in usable or comp_r.get("reproduced_ok") is None: continue
    rules[comp_r.get("rule")] += 1
    if comp_r.get("reproduced_ok"): rules_agree[comp_r.get("rule")] += 1
out["booked_rules"] = dict(rules); out["booked_rules_agree"] = dict(rules_agree); out["booked_by_rule"] = {k: {"agree": rules_agree.get(k, 0), "disagree": v - rules_agree.get(k, 0)} for k, v in rules.items()}
out["summary"]["originals_by_reticuli"] = sum(1 for x in T if x["submitter"] == "Reticuli"); out["summary"]["originals_by_dexagon"] = sum(1 for x in T if x["submitter"] == "Dexagon")
sds = [x["sd"] for x in T]; out["summary"]["sd_median_pp"] = round(statistics.median(sds), 2); out["summary"]["sd_quartiles_pp"] = [round(q, 2) for q in statistics.quantiles(sds, n=4)]
out["summary"]["abs_value_median_pp"] = round(statistics.median(abs(x["value"]) for x in T), 2)
out["summary"]["items_median"] = statistics.median([x["items"] for x in T if x["items"]]); out["summary"]["cells_median"] = statistics.median([x["cells"] for x in T if x["cells"]])
out["summary"]["p_aggregate_sqrt2_median"] = round(statistics.median(x["p_aggregate_sqrt2"] for x in T), 4)
# markdown table
L = ["| original | proposal | submitter | value | 95% interval | sd | tolerance | tol/sd | P(agg within tol) | booked disagreements | state |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for x in sorted(T, key=lambda x: x["p_aggregate"]): L.append(f"| {x['hash']} | {x['proposal'] or ''} | {x['submitter']} | {x['value']:+.3f} | [{x['lo']:+.2f}, {x['hi']:+.2f}] | {x['sd']:.2f} | {x['tolerance']:.3f} | {x['tol_over_sd']:.3f} | {x['p_aggregate']:.3f} | {x['disagreement_count']} | {x['settlement_state']} |")
open("tables.md", "w").write("\n".join(L) + "\n")
# calibration against the exact binomial on 3ce6e06b
cal = next((x for x in T if x["hash"].startswith("3ce6e06b")), None); out["calibration_3ce6e06b"] = {"normal_p_aggregate": cal["p_aggregate"] if cal else None, "exact_binomial_p_aggregate_from_step_tol": 0.3116, "normal_tol_over_sd": cal["tol_over_sd"] if cal else None}
out["classes"] = dict(out["classes"])
json.dump(out, open("analysis.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "originals_table"}, indent=1))
print("\nlowest 12 by p_aggregate:")
for x in sorted(T, key=lambda x: x["p_aggregate"])[:12]: print(f"  {x['hash']} {x['submitter']:>14} v={x['value']:+8.3f} [{x['lo']:+.2f},{x['hi']:+.2f}] tol/sd={x['tol_over_sd']:.3f} p={x['p_aggregate']:.3f} reps={x['replication_count']} dis={x['disagreement_count']} state={x['settlement_state']}")
print("\nhighest 8:")
for x in sorted(T, key=lambda x: -x["p_aggregate"])[:8]: print(f"  {x['hash']} {x['submitter']:>14} v={x['value']:+8.3f} [{x['lo']:+.2f},{x['hi']:+.2f}] tol/sd={x['tol_over_sd']:.3f} p={x['p_aggregate']:.3f} reps={x['replication_count']} dis={x['disagreement_count']} state={x['settlement_state']}")
