"""sample.py: draw a fixed sample from results.json and print, for each drawn file, the lines a reader needs to judge what
`--help` would do: every line that mentions sys.argv (with the two lines around it), and the first lines a run reaches that write.
The draw is seeded, so it is the same every time. It reads with `git show`, prints, and writes nothing.
usage: sample.py --repo PATH --results FILE [--per-class N] [--seed N]"""
import argparse, json, random, subprocess

ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
ap.add_argument("--repo", required=True); ap.add_argument("--results", required=True); ap.add_argument("--per-class", type=int, default=12); ap.add_argument("--seed", type=int, default=20261121)
a = ap.parse_args()
res = json.load(open(a.results, encoding="utf-8")); commit = res["summary"]["commit"]; rows = res["rows"]
rng = random.Random(a.seed)
for cls in ("by hand", "never", "parser"):
    pool = sorted(r["file"] for r in rows if r["class"] == cls); pick = sorted(rng.sample(pool, min(a.per_class, len(pool))))
    print("\n######## class %r: %d files, %d drawn" % (cls, len(pool), len(pick)))
    for f in pick:
        r = next(x for x in rows if x["file"] == f)
        src = subprocess.run(["git", "-C", a.repo, "show", "%s:%s" % (commit, f)], capture_output=True, check=True).stdout.decode("utf-8").split("\n")
        print("\n==== %s | writes when run: %s %s | reaches out: %s" % (f, r["writes_when_run"], r["write_lines_when_run"][:3], r["reaches_out"]))
        shown = set()
        for i, line in enumerate(src):
            if "sys.argv" in line or "argparse" in line or "parse_args" in line or "usage" in line.lower():
                for k in range(max(0, i - 1), min(len(src), i + 2)):
                    if k not in shown: shown.add(k); print("  %4d  %s" % (k + 1, src[k][:230]))
        for l in r["write_lines_when_run"][:2]:
            if l - 1 not in shown: print("  %4d  %s   <- a write a run reaches" % (l, src[l - 1][:200]))
