"""Counterfactual reference for protocol row a-gpjvfpt63g2zq0cx (attested-strata-v1), successor to the 09-17
packet's reference.py. Independently written Python of (a) TODAY's settlement receipts (point-relative-v1,
point-and-strata-relative-v1, interval-overlap-commensurable-v1), validated against every served receipt in the
frozen raw snapshot, (b) the row's two additions: opted-pair settlement "pooled-then-strata" (the 0.35.0 pooled attested intervals must
intersect, THEN every aligned stratum's attested intervals must intersect; missing pooled or stratum bounds HOLD; no
degenerate hold at pair level) and the keyed at_least reading with its pooled-bound condition and
oppose-before-degenerate-hold precedence. Revision 3 (Dexagon bbdd711e): keyed reading selects CONFIRMED ORIGINALS only (active_originals/confirmed_originals/requirement_state, shared with candidate.py). Revision 2 (Dexagon f501fcab): pooled intersection retained; F10 reads the
legacy branch from an INDEPENDENT baseline (served row metadata + Dexagon's PHP oracle receipt), not stance() vs itself. Declared outcomes are quoted from the row's predicted_measurement; the
script exits non-zero on any mismatch. No register code imported.
Usage: python3 reference.py --raw raw/ [--out reference_outcomes.json]"""
import json, hashlib, os, sys, glob, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from replay import replay, draw_index, DRAWS, quantiles, cells_by_item, sample_value

IDENTITY = "attested-strata-v1"
ROW_TOLERANCE = 0.0001        # the row's F4 falsifier: a filer bound differing from the replay by MORE THAN 0.0001 is refused
SERVER_TOLERANCE_5723faa = 0.00011  # src/Service/IntervalProvenance.php private const TOLERANCE at register 5723faa: implementation must move to 0.0001
POINT_FLOOR, POINT_REL = 0.02, 0.1

def canon(x): return json.dumps(x, sort_keys=True, separators=(",", ":"), default=str)
def opted(row): return (row.get("manifest") or {}).get("settlement_analysis") == IDENTITY
def has_bounds(row): return all(s.get("value_lo") is not None and s.get("value_hi") is not None for s in row["strata"])
def degenerate(s): return any((s.get("arms") or {}).get(a) in (0, 1) for a in ("english", "ainglish"))

def active_originals(measurements, metric="comprehension_accuracy_delta"):
    """The register's readiness selection (EvidenceReadiness::assess at 3c82903): ORIGINALS only (replicates_hash null,
    is_replication false), not voided, evidence_state valid, metric matching. Replications never stand as originals."""
    return [m for m in (measurements or []) if m.get("metric") == metric and not m.get("is_replication") and m.get("replicates_hash") is None
            and m.get("voided_at") is None and m.get("evidence_state") == "valid"]

def confirmed_originals(measurements, metric="comprehension_accuracy_delta"):
    """Only CONFIRMED originals feed a requirement's stances (confirmed true and counts_toward_verdict true); an active but
    unconfirmed original keeps a bounded requirement UNRESOLVED (state replicate_original), never satisfied."""
    return [m for m in active_originals(measurements, metric) if m.get("confirmed") is True and m.get("counts_toward_verdict") is True]

def requirement_state(stances, active_count):
    """Readiness bucket for one requirement from its confirmed-original stances, register precedence: no confirmed original ->
    'missing' when no active original exists, else 'unresolved'; any opposes -> 'opposing'; any neutral/unresolved -> 'unresolved';
    otherwise (every stance supports) -> 'satisfied'."""
    if not stances: return "missing" if active_count == 0 else "unresolved"
    if "opposes" in stances: return "opposing"
    if any(x in ("neutral", "unresolved") for x in stances): return "unresolved"
    return "satisfied"
def tol(o): return max(POINT_FLOOR, POINT_REL * abs(o))

# ---------------- today's rules, reimplemented from the served receipt semantics ----------------
def today_receipt(orig, rep, rule_applied):
    """orig/rep: {value, value_lo, value_hi, strata:[{id, value}]}. Returns the settlement fields of today's receipt."""
    o, r = orig["value"], rep["value"]
    if rule_applied == "interval-overlap-commensurable-v1":
        agg = orig["value_lo"] <= rep["value_hi"] and rep["value_lo"] <= orig["value_hi"]
    else:
        agg = abs(r - o) <= tol(o)
    strata = []
    by = {s["id"]: s for s in rep.get("strata") or []}
    for s in orig.get("strata") or []:
        rs = by.get(s["id"])
        ok = rs is not None and abs(rs["value"] - s["value"]) <= tol(s["value"])
        strata.append({"id": s["id"], "reproduced_ok": ok})
    rec = {"rule_applied": rule_applied, "reproduced_ok": bool(agg and all(x["reproduced_ok"] for x in strata))}
    if strata: rec["aggregate_reproduced_ok"] = bool(agg); rec["strata"] = strata
    return rec

def served_receipt(m):
    rc = m["replication_comparison"]
    rec = {"rule_applied": rc.get("rule_applied"), "reproduced_ok": m.get("reproduced_ok")}
    if rc.get("strata"):
        rec["aggregate_reproduced_ok"] = rc.get("aggregate_reproduced_ok")
        rec["strata"] = [{"id": s["id"], "reproduced_ok": s.get("reproduced_ok")} for s in rc["strata"]]
    return rec

def vals(m):
    return {"value": m["value"], "value_lo": m.get("value_lo"), "value_hi": m.get("value_hi"),
            "strata": [{"id": s["id"], "value": s["value"], "value_lo": s.get("value_lo"), "value_hi": s.get("value_hi"), "arms": s.get("arms")} for s in (m.get("stratum_results") or [])]}

TODAY_RULES = ("point-relative-v1", "point-and-strata-relative-v1", "interval-overlap-commensurable-v1")

def positive_control(rows):
    """Recompute today's receipt for every settled replication and compare to the served receipt."""
    n = 0; mism = []
    for m in rows.values():
        rc = m.get("replication_comparison")
        if not (m.get("is_replication") and rc and rc.get("rule_applied") in TODAY_RULES and m.get("reproduced_ok") is not None): continue
        o = rows.get(m.get("replicates_hash"))
        if not o: continue
        got = today_receipt(vals(o), vals(m), rc["rule_applied"]); exp = served_receipt(m); n += 1
        if canon(got) != canon(exp): mism.append({"rep": m["manifest_hash"][:8], "orig": o["manifest_hash"][:8], "served": exp, "recomputed": got})
    return n, mism

# ---------------- the row's additions ----------------
def settle_pair(orig, rep, rule_applied="point-and-strata-relative-v1"):
    """Branch keyed by the mint-time identity on BOTH rows. Today's branch returns today's receipt (recomputed).
    New branch = pooled-then-strata: (1) both rows carry attested pooled bounds, else HOLD; (2) the pooled intervals
    intersect (the 0.35.0 gate the row names as precondition), else reproduced_ok False with failing "pooled";
    (3) every aligned stratum carries bounds, else HOLD; (4) every aligned stratum's intervals intersect, else False."""
    if not (opted(orig) and opted(rep)):
        return "today", today_receipt(orig, rep, rule_applied)
    if any(x.get("value_lo") is None or x.get("value_hi") is None for x in (orig, rep)):
        return "new_branch", {"reproduced_ok": None, "held": "missing pooled bounds"}
    if orig["value_hi"] < rep["value_lo"] or rep["value_hi"] < orig["value_lo"]:
        return "new_branch", {"reproduced_ok": False, "failing_stratum": "pooled"}
    if not (has_bounds(orig) and has_bounds(rep)):
        return "new_branch", {"reproduced_ok": None, "held": "missing stratum bounds"}
    by = {s["id"]: s for s in rep["strata"]}
    for s in orig["strata"]:
        r = by.get(s["id"])
        if r is None: return "new_branch", {"reproduced_ok": None, "held": "missing stratum bounds"}
        if s["value_hi"] < r["value_lo"] or r["value_hi"] < s["value_lo"]:
            return "new_branch", {"reproduced_ok": False, "failing_stratum": s["id"]}
    return "new_branch", {"reproduced_ok": True}

def stance(prereq, row):
    """Keyed comprehension_accuracy_delta at_least reading, row precedence (3): oppose, then support, else unresolved."""
    assert prereq["metric"] == "comprehension_accuracy_delta" and "at_least" in prereq
    L = prereq["at_least"]
    if prereq.get("bound_reading") is None:
        return legacy_unkeyed_stance(row, L)   # 0.37.0 reading, unchanged: generic unresolved first, then point
    assert prereq["bound_reading"] == "attested_interval_v1"
    if not (opted(row) and row.get("attested")):
        return "unresolved"   # out of scope: identity AND attestation required; never point-satisfied
    strata = row["strata"]; any_degenerate = any(degenerate(s) for s in strata)
    pooled_lo, pooled_hi = row.get("value_lo"), row.get("value_hi")
    # OPPOSES: any nondegenerate required stratum upper bound below L, or the pooled interval (no degenerate component) upper bound below L
    for s in strata:
        if not degenerate(s) and s["value_hi"] < L: return "opposes"
    if not any_degenerate and pooled_hi is not None and pooled_hi < L: return "opposes"
    # SUPPORTS: pooled lower bound and every stratum lower bound reach L, and no arm in any required stratum is exactly 0 or 1
    if not any_degenerate and pooled_lo is not None and pooled_lo >= L and all(s["value_lo"] >= L for s in strata):
        return "supports"
    return "unresolved"

UNRESOLVED_BOUNDS = ("ceiling", "floor", "strata_unresolved")

def legacy_unkeyed_stance(row, L):
    """The register's existing unkeyed at_least reading, written from the SERVED row fields only:
    a row whose served resolution_bound is ceiling/floor/strata_unresolved has generic stance unresolved and the
    prerequisite reads unresolved; an inactive row reads unresolved; otherwise value >= at_least decides."""
    if row.get("resolution_bound") in UNRESOLVED_BOUNDS or row.get("generic_stance") == "unresolved": return "unresolved"
    if row.get("evidence_state") not in (None, "valid"): return "unresolved"
    return "supports" if row["value"] >= L else "opposes"

def veto_state(row):
    """The confirmed-loss veto reads only the generic stance and confirmation; neither new rule touches it."""
    return "vetoes" if row.get("confirmed") and row.get("generic_stance") == "opposes" else "no_veto"

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

def refuses_filer_bound(diff, constant=ROW_TOLERANCE): return diff > constant

# ---------------- fixtures ----------------
def st(id_, lo, hi, arms=None, value=None):
    return {"id": id_, "value_lo": lo, "value_hi": hi, "arms": arms or {"english": 0.7, "ainglish": 0.7}, "value": value if value is not None else (lo + hi) / 2}
OPT = {"settlement_analysis": IDENTITY}; NOOPT = {}
P5 = {"metric": "comprehension_accuracy_delta", "at_least": -5, "bound_reading": "attested_interval_v1"}
P9 = {"metric": "comprehension_accuracy_delta", "at_least": -5}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")); ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference_outcomes.json"))
    a = ap.parse_args()
    rows = {}
    for fp in glob.glob(f"{a.raw}/measurements/*.json"):
        m = json.load(open(fp)); rows[m["manifest_hash"]] = m
    props = {}
    for fp in glob.glob(f"{a.raw}/proposals/*.json"):
        p = json.load(open(fp)); props[p["slug"]] = p
    out = {}
    def fx(name, declared, got, ok): out[name] = {"declared": declared, "reference": got, "match": bool(ok)}

    # positive control of the legacy reimplementation against every served receipt
    n, mism = positive_control(rows)
    fx("legacy_receipt_control", "the reimplemented today-branch receipt equals the served receipt for every settled replication pair in the snapshot",
       {"pairs_checked": n, "mismatches": mism[:20], "mismatch_count": len(mism)}, n > 0 and not mism)

    # F1 opted/opted, per-form 0 vs +0.1, [-1,+1] vs [-0.9,+1.1]
    o = {"manifest": OPT, "value": 0.05, "value_lo": -1, "value_hi": 1, "strata": [st("a", -1, 1), st("b", -1, 1)]}; r = {"manifest": OPT, "value": 0.05, "value_lo": -0.9, "value_hi": 1.1, "strata": [st("a", -0.9, 1.1), st("b", -0.9, 1.1)]}
    g = settle_pair(o, r); fx("F1", "reproduced_ok true", g, g[0] == "new_branch" and g[1]["reproduced_ok"] is True)
    # F1b pooled-then-strata: pooled intervals DISJOINT while every stratum touches (Dexagon's witness fb5835e0/895db45a shape: [-12.5478,-0.9502] vs [0,0])
    o1b = {"manifest": OPT, "value": -6.835, "value_lo": -12.5478, "value_hi": -0.9502, "strata": [st("x", -5.34, 0.0), st("y", -22.43, 0.32)]}
    r1b = {"manifest": OPT, "value": 0, "value_lo": 0, "value_hi": 0, "strata": [st("x", 0, 0), st("y", 0, 0)]}
    g = settle_pair(o1b, r1b); fx("F1b", "pooled intervals disjoint, all strata touch: reproduced_ok false, failing 'pooled' (pooled-then-strata)", g, g[0] == "new_branch" and g[1]["reproduced_ok"] is False and g[1].get("failing_stratum") == "pooled")
    # F1c pooled intersects, one stratum disjoint
    r1c = {"manifest": OPT, "value": 0.05, "value_lo": -0.9, "value_hi": 1.1, "strata": [st("a", -0.9, 1.1), st("b", 1.5, 3)]}
    g = settle_pair(o, r1c); fx("F1c", "pooled intervals intersect, one stratum disjoint: reproduced_ok false, failing stratum b", g, g[0] == "new_branch" and g[1]["reproduced_ok"] is False and g[1].get("failing_stratum") == "b")
    r2 = {"manifest": OPT, "value": 0.05, "value_lo": -0.9, "value_hi": 1.1, "strata": [{"id": "a", "value_lo": None, "value_hi": None, "value": 0}, {"id": "b", "value_lo": None, "value_hi": None, "value": 0.1}]}
    g = settle_pair(o, r2); fx("F2", "reproduced_ok null, held", g, g[0] == "new_branch" and g[1]["reproduced_ok"] is None)
    r2p = {"manifest": OPT, "value": 0.05, "value_lo": None, "value_hi": None, "strata": [st("a", -0.9, 1.1), st("b", -0.9, 1.1)]}
    g = settle_pair(o, r2p); fx("F2p", "replication lacking attested POOLED bounds: reproduced_ok null, held (missing pooled bounds)", g, g[0] == "new_branch" and g[1]["reproduced_ok"] is None and g[1].get("held") == "missing pooled bounds")
    # F3 a pair with no intervals on either side, no identity: point-and-strata receipt, byte-identical
    o3 = {"manifest": NOOPT, "value": -10, "value_lo": -10, "value_hi": -10, "strata": [{"id": "a", "value": -12}, {"id": "b", "value": -8}]}
    r3 = {"manifest": NOOPT, "value": -9.5, "value_lo": -9.5, "value_hi": -9.5, "strata": [{"id": "a", "value": -11}, {"id": "b", "value": -8}]}
    direct = today_receipt(o3, r3, "point-and-strata-relative-v1"); g = settle_pair(o3, r3, "point-and-strata-relative-v1")
    fx("F3", "point-and-strata-relative-v1, byte-identical receipt", {"branch": g[0], "direct": direct, "via_selector": g[1], "byte_identical": canon(direct) == canon(g[1])},
       g[0] == "today" and canon(direct) == canon(g[1]) and direct["reproduced_ok"] is True)
    # F3b old/old attested stratified pair WITHOUT identity (the live cell-failed shape): served receipt == recomputed == selector output
    live = [m for m in rows.values() if m.get("is_replication") and (m.get("replication_comparison") or {}).get("rule_applied") == "interval-overlap-commensurable-v1"
            and (m.get("replication_comparison") or {}).get("aggregate_reproduced_ok") is True and m.get("reproduced_ok") is False and rows.get(m.get("replicates_hash"))]
    live.sort(key=lambda m: m["manifest_hash"]); m3b = live[0]; o3b = rows[m3b["replicates_hash"]]
    served = served_receipt(m3b); g = settle_pair(vals(o3b) | {"manifest": o3b.get("manifest") or {}}, vals(m3b) | {"manifest": m3b.get("manifest") or {}}, "interval-overlap-commensurable-v1")
    fx("F3b", "today's receipt byte for byte on read and recomputation; reproduced_ok false stays false",
       {"pair": [m3b["manifest_hash"][:8], o3b["manifest_hash"][:8]], "branch": g[0], "served": served, "via_selector": g[1], "byte_identical": canon(served) == canon(g[1]), "live_cell_failed_pairs": len(live)},
       g[0] == "today" and canon(served) == canon(g[1]) and g[1]["reproduced_ok"] is False)
    # F3c mixed pair, one row opted: today's branch, today's result (same served receipt)
    g = settle_pair(vals(o3b) | {"manifest": OPT}, vals(m3b) | {"manifest": m3b.get("manifest") or {}}, "interval-overlap-commensurable-v1")
    fx("F3c", "mixed pair: today's branch, today's result", {"branch": g[0], "via_selector": g[1], "byte_identical_to_served": canon(served) == canon(g[1])}, g[0] == "today" and canon(served) == canon(g[1]))
    # F3d joint mask vs local, DETERMINISTIC: every cell value derived by sha256, expected outcome pinned as literals
    def arm_for(seed, reader, item): return "ainglish" if hashlib.sha256(f"{seed}|{reader}|{item}".encode()).digest()[0] % 2 == 1 else "english"
    def correct_for(seed, reader, item): return hashlib.sha256(f"correct|{seed}|{reader}|{item}".encode()).digest()[0] % 3 != 0
    seed = F3D_SEED; readers = ["r1", "r2"]
    items = sorted([{"id": f"a-{i:02d}", "stratum": "a"} for i in range(6)] + [{"id": f"b-{i:02d}", "stratum": "b"} for i in range(3)], key=lambda x: x["id"])
    cells = []
    for it in items:
        for rd in readers:
            arm = arm_for(seed, rd, it["id"]); correct = correct_for(seed, rd, it["id"])
            if it["stratum"] == "b" and it["id"] != "b-00" and arm == "english": correct = None   # only b-00 has a live english cell
            cells.append({"item_id": it["id"], "reader": rd, "arm": arm, "correct": correct})
    cells.sort(key=lambda c: (c["item_id"], c["reader"]))
    att = {"items": items, "readers": readers, "cells": cells, "seed": seed}
    contract = [{"id": "a", "weight": 1, "share": 0.5}, {"id": "b", "weight": 1, "share": 0.5}]
    joint = replay(att, contract)
    by_item = cells_by_item(cells, items); local = {}
    for row in contract:
        src = [it["id"] for it in items if it["stratum"] == row["id"]]; v_ = []
        for d in range(DRAWS):
            v = sample_value([src[draw_index(seed, row["id"], d, p, len(src))] for p in range(len(src))], by_item)
            if v is not None: v_.append(v)
        lo, hi, n_ = quantiles(v_); local[row["id"]] = {"lo": lo, "hi": hi, "accepted": n_}
    f3d = {"cells_sha256": hashlib.sha256(canon(cells).encode()).hexdigest(), "joint_accepted": joint["accepted"],
           "joint_strata": {k: {"lo": v["lo"], "hi": v["hi"], "accepted": v["accepted"]} for k, v in joint["strata"].items()}, "local_strata": local,
           "differs_for_a": (joint["strata"]["a"]["lo"], joint["strata"]["a"]["hi"]) != (local["a"]["lo"], local["a"]["hi"])}
    fx("F3d", "served stratum bounds equal the joint-mask quantiles, not the local ones (complete expected outcome pinned in EXPECTED_F3D)",
       f3d, EXPECTED_F3D is not None and canon(f3d) == canon(EXPECTED_F3D))
    # F4 rounding boundary, row wording governs
    b = {"0.0001": refuses_filer_bound(0.0001), "0.000105": refuses_filer_bound(0.000105), "0.00011": refuses_filer_bound(0.00011), "0.000111": refuses_filer_bound(0.000111)}
    fx("F4", "filer stratum bounds differing from the replay by more than 0.0001: 422",
       {"reference_constant": ROW_TOLERANCE, "refused": b, "server_constant_at_5723faa": SERVER_TOLERANCE_5723faa,
        "implementation_note": "IntervalProvenance::TOLERANCE must move from 0.00011 to 0.0001 when the row is implemented; the row's wording is the falsifier and is not amended"},
       b["0.0001"] is False and b["0.000105"] is True and b["0.00011"] is True and b["0.000111"] is True)
    # F5..F8 keyed reading with pooled bounds
    r5 = {"manifest": OPT, "attested": True, "value": -0.5, "value_lo": -2, "value_hi": 1, "resolution_bound": "resolvable", "evidence_state": "valid", "strata": [st("a", -3, 2), st("b", -4, 1)]}
    fx("F5", "supports", stance(P5, r5), stance(P5, r5) == "supports")
    r6 = {"manifest": OPT, "attested": True, "value": -3, "value_lo": -6, "value_hi": -1, "strata": [st("a", -3, 2), st("b", -7, -6)]}
    fx("F6", "opposes", stance(P5, r6), stance(P5, r6) == "opposes")
    r7 = {"manifest": OPT, "attested": True, "value": -3, "value_lo": -6, "value_hi": 0, "strata": [st("a", -3, 2), st("b", -7, 1)]}
    fx("F7", "unresolved", stance(P5, r7), stance(P5, r7) == "unresolved")
    d8 = st("b", 0, 0, arms={"english": 1, "ainglish": 1})
    r8 = {"manifest": OPT, "attested": True, "value": -1, "value_lo": -2, "value_hi": 1, "strata": [st("a", -3, 2), d8]}
    fx("F8", "unresolved, pooled bound served reported-only", stance(P5, r8), stance(P5, r8) == "unresolved")
    r8b = {"manifest": OPT, "attested": True, "value": -3, "value_lo": -6, "value_hi": -3, "strata": [st("a", -7, -6), d8]}
    fx("F8b", "opposes; the degenerate form does not erase it", stance(P5, r8b), stance(P5, r8b) == "opposes")
    fx("F8c", "UNRESOLVED (out of scope); generic stance and settlement receipt unchanged", stance(P5, {"manifest": NOOPT, "attested": True, "value": -1, "value_lo": -3, "value_hi": 2, "strata": [st("a", -3, 2)]}),
       stance(P5, {"manifest": NOOPT, "attested": True, "value": -1, "value_lo": -3, "value_hi": 2, "strata": [st("a", -3, 2)]}) == "unresolved")
    r8d = {"manifest": NOOPT, "attested": True, "value": -1, "value_lo": -20, "value_hi": 18, "resolution_bound": "resolvable", "evidence_state": "valid", "strata": [st("a", -20, 18)]}
    g = {"keyed": stance(P5, r8d), "unkeyed": stance(P9, r8d)}
    fx("F8d", "keyed: UNRESOLVED not supports (0.37.0 point would pass); without bound_reading: supports", g, g["keyed"] == "unresolved" and g["unkeyed"] == "supports")
    fx("F8e", "mint against keyed contract without identity: rejected before inference", mint_check([P5], NOOPT), mint_check([P5], NOOPT).startswith("rejected"))
    # pooled-bound cases (Dexagon item 5): pooled decides while strata alone would not
    rp1 = {"manifest": OPT, "attested": True, "value": -6, "value_lo": -8, "value_hi": -5.5, "strata": [st("a", -9, -3), st("b", -9, -3)]}
    rp2 = {"manifest": OPT, "attested": True, "value": -1, "value_lo": -6, "value_hi": 2, "strata": [st("a", -4, 2), st("b", -4, 2)]}
    fx("F5p", "pooled upper bound below -5 with every stratum straddling: OPPOSES (pooled condition, no degenerate component)", stance(P5, rp1), stance(P5, rp1) == "opposes")
    fx("F5q", "every stratum lower bound at or above -5 but pooled lower bound below: UNRESOLVED, not supports", stance(P5, rp2), stance(P5, rp2) == "unresolved")
    # real replayed rows where the pooled bound decides at L=-5 (labelled by their manifest hash; from the frozen raw snapshot)
    real = replayed_pooled_cases(rows)
    fx("F5r", "two real attested stratified rows read under the keyed contract at -5, with replayed pooled and stratum bounds (support and opposition)", real,
       real.get("supports") is not None and real.get("opposes") is not None and real["supports"]["stance"] == "supports" and real["opposes"]["stance"] == "opposes")
    fx("F9", "the 0.37.0 point reading, unchanged", stance(P9, r5), stance(P9, r5) == "supports")
    # F10 the live typed comprehension at_least contracts: legacy label from an INDEPENDENT baseline (served metadata, and
    # Dexagon's read-only PHP oracle receipt pinned under audit_inputs/), compared with the candidate's legacy branch.
    oracle_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_inputs", "dexagon-legacy-stance-oracle.json")
    oracle = json.load(open(oracle_path)); oracle_sha = hashlib.sha256(open(oracle_path, "rb").read()).hexdigest()
    oracle_by = {o_["hash"]: o_ for o_ in oracle["observations"]}
    live_c = []; oracle_rows_seen = 0
    for s, p in sorted(props.items()):
        for pre in ((p.get("evidence_contract") or {}).get("prerequisites") or []):
            if isinstance(pre, dict) and pre.get("metric") == "comprehension_accuracy_delta" and "at_least" in pre:
                cad = sorted([m for m in (p.get("measurements") or []) if m.get("metric") == "comprehension_accuracy_delta" and m.get("evidence_state") == "valid"], key=lambda m: m.get("manifest_hash") or "")
                reads = []
                for m in cad:
                    h = m.get("manifest_hash"); L = pre["at_least"]
                    # baseline (i): served fields only, no candidate code
                    served_generic = "unresolved" if m.get("resolution_bound") in UNRESOLVED_BOUNDS else ("supports" if m["value"] >= L else "opposes")
                    # baseline (ii): the PHP oracle receipt, if it covers this row
                    orc = oracle_by.get(h); oracle_rows_seen += 1 if orc else 0
                    row = {"manifest": {}, "attested": bool(m.get("interval_provenance")), "value": m["value"], "value_lo": m.get("value_lo"), "value_hi": m.get("value_hi"),
                           "resolution_bound": m.get("resolution_bound"), "evidence_state": m.get("evidence_state"), "strata": []}
                    after = stance(pre, row)   # the candidate's legacy branch (no bound_reading on this contract)
                    reads.append({"hash": (h or "")[:8], "value": m["value"], "resolution_bound": m.get("resolution_bound"),
                                  "legacy_from_served_fields": served_generic, "legacy_from_php_oracle": orc["legacy_prerequisite_stance"] if orc else None,
                                  "candidate_legacy_branch": after,
                                  "identical": served_generic == after and (orc is None or orc["legacy_prerequisite_stance"] == after)})
                live_c.append({"slug": s, "prerequisite": pre, "rows": reads, "row_count": len(reads), "vacuous": len(reads) == 0, "identical": all(x["identical"] for x in reads)})
    # synthetic nondegenerate rows that actually exercise the point comparator on the legacy branch
    synth = [{"value": 1.0, "resolution_bound": "resolvable", "evidence_state": "valid"}, {"value": -1.0, "resolution_bound": "resolvable", "evidence_state": "valid"}]
    synth_reads = [{"value": r_["value"], "legacy_from_served_fields": ("supports" if r_["value"] >= 0 else "opposes"), "candidate_legacy_branch": stance({"metric": "comprehension_accuracy_delta", "at_least": 0}, r_ | {"manifest": {}, "strata": []})} for r_ in synth]
    populated = [c_ for c_ in live_c if not c_["vacuous"]]
    f10 = {"oracle_receipt_sha256": oracle_sha, "oracle_source_sha256": oracle.get("source_sha256"), "oracle_rows_matched": oracle_rows_seen, "contracts": live_c,
           "populated_contracts": len(populated), "vacuous_contracts": [c_["slug"] for c_ in live_c if c_["vacuous"]], "synthetic_point_cases": synth_reads}
    fx("F10", "the live typed comprehension at_least contracts read identically before and after; the two populated frozen rows a9d3a180/763f2a41 read UNRESOLVED on both baselines; the empty contract is counted as vacuous",
       f10, len(live_c) >= 1 and all(c_["identical"] for c_ in live_c) and len(populated) >= 1
           and all(x["legacy_from_served_fields"] == "unresolved" and x["legacy_from_php_oracle"] == "unresolved" and x["candidate_legacy_branch"] == "unresolved" for c_ in populated for x in c_["rows"])
           and oracle_rows_seen == sum(len(c_["rows"]) for c_ in populated)
           and all(x["legacy_from_served_fields"] == x["candidate_legacy_branch"] for x in synth_reads) and synth_reads[0]["candidate_legacy_branch"] == "supports" and synth_reads[1]["candidate_legacy_branch"] == "opposes")
    # F11 confirmed generic-stance loss whose lower bound is above -5: veto state unchanged
    r11 = {"manifest": OPT, "attested": True, "confirmed": True, "generic_stance": "opposes", "value": -3, "value_lo": -4.5, "value_hi": -1.5, "strata": [st("a", -4.5, -1.5)]}
    before = veto_state(r11); keyed_read = stance(P5, r11); after = veto_state(r11)
    fx("F11", "confirmed generic-stance loss with lower bound above -5: veto state unchanged", {"veto_before": before, "keyed_prerequisite_reading": keyed_read, "veto_after": after},
       before == "vetoes" and after == before and keyed_read == "supports")
    v = {"other_metric": contract_validation({"metric": "token_delta", "at_most": 0, "bound_reading": "attested_interval_v1"}),
         "beside_at_most": contract_validation({"metric": "comprehension_accuracy_delta", "at_most": 0, "bound_reading": "attested_interval_v1"}),
         "other_value": contract_validation({"metric": "comprehension_accuracy_delta", "at_least": -5, "bound_reading": "v2"})}
    fx("validation", "reject bound_reading on other metric / beside at_most / other value", v, all(x.startswith("rejected") for x in v.values()))
    # before/after oracle (candidate.py transforms the snapshot; oracle.py, which imports nothing from candidate.py, diffs surfaces)
    op = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oracle_result.json")
    if os.path.exists(op):
        orr = json.load(open(op))
        fx("uvf_before_after_oracle", "candidate transformation of the frozen snapshot changes zero verdict surfaces and selects zero pairs/contracts for the new branch; the positive control (one synthetic opted pair injected) changes exactly one surface and the oracle reports it",
           orr, orr.get("snapshot", {}).get("changed_surfaces") == 0 and orr.get("snapshot", {}).get("new_branch_pairs") == 0 and orr.get("snapshot", {}).get("keyed_contracts") == 0
               and orr.get("positive_control", {}).get("changed_surfaces") == 1 and orr.get("positive_control", {}).get("new_branch_pairs") == 1)
    cp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "controls_result.json")
    if os.path.exists(cp):
        cr = json.load(open(cp))
        ts, ro = cr.get("two_state", {}), cr.get("replication_only", {})
        fx("keyed_selection_controls", "two-state control: the sole comprehension original UNCONFIRMED leaves the keyed requirement unresolved (not satisfied); the identical original CONFIRMED engages the reading and satisfies it; replication-only control: a keyed contract whose only comprehension rows are replications selects zero originals and reads missing, never satisfied",
           cr, ts.get("unconfirmed", {}).get("bucket") == "unresolved" and ts.get("unconfirmed", {}).get("satisfied") is False
               and ts.get("confirmed", {}).get("bucket") == "satisfied" and ts.get("confirmed", {}).get("satisfied") is True
               and ro.get("bucket") == "missing" and ro.get("satisfied") is False and ro.get("active_originals") == 0 and ro.get("replications_excluded", 0) >= 1)
    allm = all(x["match"] for x in out.values())
    json.dump(out, open(a.out, "w"), indent=1, default=str, sort_keys=True)
    print(json.dumps({k: {"match": x["match"], "declared": x["declared"]} for k, x in out.items()}, indent=1))
    print("OUTCOMES_SHA256", hashlib.sha256(canon(out).encode()).hexdigest())
    print("ALL_MATCH", allm)
    if not allm: sys.exit(1)

def replayed_pooled_cases(rows, L=-5):
    """Find real attested stratified rows where, read under {at_least L, bound_reading}, the pooled bound is decisive:
    opposes: pooled hi < L, no degenerate arm, and NO single nondegenerate stratum hi < L;
    supports: pooled lo >= L and every stratum lo >= L and no degenerate arm."""
    from replay import check_row
    found = {"supports": None, "opposes": None, "rule": f"at_least {L}, bound_reading attested_interval_v1, identity assumed present for the counterfactual read"}
    for h in sorted(rows):
        m = rows[h]
        if not (m.get("interval_provenance_attestation") and (m.get("manifest") or {}).get("settlement_strata") and m.get("stratum_results")): continue
        r = check_row(m)
        if not (r and r["pooled_match"] and r["strata"]): continue
        arms = {s["id"]: s.get("arms") or {} for s in m["stratum_results"]}
        strata = [{"id": k, "value_lo": v["lo"], "value_hi": v["hi"], "arms": arms.get(k, {})} for k, v in r["strata"].items()]
        row = {"manifest": {"settlement_analysis": IDENTITY}, "attested": True, "value": m["value"], "value_lo": r["replayed"][0], "value_hi": r["replayed"][1], "strata": strata}
        s_ = stance({"metric": "comprehension_accuracy_delta", "at_least": L, "bound_reading": "attested_interval_v1"}, row)
        if any(degenerate(s) for s in strata): continue
        rec = {"hash": h[:12], "value": m["value"], "pooled": r["replayed"], "strata": {s["id"]: [s["value_lo"], s["value_hi"]] for s in strata}, "stance": s_}
        if s_ == "opposes" and found["opposes"] is None and not any(s["value_hi"] < L for s in strata): found["opposes"] = rec
        if s_ == "supports" and found["supports"] is None: found["supports"] = rec
        if found["supports"] and found["opposes"]: break
    return found

# F3d fixture seed: the first value in the scan 20260917, 20260918, ... whose joint-mask quantiles for stratum a differ from its
# locally valid quantiles (20260917-20260919 happen to coincide on a). Fixed here; every cell value is sha256-derived, so the
# fixture is identical in every process regardless of PYTHONHASHSEED. The complete expected outcome is pinned below.
F3D_SEED = 20260920
EXPECTED_F3D = {"cells_sha256": "d3076001359db1fca0d7b8068f189bebb9ee9d83fc6c0e1a5da06b03c372111b", "differs_for_a": True, "joint_accepted": 1367,
  "joint_strata": {"a": {"accepted": 1367, "hi": 55.55555555555556, "lo": -25.0}, "b": {"accepted": 1367, "hi": -60.0, "lo": -100.0}},
  "local_strata": {"a": {"accepted": 1998, "hi": 50.0, "lo": -25.0}, "b": {"accepted": 1369, "hi": -60.0, "lo": -100.0}}}
if __name__ == "__main__":
    main()
