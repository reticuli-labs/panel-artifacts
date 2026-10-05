#!/usr/bin/env python3
"""Fold per-comment verdicts (verdicts.json: {comment_id: {"account": ..., "P1_counts": bool, "P1_grew": bool, "P2": bool, "P3": bool,
"P4_fraction_lt_half": true|false|null, "P5": bool, "note": ...}}) into score.json by the rules in rubric.md. Reads only this directory."""
import json, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; V = json.load(open(HERE / "verdicts.json")); by = collections.defaultdict(list)
for cid, v in V.items(): by[v["account"]].append(v)
acc = {a: {"P1": any(x.get("P1_counts") for x in vs) and any(x.get("P1_grew") for x in vs), "P2": any(x.get("P2") for x in vs), "P3": any(x.get("P3") for x in vs),
           "P4": next((x["P4_fraction_lt_half"] for x in vs if x.get("P4_fraction_lt_half") is not None), None), "P5": any(x.get("P5") for x in vs)} for a, vs in by.items()}
p4 = [v["P4"] for v in acc.values() if v["P4"] is not None]
score = {"P1": sum(1 for v in acc.values() if v["P1"]) >= 3, "P2": any(v["P2"] for v in acc.values()), "P3": any(v["P3"] for v in acc.values()),
         "P4": (sum(p4) > len(p4) / 2) if p4 else False, "P5": any(v["P5"] for v in acc.values())}
out = {"kind": "reticuli.skip-go-back.score.v1", "accounts": acc, "P1_count": sum(1 for v in acc.values() if v["P1"]), "P4_n": len(p4), "score": score, "held": sum(score.values()), "of": 5}
json.dump(out, open(HERE / "score.json", "w"), indent=1); print(json.dumps(out, indent=1))
