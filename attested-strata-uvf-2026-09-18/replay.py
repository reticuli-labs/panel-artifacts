"""Independent Python port of IntervalProvenance::bootstrap (register src/Service/IntervalProvenance.php @766bc18).
Replays the attested item bootstrap from the SERVED attestation journal (items, readers, cells, seed) and returns
pooled lo/hi (positive control against served value_lo/value_hi) plus per-stratum lo/hi over the joint accepted mask
(the proposed attested-strata-v1 reading). No register code is imported; hashing is stdlib sha256."""
import hashlib, struct, json, math
KIND = "ainglish.panel.bootstrap-items-attestation.v1"
DRAWS = 2000

def draw_index(seed, stratum, draw, position, population):
    b = hashlib.sha256(b"\0".join([KIND.encode(), str(seed).encode(), stratum.encode(), str(draw).encode(), str(position).encode()])).digest()
    high, low = struct.unpack(">II", b[:8])
    base_mod = 4294967296 % population
    return ((high % population) * base_mod + (low % population)) % population

def cells_by_item(cells, items):
    out = {it["id"]: [] for it in items}
    for c in cells: out[c["item_id"]].append(c)
    return out

def totals(ids, by_item):
    t = {"english": [0, 0], "ainglish": [0, 0]}  # correct, live
    for i in ids:
        for c in by_item[i]:
            if not isinstance(c["correct"], bool): continue
            t[c["arm"]][1] += 1
            t[c["arm"]][0] += 1 if c["correct"] else 0
    return t

def sample_value(sample, by_item):
    t = totals(sample, by_item)
    if t["english"][1] == 0 or t["ainglish"][1] == 0: return None
    return 100.0 * (t["ainglish"][0] / t["ainglish"][1] - t["english"][0] / t["english"][1])

def quantiles(est):
    est = sorted(est); n = len(est)
    return est[(25 * n) // 1000], est[(975 * n) // 1000], n

def replay(attestation, contract):
    """contract: list of {id, weight, share} (manifest settlement_strata with shares) or None.
    Returns dict(pooled_lo, pooled_hi, accepted, strata: {id: {lo, hi, width, accepted}})"""
    items = attestation["items"]; cells = attestation["cells"]; seed = attestation["seed"]
    by_item = cells_by_item(cells, items)
    if contract is None:
        ids = [it["id"] for it in items]; est = []
        for d in range(DRAWS):
            sample = [ids[draw_index(seed, "", d, p, len(ids))] for p in range(len(ids))]
            v = sample_value(sample, by_item)
            if v is not None: est.append(v)
        lo, hi, n = quantiles(est)
        return {"pooled_lo": lo, "pooled_hi": hi, "accepted": n, "strata": None}
    sources = {}
    for row in contract:
        sources[row["id"]] = [it["id"] for it in items if it["stratum"] == row["id"]]
        assert sources[row["id"]], f"no item for stratum {row['id']}"
    est = []; per = {row["id"]: [] for row in contract}
    for d in range(DRAWS):
        parts = {}
        for row in contract:
            src = sources[row["id"]]
            sample = [src[draw_index(seed, row["id"], d, p, len(src))] for p in range(len(src))]
            parts[row["id"]] = sample_value(sample, by_item)
        if any(v is None for v in parts.values()):
            continue  # joint accepted-draw mask: the whole draw is rejected, in every stratum
        est.append(sum(row["share"] * parts[row["id"]] for row in contract))
        for k, v in parts.items(): per[k].append(v)
    lo, hi, n = quantiles(est)
    strata = {}
    for k, vals in per.items():
        slo, shi, sn = quantiles(vals)
        strata[k] = {"lo": slo, "hi": shi, "width": shi - slo, "accepted": sn}
    return {"pooled_lo": lo, "pooled_hi": hi, "accepted": n, "strata": strata}

def contract_from_manifest(manifest):
    ss = manifest.get("settlement_strata")
    if not ss: return None
    # shares: manifest may give weight only; server MeasurementStrata::contract derives share = weight / sum(weights)
    total = sum(float(r.get("weight", 1)) for r in ss)
    return [{"id": r["id"], "weight": float(r.get("weight", 1)), "share": float(r.get("weight", 1)) / total} for r in ss]

def check_row(m, tol=0.00011):
    att = m.get("interval_provenance_attestation")
    if not att: return None
    contract = contract_from_manifest(m.get("manifest") or {})
    r = replay(att, contract)
    served_lo, served_hi = m.get("value_lo"), m.get("value_hi")
    ok = served_lo is not None and abs(r["pooled_lo"] - served_lo) <= tol and abs(r["pooled_hi"] - served_hi) <= tol
    acc_ok = r["accepted"] == (m.get("interval_provenance") or {}).get("accepted_draws")
    return {"hash": m.get("manifest_hash"), "served": [served_lo, served_hi], "replayed": [r["pooled_lo"], r["pooled_hi"]], "pooled_match": ok, "accepted_match": acc_ok, "accepted": r["accepted"], "strata": r["strata"]}

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        d = json.load(open(path))
        rows = [d["src"], d["rep"]] if "src" in d else [d]
        for m in rows:
            res = check_row(m)
            print(json.dumps({k: v for k, v in res.items() if k != "strata"}))
            if res["strata"]:
                for k, v in res["strata"].items(): print(f"   {k:22s} lo {v['lo']:8.3f} hi {v['hi']:8.3f} width {v['width']:7.3f} n {v['accepted']}")
