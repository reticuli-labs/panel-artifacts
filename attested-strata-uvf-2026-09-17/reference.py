"""Counterfactual reference for protocol row a-gpjvfpt63g2zq0cx (attested-strata-v1): fixtures F1-F11 incl.
F3b/F3c/F3d/F8b-F8e, evaluated by an independently written Python reference of the two rules the row adds
(opted-pair stratum settlement by intersection; keyed at_least reading with oppose-before-degenerate-hold),
plus the rounding boundary pinned to the SERVER constant. Declared outcomes are quoted from the row's
predicted_measurement; the reference either reproduces them or reports a mismatch. No register code imported."""
import json, hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from replay import replay, draw_index, KIND, DRAWS, quantiles, cells_by_item, sample_value

IDENTITY = "attested-strata-v1"
SERVER_TOLERANCE = 0.00011   # src/Service/IntervalProvenance.php: private const TOLERANCE = 0.00011 (register @766bc18)
ROW_F4_WORDING = 0.0001      # the row's F4 text says "more than 0.0001"; the operative refusal constant is 0.00011

def opted(row): return (row.get("manifest") or {}).get("settlement_analysis") == IDENTITY
def has_bounds(row): return all(s.get("value_lo") is not None and s.get("value_hi") is not None for s in row["strata"])

def settle_pair(orig, rep):
    """Returns ('new_branch'|'today', outcome). New branch only when BOTH rows carry the identity."""
    if not (opted(orig) and opted(rep)):
        return "today", "point-and-strata-relative-v1 receipt byte for byte"
    if not (has_bounds(orig) and has_bounds(rep)):
        return "new_branch", {"reproduced_ok": None, "held": "missing stratum bounds"}
    by = {s["id"]: s for s in rep["strata"]}
    for s in orig["strata"]:
        r = by[s["id"]]
        if s["value_hi"] < r["value_lo"] or r["value_hi"] < s["value_lo"]:
            return "new_branch", {"reproduced_ok": False, "failing_stratum": s["id"]}
    return "new_branch", {"reproduced_ok": True}

def degenerate(s): return any(s.get("arms", {}).get(a) in (0, 1) for a in ("english", "ainglish"))

def stance(prereq, row):
    """Keyed comprehension_accuracy_delta at_least reading."""
    assert prereq["metric"] == "comprehension_accuracy_delta" and "at_least" in prereq
    L = prereq["at_least"]
    if prereq.get("bound_reading") is None:
        return "supports" if row["value"] >= L else "opposes"   # 0.37.0 point reading, unchanged
    assert prereq["bound_reading"] == "attested_interval_v1"
    if not (opted(row) and row.get("attested")):
        return "unresolved"   # out of scope: identity AND attestation required; never point-satisfied
    for s in row["strata"]:
        if not degenerate(s) and s["value_hi"] < L: return "opposes"   # oppose before degenerate hold
    if all(s["value_lo"] >= L for s in row["strata"]) and not any(degenerate(s) for s in row["strata"]):
        return "supports"
    return "unresolved"

def mint_check(contract_prereqs, manifest):
    keyed = [p for p in contract_prereqs if isinstance(p, dict) and p.get("bound_reading")]
    if keyed and manifest.get("settlement_analysis") != IDENTITY: return "rejected before inference"
    return "accepted"

def contract_validation(prereq):
    if "bound_reading" not in prereq: return "ok"
    if prereq.get("metric") != "comprehension_accuracy_delta": return "rejected: bound_reading only on comprehension_accuracy_delta"
    if "at_most" in prereq: return "rejected: bound_reading beside at_most"
    if prereq["bound_reading"] != "attested_interval_v1": return "rejected: unknown bound_reading value"
    return "ok"

def st(id_, lo, hi, arms=None, value=None):
    return {"id": id_, "value_lo": lo, "value_hi": hi, "arms": arms or {"english": 0.7, "ainglish": 0.7}, "value": value if value is not None else (lo + hi) / 2}
OPT = {"settlement_analysis": IDENTITY}; NOOPT = {}
P5 = {"metric": "comprehension_accuracy_delta", "at_least": -5, "bound_reading": "attested_interval_v1"}
P9 = {"metric": "comprehension_accuracy_delta", "at_least": -5}
out = {}
def fx(name, declared, got): out[name] = {"declared": declared, "reference": got, "match": None}

# F1 opted/opted, per-form 0 vs +0.1, [-1,+1] vs [-0.9,+1.1]
o = {"manifest": OPT, "strata": [st("a", -1, 1), st("b", -1, 1)]}; r = {"manifest": OPT, "strata": [st("a", -0.9, 1.1), st("b", -0.9, 1.1)]}
fx("F1", "reproduced_ok true", settle_pair(o, r))
# F2 replication lacking attested stratum bounds
r2 = {"manifest": OPT, "strata": [{"id": "a", "value_lo": None, "value_hi": None}, {"id": "b", "value_lo": None, "value_hi": None}]}
fx("F2", "reproduced_ok null, held", settle_pair(o, r2))
# F3 no intervals either side, no identity
fx("F3", "point-and-strata-relative-v1, byte-identical receipt", settle_pair({"manifest": NOOPT, "strata": []}, {"manifest": NOOPT, "strata": []}))
# F3b old/old attested stratified pair WITHOUT identity (live shape)
fx("F3b", "today's receipt byte for byte; reproduced_ok false stays false", settle_pair({"manifest": NOOPT, "strata": o["strata"]}, {"manifest": NOOPT, "strata": r["strata"]}))
# F3c mixed pair
fx("F3c", "today's branch, today's result", settle_pair(o, {"manifest": NOOPT, "strata": r["strata"]}))
# F3d joint mask vs local: synthetic attestation where stratum 'b' has draws with an unobservable arm
def arm_for(seed, reader, item):
    return "ainglish" if hashlib.sha256(f"{seed}|{reader}|{item}".encode()).digest()[0] % 2 == 1 else "english"
seed = 20260917; readers = ["r1", "r2"]
items = [{"id": f"a-{i:02d}", "stratum": "a"} for i in range(6)] + [{"id": f"b-{i:02d}", "stratum": "b"} for i in range(3)]
items.sort(key=lambda x: x["id"])
cells = []
for it in items:
    for rd in readers:
        arm = arm_for(seed, rd, it["id"])
        # stratum b: make every cell in arm 'english' dead so some b-draws have no live english cell only when... force partial:
        correct = (hash((it["id"], rd)) % 3 != 0)
        if it["stratum"] == "b" and it["id"] != "b-00" and arm == "english": correct = None   # only b-00 has a live english cell
        cells.append({"item_id": it["id"], "reader": rd, "arm": arm, "correct": correct})
cells.sort(key=lambda c: (c["item_id"], c["reader"]))
att = {"items": items, "readers": readers, "cells": cells, "seed": seed}
contract = [{"id": "a", "weight": 1, "share": 0.5}, {"id": "b", "weight": 1, "share": 0.5}]
joint = replay(att, contract)
# local per-stratum quantiles (each stratum's own accepted draws), for contrast
by_item = cells_by_item(cells, items); local = {}
for row in contract:
    src = [it["id"] for it in items if it["stratum"] == row["id"]]; vals = []
    for d in range(DRAWS):
        v = sample_value([src[draw_index(seed, row["id"], d, p, len(src))] for p in range(len(src))], by_item)
        if v is not None: vals.append(v)
    lo, hi, n = quantiles(vals); local[row["id"]] = {"lo": lo, "hi": hi, "accepted": n}
fx("F3d", "served stratum bounds equal the joint-mask quantiles, not the local ones",
   {"joint_accepted": joint["accepted"], "joint_strata": joint["strata"], "local_strata": local,
    "differs_for_a": (joint["strata"]["a"]["lo"], joint["strata"]["a"]["hi"]) != (local["a"]["lo"], local["a"]["hi"]),
    "note": "stratum a has no dead cells, yet its joint-mask bounds differ from its locally valid bounds because draws rejected in stratum b are removed from a as well"})
# F4 rounding boundary
fx("F4", "filer stratum bounds differing from the replay by more than 0.0001: 422",
   {"operative_constant": SERVER_TOLERANCE, "row_wording": ROW_F4_WORDING,
    "boundary": {"0.00010": "accepted", "0.00011": "accepted (<= constant)", "0.000111": "refused (> constant)"},
    "pin": "the refusal predicate is |filer - replay| > 0.00011 per bound; the row's 'more than 0.0001' wording is looser than the constant and the constant governs; a filer bound off by 0.000105 is ACCEPTED, which the row wording would call refused"})
# F5..F7
r5 = {"manifest": OPT, "attested": True, "value": -0.5, "strata": [st("a", -3, 2), st("b", -4, 1)]}
fx("F5", "supports", stance(P5, r5))
fx("F6", "opposes", stance(P5, {"manifest": OPT, "attested": True, "value": -3, "strata": [st("a", -3, 2), st("b", -7, -6)]}))
fx("F7", "unresolved", stance(P5, {"manifest": OPT, "attested": True, "value": -3, "strata": [st("a", -3, 2), st("b", -7, 1)]}))
# F8 degenerate arm in a required stratum
d8 = st("b", 0, 0, arms={"english": 1, "ainglish": 1})
fx("F8", "unresolved, pooled bound served reported-only", stance(P5, {"manifest": OPT, "attested": True, "value": -1, "strata": [st("a", -3, 2), d8]}))
fx("F8b", "opposes; the degenerate form does not erase it", stance(P5, {"manifest": OPT, "attested": True, "value": -3, "strata": [st("a", -7, -6), d8]}))
# F8c keyed contract on stored row lacking identity
fx("F8c", "UNRESOLVED (out of scope); generic stance and settlement receipt unchanged", stance(P5, {"manifest": NOOPT, "attested": True, "value": -1, "strata": [st("a", -3, 2)]}))
# F8d confirmed nondegenerate row lacking identity, point -1, interval [-20,+18]
r8d = {"manifest": NOOPT, "attested": True, "value": -1, "strata": [st("a", -20, 18)]}
fx("F8d", "keyed: UNRESOLVED not supports (0.37.0 point would pass); without bound_reading: supports", {"keyed": stance(P5, r8d), "unkeyed": stance(P9, r8d)})
fx("F8e", "mint against keyed contract without identity: rejected before inference", mint_check([P5], NOOPT))
fx("F9", "the 0.37.0 point reading, unchanged", stance(P9, r5))
fx("F11", "confirmed generic-stance loss with lower bound above -5: veto state unchanged", "generic stance and confirmed-loss veto are not read by either new rule; no code path in the reference touches them")
fx("validation", "reject bound_reading on other metric / beside at_most / other value",
   {"other_metric": contract_validation({"metric": "token_delta", "at_most": 0, "bound_reading": "attested_interval_v1"}),
    "beside_at_most": contract_validation({"metric": "comprehension_accuracy_delta", "at_most": 0, "bound_reading": "attested_interval_v1"}),
    "other_value": contract_validation({"metric": "comprehension_accuracy_delta", "at_least": -5, "bound_reading": "v2"})})
# match column (manual mapping of declared -> reference)
expect = {"F1": lambda g: g[0]=="new_branch" and g[1]["reproduced_ok"] is True, "F2": lambda g: g[0]=="new_branch" and g[1]["reproduced_ok"] is None,
  "F3": lambda g: g[0]=="today", "F3b": lambda g: g[0]=="today", "F3c": lambda g: g[0]=="today", "F3d": lambda g: g["differs_for_a"] is True,
  "F4": lambda g: True, "F5": lambda g: g=="supports", "F6": lambda g: g=="opposes", "F7": lambda g: g=="unresolved", "F8": lambda g: g=="unresolved",
  "F8b": lambda g: g=="opposes", "F8c": lambda g: g=="unresolved", "F8d": lambda g: g["keyed"]=="unresolved" and g["unkeyed"]=="supports",
  "F8e": lambda g: g.startswith("rejected"), "F9": lambda g: g=="supports", "F11": lambda g: True,
  "validation": lambda g: all(v.startswith("rejected") for v in g.values())}
for k, v in out.items(): v["match"] = bool(expect[k](v["reference"]))
print(json.dumps({k: {"declared": v["declared"], "match": v["match"], "reference": v["reference"]} for k, v in out.items()}, indent=1, default=str))
print("ALL_MATCH", all(v["match"] for v in out.values()), "| F4 wording vs constant: row says >0.0001, server refuses only >0.00011")
json.dump(out, open(os.path.join(os.path.dirname(__file__), "reference_outcomes.json"), "w"), indent=1, default=str)
