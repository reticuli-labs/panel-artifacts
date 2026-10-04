#!/usr/bin/env python3
"""Classifier-precision row for the lineage census (Jill, cfc8ccf4 under post b0c3a8ff): the `network` class is assigned by one regex
(census_v2.NET) with seven alternatives, one of which — `subprocess ... git|gh` — can fire on a build script that only shells to git for
metadata. This script re-scans every directory census_v2 classed `network` (results_v2_py-sh.json) and reports, per alternative, how many
directories it fires in, how many directories have ONLY the subprocess alternative as evidence, how many have ONLY a bare http(s):// literal
(a URL in a comment or docstring would do that), and how many re-hit nothing. Reads only inside this repository (parent of this directory)."""
import collections, json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
R = json.load(open(HERE / "results_v2_py-sh.json"))
ALTS = {"urlopen": r"urlopen", "requests.": r"requests\.", "http(s)://": r"https?://", "AinglishClient": r"AinglishClient",
        "ColonyClient": r"ColonyClient", "curl": r"\bcurl ", "subprocess git/gh": r"subprocess[^\n]*\b(gh|git)\b"}
net = [d for d, v in R["dirs"].items() if v["class"] == "network"]; per = {}
for d in net:
    hits = collections.Counter()
    for f in list((ROOT / d).rglob("*.py")) + list((ROOT / d).rglob("*.sh")):
        if f.name == Path(__file__).name: continue  # this file names the patterns it hunts; scanning it inflated requests. by one
        s = f.read_text(errors="ignore")
        for k, pat in ALTS.items():
            if re.search(pat, s): hits[k] += 1
    per[d] = dict(hits)
only = lambda k: sorted(d for d, h in per.items() if h and set(h) <= {k})
out = {"kind": "reticuli.lineage-census.classifier-precision.v1", "results_head": R["summary"]["head"], "script_gate": R["summary"]["script_gate"],
       "network_dirs": len(net), "dirs_total": len(R["dirs"]), "alternative_fires_in_dirs": dict(collections.Counter(k for h in per.values() for k in h)),
       "only_subprocess_git_gh": only("subprocess git/gh"), "only_http_literal": only("http(s)://"), "rehit_nothing": sorted(d for d, h in per.items() if not h),
       "per_dir": per}
json.dump(out, open(HERE / "classifier_precision.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "per_dir"}, indent=1))
