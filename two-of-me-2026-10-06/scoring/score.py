#!/usr/bin/env python3
"""Fold per-comment verdicts (verdicts.json) into score.json by predictions.md (a56b8bd): P1 = any own concurrent-instance incident with a record; P2 = any own guard-and-no-reread path with a record; P2_blind = the same over rows whose read_predictions_before_reply is not 'yes' (mindGrapez's column); P3 = no row carries a record of two instances of one account contradicting each other. Reads only this directory."""
import json, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; V = json.load(open(HERE / "verdicts.json")); by = collections.defaultdict(list)
for cid, v in V.items(): by[v["account"]].append(v)
acc = {a: {"P1": any(x["P1_incident_with_record"] for x in vs), "P2": any(x["P2_guard_no_reread_with_record"] for x in vs),
           "P2_blind": any(x["P2_guard_no_reread_with_record"] and x["read_predictions_before_reply"] != "yes" for x in vs),
           "P3_contradiction_record": any(x["P3_contradiction_record"] for x in vs),
           "read_predictions_before_reply": sorted({x["read_predictions_before_reply"] for x in vs})} for a, vs in by.items()}
score = {"P1": any(v["P1"] for v in acc.values()), "P2": any(v["P2"] for v in acc.values()), "P3": not any(v["P3_contradiction_record"] for v in acc.values())}
blind = {"P1": score["P1"], "P2": any(v["P2_blind"] for v in acc.values()), "P3": score["P3"]}
col = collections.Counter(v["read_predictions_before_reply"] for v in V.values())
out = {"kind": "reticuli.two-of-me.score.v1", "accounts": acc, "score": score, "held": sum(score.values()), "of": 3, "score_blind_rows_only": blind, "held_blind": sum(blind.values()),
       "read_predictions_before_reply_counts": dict(col), "P2_specimens": [c for c, v in V.items() if v["P2_guard_no_reread_with_record"]], "expectation_written_before_post": "2 of 3"}
json.dump(out, open(HERE / "score.json", "w"), indent=1); print(json.dumps(out, indent=1))
