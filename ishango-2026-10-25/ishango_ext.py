"""Extension asked for by Odi_line (2026-10-25, thread 391b5ce0): charge the column-D swap to the null as well as the count edits.
Family B = Baur v4 Table 2 properties, as implemented in author_test.py (copied verbatim below, not imported). Family A = the classic six claims, as in ishango_null.py.
Three nulls on random arrangements of the config-1 pool (16 values redistributed into G4 / D4 / M8, the paper's own permutation test), each arrangement scored at its best over a stated freedom:
  edits_only      : <=4 single-notch +-1 edits (34,113 resolutions incl. identity)      [the 10-25 fair null, re-run here so the per-trial values are saved]
  swap_only       : all 24 orderings of D against G (the pairing freedom the 11/21 swap used), no edits
  swap_and_edits  : all 24 orderings x <=4 edits, best of 818,712 readings per arrangement
Also recomputes the partial-adjustment table (dl/ishango_partial.json) from code so it is reproducible. Seeds fixed. Writes dl/ext.json (summary) and dl/ext_per_trial.json (raw per-trial best scores)."""
import numpy as np, json, itertools, time
def props(G, D, M):
    sg, sd = G.sum(1), D.sum(1); p1 = sg == sd
    rows = np.sort(G + D, 1); d = np.diff(rows, axis=1); p2 = (d[:, 0] == d[:, 1]) & (d[:, 1] == d[:, 2]) & (d[:, 0] > 0)
    pairs = M.reshape(-1, 4, 2); prod = np.sort(pairs[:, :, 0] * pairs[:, :, 1], 1); p3 = (prod == rows).all(1)
    def split2(X):
        return ((X[:, 0] + X[:, 1] == X[:, 2] + X[:, 3]) | (X[:, 0] + X[:, 2] == X[:, 1] + X[:, 3]) | (X[:, 0] + X[:, 3] == X[:, 1] + X[:, 2]))
    p4 = split2(G) & split2(D); p5 = split2(pairs.max(2))
    return np.stack([p1, p2, p3, p4, p5], 1)
def scoreB(V):  # V: (n,16) laid out G(4) D(4) M(8)
    return props(V[:, 0:4], V[:, 4:8], V[:, 8:16]).sum(1)
MAXV = 64
PRIME = np.zeros(MAXV + 2, bool); PRIME[[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]] = True
NEAR = np.zeros(MAXV + 2, bool); NEAR[[9, 11, 19, 21]] = True
def propsA(B):  # B: (n,16) laid out M(8) G(4) D(4), as in ishango_null.py
    B = np.clip(B, 0, MAXV); a, b, c = B[:, 0:8], B[:, 8:12], B[:, 12:16]
    sa, sb, sc = a.sum(1), b.sum(1), c.sum(1)
    p1 = PRIME[b].all(1) | PRIME[c].all(1); p2 = NEAR[b].all(1) | NEAR[c].all(1)
    p3 = (sa == sb) | (sb == sc) | (sa == sc); p4 = (sa % 12 == 0) & (sb % 12 == 0) & (sc % 12 == 0)
    pairs = a.reshape(-1, 4, 2); dbl = ((pairs[:, :, 0] * 2 == pairs[:, :, 1]) | (pairs[:, :, 1] * 2 == pairs[:, :, 0])).sum(1); p5 = dbl >= 3
    p6 = (sa + sb + sc) % 12 == 0
    return np.stack([p1, p2, p3, p4, p5, p6], 1)
def toA(V):  # G D M  ->  M G D
    return np.concatenate([V[:, 8:16], V[:, 0:4], V[:, 4:8]], 1)
cfg1 = np.array([11, 13, 17, 19, 11, 21, 19, 9, 3, 6, 4, 8, 9, 4, 5, 7])     # Baur Table 1 config 1: documented, damaged pair read 9,4
cfg3 = np.array([11, 13, 17, 19, 21, 11, 19, 9, 4, 8, 4, 6, 9, 4, 4, 7])     # Baur Table 1 config 3: adjusted
heinz = np.array([11, 13, 17, 19, 11, 21, 19, 9, 3, 6, 4, 8, 10, 5, 5, 7])   # de Heinzelin as usually quoted (damaged pair 10,5)
swap_only = cfg1.copy(); swap_only[4:8] = [21, 11, 19, 9]                      # D swapped, M untouched
m_only = cfg1.copy(); m_only[8:16] = cfg3[8:16]                                # M edited as in config 3, D untouched
out = {"seed": 7, "layout": "G(4) D(4) M(8); family A scored on M(8) G(4) D(4)"}
def both(v):
    return {"B_props": props(v[None, :4], v[None, 4:8], v[None, 8:])[0].tolist(), "B_score": int(scoreB(v[None])[0]), "A_props": propsA(toA(v[None]))[0].tolist(), "A_score": int(propsA(toA(v[None])).sum())}
# the partial-adjustment table, recomputed
part = {"cfg1_documented": both(cfg1), "D_swap_only": both(swap_only), "M_edits_only_no_swap": both(m_only), "cfg3_adjusted": both(cfg3), "cfg1_damaged_10_5": both(heinz)}
T = []
for i, j in itertools.combinations(range(16), 2):
    v = cfg1.copy(); v[i], v[j] = v[j], v[i]; T.append(v)
T = np.array(T); sc = scoreB(T); part["cfg1_transpositions"] = {"n": int(len(T)), "B_score_hist": {str(k): int((sc == k).sum()) for k in range(6)}}
PERM = list(itertools.permutations(range(4)))
def d_orderings(base):
    V = np.array([np.concatenate([base[:4], base[4:8][list(p)], base[8:]]) for p in PERM]); s = scoreB(V); return {"n": 24, "B_score_hist": {str(k): int((s == k).sum()) for k in range(6)}}
part["D_orderings_with_cfg1_M"] = d_orderings(cfg1); part["D_orderings_with_cfg3_M"] = d_orderings(cfg3)
saved = json.load(open("dl/ishango_partial.json"))
assert part == saved, "recomputed partial table differs from the 10-25 saved copy"
out["partial_table_recomputed_matches_10_25_copy"] = True; out["partial_table"] = part
print("partial table recomputed, matches saved copy")
# freedoms
deltas = [np.zeros(16, int)]
for k in range(1, 5):
    for idx in itertools.combinations(range(16), k):
        for signs in itertools.product((-1, 1), repeat=k):
            d = np.zeros(16, int); d[list(idx)] = signs; deltas.append(d)
Dm = np.array(deltas, dtype=np.int64); assert len(Dm) == 34113
def with_orderings(V):  # (n,16) -> (24n,16): every ordering of D
    return np.concatenate([np.concatenate([V[:, :4], V[:, 4:8][:, list(p)], V[:, 8:]], 1) for p in PERM], 0)
# the paper's configuration under each freedom, from config 1
out["cfg1_best"] = {"edits_only": int(scoreB(cfg1[None] + Dm).max()), "swap_only": int(scoreB(with_orderings(cfg1[None])).max()), "swap_and_edits": int(max(scoreB(v[None] + Dm).max() for v in with_orderings(cfg1[None])))}
print("config 1 best score under each freedom:", out["cfg1_best"])
rng = np.random.default_rng(7)
def draws(pool, n):
    idx = np.argsort(rng.random((n, 16)), 1); return pool[idx]
per = {}
t0 = time.time(); N1 = 1_000_000; A = draws(cfg1, N1)
s_none = scoreB(A); s_swap = scoreB(with_orderings(A)).reshape(24, N1).max(0)
out["null_no_freedom"] = {"pool": "config1", "n": N1, "hist": {str(k): int((s_none == k).sum()) for k in range(6)}}
out["null_swap_only"] = {"pool": "config1", "n": N1, "hist": {str(k): int((s_swap == k).sum()) for k in range(6)}, "seconds": round(time.time() - t0, 1)}
print("no freedom", out["null_no_freedom"]["hist"], "| swap only (24 orderings)", out["null_swap_only"]["hist"], round(time.time() - t0, 1), "s")
M = 3000; B3 = A[:M]; be = np.empty(M, int); bs = np.empty(M, int); bse = np.empty(M, int); t0 = time.time()
for i in range(M):
    v = B3[i]; be[i] = scoreB(v[None] + Dm).max(); W = with_orderings(v[None]); bs[i] = scoreB(W).max(); bse[i] = max(scoreB(w[None] + Dm).max() for w in W)
    if i % 500 == 499: print("  ", i + 1, "of", M, round(time.time() - t0), "s", flush=True)
for name, arr in (("edits_only", be), ("swap_only_3000", bs), ("swap_and_edits", bse)):
    out["null_" + name] = {"pool": "config1", "n": M, "hist": {str(k): int((arr == k).sum()) for k in range(6)}, "p_best_ge4": float((arr >= 4).mean()), "p_best_eq5": float((arr == 5).mean())}
    per[name] = arr.tolist(); print(name, out["null_" + name]["hist"])
per["arrangements_first_3000"] = B3.tolist(); out["seconds_3000"] = round(time.time() - t0, 1)
json.dump(out, open("dl/ext.json", "w"), indent=1); json.dump(per, open("dl/ext_per_trial.json", "w")); print("saved")
