"""Must-fail arm for reversed_order_test.py: a mutant of the liveness reader that (a) does not re-sort checkpoints and (b) takes the LAST heartbeat anchor as in-force (last-wins) must FAIL the reversed-order test on at least one self-test feed, or the test could not detect what it exists for."""
import sys, json, copy, types
SRC = sys.argv[1]  # path to Touchstone public/liveness-verify.py (https://touchstone.cv/liveness-verify.py)
src = open(SRC, encoding="utf-8").read()
a = 'return sorted(cps, key=lambda c: (c.get("seq_start", 0), c.get("id", "")))'
assert src.count("def chain_order") == 1
import re
m = re.search(r"def chain_order\(cps\):\n(?:    .*\n)+?    return (.+)\n", src); assert m, "chain_order body not found"
orig_return = m.group(0)
mut = src.replace(orig_return, orig_return.rsplit("return", 1)[0] + "return list(cps)\n")
cap = "            if in_force is not None and hb_t < in_force:\n                in_force = hb_t\n"
assert src.count(cap) == 1, src.count(cap)
mut = mut.replace(cap, "            if in_force is not None:\n                in_force = hb_t  # MUTANT: last-wins\n")
assert mut != src
mod = types.ModuleType("lv_mutant"); exec(compile(mut, "lv_mutant", "exec"), mod.__dict__)
import importlib.util
spec = importlib.util.spec_from_file_location("lv", SRC); lv = importlib.util.module_from_spec(spec); spec.loader.exec_module(lv)

VF = ['result', 'contradictions', 'liveness_gaps', 'in_force_from', 'open_class', 'open_gap_seconds', 'open_graded_seconds', 'pre_commitment_windows']
def verdict_fields(r): return {k: r.get(k) for k in VF}
rows = []
for name, feed, now in lv.selftest_cases():
    fwd = mod.evaluate(copy.deepcopy(feed), now=now); rev = copy.deepcopy(feed); rev["checkpoints"] = list(reversed(rev["checkpoints"])); bwd = mod.evaluate(rev, now=now)
    same = json.dumps(fwd, sort_keys=True, default=str) == json.dumps(bwd, sort_keys=True, default=str); same_verdict = json.dumps(verdict_fields(fwd), sort_keys=True, default=str) == json.dumps(verdict_fields(bwd), sort_keys=True, default=str)
    rows.append({"case": name, "same_reversed": same, "same_verdict_fields": same_verdict, "fwd_in_force": fwd.get("in_force_from"), "rev_in_force": bwd.get("in_force_from"), "fwd_contradictions": fwd.get("contradictions"), "rev_contradictions": bwd.get("contradictions")})
    if not same: print(f"MUTANT DIFFERS on {name!r}: in_force {fwd.get('in_force_from')} vs {bwd.get('in_force_from')} | contradictions {fwd.get('contradictions')} vs {bwd.get('contradictions')} | gaps {len(fwd.get('gaps',[]) or [])} vs {len(bwd.get('gaps',[]) or [])}")
diff = [r for r in rows if not r["same_reversed"]]; vdiff = [r for r in rows if not r["same_verdict_fields"]]
print("mutant: full output order-dependent on", len(diff), "of", len(rows), "feeds; VERDICT fields differ on", len(vdiff))
assert vdiff, "the mutant passed the reversed-order test: the test cannot detect last-wins"
json.dump({"mutations": ["chain_order returns the feed as served (no re-sort)", "in_force takes the LAST heartbeat anchor instead of the earliest"], "order_dependent_cases": diff, "verdict_dependent_cases": vdiff, "verdict_fields": VF, "cases": len(rows)}, open("reversed_order_mutant.json", "w"), indent=1)
