"""Saturnia 8335d348: the stored `rule` label is not the rule applied. Re-split the 135 booked comparisons by `rule_applied` and `point_effect`, apply the literal point predicate |diff| <= tolerance.effective, and compare observed against the faithful model only where the point rule decided. Reads all_measurements.json + analysis.json; writes errata3_rules.json."""
import json, collections, math
D = json.load(open("all_measurements.json")); rows = D["rows"]; o = json.load(open("analysis.json")); T = {x["hash"]: x for x in o["originals_table"]}
reps = [r for r in rows if r.get("metric") == "comprehension_accuracy_delta" and r.get("is_replication")]
recs = []
for r in reps:
    c = r.get("replication_comparison") or {}; src = (r.get("replicates_hash") or "")[:12]
    if src not in T or c.get("reproduced_ok") is None: continue
    tol = (c.get("tolerance") or {}).get("effective"); diff = c.get("absolute_difference")
    lit = (diff is not None and tol is not None and diff <= tol + 1e-9)
    recs.append({"rep": r["manifest_hash"][:12], "src": src, "rule": c.get("rule"), "rule_applied": c.get("rule_applied"), "point_effect": c.get("point_effect"), "ok": bool(c["reproduced_ok"]), "agg_ok": c.get("aggregate_reproduced_ok"), "literal_point_pass": lit, "diff": diff, "tol": tol, "p": T[src]["p_aggregate"], "keys": sorted(k for k in c.keys())})
print("comparison keys seen:", sorted(set(k for x in recs for k in x["keys"]))[:40])
by = collections.Counter((x["rule"], x["rule_applied"]) for x in recs); print("rule x rule_applied:", dict(by))
pe = collections.Counter((x["rule"], x["point_effect"]) for x in recs); print("rule x point_effect:", dict(pe))
out = {"n": len(recs), "rule_x_rule_applied": {f"{k[0]} | {k[1]}": v for k, v in by.items()}, "rule_x_point_effect": {f"{k[0]} | {k[1]}": v for k, v in pe.items()}, "cohorts": {}}
for label, sel in (("stored rule point-relative-v1", lambda x: x["rule"] == "point-relative-v1"), ("stored rule point-and-strata-relative-v1", lambda x: x["rule"] == "point-and-strata-relative-v1"), ("rule_applied == point (any stored label)", lambda x: (x["rule_applied"] or "").startswith("point")), ("rule_applied absent (not served)", lambda x: x["rule_applied"] is None), ("rule_applied interval-overlap", lambda x: (x["rule_applied"] or "").startswith("interval")), ("point decided: rule_applied point OR absent", lambda x: x["rule_applied"] is None or (x["rule_applied"] or "").startswith("point"))):
    L = [x for x in recs if sel(x)]
    if not L: out["cohorts"][label] = {"n": 0}; continue
    exp = sum(x["p"] for x in L); obs = sum(1 for x in L if x["ok"]); lit = sum(1 for x in L if x["literal_point_pass"]); both = sum(1 for x in L if x["ok"] and x["literal_point_pass"]); agg = sum(1 for x in L if x["agg_ok"] is True)
    out["cohorts"][label] = {"n": len(L), "sources": len({x["src"] for x in L}), "booked_ok": obs, "literal_point_pass": lit, "booked_ok_and_literal_pass": both, "booked_ok_without_literal_pass": obs - both, "aggregate_reproduced_ok_true": agg, "expected_faithful_sd1": round(exp, 2)}
# the literal-point event on ALL 135, against the model (this is the event the model prices, regardless of how the register booked it)
lit_all = sum(1 for x in recs if x["literal_point_pass"]); out["literal_point_event_all_135"] = {"observed_literal_pass": lit_all, "expected_faithful_sd1": round(sum(x["p"] for x in recs), 2), "expected_faithful_sd_sqrt2": round(sum(T[x["src"]]["p_aggregate_sqrt2"] for x in recs), 2)}
ex = [x for x in recs if x["rep"].startswith("110117db")]; out["example_110117db"] = ex[0] if ex else None
json.dump(out, open("errata3_rules.json", "w"), indent=1, default=str); print(json.dumps({k: v for k, v in out.items() if k != "example_110117db"}, indent=1)); print("example:", json.dumps(ex[0], default=str)[:600] if ex else None)
