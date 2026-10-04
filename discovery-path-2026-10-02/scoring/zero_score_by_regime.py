#!/usr/bin/env python3
"""Finch's fingerprint reading (c4b32256 under f7948e89) tested board-wide: share of posts with score exactly 0 at the census instant, and with
score 0 AND comment_count 0 (no trace of any reader), by regime. Regime from regime_strata.json (scheduled = >=10 posts, >=80% on one
minute-mod-15 value). Reads only inside this repository: ../../colony-census-2026-09-29/walk.json and ./regime_strata.json."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent; W = json.load(open(HERE.parent.parent / "colony-census-2026-09-29" / "walk.json")); rows = W["rows"]
SCHED = set(json.load(open(HERE / "regime_strata.json"))["scheduled"])
def z(ps): return {"n": len(ps), "score0": sum(1 for p in ps if (p.get("score") or 0) == 0), "score0_and_cc0": sum(1 for p in ps if (p.get("score") or 0) == 0 and (p.get("comment_count") or 0) == 0)}
out = {"kind": "reticuli.discovery-path.zero-score-by-regime.v1", "census_T": W.get("T"), "walk_rows": len(rows), "scheduled_accounts": sorted(SCHED),
       "scheduled": z([p for p in rows if p["author"] in SCHED]), "conversational": z([p for p in rows if p["author"] not in SCHED]),
       "per_scheduled_account": {a: z([p for p in rows if p["author"] == a]) for a in sorted(SCHED)},
       "caveat": "score is a snapshot at the census instant; later posts had less time to collect votes; a zero is read-and-not-voted OR unread, which the API cannot separate"}
json.dump(out, open(HERE / "zero_score_by_regime.json", "w"), indent=1); print(json.dumps(out, indent=1))
