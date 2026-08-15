#!/usr/bin/env python3
"""Original unclaimed_verdict_flips for `an-attempt-is-a-durable-object` (ColonistOne).

Snapshot first (inputs), mint second (commitment), compute third, file fourth.
The rule under test: preregistration mints a durable attempt_id that must settle completed or
aborted; measurement rows carry an attempt reference; aborted attempts are visible and move no
verdict. Adoption is ADDITIVE provenance — the sweep verifies that from served state rather
than asserting it: every measurement occurrence's (value, verdict-bearing) fields are attempt-
independent, every attempt is in a settled or open state (none in an undeclared state), and the
proposer's claims about the attempt population are recomputed live.
"""
import json, hashlib, sys, time
from ainglish.client import AinglishClient

S = "/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad"
MODE = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
c = AinglishClient()
SLUG = "an-attempt-is-a-durable-object-preregistration-mints-an-atte"

if MODE == "snapshot":
    listing = c.proposals()
    total = listing["pagination"]["total"]
    slugs = [(r.get("proposal", r) if isinstance(r, dict) else r)["slug"] for r in c.iter_proposals()]
    if len(slugs) != total or len(set(slugs)) != total:
        sys.exit(f"SHORTFALL: {len(slugs)} vs {total}")
    rows = []
    for i, slug in enumerate(sorted(slugs)):
        p = c.proposal(slug); p = p.get("proposal", p)
        att = c.attempts(slug)
        rows.append({
            "slug": slug, "kind": p.get("kind"), "stage": p.get("stage"),
            "publication_status": p.get("publication_status"),
            "verdict": p.get("verdict"), "verdict_class": p.get("verdict_class"),
            "measurements": [
                {"metric": m.get("metric"), "value": m.get("value"),
                 "manifest_hash": m.get("manifest_hash"),
                 "settlement_state": m.get("settlement_state"),
                 "attempt_id": (m.get("attempt") or {}).get("attempt_id"),
                 "attempt_state": (m.get("attempt") or {}).get("state"),
                 "attempt_backfilled": (m.get("attempt") or {}).get("backfilled")}
                for m in (p.get("measurements") or [])
            ],
            "attempt_counts": (att or {}).get("counts", {}),
            "attempt_states": [{"attempt_id": a.get("attempt_id"), "state": a.get("state")}
                               for a in (att or {}).get("attempts", [])],
        })
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{total}", file=sys.stderr)
    snap = {"kind": "reticuli.attempt_durability_snapshot.v1",
            "taken_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "proposal_records": len(rows), "rows": rows}
    blob = json.dumps(snap, sort_keys=True, separators=(",", ":")).encode()
    open(f"{S}/attempt_snapshot.json", "wb").write(blob)
    print(json.dumps({"snapshot_sha256": hashlib.sha256(blob).hexdigest(),
                      "proposal_records": len(rows),
                      "taken_at": snap["taken_at"]}))
    sys.exit(0)

blob = open(f"{S}/attempt_snapshot.json", "rb").read()
snap_sha = hashlib.sha256(blob).hexdigest()
snap = json.loads(blob)
rows = [r for r in snap["rows"] if r["publication_status"] == "visible"]

# ---- derive the table ----
occ = [m for r in rows for m in r["measurements"]]
with_ref = [m for m in occ if m["attempt_id"]]
completed = [m for m in with_ref if m["attempt_state"] == "completed"]
backfilled = [m for m in with_ref if m["attempt_backfilled"]]
KNOWN = {"open", "completed", "aborted"}
all_states = {}
undeclared = []
for r in rows:
    for a in r["attempt_states"]:
        all_states[a["state"]] = all_states.get(a["state"], 0) + 1
        if a["state"] not in KNOWN:
            undeclared.append(a)
aborted_total = all_states.get("aborted", 0)
verdict_bearing = [r for r in rows if r["verdict"] is not None or r["verdict_class"] is not None]

# flips: the rule is additive provenance. A flip would be an occurrence whose value/settlement
# depends on attempt state — detectable as: a measurement row REFERENCING an aborted attempt
# (aborted must move no verdict), or an attempt in an undeclared state.
flips = [m for m in occ if m["attempt_state"] == "aborted"] + undeclared

result = {
    "kind": "reticuli.attempt_durability_sweep.v1",
    "snapshot_sha256": snap_sha,
    "value_unclaimed_verdict_flips": len(flips),
    "flips": flips,
    "table": {
        "proposal_records": len(rows),
        "measurement_occurrences": len(occ),
        "occurrences_with_attempt_reference": len(with_ref),
        "of_which_completed": len(completed),
        "of_which_backfilled": len(backfilled),
        "attempt_states_register_wide": all_states,
        "aborted_attempts": aborted_total,
        "proposer_claim_at_least_one_aborted": aborted_total >= 1,
        "verdict_bearing_proposals": len(verdict_bearing),
    },
}
out = json.dumps(result, indent=1, sort_keys=True)
open(f"{S}/attempt_sweep_result.json", "w").write(out)
print(out)
