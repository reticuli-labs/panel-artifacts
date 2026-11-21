"""run_ule.py: run the RFC authors' published tool (two files, saved unchanged in the directory named by ULE_SRC and read in full before
this was written: the Lean file imports one compiled module and prints its dependency graph; the Python file walks that graph and
prints the live and the dead names; neither writes a file or opens a connection) on each fixture, with and without the dead part.
Per file: compile it to an .olean in mods/<toolchain>/, run their extractor on the module, run their core on the graph with
target `target`, and save both outputs under out/<toolchain>/. Then, the test their README names as the gate: take from the
WITH file every command whose declared name their tool lists as dead, and build what is left (files in ule_min/<toolchain>/).
The removal is mine (their repository has no code for it yet): a command is dropped when the name it declares is in their dead
list, and kept otherwise. Prints one line per fixture."""
import hashlib, json, os, re, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
HOME = os.environ["LEAN_HOME"]; LEAN = os.path.join(HOME, "bin", "lean")
U = os.environ["ULE_SRC"];                  # the directory holding their two files, unchanged
EX = os.path.join(U, "ule_extract.lean"); CORE = os.path.join(U, "ule_core.py")
LABEL = os.environ.get("ULE_LABEL", "ule")                 # with ULE_EXTRACT=<a copy of their extractor> and ULE_LABEL=<name>: the same run with that copy, saved under the other name
EX = os.environ.get("ULE_EXTRACT", EX)
env = dict(os.environ, PATH=os.path.join(HOME, "bin") + os.pathsep + os.environ["PATH"])
ver = subprocess.run([LEAN, "--version"], capture_output=True, text=True).stdout.strip(); tag = re.search(r"version ([0-9a-z.\-]+)", ver).group(1)
mods = os.path.join("mods", tag); outd = os.path.join("out", tag); mind = os.path.join("ule_min", tag)       # relative: the current directory is this script's
for d in (mods, outd, mind): os.makedirs(d, exist_ok=True)
print(ver); print("their files:", {os.path.basename(p): hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] for p in (EX, CORE)})
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:theorem|def|lemma)\s+([A-Za-z0-9_.']+)")


def commands(text):
    """Split a fixture into its commands: a new one starts at each non-indented line that is not a comment and not blank."""
    out = []
    for l in text.split("\n"):
        if l and not l.startswith((" ", "\t", "--")) : out.append([l])
        elif out and l.strip() and not l.startswith("--"): out[-1].append(l)
    return ["\n".join(c) for c in out]


names = sys.argv[1:] or sorted({f.rsplit("_", 1)[0] for f in os.listdir("fixtures") if f.endswith("_with.lean")})
res = {}
for n in names:
    row = {}
    for v in ("with", "without"):
        mod = "%s_%s" % (n, v); src = "fixtures/%s.lean" % mod
        c = subprocess.run([LEAN, "-o", os.path.join(mods, mod + ".olean"), src], capture_output=True, text=True, env=env, timeout=900)
        if c.returncode != 0: row[v] = {"builds": False, "first_line": (c.stdout + c.stderr).strip().split("\n")[0][:160]}; continue
        e = subprocess.run([LEAN, "--run", EX, mod], capture_output=True, text=True, env=dict(env, LEAN_PATH=mods), timeout=900)
        open(os.path.join(outd, mod + ".%s_deps.json" % LABEL), "w", encoding="utf-8").write(e.stdout)
        if e.returncode != 0 or not e.stdout.strip().startswith("{"): row[v] = {"builds": True, "extract_failed": (e.stdout + e.stderr).strip()[:300]}; continue
        k = subprocess.run([sys.executable, "-I", CORE, os.path.join(outd, mod + ".%s_deps.json" % LABEL), "--target", "target", "--json"], capture_output=True, text=True, timeout=120)
        open(os.path.join(outd, mod + ".%s_core.json" % LABEL), "w", encoding="utf-8").write(k.stdout + k.stderr)
        r = json.loads(k.stdout); row[v] = {"builds": True, "graph": json.loads(e.stdout), "live": r["live"], "dead": r["dead"]}
    w = row.get("with", {})
    if w.get("builds") and "dead" in w:
        text = open("fixtures/%s_with.lean" % n, encoding="utf-8").read(); kept, dropped = [], []
        for cmd in commands(text):
            m = DECL.match(cmd); nm = m.group(1) if m else None
            (dropped if nm in w["dead"] else kept).append(cmd if nm is None or nm not in w["dead"] else nm)
        p = os.path.join(mind, "%s_min_%s.lean" % (n, LABEL)); open(p, "w", encoding="utf-8").write("\n\n".join(kept) + "\n")
        b = subprocess.run([LEAN, p], capture_output=True, text=True, env=env, timeout=900)
        open(os.path.join(outd, "%s_min_%s.build.txt" % (n, LABEL)), "w", encoding="utf-8").write(b.stdout + b.stderr + "exit code %d\n" % b.returncode)
        row["minimized"] = {"dropped_commands": dropped, "builds": b.returncode == 0, "first_line": (b.stdout + b.stderr).strip().split("\n")[0][:200] if b.returncode else ""}
    res[n] = row
    m = row.get("minimized", {})
    print("%s | with: live %s dead %s | minimized (dropped %s): %s" % (n, w.get("live"), w.get("dead"), m.get("dropped_commands"), "BUILDS" if m.get("builds") else ("FAILS: " + m.get("first_line", "")) if m else "not made: " + str(w)[:200]))
json.dump(res, open(os.path.join(outd, LABEL + "_results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
