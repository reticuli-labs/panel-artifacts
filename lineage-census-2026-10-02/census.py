"""Apply predictions.md to every top-level directory of this repository at HEAD. Mechanical; writes results.json."""
import os, re, json, subprocess, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
HEAD = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
tracked = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True).stdout.splitlines()
dirs = sorted({p.split("/", 1)[0] for p in tracked if "/" in p})
EXT = r"(?:json|jsonl|txt|csv|md|sha256|log|png|html|py|yml|yaml|gz)"
LIT = re.compile(r"""["']([^"'\s]{1,200}\.""" + EXT + r""")["']""")
OPEN = re.compile(r"""open\(\s*["']([^"']+)["']""")
NET = re.compile(r"urlopen|requests\.|http://|https://|AinglishClient|ColonyClient|\bcurl |subprocess[^\n]*\b(gh|git)\b")
DECL = re.compile(r"\b(live|API|snapshot|fetched|as served|as read|pulled)\b")
out = {}
for d in dirs:
    files = [p for p in tracked if p.startswith(d + "/")]
    rel = [p[len(d) + 1:] for p in files]; names = {os.path.basename(p) for p in rel}; relset = set(rel)
    scripts = [p for p in files if p.endswith((".py", ".sh"))]
    refs = collections.Counter(); net = False
    for s in scripts:
        try: txt = open(os.path.join(ROOT, s), encoding="utf-8", errors="replace").read()
        except Exception: continue
        if NET.search(txt): net = True
        own = os.path.basename(s)
        for m in list(LIT.finditer(txt)) + list(OPEN.finditer(txt)):
            r = m.group(1)
            if r == own or r.startswith(("http://", "https://")): continue
            if r.startswith(("/", "~", "..")): refs["external:" + r] += 1
            elif r in relset or os.path.basename(r) in names or any(x.endswith("/" + r) for x in relset): refs["present:" + r] += 1
            else: refs["absent:" + r] += 1
    kinds = collections.Counter(k.split(":", 1)[0] for k in refs)
    if not scripts: cls = "no-script"
    elif net: cls = "network"
    elif kinds.get("external"): cls = "external"
    elif kinds.get("absent"): cls = "incomplete"
    else: cls = "self-contained"
    readme = " ".join(open(os.path.join(ROOT, p), encoding="utf-8", errors="replace").read() for p in files if p.endswith(".md"))
    declares = bool(DECL.search(readme))
    out[d] = {"class": cls, "scripts": len(scripts), "files": len(files), "refs": dict(refs), "has_external_ref": bool(kinds.get("external")), "declares": declares, "has_md": any(p.endswith(".md") for p in files)}
sb = {d: v for d, v in out.items() if v["scripts"]}
cls = collections.Counter(v["class"] for v in sb.values())
dep = {d: v for d, v in sb.items() if v["class"] in ("network", "external")}
summary = {"head": HEAD, "dirs": len(dirs), "script_bearing": len(sb), "classes": dict(cls),
           "external_ref_dirs": sum(1 for v in out.values() if v["has_external_ref"]),
           "dependent": len(dep), "dependent_declaring": sum(1 for v in dep.values() if v["declares"]),
           "self_contained_pct_of_script_bearing": round(100 * cls.get("self-contained", 0) / max(1, len(sb)), 1),
           "network_pct_of_script_bearing": round(100 * cls.get("network", 0) / max(1, len(sb)), 1)}
summary["predictions"] = {"p1_self_contained_le_40pct": summary["self_contained_pct_of_script_bearing"] <= 40,
                          "p2_network_ge_50pct": summary["network_pct_of_script_bearing"] >= 50,
                          "p3_external_ref_dirs_ge_10": summary["external_ref_dirs"] >= 10,
                          "p4_dependent_declaring_lt_half": summary["dependent_declaring"] < summary["dependent"] / 2 if dep else None}
json.dump({"kind": "reticuli.lineage-census.v1", "summary": summary, "dirs": out}, open(os.path.join(HERE, "results.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
