#!/usr/bin/env python3
"""Post-deploy original for screen-coherence (my own filing; disjoint confirmation comes later).

The rename shipped; live state is the POST-state. From outside, the checkable claims are:
  F1  no corruption surface still serves the retired key (silent_single_edit on neighbours,
      has_silent_single_edit on corruption blocks);
  F2  every neighbour's within_one_edit VALUE equals the derivable truth (edit_distance <= 1) —
      the rename claimed identical values, and the value is recomputable from served data;
  F3  every corruption block's has_within_one_edit equals any(neighbour.within_one_edit);
  F4  CONTROL: every slot_crossproduct block still serves has_silent_single_edit (the load-
      bearing gate keeps its name and its flag).
value = count of violations across F1-F4 (each violating row/block counts once).
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
        det = p.get("deterministic") or {}
        keep = {}
        oec = det.get("one_edit_corruption")
        if isinstance(oec, dict):
            keep["one_edit_corruption"] = {
                "keys": sorted(oec.keys()),
                "has_within_one_edit": oec.get("has_within_one_edit"),
                "neighbours": [{"keys": sorted(n.keys()),
                                "edit_distance": n.get("edit_distance"),
                                "within_one_edit": n.get("within_one_edit"),
                                "silent_single_edit": n.get("silent_single_edit", "__absent__")}
                               for n in (oec.get("neighbours") or [])],
            }
        sxp = det.get("slot_crossproduct")
        if isinstance(sxp, dict):
            keep["slot_crossproduct"] = {"keys": sorted(sxp.keys()),
                                         "has_silent_single_edit": sxp.get("has_silent_single_edit", "__absent__")}
        rows.append({"slug": slug, "stage": p.get("stage"),
                     "publication_status": p.get("publication_status"), "det": keep})
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{total}", file=sys.stderr)
    snap = {"kind": "reticuli.screen_coherence_snapshot.v1",
            "taken_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "proposal_records": len(rows), "rows": rows}
    blob = json.dumps(snap, sort_keys=True, separators=(",", ":")).encode()
    open(f"{S}/screen_coherence_snapshot.json", "wb").write(blob)
    print(json.dumps({"snapshot_sha256": hashlib.sha256(blob).hexdigest(),
                      "proposal_records": len(rows), "taken_at": snap["taken_at"]}))
    sys.exit(0)

blob = open(f"{S}/screen_coherence_snapshot.json", "rb").read()
snap_sha = hashlib.sha256(blob).hexdigest()
rows = [r for r in json.loads(blob)["rows"] if r["publication_status"] == "visible"]

flips = []
n_neighbours = n_blocks = n_controls = 0
for r in rows:
    oec = r["det"].get("one_edit_corruption")
    if oec:
        n_blocks += 1
        if "has_silent_single_edit" in oec["keys"]:
            flips.append({"slug": r["slug"], "check": "F1-block-retired-key"})
        derived_any = False
        for n in oec["neighbours"]:
            n_neighbours += 1
            if n["silent_single_edit"] != "__absent__":
                flips.append({"slug": r["slug"], "check": "F1-neighbour-retired-key"})
            truth = (n["edit_distance"] is not None and n["edit_distance"] <= 1)
            if bool(n["within_one_edit"]) != truth:
                flips.append({"slug": r["slug"], "check": "F2-value",
                              "edit_distance": n["edit_distance"], "served": n["within_one_edit"]})
            derived_any = derived_any or truth
        if bool(oec["has_within_one_edit"]) != derived_any:
            flips.append({"slug": r["slug"], "check": "F3-aggregate",
                          "served": oec["has_within_one_edit"], "derived": derived_any})
    sxp = r["det"].get("slot_crossproduct")
    if sxp:
        n_controls += 1
        if sxp["has_silent_single_edit"] == "__absent__":
            flips.append({"slug": r["slug"], "check": "F4-control-lost-flag"})

result = {
    "kind": "reticuli.screen_coherence_sweep.v1",
    "snapshot_sha256": snap_sha,
    "value_unclaimed_verdict_flips": len(flips),
    "flips": flips,
    "table": {
        "live_proposals": len(rows),
        "corruption_blocks": n_blocks,
        "corruption_neighbour_rows": n_neighbours,
        "slot_crossproduct_controls": n_controls,
        "filing_time_eligible": {"neighbour_rows": 73, "blocks": 23, "controls": 11},
    },
}
out = json.dumps(result, indent=1, sort_keys=True)
open(f"{S}/screen_coherence_result.json", "w").write(out)
print(out)
