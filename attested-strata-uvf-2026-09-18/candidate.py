"""Executable CANDIDATE transformation for protocol row a-gpjvfpt63g2zq0cx (attested-strata-v1), applied to a frozen snapshot.
It recomputes every verdict surface census.py counts, exactly as census.py projects them, but with the row's two rules
switched on: (1) pair settlement branch keyed by the mint-time identity on BOTH rows (reference.settle_pair, pooled-then-strata),
(2) the keyed at_least reading for contracts carrying bound_reading (reference.stance). Rows/contracts the predicates do not
select are copied through unchanged, so any difference between surfaces_before.json and surfaces_after.json is attributable
to the candidate rules. oracle.py (which does NOT import this module) diffs the two files.
Usage: python3 candidate.py --raw raw/ --before surfaces_before.json --out surfaces_after.json [--inject-control DIR] [--controls controls_result.json]
Revision 3: the keyed reading inherits the register selection (active originals, confirmed subset; replications never stand as originals).
--inject-control writes a modified copy of the snapshot under DIR in which one existing cell-failed interval pair is given the
identity on both manifests (nothing else changes); running candidate.py on that copy is the positive control."""
import json, glob, os, sys, argparse, shutil, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference import settle_pair, stance, IDENTITY, vals, active_originals, confirmed_originals, requirement_state
from replay import check_row

def load(raw):
    rows = {}; props = {}
    for fp in sorted(glob.glob(f"{raw}/measurements/*.json")):
        m = json.load(open(fp)); rows[m["manifest_hash"]] = m
    for fp in sorted(glob.glob(f"{raw}/proposals/*.json")):
        p = json.load(open(fp)); props[p["slug"]] = p
    return rows, props

def g(d, *ks):
    for k in ks: d = d.get(k) if isinstance(d, dict) else None
    return d

def attested_row(m, widths_cache):
    """Row dict for reference.settle_pair/stance with REPLAYED pooled + stratum bounds (never the filer's)."""
    h = m["manifest_hash"]
    if h not in widths_cache:
        r = check_row(m) if m.get("interval_provenance_attestation") else None
        widths_cache[h] = r
    r = widths_cache[h]
    arms = {s["id"]: s.get("arms") or {} for s in (m.get("stratum_results") or [])}
    if not r: return {"manifest": m.get("manifest") or {}, "attested": False, "value": m["value"], "value_lo": None, "value_hi": None, "strata": [], "resolution_bound": m.get("resolution_bound"), "evidence_state": m.get("evidence_state")}
    return {"manifest": m.get("manifest") or {}, "attested": bool(r["pooled_match"]), "value": m["value"], "value_lo": r["replayed"][0], "value_hi": r["replayed"][1],
            "resolution_bound": m.get("resolution_bound"), "evidence_state": m.get("evidence_state"),
            "strata": [{"id": k, "value_lo": v["lo"], "value_hi": v["hi"], "value": None, "arms": arms.get(k, {})} for k, v in r["strata"].items()]}

def transform(rows, props, before):
    """Return (surfaces_after, report). Surfaces keep census.py's exact shape and key set."""
    after = json.loads(json.dumps(before)); widths = {}
    new_branch_pairs = []; keyed = []; keyed_detail = []
    for h, m in rows.items():
        if not m.get("is_replication"): continue
        o = rows.get(m.get("replicates_hash"))
        if not o: continue
        if (m.get("manifest") or {}).get("settlement_analysis") == IDENTITY and (o.get("manifest") or {}).get("settlement_analysis") == IDENTITY:
            branch, res = settle_pair(attested_row(o, widths), attested_row(m, widths), g(m, "replication_comparison", "rule_applied") or "point-and-strata-relative-v1")
            assert branch == "new_branch"
            new_branch_pairs.append(h)
            after[f"m:{h}"]["reproduced_ok"] = res["reproduced_ok"]
            # the pooled gate is the first check of the new branch, so the aggregate flag follows it
            after[f"m:{h}:agg"] = None if res["reproduced_ok"] is None else (res.get("failing_stratum") != "pooled")
    for slug, p in props.items():
        for pre in ((p.get("evidence_contract") or {}).get("prerequisites") or []):
            if isinstance(pre, dict) and pre.get("bound_reading"):
                keyed.append((slug, pre))
                # Revision 3 (Dexagon bbdd711e): the register's readiness selection is inherited BEFORE the bound reading:
                # active ORIGINALS only (never a replication), then only CONFIRMED originals feed stances. An unconfirmed
                # original leaves a bounded requirement unresolved; a replication never stands as an original.
                ms_ = p.get("measurements") or []
                act = active_originals(ms_); conf = confirmed_originals(ms_)
                repl_excluded = sum(1 for m in ms_ if m.get("metric") == "comprehension_accuracy_delta" and (m.get("is_replication") or m.get("replicates_hash")))
                stances = [stance(pre, attested_row(rows.get(m.get("manifest_hash"), m), widths)) for m in conf]
                bucket = requirement_state(stances, len(act))
                keyed_detail.append({"slug": slug, "active_originals": len(act), "confirmed_originals": len(conf), "replications_excluded": repl_excluded, "stances": stances, "bucket": bucket})
                sat = set(after[f"p:{slug}"].get("readiness_satisfied") or []); miss = set(after[f"p:{slug}"].get("readiness_missing") or [])
                unres = set(after[f"p:{slug}"].get("readiness_unresolved") or []); opp = set(after[f"p:{slug}"].get("readiness_opposing") or [])
                for S in (sat, miss, unres, opp): S.discard("comprehension_accuracy_delta")
                {"missing": miss, "opposing": opp, "unresolved": unres, "satisfied": sat}[bucket].add("comprehension_accuracy_delta")
                after[f"p:{slug}"]["readiness_satisfied"] = sorted(sat); after[f"p:{slug}"]["readiness_missing"] = sorted(miss)
                after[f"p:{slug}"]["readiness_unresolved"] = sorted(unres); after[f"p:{slug}"]["readiness_opposing"] = sorted(opp)
    return after, {"new_branch_pairs": new_branch_pairs, "keyed_contracts": [k[0] for k in keyed], "keyed_detail": keyed_detail}

def inject_control(raw, out_dir, rows):
    """Copy the snapshot; give ONE existing cell-failed interval-rule pair (lowest replication hash) the identity on both manifests."""
    if os.path.exists(out_dir): shutil.rmtree(out_dir)
    shutil.copytree(raw, out_dir)
    cands = sorted(h for h, m in rows.items() if m.get("is_replication") and g(m, "replication_comparison", "rule_applied") == "interval-overlap-commensurable-v1"
                   and g(m, "replication_comparison", "aggregate_reproduced_ok") is True and m.get("reproduced_ok") is False and rows.get(m.get("replicates_hash")) and m.get("interval_provenance_attestation") and rows[m["replicates_hash"]].get("interval_provenance_attestation"))
    h = cands[0]; o = rows[h]["replicates_hash"]
    for x in (h, o):
        fp = f"{out_dir}/measurements/{x}.json"; m = json.load(open(fp)); m.setdefault("manifest", {})["settlement_analysis"] = IDENTITY
        json.dump(m, open(fp, "w"), indent=1, sort_keys=True)
    return {"replication": h, "original": o}

CONTROL_SOURCE = "b2d2e231ec71a2fcd17b07e467e5213a09ab61aa40033fdd3167aec1e259c31f"   # the retained attested row F5r reads as pooled support

def controls(rows):
    """Executable selection controls (Revision 3, Dexagon bbdd711e). Synthetic, clearly labelled, never submit-ready:
    (a) two-state: one comprehension ORIGINAL built from CONTROL_SOURCE's retained cells with the identity, under a keyed
        contract {at_least -5, bound_reading}; run unconfirmed (confirmed=false, counts_toward_verdict=false) then confirmed.
    (b) replication-only: the same row marked as a replication of another hash; no original exists."""
    base = rows[CONTROL_SOURCE]; L = -5
    pre = {"metric": "comprehension_accuracy_delta", "at_least": L, "bound_reading": "attested_interval_v1"}
    def synth(confirmed, as_replication):
        m = json.loads(json.dumps(base)); m["manifest"] = dict(m.get("manifest") or {}); m["manifest"]["settlement_analysis"] = IDENTITY
        m["manifest_hash"] = "synthetic-" + ("replication" if as_replication else "original") + ("-confirmed" if confirmed else "-unconfirmed")
        m.update(confirmed=confirmed, counts_toward_verdict=confirmed, evidence_state="valid", voided_at=None, retraction=None,
                 is_replication=as_replication, replicates_hash=("synthetic-absent-original" if as_replication else None),
                 synthetic_not_submit_ready=True)
        return m
    def run(m):
        slug = "synthetic-control"; key = f"p:{slug}"
        p = {"slug": slug, "stage": "seconded", "evidence_contract": {"claim_carrier": ["unclaimed_verdict_flips"], "prerequisites": [pre]}, "measurements": [m]}
        before = {key: {"stage": "seconded", "readiness_satisfied": [], "readiness_missing": ["comprehension_accuracy_delta"], "readiness_unresolved": [], "readiness_opposing": []}}
        after, rep = transform({m["manifest_hash"]: m, CONTROL_SOURCE: base}, {slug: p}, before)
        d = rep["keyed_detail"][0]
        return {"input": {"confirmed": m["confirmed"], "counts_toward_verdict": m["counts_toward_verdict"], "is_replication": m["is_replication"], "replicates_hash": m["replicates_hash"]},
                "active_originals": d["active_originals"], "confirmed_originals": d["confirmed_originals"], "replications_excluded": d["replications_excluded"],
                "stances": d["stances"], "bucket": d["bucket"], "satisfied": "comprehension_accuracy_delta" in after[key]["readiness_satisfied"], "readiness_after": after[key]}
    return {"scope": "synthetic selection controls; not measurements, never submit-ready; retained cells of " + CONTROL_SOURCE[:12],
            "contract": pre,
            "two_state": {"unconfirmed": run(synth(False, False)), "confirmed": run(synth(True, False))},
            "replication_only": run(synth(False, True))}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", required=True); ap.add_argument("--before", required=True); ap.add_argument("--out", required=True); ap.add_argument("--inject-control", default=None); ap.add_argument("--report", default=None); ap.add_argument("--controls", default=None)
    a = ap.parse_args()
    rows, props = load(a.raw)
    if a.controls:
        cr = controls(rows); json.dump(cr, open(a.controls, "w"), indent=1, sort_keys=True)
        print(json.dumps({"two_state": {k: v["bucket"] for k, v in cr["two_state"].items()}, "replication_only": cr["replication_only"]["bucket"]})); return
    if a.inject_control:
        inj = inject_control(a.raw, a.inject_control, rows)
        json.dump(inj, open(os.path.join(a.inject_control, "INJECTED.json"), "w"), indent=1); print("injected", inj); return
    before = json.load(open(a.before))
    after, rep = transform(rows, props, before)
    json.dump(after, open(a.out, "w"), sort_keys=True, indent=0, default=str)
    rep["surfaces_after_sha256"] = hashlib.sha256(json.dumps(after, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    if a.report: json.dump(rep, open(a.report, "w"), indent=1)
    print(json.dumps({"new_branch_pairs": len(rep["new_branch_pairs"]), "keyed_contracts": len(rep["keyed_contracts"]), "surfaces_after_sha256": rep["surfaces_after_sha256"]}))

if __name__ == "__main__":
    main()
