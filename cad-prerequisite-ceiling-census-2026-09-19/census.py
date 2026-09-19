#!/usr/bin/env python3
"""Census of comprehension_accuracy_delta (CAD) as a PREREQUISITE vs as the CLAIM CARRIER, against the
resolution bound of the CAD rows meant to satisfy it. Read-only over the public register via the SDK
(iter_proposals carries the completeness guard). Every proposal, no pre-filter."""
import json, collections, datetime
from ainglish.client import AinglishClient
c = AinglishClient()
out = {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "proposals": []}
for p in c.iter_proposals():
    full = c.proposal(p["slug"])
    ec = full.get("evidence_contract") or {}
    carrier = ec.get("claim_carrier") or []
    carrier_metrics = [x if isinstance(x, str) else x.get("metric") for x in carrier]
    prereq = [(x if isinstance(x, dict) else {"metric": x}) for x in (ec.get("prerequisites") or [])
              if (x.get("metric") if isinstance(x, dict) else x) == "comprehension_accuracy_delta"]
    cad_rows = [m for m in (full.get("measurements") or []) if m.get("metric") == "comprehension_accuracy_delta"]
    rows = [{"hash": (m.get("manifest_hash") or "")[:12], "value": m.get("value"), "lo": m.get("value_lo"), "hi": m.get("value_hi"),
             "rb": m.get("resolution_bound"), "repl": bool(m.get("is_replication")), "state": m.get("settlement_state"),
             "counts": m.get("counts_toward_verdict"), "evidence_state": m.get("evidence_state"), "arms": m.get("arms")} for m in cad_rows]
    out["proposals"].append({"slug": full["slug"], "public_id": full.get("public_id"), "stage": full.get("stage"), "kind": full.get("kind"),
        "declared": bool(ec), "cad_is_carrier": "comprehension_accuracy_delta" in carrier_metrics,
        "cad_prerequisite": prereq[0] if prereq else None, "cad_rows": rows,
        "readiness": {k: (full.get("evidence_readiness") or {}).get(k) for k in ("evidence_ready", "satisfied", "missing_evidence", "unresolved_evidence", "opposing_evidence")}})
P = out["proposals"]
def summary(sel, label):
    props = [p for p in P if sel(p)]
    rows = [r for p in props for r in p["cad_rows"]]
    active = [r for r in rows if r["evidence_state"] in (None, "valid") and r["state"] not in ("retracted_by_submitter", "voided_by_submitter")]
    rb = collections.Counter(r["rb"] for r in active)
    orig = [r for r in active if not r["repl"]]
    rb_orig = collections.Counter(r["rb"] for r in orig)
    sat = [p for p in props if "comprehension_accuracy_delta" in ((p["readiness"].get("satisfied") or []))]
    unres = [p for p in props if "comprehension_accuracy_delta" in ((p["readiness"].get("unresolved_evidence") or []))]
    return {"label": label, "proposals": len(props), "with_any_cad_row": sum(1 for p in props if p["cad_rows"]),
            "active_cad_rows": len(active), "active_originals": len(orig), "rb_all_active": dict(rb), "rb_originals": dict(rb_orig),
            "readiness_cad_satisfied": len(sat), "readiness_cad_unresolved": len(unres), "slugs_satisfied": [p["slug"] for p in sat]}
out["summary"] = {
    "declared_contracts": sum(1 for p in P if p["declared"]),
    "prereq_at_least": summary(lambda p: p["cad_prerequisite"] is not None and "at_least" in p["cad_prerequisite"], "CAD prerequisite with at_least"),
    "prereq_any": summary(lambda p: p["cad_prerequisite"] is not None, "CAD prerequisite (any bound)"),
    "carrier": summary(lambda p: p["cad_is_carrier"], "CAD as claim carrier"),
    "thresholds": dict(collections.Counter(json.dumps(p["cad_prerequisite"].get("at_least", p["cad_prerequisite"].get("at_most"))) for p in P if p["cad_prerequisite"])),
    "all_active_cad_rows_rb": dict(collections.Counter(r["rb"] for p in P for r in p["cad_rows"] if r["evidence_state"] in (None, "valid") and r["state"] not in ("retracted_by_submitter", "voided_by_submitter"))),
}
json.dump(out, open(__file__.rsplit("/", 1)[0] + "/census.json", "w"), indent=1)
print(json.dumps(out["summary"], indent=1))
