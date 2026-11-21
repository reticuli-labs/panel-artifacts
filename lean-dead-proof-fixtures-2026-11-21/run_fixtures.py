"""run_fixtures.py [name ...]: for each fixture source in src/ (all of them when none is named), write two files into fixtures/:
<name>_with.lean (the source with its marker lines taken out) and <name>_without.lean (the same with every block between a
--DEAD line and a --/DEAD line taken out), run Runner.lean on both with the toolchain named in LEAN_HOME, with asynchronous
elaboration on and off, and save what it prints under out/<toolchain>/. It prints, per fixture, whether on/off agree. The roots
whose reach and axioms are printed are listed in ROOTS below. Nothing here talks to a network."""
import os, re, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
HOME = os.environ["LEAN_HOME"]; LEAN = os.path.join(HOME, "bin", "lean")        # LEAN_HOME: the unpacked toolchain, e.g. the directory lean-4.36.0-linux
RUNNER = os.environ.get("RUNNER", "Runner.lean")
ROOTS = {"F0": ["lemma1", "unused", "target"], "F1": ["f", "dead", "target", "f.eq_1", "f.eq_2"], "F2a": ["np", "nq", "dead", "target"], "F2b": ["np", "nq", "dead", "target"],
         "F2c": ["deadD", "liveD", "target"], "F2d": ["deadM", "liveM", "target"], "F2e": ["deadT", "target"],
         "F3a": ["slow", "fast", "slow_eq_fast", "target"], "F3b": ["g", "gImpl", "target"], "F3c": ["slow", "fast", "slow_eq_fast", "target"], "F3d": ["h", "hImpl", "target"]}
names = sys.argv[1:] or sorted(f[:-5] for f in os.listdir("src") if f.endswith(".lean"))
ver = subprocess.run([LEAN, "--version"], capture_output=True, text=True).stdout.strip(); tag = re.search(r"version ([0-9a-z.\-]+)", ver).group(1)
os.makedirs("fixtures", exist_ok=True); os.makedirs("out/" + tag, exist_ok=True); print(ver)
for n in names:
    src = open("src/%s.lean" % n, encoding="utf-8").read().split("\n"); assert src.count("--DEAD") == src.count("--/DEAD") >= 1, n
    with_, without, inside = [], [], False
    for l in src:
        if l == "--DEAD": assert not inside; inside = True; continue
        if l == "--/DEAD": assert inside; inside = False; continue
        with_.append(l)
        if not inside: without.append(l)
    assert not inside and len(with_) > len(without)
    for v, lines in (("with", with_), ("without", without)):
        open("fixtures/%s_%s.lean" % (n, v), "w", encoding="utf-8").write("\n".join(lines))
        outs = {}
        pe = dict(os.environ, PATH=os.path.join(HOME, "bin") + os.pathsep + os.environ["PATH"])
        pl = subprocess.run([LEAN, "fixtures/%s_%s.lean" % (n, v)], capture_output=True, text=True, env=pe, timeout=900)      # the plain build: what the compiler itself says of the file
        open("out/%s/%s_%s.build.txt" % (tag, n, v), "w", encoding="utf-8").write(pl.stdout + pl.stderr + "exit code %d\n" % pl.returncode)
        print("%s_%s: plain build exit %d%s" % (n, v, pl.returncode, (" | " + (pl.stdout + pl.stderr).strip().split("\n")[0][:150]) if pl.returncode else ""))
        for a in ("1", "0"):
            r = subprocess.run([LEAN, "--run", RUNNER, "fixtures/%s_%s.lean" % (n, v)] + ROOTS[n], capture_output=True, text=True, env=dict(os.environ, ASYNC=a, PATH=os.path.join(HOME, "bin") + os.pathsep + os.environ["PATH"]), timeout=900)
            outs[a] = r.stdout + r.stderr
            open("out/%s/%s_%s.async%s.txt" % (tag, n, v, a), "w", encoding="utf-8").write(outs[a] + "exit code %d\n" % r.returncode)
            if r.returncode != 0 or "constants of this file at the end" not in outs[a]: print("%s_%s async %s: THE READER DID NOT FINISH (exit %d): %s" % (n, v, a, r.returncode, outs[a].strip().split("\n")[-1][:200])); outs[a] = "failed " + a
        same = outs["1"].split("\n")[1:] == outs["0"].split("\n")[1:]
        print("%s_%s: written | async on and off print %s" % (n, v, "the same" if same else "DIFFERENT lines"))
