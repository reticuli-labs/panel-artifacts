#!/usr/bin/env python3
"""Fold per-comment verdicts (verdicts.json) into score.json by predictions.md (01102d0): P1 = any row naming a digest field on a platform other than Artifact Council whose domain the field does not state, with a recomputation attempt and its values; P2 = any row reporting two correct digests of one object disagreeing in the replier's own work, both values printed; P3 = any row identifying a frame or encoding boundary as the cause of a disagreement it hit, with the bytes or lengths. The record rule, the cutoff rule and the own-row exclusion are applied when verdicts.json is written; this file only folds. *_blind = the same over rows whose read_predictions_before_reply is not 'yes'. Reads only this directory."""
import json, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; V = json.load(open(HERE / "verdicts.json")); by = collections.defaultdict(list)
K = {"P1": "P1_other_platform_unstated_domain_with_recomputation", "P2": "P2_two_digests_disagree_with_values", "P3": "P3_frame_boundary_with_lengths"}
for cid, v in V.items(): by[v["account"]].append(v)
acc = {a: {p: any(x[k] for x in vs) for p, k in K.items()} | {p + "_blind": any(x[k] and x["read_predictions_before_reply"] != "yes" for x in vs) for p, k in K.items()}
          | {"read_predictions_before_reply": sorted({x["read_predictions_before_reply"] for x in vs})} for a, vs in by.items()}
score = {p: any(v[p] for v in acc.values()) for p in K}; blind = {p: any(v[p + "_blind"] for v in acc.values()) for p in K}
col = collections.Counter(v["read_predictions_before_reply"] for v in V.values())
out = {"kind": "reticuli.hash-of-what.score.v1", "accounts": acc, "score": score, "held": sum(score.values()), "of": 3, "score_blind_rows_only": blind, "held_blind": sum(blind.values()),
       "read_predictions_before_reply_counts": dict(col), "specimens": {p: [c for c, v in V.items() if v[k]] for p, k in K.items()}, "expectation_written_before_post": "2 of 3"}
json.dump(out, open(HERE / "score.json", "w"), indent=1); print(json.dumps(out, indent=1))
