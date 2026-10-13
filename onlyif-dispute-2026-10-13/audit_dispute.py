"""Classify every disputed original in the queue's needs_dispute_settlement section by its eligible replications.
Inputs: queue.json (public GET /api/v1/queue) + rows/<slug>.json (public GET /api/v1/proposals/<slug>), both read at the
queue's generated_at. STRICT = every eligible replication has the original's sign and none is within tolerance."""
import json, glob, sys
q = json.load(open("queue.json")); rows = {}
for f in glob.glob("rows/*.json"):
    d = json.load(open(f)); rows[d["slug"]] = d
def sgn(v): return (v > 0) - (v < 0)
total = 0; by_metric = {}; strict = []; loose = []; no_elig = 0; any_ok = 0; sign_split = 0
for r in q["needs_dispute_settlement"]:
    p = rows[r["slug"]]
    for o in p["measurements"]:
        if o["is_replication"] or o.get("settlement_state") != "disputed" or o.get("retraction"): continue
        rc = next((x for x in (p.get("replication_consensus") or []) if x["original_manifest_hash"] == o["manifest_hash"]), None)
        reps = [x for x in (rc["replications"] if rc else []) if x.get("settlement_eligible")]
        if not reps: no_elig += 1; continue
        total += 1; by_metric[o["metric"]] = by_metric.get(o["metric"], 0) + 1
        ov = o["value"]; none_ok = not any(x.get("reproduced_ok") for x in reps)
        same = sum(sgn(x["value"]) == sgn(ov) for x in reps)
        rec = {"slug": r["slug"], "public_id": p["public_id"], "metric": o["metric"], "original": ov, "original_hash": o["manifest_hash"],
               "tolerance_effective": rc.get("tolerance_effective"), "replications": [x["value"] for x in reps], "same_sign": same, "n": len(reps)}
        if not none_ok: any_ok += 1
        if none_ok and same == len(reps): strict.append(rec)
        if none_ok and same * 2 > len(reps): loose.append(rec)
        if same < len(reps): sign_split += 1
out = {"generated_at": q["generated_at"], "dispute_rows": len(q["needs_dispute_settlement"]), "disputed_originals_with_eligible_replication": total,
       "by_metric": by_metric, "disputed_originals_without_eligible_replication": no_elig, "with_any_reproduced_ok": any_ok,
       "with_a_sign_split": sign_split, "strict_count": len(strict), "loose_count": len(loose), "strict": strict, "loose_slugs": sorted({x["slug"] for x in loose})}
json.dump(out, open("dispute_audit_strict.json", "w"), indent=1)
print({k: v for k, v in out.items() if k not in ("strict", "loose_slugs")})
