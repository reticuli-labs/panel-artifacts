"""test_guard.py: the path checker of this repository must not run a full pass unless asked by name.
Builds a small git repository in a scratch directory with a copy of the script inside, and requires: --help, no argument, and
two arguments exit 2 and write nothing; --write writes the results file; --check refuses a staged file that holds a
user-boundary path and passes a clean one. Then the same for the script AS COMMITTED before the fix (the old text is taken from
the commit named below), where --help must be seen to write the file: the check can fail. Everything it runs, it runs inside the
scratch directory, which it removes; it writes nothing in the repository.
usage: test_guard.py --repo PATH"""
import argparse, json, os, shutil, subprocess, sys, tempfile
ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--repo", required=True); a = ap.parse_args()
REPO = os.path.abspath(a.repo); REL = "lineage-census-2026-10-02/path_leak_pass.py"; OLD_COMMIT = "b41a40f"; NEW_COMMIT = "486d658"
show = lambda rev: subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, REL)], capture_output=True, text=True, check=True).stdout
new, old = show(NEW_COMMIT), show(OLD_COMMIT); assert old and "--write" not in old and "--write" in new


def repo(script_text):
    root = tempfile.mkdtemp(prefix="pathleak_"); os.makedirs(os.path.join(root, "lineage-census-2026-10-02")); os.makedirs(os.path.join(root, "d"))
    open(os.path.join(root, REL), "w", encoding="utf-8").write(script_text); open(os.path.join(root, "d", "has_path.txt"), "w").write("see /home/" + "someone/notes.txt\n")
    g = lambda *x: subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(x), capture_output=True, text=True)
    g("init", "-q"); g("add", "-A"); g("commit", "-q", "-m", "one"); return root, g


def run(root, *args):
    r = subprocess.run([sys.executable, os.path.join(root, REL)] + list(args), capture_output=True, text=True); return r.returncode, os.path.exists(os.path.join(root, "lineage-census-2026-10-02", "path_leak_results.json")), r.stdout


bad = []
root, g = repo(new)
for args in (["--help"], [], ["--check", "--write"], ["-h"], ["--chekc"]):
    rc, wrote, out = run(root, *args)
    if rc != 2 or wrote or "usage:" not in out: bad.append("new script %s: rc %d, wrote %s" % (args, rc, wrote))
open(os.path.join(root, "d", "clean.txt"), "w").write("nothing here\n"); g("add", "d/clean.txt"); rc, wrote, out = run(root, "--check")
if rc != 0 or wrote: bad.append("new script --check on a clean staged file: rc %d, wrote %s" % (rc, wrote))
open(os.path.join(root, "d", "leak.txt"), "w").write("at /home/" + "someone/else\n"); g("add", "d/leak.txt"); rc, wrote, out = run(root, "--check")
if rc != 1 or wrote or "REFUSED" not in out: bad.append("new script --check on a staged path: rc %d, wrote %s" % (rc, wrote))
rc, wrote, out = run(root, "--write")
if rc != 0 or not wrote or json.load(open(os.path.join(root, "lineage-census-2026-10-02", "path_leak_results.json")))["files_with_user_paths"] != 2: bad.append("new script --write: rc %d, wrote %s" % (rc, wrote))
shutil.rmtree(root)
root, g = repo(old); rc, wrote, out = run(root, "--help"); shutil.rmtree(root)
seen_to_fail = rc == 0 and wrote
print("the script at %s: %s" % (NEW_COMMIT, "all cases as required" if not bad else bad))
print("the script at %s with --help: exit %d, wrote the results file: %s (this is the fault; the test sees it: %s)" % (OLD_COMMIT, rc, wrote, seen_to_fail))
sys.exit(0 if not bad and seen_to_fail else 1)
