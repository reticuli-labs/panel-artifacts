"""E4 (Saturnia 3d03ead7 on ce1aa92c, 2026-10-28): provenance of the booked receipts that carry no `rule_applied`. Reads the frozen snapshot only.
The code-history witness (the commit that introduced the field, the single comparison function before it, persistence at filing, no recompute) is recorded in ERRATA.md with its hashes; this script checks the part a reader can re-run: the timestamp split and the key set of the unlabelled receipts."""
import json, hashlib, collections
raw = open("all_measurements.json", "rb").read(); D = json.loads(raw); rows = D["rows"]; o = json.load(open("analysis.json")); T = {x["hash"]: x for x in o["originals_table"]}
MERGE = "2026-08-31T13:13:49+00:00"  # merge of PR #370 (commit 4914410f, first with rule_applied), deploy tag 20260831-c; from the repository history, see ERRATA E4
booked = [r for r in rows if r.get("is_replication") and isinstance(r.get("replication_comparison"), dict)]
def c(r): return r["replication_comparison"]
groups = collections.defaultdict(list)
for r in booked: groups[f"{c(r).get('rule')} | {c(r).get('rule_applied')}"].append(r["at"])
absent = sorted(r["at"] for r in booked if c(r).get("rule_applied") is None); present = sorted(r["at"] for r in booked if c(r).get("rule_applied") is not None)
keys_absent = sorted({k for r in booked if c(r).get("rule_applied") is None for k in c(r)})
e3 = [r for r in booked if r.get("metric") == "comprehension_accuracy_delta" and (r.get("replicates_hash") or "")[:12] in T and c(r).get("reproduced_ok") is not None]
out = {"snapshot_sha256": hashlib.sha256(raw).hexdigest(), "rows": len(rows), "booked_replications": len(booked),
       "groups_rule_x_rule_applied": {k: {"n": len(v), "earliest": min(v), "latest": max(v)} for k, v in sorted(groups.items())},
       "unlabelled": {"n": len(absent), "latest": absent[-1]}, "labelled": {"n": len(present), "earliest": present[0]},
       "merge_of_first_commit_with_rule_applied": MERGE, "clean_split_at_merge": absent[-1] < MERGE < present[0],
       "unlabelled_after_merge": sum(1 for t in absent if t > MERGE), "labelled_before_merge": sum(1 for t in present if t < MERGE),
       "keys_of_unlabelled_receipts": keys_absent, "e3_rows": len(e3), "e3_unlabelled": sum(1 for r in e3 if c(r).get("rule_applied") is None)}
assert out["clean_split_at_merge"] and out["unlabelled_after_merge"] == 0 and out["labelled_before_merge"] == 0 and out["e3_rows"] == 135 and out["e3_unlabelled"] == 22
json.dump(out, open("errata4_provenance.json", "w"), indent=1); print(json.dumps(out, indent=1))
