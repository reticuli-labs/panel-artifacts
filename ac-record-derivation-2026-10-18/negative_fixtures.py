"""Skitter's suggestion (6a73db70 on 024ca2b6): keep the inputs on which the two predicates part in the fixture set, so the negative branch stays calibrated when a library is swapped. For every Artifact Council address whose Solana bump is below 255, list each candidate hash that Solana rejects as a PDA (it decompresses) and record both predicates' verdicts on it. Inputs are the saved derivation reads, passed as paths; no network."""

import hashlib, os, json, sys
from nacl.bindings import crypto_core_ed25519_is_valid_point as sodium_valid
P = 2**255 - 19; D = (-121665 * pow(121666, P - 2, P)) % P
L = 2**252 + 27742317777372353535851937790883648493
I_SQRT = pow(2, (P - 1) // 4, P)
def decompress(b):
    y = int.from_bytes(b, "little"); sign = y >> 255; y &= (1 << 255) - 1
    if y >= P: return None, "non_canonical_y"
    u = (y * y - 1) % P; v = (D * y * y + 1) % P; x2 = (u * pow(v, P - 2, P)) % P
    if x2 == 0:
        if sign: return None, "x_zero_sign_set"
        return (0, y), None
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0: x = (x * I_SQRT) % P
    if (x * x - x2) % P != 0: return None, "not_on_curve"
    if (x & 1) != sign: x = P - x
    return (x, y), None
# extended coordinates (X, Y, Z, T), identity (0,1,1,0)
def add(p, q):
    X1, Y1, Z1, T1 = p; X2, Y2, Z2, T2 = q
    A = (Y1 - X1) * (Y2 - X2) % P; B = (Y1 + X1) * (Y2 + X2) % P; C = 2 * T1 * T2 * D % P; Dd = 2 * Z1 * Z2 % P
    E = B - A; F = Dd - C; G = Dd + C; H = B + A
    return (E * F % P, G * H % P, F * G % P, E * H % P)
def mul(k, p):
    r = (0, 1, 1, 0)
    while k:
        if k & 1: r = add(r, p)
        p = add(p, p); k >>= 1
    return r
def is_identity(p):
    X, Y, Z, T = p; return X % P == 0 and (Y - Z) % P == 0
def classify(b):
    pt, why = decompress(b)
    if pt is None: return "not_decompressible:" + why
    x, y = pt; ext = (x, y, 1, x * y % P)
    if is_identity(ext): return "identity"
    if is_identity(mul(8, ext)): return "small_order"
    if is_identity(mul(L, ext)): return "prime_subgroup"
    if is_identity(mul(8 * L, ext)): return "off_subgroup_large_order"
    return "UNEXPECTED_order"

import base58
def le64(n): return n.to_bytes(8, "little")
def candidates(seeds, program):
    pb = base58.b58decode(program); rows = []
    for bump in range(255, -1, -1):
        h = hashlib.sha256(b"".join(seeds) + bytes([bump]) + pb + b"ProgramDerivedAddress").digest(); c = classify(h)
        rows.append({"bump": bump, "candidate_hex": h.hex(), "solana_is_pda": c.startswith("not_decompressible"), "libsodium_valid_point": bool(sodium_valid(h)), "point_class": c})
        if c.startswith("not_decompressible"): return rows
if __name__ == "__main__":
    fixed = json.load(open(sys.argv[1])); before = json.load(open(sys.argv[2])); PROGRAM = sys.argv[3]
    art_addr = {(p["artifact"], p["page"], p["version"]): p["address"] for p in before["pages"]}
    out = {"program": PROGRAM, "rule": "pda = first bump from 255 downward whose sha256(seeds || bump || program || 'ProgramDerivedAddress') does NOT decompress as an Edwards point; libsodium's valid-point predicate additionally rejects off-subgroup points, so on every row below the first it returns False where Solana continues", "records": [], "artifacts": []}
    for p in fixed["pages"]:
        if p["bump"] is None or p["bump"] == 255: continue
        rows = candidates([b"record", base58.b58decode(art_addr[(p["artifact"], p["page"], p["version"])]), le64(p["seq"])], PROGRAM)
        assert rows[-1]["bump"] == p["bump"] and base58.b58encode(bytes.fromhex(rows[-1]["candidate_hex"])).decode() == p["record"]
        out["records"].append({"artifact": p["artifact"], "page": p["page"], "version": p["version"], "seq": p["seq"], "record": p["record"], "candidates": rows})
    for a in fixed["artifacts"]:
        if a["bump"] is None or a["bump"] == 255: continue
        rows = candidates([b"artifact", le64(a["n"])], PROGRAM)
        assert rows[-1]["bump"] == a["bump"] and base58.b58encode(bytes.fromhex(rows[-1]["candidate_hex"])).decode() == a["address"]
        out["artifacts"].append({"name": a["name"], "n": a["n"], "address": a["address"], "candidates": rows})
    neg = [r for x in out["records"] + out["artifacts"] for r in x["candidates"] if not r["solana_is_pda"]]
    out["summary"] = {"records_below_255": len(out["records"]), "artifacts_below_255": len(out["artifacts"]), "negative_branch_inputs": len(neg), "libsodium_rejects_all_of_them": all(not r["libsodium_valid_point"] for r in neg), "point_classes": sorted({r["point_class"] for r in neg})}
    print(json.dumps(out["summary"])); json.dump(out, open(sys.argv[4], "w"), indent=1)
