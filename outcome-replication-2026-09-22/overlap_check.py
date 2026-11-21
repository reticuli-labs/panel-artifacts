"""overlap_check.py <source items.json>: the fresh-input check that gen_items.py could not run from this tree (Erratum 1), run
against the source bank itself. Offline, read-only. The source is Dexagon's public items file for the original cba951d7
(canonical JSON SHA-256 478551f7d70f7725277b2bdc2888d1484698ffda55bfaec50da91cf51d9dc728); it is not copied into this repository.
Reports: arm texts of this bank found in the source; model labels shared; worlds (paths, masses and x) of this bank that also occur
in the source. Plants one source item into a copy of this bank's list first and must find it."""
import hashlib, json, re, sys

src = json.load(open(sys.argv[1], encoding="utf-8")); mine = json.load(open("items.json", encoding="utf-8"))
assert hashlib.sha256(json.dumps(src, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest() == "478551f7d70f7725277b2bdc2888d1484698ffda55bfaec50da91cf51d9dc728", "not the source bank"
bodies = {x["english"] for x in src} | {x["ainglish"] for x in src}
found = lambda items: [i["id"] for i in items if i["english"] in bodies or i["ainglish"] in bodies]
assert len(found(mine[:] + [src[0]])) == len(found(mine)) + 1, "the planted source item was not found"
labels = lambda items: {m for x in items for m in re.findall(r"model ([A-Z]\d+)", x["english"])}
sig = lambda t: (tuple(re.findall(r"value (-?\d+) units with mass (\d+/\d+|\d+)", t)), tuple(re.findall(r"Here x = (-?\d+(?:/\d+)?) units", t)))
s_src = {sig(x["english"]) for x in src if not x.get("calibration")}; s_mine = [sig(x["english"]) for x in mine if not x.get("calibration")]
print(json.dumps({"source_items": len(src), "items_here": len(mine), "arm_texts_here_found_in_source": len(found(mine)), "model_labels_shared": len(labels(src) & labels(mine)),
                  "worlds_here_also_in_source": sum(1 for s in s_mine if s in s_src), "real_items_here": len(s_mine), "distinct_worlds_here": len(set(s_mine))}, indent=1))
