"""mutants.py --work DIR --out FILE: is selfcheck.py able to fail? Writes altered COPIES of degenerate.py into DIR (one change per
copy; the file beside this script is never touched), runs selfcheck.py against each, and records which line of the selfcheck
refused it. An unaltered copy is run first and must pass. Exit code 0 only when the control passes and every altered copy fails."""
import argparse, json, os, subprocess, sys
ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--work", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); src = open(os.path.join(HERE, "degenerate.py"), encoding="utf-8").read(); os.makedirs(a.work, exist_ok=True)
MUTANTS = [
    ("first_picks_the_last", 'if rule == "first": return 0', 'if rule == "first": return len(options) - 1'),
    ("longest_takes_the_shortest", 'm = max(size) if rule == "longest" else min(size)', 'm = min(size) if rule == "longest" else max(size)'),
    ("a_tie_in_length_picks_the_first", "return size.index(m) if size.count(m) == 1 else None", "return size.index(m)"),
    ("a_tie_in_echo_picks_the_first", "return shared.index(m) if shared.count(m) == 1 else None", "return shared.index(m)"),
    ("echo_compares_without_lower_case", "q = set(WORD.findall(question.lower()))", "q = set(WORD.findall(question))"),
    ("tail_leaves_out_the_observed_score", "dist[right:].sum()", "dist[right + 1:].sum()"),
    ("threshold_not_divided_by_the_tests", "alpha = FAMILY_ALPHA / max(1, len(tests))", "alpha = FAMILY_ALPHA"),
    ("calibration_items_counted", 'real = lambda v: not v.get("calibration") and not v.get("identical_arms")', "real = lambda v: True"),
    ("listed_ceiling_ignores_the_order", 'tuple(v["options"]) if listed else tuple(sorted(v["options"]))', 'tuple(sorted(v["options"]))'),
    ("expected_score_is_zero", "n = len(ks); exp = sum(1.0 / k for k in ks)", "n = len(ks); exp = 0.0"),
    ("fewer_than_ten_items_tested", "MIN_N = 10", "MIN_N = 5"),
    ("right_means_first_position", 'right += v["options"][pos] == v["answer"]', "right += pos == 0"),
    ("an_item_in_two_banks_pooled_twice", "if i not in seen and real(items[i])", "if real(items[i])"),
]


def run(path):
    r = subprocess.run([sys.executable, os.path.join(HERE, "selfcheck.py"), "--module", path], capture_output=True, text=True)
    where = [l.strip() for l in r.stderr.splitlines() if l.strip().startswith("File") and "selfcheck.py" in l]
    return r.returncode, (where[-1].split(", ")[1] if where else ""), (r.stderr.strip().splitlines() or [r.stdout.strip()])[-1][:160]


ctl = os.path.join(a.work, "control_unaltered.py"); open(ctl, "w", encoding="utf-8").write(src); rc, line, last = run(ctl)
out = {"control_unaltered": {"exit": rc, "last_line": last}, "mutants": []}; print("control (unaltered copy): exit %d | %s" % (rc, last))
for name, old, new in MUTANTS:
    assert src.count(old) == 1, (name, src.count(old))
    p = os.path.join(a.work, name + ".py"); open(p, "w", encoding="utf-8").write(src.replace(old, new)); rc, line, last = run(p)
    out["mutants"].append({"name": name, "change": [old, new], "exit": rc, "refused_at": line, "last_line": last}); print("%-38s exit %d | %-9s | %s" % (name, rc, line, last))
ok = out["control_unaltered"]["exit"] == 0 and all(m["exit"] != 0 and m["refused_at"] for m in out["mutants"]); out["all_caught"] = ok
json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False); print("control passes and every altered copy fails:", ok); sys.exit(0 if ok else 1)
