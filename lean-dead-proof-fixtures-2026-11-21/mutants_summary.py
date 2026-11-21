"""mutants_summary.py: show that summarize.py can fail. For each case below: copy out/ and summarize.py into a fresh scratch
directory, change ONE thing in the copy of an output, run the copy of summarize.py there, and require that it stops, with the
line it stopped at printed. First the unchanged copy must pass. Nothing under out/ itself is touched."""
import json, os, re, shutil, subprocess, sys, tempfile
D = os.path.dirname(os.path.abspath(__file__))


def sub(path, old, new, count=None):
    def f(root):
        p = os.path.join(root, path); t = open(p, encoding="utf-8").read(); assert t.count(old) >= 1 and (count is None or t.count(old) == count), (path, old, t.count(old))
        open(p, "w", encoding="utf-8").write(t.replace(old, new))
    return f


def js(path, edit):
    def f(root):
        p = os.path.join(root, path); j = json.load(open(p, encoding="utf-8")); edit(j); json.dump(j, open(p, "w", encoding="utf-8"))
    return f


def set_(j, keys, val):
    for k in keys[:-1]: j = j[k]
    assert j[keys[-1]] != val; j[keys[-1]] = val


CASES = [
 ("the control no longer lists the used lemma", sub("out/4.36.0/F0_with.async1.txt", "ROOT target (theorem) reaches in this file: [fast, lemma1, slow]", "ROOT target (theorem) reaches in this file: [fast, slow]", 1)),
 ("the equation theorems filed under another command", sub("out/4.36.0/F1_with.async1.txt", "] theorem dead : f 0 = 1", "] theorem other : f 0 = 1", 1)),
 ("4.9.0: no renumbering", sub("out/4.9.0/F2a_with.async1.txt", "_auxLemma.2", "_auxLemma.1")),
 ("4.36.0: the target's auxiliary name moves", sub("out/4.36.0/F2a_without.async1.txt", "target._simp_1_1", "target._simp_2_1")),
 ("the match is not shared", sub("out/4.36.0/F2d_with.async1.txt", "ROOT liveM (def) reaches in this file: [deadM.match_1]", "ROOT liveM (def) reaches in this file: [liveM.match_1]", 1)),
 ("sorry shows among the target's axioms", sub("out/4.36.0/F3c_with.async1.txt", "ROOT target axioms: [target._native.native_decide.ax_1_1]", "ROOT target axioms: [sorryAx, target._native.native_decide.ax_1_1]", 1)),
 ("the file without the false lemma builds", sub("out/4.36.0/F3c_without.build.txt", "exit code 1", "exit code 0", 1)),
 ("the later attribute takes effect on 4.36.0", sub("out/4.36.0/F3b_with.build.txt", "exit code 1", "exit code 0", 1)),
 ("their tool lists nq as live", js("out/4.36.0/ule_results.json", lambda j: (j["F2a"]["with"]["dead"].remove("nq"), j["F2a"]["with"]["live"].append("nq")))),
 ("their kept file builds", js("out/4.36.0/ule_results.json", lambda j: set_(j, ["F2a", "minimized", "builds"], True))),
 ("the variant's kept file fails", js("out/4.9.0/keepint_results.json", lambda j: set_(j, ["F2b", "minimized", "builds"], False))),
 ("another fixture's kept file fails (the count)", js("out/4.36.0/ule_results.json", lambda j: set_(j, ["F2c", "minimized", "builds"], False))),
]


def run(root):
    r = subprocess.run([sys.executable, os.path.join(root, "summarize.py")], capture_output=True, text=True)
    m = re.findall(r'summarize\.py", line (\d+)', r.stderr); return r.returncode, (int(m[-1]) if m else None), (r.stderr.strip().split("\n")[-1][:120] if r.returncode else "")


def copy():
    root = tempfile.mkdtemp(prefix="lean_mut_"); shutil.copytree(os.path.join(D, "out"), os.path.join(root, "out")); shutil.copy(os.path.join(D, "summarize.py"), root); return root


root = copy(); rc, line, msg = run(root); shutil.rmtree(root); assert rc == 0, "the unchanged copy does not pass: " + msg
print("unchanged copy: passes"); out = []; bad = 0
for name, mut in CASES:
    root = copy(); mut(root); rc, line, msg = run(root); shutil.rmtree(root)
    ok = rc != 0 and line is not None and "AssertionError" in msg; bad += not ok
    out.append({"case": name, "stopped": rc != 0, "line": line, "error": msg}); print("%-55s %s line %s | %s" % (name, "STOPPED" if ok else "NOT CAUGHT", line, msg[:60]))
json.dump(out, open(os.path.join(D, "mutants_summary.json"), "w", encoding="utf-8"), indent=1)
print("%d cases, %d not caught" % (len(CASES), bad)); sys.exit(1 if bad else 0)
