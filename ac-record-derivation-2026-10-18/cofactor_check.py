"""Why do the two on-curve predicates disagree on 44 percent of random inputs? Classify every disagreement by the order of the decompressed point. Solana accepts any decompressible encoding; libsodium's crypto_core_ed25519_is_valid_point also requires canonical form, non-small order, and membership of the prime-order subgroup. With cofactor 8, a random on-curve point lies in that subgroup with probability 1/8, so the prediction is: decompressible 1/2, libsodium-valid 1/16, disagreement 7/16 = 0.4375, essentially all of it off-subgroup points of large order."""
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
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
counts = {}; agree = {}
for i in range(N):
    h = hashlib.sha256(os.urandom(32)).digest(); c = classify(h); s = bool(sodium_valid(h)); sol = not c.startswith("not_decompressible")
    counts[c] = counts.get(c, 0) + 1
    key = (c, "sodium_valid" if s else "sodium_invalid", "solana_oncurve" if sol else "solana_offcurve"); agree[key] = agree.get(key, 0) + 1
dis = sum(v for (c, s, sol), v in agree.items() if (s == "sodium_valid") != (sol == "solana_oncurve"))
out = {"trials": N, "classes": counts, "cells": {" | ".join(k): v for k, v in sorted(agree.items())}, "disagree": dis, "disagree_rate": dis / N, "predicted_rate_7_over_16": 7 / 16,
       "disagreements_off_subgroup_large_order": agree.get(("off_subgroup_large_order", "sodium_invalid", "solana_oncurve"), 0)}
print(json.dumps(out, indent=1)); json.dump(out, open("cofactor_check.json", "w"), indent=1)
