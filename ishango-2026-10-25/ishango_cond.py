"""Conditional null for Odi_line's question: if the documented order were an accident, how often would some ordering of D make the row sums an arithmetic progression (property P2), given the order-free properties the documented reading already has (P1 equal column sums, P4 both columns split into two equal-sum pairs, P5 pair maxima split)? Arrangements of the config-1 pool, seed 11. Writes dl/ishango_cond.json."""
import numpy as np, json, itertools
def props(G, D, M):
    sg, sd = G.sum(1), D.sum(1); p1 = sg == sd
    rows = np.sort(G + D, 1); d = np.diff(rows, axis=1); p2 = (d[:, 0] == d[:, 1]) & (d[:, 1] == d[:, 2]) & (d[:, 0] > 0)
    pairs = M.reshape(-1, 4, 2); prod = np.sort(pairs[:, :, 0] * pairs[:, :, 1], 1); p3 = (prod == rows).all(1)
    def split2(X):
        return ((X[:, 0] + X[:, 1] == X[:, 2] + X[:, 3]) | (X[:, 0] + X[:, 2] == X[:, 1] + X[:, 3]) | (X[:, 0] + X[:, 3] == X[:, 1] + X[:, 2]))
    p4 = split2(G) & split2(D); p5 = split2(pairs.max(2))
    return np.stack([p1, p2, p3, p4, p5], 1)
cfg1 = np.array([11, 13, 17, 19, 11, 21, 19, 9, 3, 6, 4, 8, 9, 4, 5, 7])
P = props(cfg1[None, :4], cfg1[None, 4:8], cfg1[None, 8:])[0]; assert P.tolist() == [True, False, False, True, True]
rng = np.random.default_rng(11); N = 1_000_000
A = cfg1[np.argsort(rng.random((N, 16)), 1)]
P0 = props(A[:, :4], A[:, 4:8], A[:, 8:]); cond = P0[:, 0] & P0[:, 3] & P0[:, 4]
PERM = list(itertools.permutations(range(4)))
p2_any = np.zeros(N, bool); p2_count = np.zeros(N, int)
for p in PERM:
    p2 = props(A[:, :4], A[:, 4:8][:, list(p)], A[:, 8:])[:, 1]; p2_any |= p2; p2_count += p2
out = {"seed": 11, "n": N, "cond_P1_P4_P5_at_drawn_order": int(cond.sum()), "cond_and_P2_at_drawn_order": int((cond & P0[:, 1]).sum()), "cond_and_P2_under_some_ordering_of_D": int((cond & p2_any).sum()),
       "P2_at_drawn_order_all": int(P0[:, 1].sum()), "P2_under_some_ordering_all": int(p2_any.sum()),
       "documented_reading": {"P1_P4_P5": True, "P2_at_documented_order": False, "orderings_of_D_giving_P2": int(sum(props(cfg1[None, :4], cfg1[None, 4:8][:, list(p)], cfg1[None, 8:])[0, 1] for p in PERM))}}
json.dump(out, open("dl/ishango_cond.json", "w"), indent=1); print(json.dumps(out))
