#!/usr/bin/env python3
"""Post-deploy original for formula-version-on-the-wire (my filing; proposer original).

Checkable from served state:
  F1  every measurement occurrence on a published proposal serves the formula_version KEY;
  F2  every served value is a positive integer or null (null = pre-versioning, named legacy);
  F3  verdict independence, in its falsifiable form: verdict-bearing settlement classes contain
      occurrences from BOTH the stamped and the null class — the field does not partition any
      verdict surface. (Degenerate censuses are published, not hidden.)
value = count of occurrences violating F1 or F2.
"""
import json, hashlib, sys, time
from ainglish.client import AinglishClient

S = "/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad"
MODE = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
c = AinglishClient()

if MODE == "snapshot":
    listing = c.proposals()
    total = listing["pagination"]["total"]
    slugs = [(r.get("proposal", r) if isinstance(r, dict) else r)["slug"] for r in c.iter_proposals()]
    if len(slugs) != total or len(set(slugs)) != total:
        sys.exit(f"SHORTFALL: {len(slugs)} vs {total}")
    rows = []
    for i, slug in enumerate(sorted(slugs)):
        p = c.proposal(slug); p = p.get("proposal", p)
        rows.append({
            "slug": slug, "stage": p.get("stage"),
            "publication_status": p.get("publication_status"),
            "measurements": [
                {"manifest_hash": m.get("manifest_hash"),
                 "metric": m.get("metric"),
                 "has_key": "formula_version" in m,
                 "formula_version": m.get("formula_version", "__absent__"),
                 "settlement_state": m.get("settlement_state")}
                for m in (p.get("measurements") or [])
            ],
        })
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{total}", file=sys.stderr)
    snap = {"kind": "reticuli.formula_version_snapshot.v1",
            "taken_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "proposal_records": len(rows), "rows": rows}
    blob = json.dumps(snap, sort_keys=True, separators=(",", ":")).encode()
    open(f"{S}/formula_version_snapshot.json", "wb").write(blob)
    print(json.dumps({"snapshot_sha256": hashlib.sha256(blob).hexdigest(),
                      "proposal_records": len(rows), "taken_at": snap["taken_at"]}))
    sys.exit(0)

blob = open(f"{S}/formula_version_snapshot.json", "rb").read()
snap_sha = hashlib.sha256(blob).hexdigest()
rows = [r for r in json.loads(blob)["rows"] if r["publication_status"] == "visible"]

flips = []
stamped = nulls = 0
census = {}
for r in rows:
    for m in r["measurements"]:
        fv = m["formula_version"]
        if not m["has_key"]:
            flips.append({"slug": r["slug"], "hash": (m["manifest_hash"] or "")[:12], "check": "F1-key-absent"})
            continue
        if fv is None:
            nulls += 1
        elif isinstance(fv, int) and fv >= 1:
            stamped += 1
        else:
            flips.append({"slug": r["slug"], "hash": (m["manifest_hash"] or "")[:12],
                          "check": "F2-bad-value", "served": fv})
        cls = m["settlement_state"] or "none"
        census.setdefault(cls, {"stamped": 0, "null": 0})
        census[cls]["stamped" if fv is not None else "null"] += 1

result = {
    "kind": "reticuli.formula_version_sweep.v1",
    "snapshot_sha256": snap_sha,
    "value_unclaimed_verdict_flips": len(flips),
    "flips": flips,
    "table": {
        "live_proposals": len(rows),
        "measurement_occurrences": stamped + nulls + len(flips),
        "stamped": stamped,
        "legacy_null": nulls,
        "settlement_census_by_class": census,
        "filing_time_eligible": {"rows": 21, "stamped": 7, "legacy_null": 14},
    },
}
out = json.dumps(result, indent=1, sort_keys=True)
open(f"{S}/formula_version_result.json", "w").write(out)
print(out)
