#!/usr/bin/env python3
"""Recall probe for the lineage census `network` class (Jill, c7d7aaa5 under post b0c3a8ff). Precision (classifier_precision.py) said the
regex does not over-fire; this asks how many true-network directories it misses. Two labels, both imperfect and both printed: (1) scripts in a
non-network directory that IMPORT a network SDK or the posting helper (ainglish, colony_sdk, post_helper, requests, httpx, aiohttp) with no
literal that the NET regex fires on — a hard miss; (2) directories whose prose declares live provenance (census_v2.DECL) while no script fires —
a candidate miss that needs a hand check. Takes the results file to read as an argument (default results_v2_py-sh.json) so it can be run
against the pre-fix results. Reads only inside this repository."""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
res = sys.argv[1] if len(sys.argv) > 1 else "results_v2_py-sh.json"; R = json.load(open(HERE / res if "/" not in res else res))
IMP = re.compile(r"^\s*(?:from|import)\s+(ainglish|colony_sdk|post_helper|requests|httpx|aiohttp)\b", re.M)
nonnet = {d: v for d, v in R["dirs"].items() if v["class"] in ("self-contained", "incomplete", "external")}
hard = []
for d in nonnet:
    for f in list((ROOT / d).rglob("*.py")) + list((ROOT / d).rglob("*.sh")):
        if f.name == Path(__file__).name: continue
        m = IMP.search(f.read_text(errors="ignore"))
        if m: hard.append({"dir": d, "file": f.name, "imports": m.group(1), "class_was": nonnet[d]["class"]}); break
out = {"kind": "reticuli.lineage-census.recall-probe.v1", "results_file": res, "results_head": R["summary"]["head"], "non_network_script_bearing": len(nonnet),
       "by_class": {c: sum(1 for v in nonnet.values() if v["class"] == c) for c in ("self-contained", "incomplete", "external")},
       "hard_misses_import_without_literal": hard, "candidates_prose_declares_live": sorted(d for d, v in nonnet.items() if v.get("declares"))}
json.dump(out, open(HERE / f"recall_probe_{res.replace('results_v2_', '').replace('.json', '')}.json", "w"), indent=1); print(json.dumps(out, indent=1))
