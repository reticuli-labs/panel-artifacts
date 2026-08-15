#!/usr/bin/env python3
"""held-seconds verdict-flip sweep, corrected instrument (v2).

Corrections over v1 (aborted attempt 4a8fee5e):
  1. The cannot-ratify class is the CONJUNCTION the proposer pre-registered: slot null AND
     unscreened. slot-null alone is wrong — the register derives an effective surface from
     form+mapping (RatificationReadiness reads effectiveSlot), so 16 slot-null rows are
     screen-declared and fully determinable.
  2. Population is LIVE rows (stage in proposed/seconded/measured/ratified), per the proposer's
     "recomputes the row_classes table against live rows". Terminal-stage predecessors are
     excluded: surface-only amendments migrate Second records to successors, so terminal rows
     serve a frozen second_weight with an empty seconds list — recomputing their gate
     manufactures false failures out of a data-migration artifact.
  3. Rule reading declared: the filed rule is a WRITE-PATH rule ("the row reaches seconded only
     after an amendment declares the surface"). Adoption does not re-derive existing stages, so
     a flip is a live row whose CURRENT served stage would move on adoption. Rows already at
     seconded that the rule would have held are the grandfathered class — published by name so a
     retroactive-reading replicator can recount without refetching.

Deterministic: reads only the frozen snapshot. A stranger re-runs: fetch the snapshot by its
sha256, run this file, diff the JSON.
"""
import json, hashlib, sys

SNAP = sys.argv[1] if len(sys.argv) > 1 else "register_snapshot.json"
blob = open(SNAP, "rb").read()
snapshot_sha = hashlib.sha256(blob).hexdigest()
rows = json.loads(blob)["rows"]

ACTIVE = {"proposed", "seconded", "measured", "ratified"}

def gate(row):
    secs = row["seconds"]
    weight = sum(s["weight"] for s in secs)
    distinct = len({s["name"] for s in secs})
    return weight >= (row.get("second_threshold") or 3) and distinct >= (row.get("min_seconders") or 2), weight, distinct

word_live, protocol_rows, terminal_word, unpublished = [], 0, 0, 0
for r in rows:
    if r["publication_status"] != "visible":
        unpublished += 1
    elif r["kind"] == "protocol":
        protocol_rows += 1
    elif r["stage"] not in ACTIVE:
        terminal_word += 1
    else:
        word_live.append(r)

held_class, determinable, derived_surface = [], [], []
for r in word_live:
    if not r["slot_declared"] and r["unscreened"]:
        held_class.append(r)
    else:
        determinable.append(r)
        if not r["slot_declared"]:
            derived_surface.append(r["slug"])  # conjunction discipline: slot null but screen-declared

# write-path rule: adoption moves no existing stage -> flips are rows whose CURRENT stage moves
flips = []           # under the filed (write-path) rule: none can, by construction — derived, not asserted
grandfathered = []   # already past 'proposed' though the rule would have held their seconds
for r in held_class:
    passed, w, d = gate(r)
    if r["stage"] != "proposed":
        grandfathered.append({"slug": r["slug"], "stage": r["stage"],
                              "gate_recomputed": passed, "weight": w, "distinct": d})

result = {
    "kind": "reticuli.held_seconds_sweep.v2",
    "snapshot_sha256": snapshot_sha,
    "value_unclaimed_verdict_flips": len(flips),
    "flips": flips,
    "row_classes": {
        "live_word_rows": len(word_live),
        "held_class_eligible": len(held_class),
        "determinable_eligible": len(determinable),
        "of_which_derived_surface": len(derived_surface),
        "terminal_word_rows_excluded": terminal_word,
        "protocol_rows_excluded": protocol_rows,
        "unpublished_excluded": unpublished,
    },
    "zero_meaningful": len(held_class) > 0 and len(determinable) > 0,
    "held_class_rows": [{"slug": r["slug"], "stage": r["stage"]} for r in held_class],
    "grandfathered_under_retroactive_reading": grandfathered,
    "derived_surface_rows": derived_surface,
}
print(json.dumps(result, indent=1, sort_keys=True))
