"""Saturnia's check (519c16be on ce1aa92c): compare observed with predicted bookings for the ACTUAL event per cohort. Aggregate-only cohort (point-relative-v1): event = aggregate within tolerance, so sum P(A) IS the model expectation. Strata cohort (point-and-strata-relative-v1): event = aggregate AND every stratum; sum P(A) is only an upper bound. Reads analysis.json + all_measurements.json; writes errata_cohorts.json."""
import json, math, statistics
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
D = json.load(open("all_measurements.json")); rows = D["rows"]; o = json.load(open("analysis.json")); T = {x["hash"]: x for x in o["originals_table"]}
reps = [r for r in rows if r.get("metric") == "comprehension_accuracy_delta" and r.get("is_replication")]
co = {"point-relative-v1": [], "point-and-strata-relative-v1": []}
for r in reps:
    c = r.get("replication_comparison") or {}; src = (r.get("replicates_hash") or "")[:12]
    if src in T and c.get("reproduced_ok") is not None: co[c["rule"]].append({"src": src, "ok": bool(c["reproduced_ok"]), "p": T[src]["p_aggregate"], "p2": T[src]["p_aggregate_sqrt2"], "n_strata": len(c.get("strata") or []), "agg_ok": c.get("aggregate_reproduced_ok"), "rep": r["manifest_hash"][:12]})
out = {}
for rule, L in co.items():
    exp1 = sum(x["p"] for x in L); exp2 = sum(x["p2"] for x in L); obs = sum(1 for x in L if x["ok"])
    # Poisson-binomial exact P(X <= obs) under the sd=1 model
    pmf = [1.0]
    for x in L:
        p = x["p"]; pmf = [a * (1 - p) + (pmf[i - 1] * p if i else 0) for i, a in enumerate(pmf + [0.0])]
    tail = sum(pmf[:obs + 1])
    agg_ok_n = sum(1 for x in L if x["agg_ok"] is True); agg_ok_known = sum(1 for x in L if x["agg_ok"] is not None)
    out[rule] = {"comparisons": len(L), "distinct_sources": len({x["src"] for x in L}), "observed_booked_agreements": obs, "expected_under_faithful_sd1": round(exp1, 2), "expected_under_faithful_sd_sqrt2": round(exp2, 2), "p_value_obs_or_fewer_sd1_independent": round(tail, 4), "event": ("aggregate only: sum P(A) is the model expectation" if rule == "point-relative-v1" else "aggregate AND every stratum: sum P(A) is an upper bound only"), "aggregate_reproduced_ok_true": agg_ok_n, "aggregate_reproduced_ok_known": agg_ok_known, "strata_counts": sorted({x["n_strata"] for x in L})}
# in the strata cohort, how often did the AGGREGATE alone agree (the field aggregate_reproduced_ok), which is the event my model prices?
json.dump({"cohorts": out, "note": "shared sources: several comparisons target one original, so comparisons are not independent; the p-value treats them as independent and is therefore generous to the extra-variation reading"}, open("errata_cohorts.json", "w"), indent=1)
print(json.dumps(out, indent=1))
