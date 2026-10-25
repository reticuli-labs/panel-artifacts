"""Saturnia 8335d348 part 2 + exact tails: apply the counting filter (evidence_state valid, no retraction, settlement_eligible, counts_toward_verdict) and split by rule_applied; compute Poisson-binomial P(X <= observed) for the literal point event under the faithful one-draw model. Writes errata3_counting.json."""
import json, collections
D = json.load(open("all_measurements.json")); rows = D["rows"]; o = json.load(open("analysis.json")); T = {x["hash"]: x for x in o["originals_table"]}
def pb_tail(ps, obs):
    pmf = [1.0]
    for p in ps: pmf = [a * (1 - p) + (pmf[i - 1] * p if i else 0) for i, a in enumerate(pmf + [0.0])]
    return sum(pmf[:obs + 1])
recs = []
for r in rows:
    if r.get("metric") != "comprehension_accuracy_delta" or not r.get("is_replication"): continue
    c = r.get("replication_comparison") or {}; src = (r.get("replicates_hash") or "")[:12]
    if src not in T or c.get("reproduced_ok") is None: continue
    tol = (c.get("tolerance") or {}).get("effective"); diff = c.get("absolute_difference")
    counting = (r.get("evidence_state") == "valid" and not r.get("retraction") and r.get("settlement_eligible") is True and r.get("counts_toward_verdict") is True)
    recs.append({"rep": r["manifest_hash"][:12], "src": src, "rule": c.get("rule"), "ra": c.get("rule_applied") or "absent", "ok": bool(c["reproduced_ok"]), "agg_ok": c.get("aggregate_reproduced_ok"), "lit": bool(diff is not None and tol is not None and diff <= tol + 1e-9), "p": T[src]["p_aggregate"], "p2": T[src]["p_aggregate_sqrt2"], "counting": counting, "input_disjointness": r.get("input_disjointness")})
out = {"n_all": len(recs), "counting_rows": sum(1 for x in recs if x["counting"])}
def summ(L):
    if not L: return {"n": 0}
    ps = [x["p"] for x in L]; lit = sum(1 for x in L if x["lit"]); ok = sum(1 for x in L if x["ok"])
    return {"n": len(L), "sources": len({x["src"] for x in L}), "booked_ok": ok, "literal_point_pass": lit, "expected_sd1": round(sum(ps), 2), "expected_sqrt2": round(sum(x["p2"] for x in L), 2), "P_literal_le_obs_sd1": round(pb_tail(ps, lit), 5), "P_literal_le_obs_sqrt2": round(pb_tail([x["p2"] for x in L], lit), 5), "aggregate_reproduced_ok_true": sum(1 for x in L if x["agg_ok"] is True)}
for scope_name, scope in (("all_stored", lambda x: True), ("counting_only", lambda x: x["counting"])):
    S = [x for x in recs if scope(x)]; out[scope_name] = {"ALL": summ(S)}
    for rule in ("point-relative-v1", "point-and-strata-relative-v1"): out[scope_name][f"stored {rule}"] = summ([x for x in S if x["rule"] == rule])
    for ra in sorted({x["ra"] for x in S}): out[scope_name][f"rule_applied {ra}"] = summ([x for x in S if x["ra"] == ra])
    out[scope_name]["rule_applied point-or-absent"] = summ([x for x in S if x["ra"] in ("point-relative-v1", "absent")])
json.dump(out, open("errata3_counting.json", "w"), indent=1); print(json.dumps(out, indent=1))
