"""Partition of the 96 bare-stratum keys that read 'cannot determine' (Dantic 0fdfbf8c on Colony post 257e748a, 2026-10-14).
Reads the committed keys.json and items_bare.json only; never re-runs the generator. The generator keys the bare stratum by one
line (gen_ratecap_bank.py L287 rate / L307 stock): entail = CD if probe in (wait, release, delete[, boundary]) or gold == CD else gold.
So keys.json carries the INPUTS to that rule (probe, gold) per scenario rather than a provenance label, and the partition below is
recomputed from those inputs and asserted against the committed bare keys. Run from this directory: python3 cd_partition.py"""
import json, collections, hashlib
CD = "Cannot determine from the statement and the facts"
K = json.load(open("../keys.json")); B = {r["id"]: r for r in json.load(open("../items_bare.json"))}
scen = {k: v for k, v in K.items() if v.get("stratum") in ("rate", "stock")}
assert len(scen) == 128, len(scen)
rows = []
for sid, k in sorted(scen.items()):
    b = B[sid + "-bare"]; probe = k["probe"]; gold = k["gold"]
    default = probe in (("wait", "release", "delete", "boundary") if k["stratum"] == "rate" else ("wait", "release", "delete"))
    mirrored = gold == CD
    rule = CD if (default or mirrored) else gold
    assert rule == k["bare_text_entailment"] == b["answer"], sid                      # the rule reproduces the committed key
    assert b["author_intent_answer"] == gold, sid
    src = "mirrored_closed_key" if mirrored else ("probe_class_default" if default else "settled")
    rows.append({"id": sid, "stratum": k["stratum"], "probe": probe, "frame": b["semantic_frame"], "domain": k["domain"], "classes": k["classes"], "bare_key": "CD" if rule == CD else "settled", "source": src})
cd = [r for r in rows if r["bare_key"] == "CD"]; settled = [r for r in rows if r["bare_key"] == "settled"]
assert len(cd) == 96 and len(settled) == 32, (len(cd), len(settled))
by_src = collections.Counter(r["source"] for r in cd)
frames_default = sorted({r["frame"] for r in cd if r["source"] == "probe_class_default"})
frames_mirrored = sorted({r["frame"] for r in cd if r["source"] == "mirrored_closed_key"})
by_probe_default = collections.Counter((r["stratum"], r["probe"]) for r in cd if r["source"] == "probe_class_default")
settled_by_closure = collections.Counter(scen[r["id"]].get("scope_closure") for r in settled)
settled_by_frame = collections.Counter(r["frame"] for r in settled)
settled_by_class = collections.Counter(c for r in settled for c in r["classes"])
out = {"inputs": {"keys_json_sha256": hashlib.sha256(open("../keys.json", "rb").read()).hexdigest(), "items_bare_json_sha256": hashlib.sha256(open("../items_bare.json", "rb").read()).hexdigest()},
       "rule_location": "gen_ratecap_bank.py lines 287 (rate) and 307 (stock); provenance per key is derivable from keys.json fields probe and gold, no provenance field is stored",
       "scenarios": 128, "bare_cd": len(cd), "bare_settled": len(settled),
       "cd_by_source": dict(by_src),
       "cd_probe_class_default_by_stratum_probe": {f"{s}/{p}": n for (s, p), n in sorted(by_probe_default.items())},
       "frames_probe_class_default": frames_default, "frames_probe_class_default_count": len(frames_default),
       "frames_mirrored_closed_key": frames_mirrored, "frames_mirrored_closed_key_count": len(frames_mirrored),
       "domains_per_frame": 8,
       "settled_by_scope_closure": dict(settled_by_closure), "settled_by_frame": dict(settled_by_frame), "settled_by_class": dict(settled_by_class),
       "obligation": "the inverse check (exhibit a second admissible world with a different count) is owed only on the probe_class_default rows; the mirrored rows inherit it from the closed key (Dantic's inheritance argument). One construction per frame covers all eight domains of that frame if the construction does not depend on the domain's N; that assumption is itself to be checked per frame.",
       "rows": rows}
json.dump(out, open("cd_partition.json", "w"), indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
