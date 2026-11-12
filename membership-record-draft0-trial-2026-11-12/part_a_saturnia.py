"""Part A. Saturnia's two draft-0 records, replayed from manifests I fetched from the register, with generic.py and
without the packet's two bank-specific adapters.

usage: python3 -I part_a_saturnia.py <extracted packet dir>      (writes results_a.json beside this file)

The only packet files read are records.json and report.json. The manifests are src/*.json, fetched by fetch_sources.py.
"""
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generic as G  # noqa: E402

PACKET = sys.argv[1]
records = json.load(open(os.path.join(PACKET, "records.json")))
report = {b["bank"]: b for b in json.load(open(os.path.join(PACKET, "report.json")))["banks"]}
# the hand mapping this trial proposes: which of four basis kinds each dimension is
BASIS = {
    "consider": {"domain": ("field", "domain"), "form": ("field", "stratum"),
                 "reference": ("fields", ["domain", "matter"]), "rendering_template": ("template",)},
    "impact": {"domain": ("field", "domain"), "form": ("field", "stratum"),
               "reference": ("template_slot", "rendering_template", "incident"), "rendering_template": ("template",)},
}
out = {"banks": {}, "controls": {}}
loaded = {}
for record in records:
    bank = record["source"]["packet_bank_key"]
    raw = open(os.path.join(HERE, "src", bank + "-manifest.json"), "rb").read()
    manifest = json.loads(raw)
    items = manifest["test_set"]
    ids = [i["id"] for i in items]
    assert record["source"]["manifest_sha256"] == hashlib.sha256(raw).hexdigest(), "the record names another manifest"
    assert record["source"]["items_sha256"] == manifest["items_sha256"] == G.digest(items), "item array digest"
    assert G.digest(record) == report[bank]["record_canonical_sha256"], "record digest differs from the packet's report"
    G.structure(record, ids)
    sizes = G.replay(record, items, lambda i: i["id"], BASIS[bank])
    assert sizes == report[bank]["group_sizes"], "group sizes differ from the packet's report"
    shares = sorted(round(G.literal_share(t), 3) for d in record["dimensions"] if d["id"] == "rendering_template"
                    for g in d["groups"] for t in g["key"].values())
    out["banks"][bank] = {"manifest_sha256": hashlib.sha256(raw).hexdigest(), "items": len(items),
                          "assignments": len(items) * len(record["dimensions"]), "record_digest_matches_report": True,
                          "generic_replay_passes": True, "group_sizes": sizes, "template_literal_share_min_max": [shares[0], shares[-1]]}
    loaded[bank] = (record, items, ids)


def refuses(bank, damaged, stage):
    record, items, ids = loaded[bank]
    try:
        if stage == "structure":
            G.structure(damaged, ids)
        else:
            G.structure(damaged, ids)          # must still pass: the damage keeps counts and coverage
            G.replay(damaged, items, lambda i: i["id"], BASIS[bank])
    except G.Refused as e:
        return str(e)
    return None


def dim(record, name):
    return next(d for d in record["dimensions"] if d["id"] == name)


# controls: each must be refused, or the replay above proves nothing
for bank in ("consider", "impact"):
    record = loaded[bank][0]
    c = {}
    # 1. the packet's own boundary control: swap two assignments, counts and coverage intact
    for name in ("domain", "form", "reference", "rendering_template"):
        d = copy.deepcopy(record)
        a, b = dim(d, name)["groups"][:2]
        a["members"][0], b["members"][0] = b["members"][0], a["members"][0]
        c["swap_two_members_in_" + name] = refuses(bank, d, "replay")
    # 2. one character of one template changed; group id re-pinned so that only the replay can notice
    d = copy.deepcopy(record)
    g = dim(d, "rendering_template")["groups"][0]
    arm = sorted(g["key"])[0]
    g["key"][arm] = g["key"][arm].replace(".", "!", 1) if "." in g["key"][arm] else g["key"][arm] + "!"
    g["id"] = "sha256:" + G.digest(g["key"])
    c["one_template_character_changed"] = refuses(bank, d, "replay")
    # 3. a template widened to one bare slot per arm: it fits every pair, so the other group's items fit two templates
    d = copy.deepcopy(record)
    g = dim(d, "rendering_template")["groups"][0]
    g["key"] = {k: "{slot_%s}" % chr(97 + n) for n, k in enumerate(sorted(g["key"]))}
    g["id"] = "sha256:" + G.digest(g["key"])
    why = refuses(bank, d, "replay")
    # consider: an item of the other group now fits two templates. impact: the reference dimension is read first,
    # and the widened template has no incident slot to read it from.
    assert why and ("fits 2 declared templates" in why or "has no slot named incident" in why), why
    c["one_template_widened_to_a_bare_slot"] = why
    # 4. structure: a missing and a repeated member
    d = copy.deepcopy(record)
    dim(d, "domain")["groups"][0]["members"].pop()
    c["missing_member"] = refuses(bank, d, "structure")
    d = copy.deepcopy(record)
    m = dim(d, "domain")["groups"][0]["members"]
    m.append(m[0])
    c["repeated_member"] = refuses(bank, d, "structure")
    assert all(v is not None for v in c.values()), (bank, [k for k, v in c.items() if v is None])
    out["controls"][bank] = c
out["totals"] = {"items": sum(b["items"] for b in out["banks"].values()),
                 "assignments": sum(b["assignments"] for b in out["banks"].values()),
                 "dimensions_replayed_without_bank_code": sum(len(BASIS[b]) for b in BASIS),
                 "controls_run": sum(len(c) for c in out["controls"].values()),
                 "controls_refused": sum(1 for c in out["controls"].values() for v in c.values() if v)}
json.dump(out, open(os.path.join(HERE, "results_a.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
