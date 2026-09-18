"""INDEPENDENT before/after oracle for the attested-strata-v1 candidate. Imports nothing from candidate.py or reference.py.
Reads surfaces_before.json, surfaces_after.json and the raw snapshot, and reports: the exact set of changed surfaces
(key, before, after); how many replication pairs carry the identity on BOTH manifests (the pairs the candidate may change);
how many contracts carry bound_reading. Asserts nothing about what the candidate SHOULD do: it only counts and diffs, so the
same script run on the positive-control snapshot must report exactly the injected change.
Usage: python3 oracle.py --raw raw/ --before surfaces_before.json --after surfaces_after.json --label snapshot --out oracle_result.json [--merge]"""
import json, glob, argparse, os, hashlib
IDENTITY = "attested-strata-v1"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", required=True); ap.add_argument("--before", required=True); ap.add_argument("--after", required=True); ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    before = json.load(open(a.before)); after = json.load(open(a.after))
    assert set(before) == set(after), "surface key sets differ"
    changed = [{"surface": k, "before": before[k], "after": after[k]} for k in sorted(before) if json.dumps(before[k], sort_keys=True) != json.dumps(after[k], sort_keys=True)]
    rows = {}
    for fp in glob.glob(f"{a.raw}/measurements/*.json"):
        m = json.load(open(fp)); rows[m["manifest_hash"]] = m
    pairs = [h for h, m in rows.items() if m.get("is_replication") and m.get("replicates_hash") in rows
             and (m.get("manifest") or {}).get("settlement_analysis") == IDENTITY and (rows[m["replicates_hash"]].get("manifest") or {}).get("settlement_analysis") == IDENTITY]
    keyed = []
    for fp in glob.glob(f"{a.raw}/proposals/*.json"):
        p = json.load(open(fp))
        for pre in ((p.get("evidence_contract") or {}).get("prerequisites") or []):
            if isinstance(pre, dict) and pre.get("bound_reading"): keyed.append(p["slug"])
    changed_keys = {c["surface"] for c in changed}
    attributable = all(any(c.startswith(f"m:{h}") for h in pairs) or any(c == f"p:{s}" for s in keyed) for c in changed_keys)
    res = {"surfaces": len(before), "changed_surfaces": len(changed), "changed": changed[:50], "new_branch_pairs": len(pairs), "new_branch_pair_hashes": pairs, "keyed_contracts": len(keyed),
           "every_change_attributable_to_a_selected_pair_or_contract": attributable,
           "before_sha256": hashlib.sha256(json.dumps(before, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest(),
           "after_sha256": hashlib.sha256(json.dumps(after, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()}
    out = json.load(open(a.out)) if a.merge and os.path.exists(a.out) else {}
    out[a.label] = res
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps({a.label: {k: v for k, v in res.items() if k not in ("changed", "new_branch_pair_hashes")}}))

if __name__ == "__main__":
    main()
