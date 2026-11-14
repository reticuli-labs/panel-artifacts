"""Every number in the README, computed from the result files in this directory and written to summary.json. No network.
Needs, beside this directory, the October scan's result (../message-blind-floor-2026-10-12/scan_result.json) for the
measurement-to-bank index and for which banks the October rules had already flagged. Run: python3 summary.py"""
import collections, json, os
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
R = json.load(open("order_sweep.json")); N = json.load(open("order_null.json")); M = json.load(open("my_rows_sweep.json")); A = json.load(open("static_audit.json"))
S = json.load(open("../message-blind-floor-2026-10-12/scan_result.json"))
by = collections.defaultdict(list); octbest = {}
for m in S["measurements"]:
    by[m.get("bank_id")].append(m)
    if m.get("bank_id") and m.get("best") is not None: octbest[m["bank_id"]] = m["best"]
banks = list(R["banks"].values()); sc = [b for b in banks if b["state"] == "scored"]; k3 = [b for b in sc if b["options"] >= 3]
comp = [b for b in k3 if b["best_order"] == b["usable"]]; part = [b for b in k3 if b["best_order"] != b["usable"] and b["best_order_share"] >= 0.6]
meas = collections.Counter(); retracted = 0
for b in comp:
    for m in by.get(b["bank_id"], []): meas[m.get("submitter") or "submitter not served"] += 1; retracted += bool(m.get("retracted"))
mine_new = [e for e in R["extra"] if e.get("label") == "mine, newer"]
out = {"cache_date": "2026-10-12", "banks_indexed": len(banks), "banks_scored": len(sc), "not_scored": dict(collections.Counter(b["state"] for b in banks if b["state"] != "scored")),
       "scored_with_3_or_more_options": len(k3), "complete_order_rule": len(comp), "complete_and_not_flagged_at_90pct_by_the_october_rules": sum(1 for b in comp if octbest.get(b["bank_id"], 0) < 0.9),
       "partial_60_to_under_100pct": len(part), "usable_items_on_complete_banks": {"min": min(b["usable"] for b in comp), "median": sorted(b["usable"] for b in comp)[len(comp) // 2], "max": max(b["usable"] for b in comp)},
       "anchor_of_the_complete_rule": dict(collections.Counter(b["best_order_rule"].split(",")[0].split(" '")[0] for b in comp).most_common()),
       "measurements_on_complete_banks": sum(meas.values()), "of_which_already_retracted": retracted, "measurements_on_complete_banks_by_submitter": dict(meas.most_common()),
       "null": {"banks_shuffled": N["banks_shuffled"], "lost_the_complete_rule": N["banks_shuffled"] - N["still_complete_after_shuffle"], "kept_a_complete_rule": N["still_complete_after_shuffle"],
                "kept_rules": dict(collections.Counter(x["rule"] for x in N["still_complete"])), "best_share_after_shuffle": N["best_share_after_shuffle"], "unshuffled_control_complete": N["unshuffled_control_complete"]},
       "my_rows": {"total": M["total"], **M["counts"], "complete_list": [{"measurement": o["measurement"][:8], "bank": o["bank"][:8], "rule": o["rule"], "hits": o["hits"], "usable": o["usable"], "retracted": o["retracted"]} for o in M["mine"] if o["result"] == "complete"],
                   "my_newer_banks_scored": len(mine_new), "not_scored_why": dict(collections.Counter(o["why"] for o in M["mine"] if o["result"] == "not scored"))},
       "static_audit_636e31d4": {"dexagon_new_old_predictor": A["mine"]["dexagon_rule"], "of": A["mine"]["n"], "control_dexagon_bank": A["control"]["dexagon_rule"], "byte_order_rules": [A["mine"]["rules"]["smallest reference (byte order)"], A["mine"]["rules"]["largest reference (byte order)"]]}}
assert out["complete_order_rule"] == 56 and out["null"]["banks_shuffled"] == 55 and out["my_rows"]["total"] == 57 and out["my_rows"]["complete"] == 13
json.dump(out, open("summary.json", "w"), indent=1); print(json.dumps(out, indent=1))
