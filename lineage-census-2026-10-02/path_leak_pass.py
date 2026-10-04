#!/usr/bin/env python3
"""Second census pass (Hughey bb4ba502, 2026-10-04): which tracked files publish paths that cross a user boundary?
A path is not a secret; a path inventory is a fingerprint of the machine the repo was written on. Scans every tracked text
file at HEAD for user-boundary prefixes (/home/<user>/, /Users/<user>/, ~/, $HOME) and reports counts per file, the distinct
directory prefixes revealed, and how many hits name a credential-shaped location (a file whose name contains key, token,
secret, credential, or ends in .json under a dotdir). Prints JSON; writes nothing but path_leak_results.json beside itself."""
import json, os, re, subprocess, collections, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
CHECK = "--check" in sys.argv   # pre-commit mode: scan STAGED files only, exit 1 on any user-boundary path, write nothing
ALLOW = {"lineage-census-2026-10-02/path_leak_pass.py", "lineage-census-2026-10-02/path_leak_results.json", "lineage-census-2026-10-02/README.md", "lineage-census-2026-10-02/others.md"}  # the pass's own report and the census notes quote the strings it hunts
HEAD = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
tracked = subprocess.run(["git", "-C", str(ROOT), "diff", "--cached", "--name-only", "--diff-filter=ACMR"] if CHECK else ["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.splitlines()
PAT = re.compile(r"(?:/home/[A-Za-z0-9_.-]+|/Users/[A-Za-z0-9_.-]+|(?<![A-Za-z0-9])~/|\$HOME)(?:/[A-Za-z0-9_.@-]+)*")
CRED = re.compile(r"(key|token|secret|credential|passw|\.ssh|colony\.json|artifactcouncil)", re.I)
per_file = {}; prefixes = collections.Counter(); cred_hits = []
for p in tracked:
    if p in ALLOW: continue   # the pass's own report quotes the strings it hunts, in both modes
    fp = ROOT / p
    if not fp.is_file() or fp.suffix in (".gz", ".png", ".ots"): continue
    try: txt = fp.read_text(encoding="utf-8", errors="replace")
    except Exception: continue
    hits = PAT.findall(txt)
    if not hits: continue
    per_file[p] = len(hits)
    for h in hits:
        parts = h.split("/"); prefixes["/".join(parts[:4])] += 1
        if CRED.search(h): cred_hits.append({"file": p, "path": h})
out = {"kind": "reticuli.lineage-census.path-leak.v1", "head": HEAD, "tracked_files": len(tracked), "files_with_user_paths": len(per_file), "hits": sum(per_file.values()),
       "by_extension": dict(collections.Counter(Path(f).suffix or "(none)" for f in per_file)), "distinct_prefixes": dict(prefixes.most_common(12)),
       "credential_shaped_hits": len(cred_hits), "credential_shaped_examples": cred_hits[:12], "per_file": dict(sorted(per_file.items(), key=lambda kv: -kv[1]))}
if CHECK:
    if per_file: print("REFUSED: user-boundary paths in staged files:", json.dumps(per_file)); sys.exit(1)
    print("path_leak_pass --check: staged files clean"); sys.exit(0)
json.dump(out, open(HERE / "path_leak_results.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("head", "tracked_files", "files_with_user_paths", "hits", "by_extension", "distinct_prefixes", "credential_shaped_hits", "credential_shaped_examples")}, indent=1))
