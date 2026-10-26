"""Ishango bone: how special is the standard reading under a pre-stated pattern family, (a) against random bones, (b) against its own neighbourhood of up-to-4 one-notch 'resolutions', (c) random bones that are also allowed up to 4 resolutions chosen to maximise the score. Exact enumeration for (b); Monte Carlo with fixed seed for (a) and (c). Writes dl/ishango_null.json."""
import numpy as np, json, itertools, time
rng = np.random.default_rng(1)
STD = np.array([3, 6, 4, 8, 10, 5, 5, 7, 11, 13, 17, 19, 11, 21, 19, 9])   # de Heinzelin transcription as usually quoted: 8-column, then two 4-columns
LAYOUT = [(0, 8), (8, 12), (12, 16)]
MAXV = 64
PRIME = np.zeros(MAXV + 2, bool); PRIME[[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]] = True
NEAR = np.zeros(MAXV + 2, bool); NEAR[[9, 11, 19, 21]] = True
def score(B):
    """B: (n,16) int array -> (n,6) bool pattern matrix."""
    B = np.clip(B, 0, MAXV); a, b, c = B[:, 0:8], B[:, 8:12], B[:, 12:16]
    sa, sb, sc = a.sum(1), b.sum(1), c.sum(1)
    p1 = PRIME[b].all(1) | PRIME[c].all(1)                      # a 4-column of four primes
    p2 = NEAR[b].all(1) | NEAR[c].all(1)                        # a 4-column inside 10±1 / 20±1
    p3 = (sa == sb) | (sb == sc) | (sa == sc)                   # two column sums equal
    p4 = (sa % 12 == 0) & (sb % 12 == 0) & (sc % 12 == 0)      # every column sum a multiple of 12
    pairs = a.reshape(-1, 4, 2); dbl = ((pairs[:, :, 0] * 2 == pairs[:, :, 1]) | (pairs[:, :, 1] * 2 == pairs[:, :, 0])).sum(1)
    p5 = dbl >= 3                                               # at least 3 of the 4 adjacent pairs in the 8-column are doubling pairs
    p6 = (sa + sb + sc) % 12 == 0                               # total a multiple of 12
    return np.stack([p1, p2, p3, p4, p5, p6], 1)
NAMES = ["prime_column", "near_10_20_column", "two_sums_equal", "all_sums_div12", "doubling_pairs_ge3", "total_div12"]
out = {"standard_reading": STD.tolist(), "column_sums": [int(STD[s:e].sum()) for s, e in LAYOUT], "total": int(STD.sum()), "patterns": NAMES}
s0 = score(STD[None]); out["standard_patterns"] = dict(zip(NAMES, s0[0].tolist())); out["standard_score"] = int(s0.sum()); print("standard reading", STD.tolist(), "sums", out["column_sums"], "score", out["standard_score"], out["standard_patterns"])
# (b) neighbourhood: every resolution that changes at most 4 groups by exactly ±1 (identity included)
deltas = [np.zeros(16, int)]
for k in range(1, 5):
    for idx in itertools.combinations(range(16), k):
        for signs in itertools.product((-1, 1), repeat=k):
            d = np.zeros(16, int); d[list(idx)] = signs; deltas.append(d)
D = np.array(deltas); nchg = (D != 0).sum(1); print("resolutions enumerated", len(D))
S = score(STD[None] + D); sc = S.sum(1)
out["neighbourhood"] = {"resolutions": int(len(D)), "by_changes": {}, "score_hist": {str(k): int((sc == k).sum()) for k in range(7)}}
for k in range(5):
    m = nchg == k; out["neighbourhood"]["by_changes"][str(k)] = {"n": int(m.sum()), "score6": int((sc[m] == 6).sum()), "score_ge5": int((sc[m] >= 5).sum()), "score_ge4": int((sc[m] >= 4).sum())}
alt6 = [(STD + D[i]).tolist() for i in np.where((sc == 6) & (nchg > 0))[0]]; out["neighbourhood"]["alternative_score6_readings"] = alt6[:50]; out["neighbourhood"]["n_alternative_score6"] = len(alt6)
one = nchg == 1; out["neighbourhood"]["single_change_drops_score"] = int((sc[one] < 6).sum()); out["neighbourhood"]["single_change_n"] = int(one.sum())
print("neighbourhood:", json.dumps(out["neighbourhood"]["by_changes"]), "| alt score-6 readings:", len(alt6), "| single changes that drop the score:", out["neighbourhood"]["single_change_drops_score"], "of", int(one.sum()))
# (a) random bones, three nulls, no resolutions
N = 200000
nulls = {"uniform_1_21": rng.integers(1, 22, size=(N, 16)), "empirical_with_replacement": rng.choice(STD, size=(N, 16)), "permutation_of_observed": np.array([rng.permutation(STD) for _ in range(N // 10)])}
out["null_no_resolution"] = {}
for name, B in nulls.items():
    S = score(B); sc_ = S.sum(1); n = len(B)
    out["null_no_resolution"][name] = {"n": int(n), "p_each": dict(zip(NAMES, (S.mean(0)).round(5).tolist())), "p_score_ge": {str(k): float((sc_ >= k).mean()) for k in range(1, 7)}}
    print(name, "n", n, "P(score>=k):", {k: round(v, 5) for k, v in out["null_no_resolution"][name]["p_score_ge"].items()}, "| per pattern:", {k: round(v, 4) for k, v in out["null_no_resolution"][name]["p_each"].items()})
# (c) random bones + the researcher's freedom: best score over all <=4-change resolutions
t0 = time.time(); M = 3000; best = {}
for name, B in nulls.items():
    bs = np.empty(M, int)
    for i in range(M):
        bs[i] = score(B[i][None] + D).sum(1).max()
    best[name] = {"n": M, "p_best_ge": {str(k): float((bs >= k).mean()) for k in range(1, 7)}, "mean_best": float(bs.mean())}
    print("with <=4 resolutions:", name, {k: round(v, 4) for k, v in best[name]["p_best_ge"].items()}, "mean best", round(bs.mean(), 2))
out["null_with_resolutions"] = best; out["seconds"] = round(time.time() - t0, 1); out["seed"] = 1
json.dump(out, open("dl/ishango_null.json", "w"), indent=1); print("saved", out["seconds"], "s")
