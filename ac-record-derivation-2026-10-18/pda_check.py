"""Solana-exact PDA derivation: a candidate is a PDA iff it is NOT decompressible as an Edwards point (curve25519-dalek CompressedEdwardsY::decompress), with no subgroup test. libsodium's crypto_core_ed25519_is_valid_point additionally rejects small-order/non-canonical points, so it calls some on-curve points invalid and record_pda.py accepted a bump Solana would reject."""
import json, hashlib, base58
P = 2**255 - 19; D = (-121665 * pow(121666, P - 2, P)) % P
def decompressible(b):
    y = int.from_bytes(b, "little"); sign = y >> 255; y &= (1 << 255) - 1
    if y >= P: return False
    u = (y * y - 1) % P; v = (D * y * y + 1) % P
    x2 = (u * pow(v, P - 2, P)) % P
    if x2 == 0: return sign == 0  # x = 0 with sign bit set is invalid
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0: x = (x * pow(2, (P - 1) // 4, P)) % P
    return (x * x - x2) % P == 0
def pda(seeds, program):
    pb = base58.b58decode(program)
    for bump in range(255, -1, -1):
        h = hashlib.sha256(b"".join(seeds) + bytes([bump]) + pb + b"ProgramDerivedAddress").digest()
        if not decompressible(h): return base58.b58encode(h).decode(), bump
def le64(n): return n.to_bytes(8, "little")
if __name__ == "__main__":
    from nacl.bindings import crypto_core_ed25519_is_valid_point as sodium_valid
    PROGRAM = "77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1"
    R = json.load(open("record_pda_results.json")); out = {"pages": [], "artifacts": []}
    disagree = 0; trials = 0
    for p in R["pages"]:
        ab = base58.b58decode(p["address"]); hit = None
        for seq in range(0, 4096):
            a, bump = pda([b"record", ab, le64(seq)], PROGRAM)
            if a == p["record_served"]: hit = (seq, bump); break
        out["pages"].append({"artifact": p["artifact"], "page": p["page"], "version": p["version"], "record": p["record_served"], "derives_now": hit is not None, "seq": hit[0] if hit else None, "bump": hit[1] if hit else None, "derived_before": p["derived_matches_served"]})
        print(f"{p['artifact'][:28]:28} p{p['page']} before={p['derived_matches_served']!s:5} now={hit is not None!s:5} seq={hit[0] if hit else None} bump={hit[1] if hit else None}")
    for a in R["artifact_rule_check"]:
        hit = next(((n, b) for n in range(0, 4096) for (x, b) in [pda([b"artifact", le64(n)], PROGRAM)] if x == a["address"]), None)
        out["artifacts"].append({"address": a["address"], "name": a["name"], "n": hit[0] if hit else None, "bump": hit[1] if hit else None, "derived_before": a["artifact_seed_n"] is not None})
        print(f"artifact {a['name'][:28]:28} before_n={a['artifact_seed_n']} now_n={hit[0] if hit else None}")
    # how often do the two on-curve tests disagree over random sha256 outputs
    import os
    for i in range(20000):
        h = hashlib.sha256(os.urandom(32)).digest(); trials += 1
        if decompressible(h) != bool(sodium_valid(h)): disagree += 1
    out["oncurve_test_disagreement"] = {"trials": trials, "disagree": disagree, "rate": disagree / trials}
    json.dump(out, open("record_pda_fixed_results.json", "w"), indent=1)
    print("pages deriving now", sum(1 for x in out["pages"] if x["derives_now"]), "of", len(out["pages"]), "| artifacts", sum(1 for x in out["artifacts"] if x["n"] is not None), "of", len(out["artifacts"]), "| sodium vs dalek disagreement rate", round(disagree / trials, 4))
