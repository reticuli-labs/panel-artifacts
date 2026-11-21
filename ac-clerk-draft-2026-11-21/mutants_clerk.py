"""mutants_clerk.py: show that test_clerk.py can fail. For each case: copy this directory into a fresh scratch directory, take ONE
rule out of the copy of clerk.py, run the copy's test, and require that it reports something wrong. First the unchanged copy
must pass. Nothing here is changed. Writes mutants_clerk.json."""
import json, os, shutil, subprocess, sys, tempfile
D = os.path.dirname(os.path.abspath(__file__))
CASES = [
 ("the limit frozen on a proposal is ignored", "    limit = min(x for x in (council[\"settings\"].get(\"SKIPS\"), p.get(\"skipLimit\")) if isinstance(x, int))", "    limit = council[\"settings\"][\"SKIPS\"]"),
 ("a seat is removed only above the limit", "\", and the seat is removed\" if s + 1 >= limit else \"\"", "\", and the seat is removed\" if s + 1 > limit else \"\""),
 ("the record marks removal only above the limit", "\"removed_if_closed\": skips[i] + 1 >= limit}", "\"removed_if_closed\": skips[i] + 1 > limit}"),
 ("a seat that left the council still counts", "    roster = [i for i in p[\"roster\"] if i in seated]; left = [i for i in p[\"roster\"] if i not in seated]", "    roster = list(p[\"roster\"]); left = []; skips = dict({i: 0 for i in roster}, **skips)"),
 ("early resolution at exactly the share", "    return next(n for n in range(roster + 2) if 10000 * n > bps * roster)", "    return next(n for n in range(roster + 2) if 10000 * n >= bps * roster - 9999)"),
 ("a resolved proposal is listed", "            if p.get(\"status\") != \"voting\": continue\n", ""),
 ("the vote that closes first is not put first", "    blocks.sort(); input_set", "    blocks.sort(reverse=True); input_set"),
 ("a changed input is accepted", "assert sha(b) == m[\"sha256\"] and len(b) == m[\"bytes\"], ", "assert True or sha(b) == m[\"sha256\"], "),
 ("a missed vote is not added", "\"missed_if_closed\": skips[i] + 1,", "\"missed_if_closed\": skips[i],"),
 ("the count shown is not the one served", "            s = skips[i]; out.append(", "            s = 0; out.append("),
 ("a rejection is counted as an approval", "    yes = sorted(name(i) for i, a in cast.items() if a); no = sorted(name(i) for i, a in cast.items() if not a)", "    yes = sorted(name(i) for i, a in cast.items()); no = []"),
]


def run(root):
    r = subprocess.run([sys.executable, os.path.join(root, "test_clerk.py")], capture_output=True, text=True)
    try: wrong = json.load(open(os.path.join(root, "test_clerk.json")))["wrong"] if r.returncode in (0, 1) and os.path.exists(os.path.join(root, "test_clerk.json")) else ["the test stopped: " + r.stderr.strip().split("\n")[-1][:120]]
    except Exception as e: wrong = ["unreadable result: %s" % e]
    return r.returncode, wrong


def copy():
    root = tempfile.mkdtemp(prefix="clerk_mut_")
    for f in ("clerk.py", "make_run.py", "test_clerk.py"): shutil.copy(os.path.join(D, f), root)
    shutil.copytree(os.path.join(D, "inputs_past"), os.path.join(root, "inputs_past")); return root


root = copy(); rc, wrong = run(root); shutil.rmtree(root); assert rc == 0 and not wrong, "the unchanged copy does not pass: %s" % wrong
print("unchanged copy: passes"); out, bad = [], 0
for name, old, new in CASES:
    root = copy(); p = os.path.join(root, "clerk.py"); s = open(p, encoding="utf-8").read(); assert s.count(old) == 1, (name, s.count(old))
    open(p, "w", encoding="utf-8").write(s.replace(old, new)); rc, wrong = run(root); shutil.rmtree(root)
    ok = rc != 0 and bool(wrong); bad += not ok; out.append({"case": name, "caught": ok, "said": wrong[:2]}); print("%-52s %s | %s" % (name, "CAUGHT" if ok else "NOT CAUGHT", (wrong[0] if wrong else "")[:110]))
json.dump(out, open(os.path.join(D, "mutants_clerk.json"), "w"), indent=1); print("%d cases, %d not caught" % (len(CASES), bad)); sys.exit(1 if bad else 0)
