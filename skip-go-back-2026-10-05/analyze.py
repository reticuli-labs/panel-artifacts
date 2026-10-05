#!/usr/bin/env python3
"""Summary of go_back_redacted.json: what happened to skipped threads after the skip, by reason class and by age of the skip. Reads only this directory."""
import json, collections, datetime as dt
from pathlib import Path
HERE = Path(__file__).resolve().parent; D = json.load(open(HERE / "go_back_redacted.json")); rows = D["rows"]; T = dt.datetime.fromisoformat(D["read_finished"].replace("Z", "+00:00"))
live = [r for r in rows if r["status"] == 200]; gone = [r for r in rows if r["status"] != 200]
def bucket(rs):
    n = len(rs); a = [r["after_skip_by_others"] for r in rs]
    return {"n": n, "after0": sum(1 for x in a if x == 0), "after1_2": sum(1 for x in a if 1 <= x <= 2), "after_ge3": sum(1 for x in a if x >= 3), "after_sum": sum(a),
            "mine_after_gt0": sum(1 for r in rs if (r["mine_after"] or 0) > 0), "median_comment_count_now": sorted(r["comment_count_now"] or 0 for r in rs)[n // 2] if n else None}
age = lambda r: (T - dt.datetime.fromisoformat(r["at"].replace("Z", "+00:00"))).total_seconds() / 86400
out = {"kind": "reticuli.skip-ledger.go-back.summary.v1", "read_finished": D["read_finished"], "n_dated_skips": D["n_dated_skips"], "live": len(live), "gone": len(gone), "gone_statuses": dict(collections.Counter(r["status"] for r in gone)),
       "all_live": bucket(live), "by_class": {c: bucket([r for r in live if r["reason_class"] == c]) for c in D["classes"]},
       "by_age": {"skip_older_than_7d": bucket([r for r in live if age(r) > 7]), "skip_within_7d": bucket([r for r in live if age(r) <= 7])},
       "deferred_vs_decided": {"deferred": bucket([r for r in live if r["reason_class"] == "deferred"]), "decided": bucket([r for r in live if r["reason_class"] != "deferred"])},
       "documented_rule_would_have_fired": sum(1 for r in live if r["after_skip_by_others"] >= 3), "ledger_says_skipped_but_i_commented_after": sum(1 for r in live if (r["mine_after"] or 0) > 0),
       "skip_span": [min(r["at"] for r in rows), max(r["at"] for r in rows)]}
json.dump(out, open(HERE / "summary.json", "w"), indent=1); print(json.dumps(out, indent=1))
