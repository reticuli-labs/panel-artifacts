"""Deep Seeker's one-line reader test (5179fc3f): hand the reader its inputs in reversed order and see whether the verdict changes. Applied to Touchstone's public liveness reader (public/liveness-verify.py, a pure reader: no top-level network; imported by path)."""
import importlib.util, json, copy, datetime as dt, sys
SRC = sys.argv[1]  # path to Touchstone public/liveness-verify.py (https://touchstone.cv/liveness-verify.py)
spec = importlib.util.spec_from_file_location("lv", SRC); lv = importlib.util.module_from_spec(spec); spec.loader.exec_module(lv)

VF = ['result', 'contradictions', 'liveness_gaps', 'in_force_from', 'open_class', 'open_gap_seconds', 'open_graded_seconds', 'pre_commitment_windows']
def verdict_fields(r): return {k: r.get(k) for k in VF}
rows = []
for name, feed, now in lv.selftest_cases():
    fwd = lv.evaluate(copy.deepcopy(feed), now=now)
    rev = copy.deepcopy(feed); rev["checkpoints"] = list(reversed(rev["checkpoints"]))
    bwd = lv.evaluate(rev, now=now)
    same = json.dumps(fwd, sort_keys=True, default=str) == json.dumps(bwd, sort_keys=True, default=str); same_verdict = json.dumps(verdict_fields(fwd), sort_keys=True, default=str) == json.dumps(verdict_fields(bwd), sort_keys=True, default=str)
    rows.append({"case": name, "checkpoints": len(feed["checkpoints"]), "verdict": fwd.get("verdict"), "same_reversed": same, "same_verdict_fields": same_verdict})
    print(f"{name:32} n={len(feed['checkpoints'])} verdict={fwd.get('verdict')!s:14} reversed_same={same}")
# the must-fail arm: a reader that took the LAST checkpoint's anchor as in-force would differ on the 'capped' case; show min() is what makes it order-free
multi = [r for r in rows if r["checkpoints"] >= 2]
print("cases", len(rows), "| with >=2 checkpoints", len(multi), "| order-free (full output)", sum(r["same_reversed"] for r in rows), "of", len(rows), "| verdict fields order-free", sum(r["same_verdict_fields"] for r in rows))
json.dump({"cases": rows, "reader": "touchstone public/liveness-verify.py", "verdict_fields": VF, "rule": "chain_order re-sorts on (seq_start, id); in_force = min(committed_at, heartbeat anchors)"}, open("reversed_order_test.json", "w"), indent=1)
