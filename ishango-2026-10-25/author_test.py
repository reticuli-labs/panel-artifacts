"""Reproduce Baur v4's composite permutation test (five properties, 16 values redistributed into G4 / D4 / M as four pairs), then the fair version: each random arrangement also gets the best score over up to four single-notch +-1 edits, the freedom the adjusted configuration used. Seeds fixed. Writes dl/author_test.json."""
import numpy as np, json, itertools, time
def props(G, D, M):
    """G,D: (n,4); M: (n,8) as pairs (0,1),(2,3),(4,5),(6,7). Returns (n,5) bool: P1 equal sums; P2 row sums G_i+D_i sorted form a strict AP; P3 multiset of pair products == multiset of row sums; P4 both G and D split into two pairs of equal sum; P5 the four pair maxima split into two pairs of equal sum."""
    sg, sd = G.sum(1), D.sum(1); p1 = sg == sd
    rows = np.sort(G + D, 1); d = np.diff(rows, axis=1); p2 = (d[:, 0] == d[:, 1]) & (d[:, 1] == d[:, 2]) & (d[:, 0] > 0)
    pairs = M.reshape(-1, 4, 2); prod = np.sort(pairs[:, :, 0] * pairs[:, :, 1], 1); p3 = (prod == rows).all(1)
    def split2(X):  # some split of 4 values into two pairs with equal sums
        return ((X[:, 0] + X[:, 1] == X[:, 2] + X[:, 3]) | (X[:, 0] + X[:, 2] == X[:, 1] + X[:, 3]) | (X[:, 0] + X[:, 3] == X[:, 1] + X[:, 2]))
    p4 = split2(G) & split2(D); p5 = split2(pairs.max(2))
    return np.stack([p1, p2, p3, p4, p5], 1)
def score(V):  # V: (n,16) laid out G(4) D(4) M(8)
    return props(V[:, 0:4], V[:, 4:8], V[:, 8:16]).sum(1)
cfg1 = np.array([11, 13, 17, 19, 11, 21, 19, 9, 3, 6, 4, 8, 9, 4, 5, 7])     # Baur Table 1 config 1: documented, damaged pair read 9,4
cfg3 = np.array([11, 13, 17, 19, 21, 11, 19, 9, 4, 8, 4, 6, 9, 4, 4, 7])     # Baur Table 1 config 3: adjusted
heinz = np.array([11, 13, 17, 19, 11, 21, 19, 9, 3, 6, 4, 8, 10, 5, 5, 7])   # de Heinzelin as usually quoted (damaged pair 10,5)
out = {}
for name, v in (("config1_documented", cfg1), ("config3_adjusted", cfg3), ("de_heinzelin", heinz)):
    P = props(v[None, :4], v[None, 4:8], v[None, 8:]); out[name] = {"values": v.tolist(), "score": int(P.sum()), "props": P[0].tolist()}; print(name, v.tolist(), "score", int(P.sum()), P[0].tolist())
assert out["config3_adjusted"]["score"] == 5, "the adjusted configuration must score 5 under these definitions"
rng = np.random.default_rng(42); N = 1_000_000
def draws(pool, n):
    idx = np.argsort(rng.random((n, 16)), 1); return pool[idx]
t0 = time.time()
for name, pool in (("pool_config1", cfg1), ("pool_config3_multiset", cfg3), ("pool_de_heinzelin", heinz)):
    sc = score(draws(pool, N)); hist = {str(k): int((sc == k).sum()) for k in range(6)}
    out["null_" + name] = {"n": N, "score_hist": hist, "p_ge": {str(k): float((sc >= k).mean()) for k in range(1, 6)}}
    print("null", name, "hist", hist, "P(>=4)", (sc >= 4).mean(), "P(=5)", (sc == 5).mean())
print("1e6 draws x3:", round(time.time() - t0, 1), "s")
# fair null: the same arrangements, each allowed the best score over <=4 single-notch +-1 edits (34,113 resolutions incl. identity)
deltas = [np.zeros(16, int)]
for k in range(1, 5):
    for idx in itertools.combinations(range(16), k):
        for signs in itertools.product((-1, 1), repeat=k):
            d = np.zeros(16, int); d[list(idx)] = signs; deltas.append(d)
Dm = np.array(deltas, dtype=np.int64); M = 3000; t0 = time.time()
for name, pool in (("pool_config1", cfg1), ("pool_de_heinzelin", heinz)):
    A = draws(pool, M); best = np.empty(M, int)
    for i in range(M): best[i] = score(A[i][None] + Dm).max()
    hist = {str(k): int((best == k).sum()) for k in range(6)}
    out["fair_" + name] = {"n": M, "edits_max": 4, "resolutions_per_arrangement": int(len(Dm)), "best_hist": hist, "p_best_ge": {str(k): float((best >= k).mean()) for k in range(1, 6)}}
    print("fair", name, "best-score hist", hist, "P(best>=4)", round((best >= 4).mean(), 4), "P(best=5)", round((best == 5).mean(), 4))
# neighbourhood of config 1 itself, positions fixed: how many <=4-edit readings reach 5 or 4 under the author's family
sc = score(cfg1[None] + Dm); nchg = (Dm != 0).sum(1)
out["cfg1_neighbourhood_positions_fixed"] = {"n": int(len(Dm)), "score5": int((sc == 5).sum()), "score_ge4": int((sc >= 4).sum()), "by_changes_ge4": {str(k): int(((sc >= 4) & (nchg == k)).sum()) for k in range(5)}}
print("config1 neighbourhood, positions fixed:", out["cfg1_neighbourhood_positions_fixed"])
out["seconds_fair"] = round(time.time() - t0, 1); out["seed"] = 42
json.dump(out, open("dl/author_test.json", "w"), indent=1); print("saved")
