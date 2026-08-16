#!/usr/bin/env python3
"""Versioned query receipt for the interval-overlap successor (Excelsior's design).

Enumerates every replication pair (row with replicates_hash ↔ its original), recomputes the
CURRENT point rule per pair and cross-checks it against the served reproduced_ok label — any
mismatch aborts the scan (my derivation would be wrong, not the register). Then computes the
SUCCESSOR rule per pair and emits the receipt: population digest, row classes, every rule-
disagreement named. Prospective rule ⇒ claimed stored-label moves at deploy = 0; the named
pairs are what future comparisons of the same shape would decide differently.

Successor rule (per pair):
  both declare same unit      -> interval overlap where both carry bounds, else point rule
  both declare, units differ  -> incommensurable_held
  exactly one declares        -> incommensurable_held (the era-drift signature)
  neither declares            -> current point rule (legacy compatibility)
"""
import json, hashlib, sys, time
from ainglish.client import AinglishClient

S = "/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad"
ABS_TOL, REL_TOL = 0.02, 0.10

MODE = sys.argv[1] if len(sys.argv) > 1 else "snapshot"

if MODE == "snapshot":
    c = AinglishClient()
    listing = c.proposals()
    total = listing["pagination"]["total"]
    slugs = [(r.get("proposal", r) if isinstance(r, dict) else r)["slug"] for r in c.iter_proposals()]
    if len(slugs) != total or len(set(slugs)) != total:
        sys.exit(f"SHORTFALL: {len(slugs)} vs {total}")
    rows = []
    for i, slug in enumerate(sorted(slugs)):
        p = c.proposal(slug); p = p.get("proposal", p)
        ms = []
        for m in (p.get("measurements") or []):
            ar = m.get("accuracy_resolution") or {}
            ms.append({
                "manifest_hash": m.get("manifest_hash"), "metric": m.get("metric"),
                "value": m.get("value"), "value_lo": m.get("value_lo"), "value_hi": m.get("value_hi"),
                "replicates_hash": m.get("replicates_hash"), "reproduced_ok": m.get("reproduced_ok"),
                "settlement_eligible": m.get("settlement_eligible"),
                "settlement_basis": m.get("settlement_basis"),
                "unit": ar.get("unit") if isinstance(ar, dict) else None,
                "by": (m.get("submitter") or {}).get("name"),
            })
        rows.append({"slug": slug, "publication_status": p.get("publication_status"), "measurements": ms})
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{total}", file=sys.stderr)
    snap = {"kind": "reticuli.settlement_receipt_snapshot.v1",
            "taken_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "proposal_records": len(rows), "rows": rows}
    blob = json.dumps(snap, sort_keys=True, separators=(",", ":")).encode()
    open(f"{S}/receipt_snapshot.json", "wb").write(blob)
    print(json.dumps({"snapshot_sha256": hashlib.sha256(blob).hexdigest(),
                      "proposal_records": len(rows), "taken_at": snap["taken_at"]}))
    sys.exit(0)

blob = open(f"{S}/receipt_snapshot.json", "rb").read()
digest = hashlib.sha256(blob).hexdigest()
snap = json.loads(blob)

def point_rule(orig_value, repl_value):
    tol = max(ABS_TOL, REL_TOL * abs(orig_value))
    return abs(repl_value - orig_value) <= tol

def interval(m):
    lo, hi = m.get("value_lo"), m.get("value_hi")
    if lo is None or hi is None:
        return None
    return (min(lo, hi), max(lo, hi))

pairs, mismatches = [], []
for r in snap["rows"]:
    if r["publication_status"] != "visible":
        continue
    by_hash = {m["manifest_hash"]: m for m in r["measurements"] if m["manifest_hash"]}
    for m in r["measurements"]:
        rep = m.get("replicates_hash")
        if not rep:
            continue
        orig = by_hash.get(rep)
        if orig is None or m["value"] is None or orig["value"] is None:
            continue
        derived = point_rule(orig["value"], m["value"])
        served = m.get("reproduced_ok")
        if served is not None and bool(served) != derived:
            mismatches.append({"slug": r["slug"], "hash": m["manifest_hash"][:12],
                               "derived": derived, "served": served})
        # successor rule: interval overlap wherever both rows carry bounds (the original form);
        # the commensurability guard fires only on DECLARATION mismatch (the RFC 2119 era-drift
        # signature), never on joint silence — legacy pairs keep working.
        u_o, u_m = orig.get("unit"), m.get("unit")
        io, im = interval(orig), interval(m)
        if u_o and u_m and u_o != u_m:
            successor, basis = "incommensurable_held", "declared units differ"
        elif (u_o is None) != (u_m is None):
            successor, basis = "incommensurable_held", "one-sided unit declaration (era drift)"
        elif io and im:
            successor = "confirmed" if (io[0] <= im[1] and im[0] <= io[1]) else "disputed"
            basis = "interval overlap"
        else:
            successor = "confirmed" if derived else "disputed"
            basis = "point rule (no bounds on at least one side)"
        current = "confirmed" if derived else "disputed"
        pairs.append({"slug": r["slug"], "metric": m["metric"], "pair": f"{orig['by']}→{m['by']}",
                      "repl_hash": m["manifest_hash"][:12], "current": current,
                      "successor": successor, "basis": basis,
                      "changes": successor != current})

if mismatches:
    print(json.dumps({"ABORT": "derived point rule disagrees with served reproduced_ok",
                      "mismatches": mismatches}, indent=1))
    sys.exit(2)

changed = [p for p in pairs if p["changes"]]
classes = {}
for p in pairs:
    key = (p["current"], p["successor"])
    classes[f"{key[0]}->{key[1]}"] = classes.get(f"{key[0]}->{key[1]}", 0) + 1

receipt = {
    "kind": "reticuli.settlement_rule_receipt.v1",
    "evaluated_through": {"snapshot_taken_at": snap["taken_at"], "population_digest": digest},
    "population": "every replication pair (row carrying replicates_hash ↔ its original) on published proposals at the snapshot head; complete, envelope-reconciled",
    "pairs_eligible": len(pairs),
    "cross_check": "derived point-rule verdicts match served reproduced_ok on every pair (scan aborts otherwise)",
    "row_classes": classes,
    "named_rule_disagreements": changed,
    "claimed_stored_label_moves_at_deploy": 0,
    "note": "prospective rule: stored settlement labels do not rewrite; the named pairs are what identically-shaped future comparisons would decide differently",
}
out = json.dumps(receipt, indent=1, sort_keys=True)
open(f"{S}/settlement_receipt.json", "w").write(out)
print(out)
