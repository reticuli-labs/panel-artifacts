"""Enumerate the sampling frame for the rate-cap / stock-cap successor draft (design arithmetic, no reader, no tokenizer).
A world: limit N, C creations inside the last rolling window (none at the query instant, none exactly one window old), `held`
members still held, a batch of k, and one of three questions. Rate key by exact phase partition (brute force over window starts),
checked against Dexagon's bound: fits under every alignment iff k <= N-C, under none iff k > N-c (c = 0 here)."""
import itertools, json, collections, fractions
F = fractions.Fraction
def rate_now(N, times, q, W, k):
    """Set of answers over the rolling window (q-W, q] and every fixed window [s, q] with s in (q-W, q] (Dexagon's conventions:
    a window beginning at the query instant counts an event at that instant; an event exactly one window old is excluded)."""
    pts = sorted(set(t for t in times if q - W < t <= q)); cand = [q - W] + pts + [q]
    starts = set(pts) | {q} | {(a + b) / 2 for a, b in zip(cand, cand[1:]) if a != b}
    counts = {sum(1 for t in times if q - W < t <= q)} | {sum(1 for t in times if s <= t <= q) for s in starts}
    return {n + k <= N for n in counts}
def key(s): return "yes" if s == {True} else "no" if s == {False} else "cannot determine"
rows = []; q, W = F(120), F(60)
for N in range(2, 6):
    for C in range(0, N + 1):
        times = [F(61) + F(i * 58, max(C, 1)) for i in range(C)]         # C creations strictly inside (60, 120)
        assert all(q - W < t < q for t in times)
        for held in range(0, N + 1):
            for k in range(1, N + 2):
                r_now = key(rate_now(N, times, q, W, k)); bound = "yes" if k <= N - C else ("no" if k > N else "cannot determine"); assert r_now == bound, (N, C, k, r_now, bound)
                rows.append(dict(N=N, C=C, held=held, k=k, q="now", rate=r_now, stock="yes" if held + k <= N else "no"))
                r_wait = key(rate_now(N, times, q + W, W, k)); assert r_wait == ("yes" if k <= N else "no")
                rows.append(dict(N=N, C=C, held=held, k=k, q="after one idle window", rate=r_wait, stock="yes" if held + k <= N else "no"))
                if held >= 1: rows.append(dict(N=N, C=C, held=held, k=k, q="after releasing one", rate=r_now, stock="yes" if held - 1 + k <= N else "no"))
json.dump(rows, open("frame.json", "w"))
print("worlds x questions", len(rows))
pat = collections.Counter((r["q"], r["rate"], r["stock"]) for r in rows)
for p, n in sorted(pat.items()): print("  %-24s rate %-17s stock %-3s  %4d %s" % (p[0], p[1], p[2], n, "DISCRIMINATING" if p[1] != p[2] and p[1] != "cannot determine" else ("phase-dependent" if p[1] == "cannot determine" else "same key")))
inv = [r for r in rows if r["rate"] != "cannot determine"]
print("rate key invariant:", len(inv), "of", len(rows), "| by rate key", dict(collections.Counter(r["rate"] for r in inv)), "| stock keys", dict(collections.Counter(r["stock"] for r in rows)))
print("invariant rate-no with k <= N:", sum(1 for r in inv if r["rate"] == "no" and r["k"] <= r["N"]))
print("discriminating:", dict(collections.Counter((r["rate"], r["stock"]) for r in inv if r["rate"] != r["stock"])))
print("classes (question, rate key, stock key), all:", len(pat), "| with an invariant rate key:", len([p for p in pat if p[1] != "cannot determine"]))
# Dexagon's six exposed examples (limit 3, period 60, query 120) through the same oracle
six = [([0, 10, 20], 3, 1, "yes", "no"), ([100], 1, 2, "yes", "yes"), ([100], 1, 3, "cannot determine", "no"), ([115, 116, 117], 0, 1, "cannot determine", "yes"), ([120], 1, 3, "no", "no"), ([0, 10, 20], 2, 2, "yes", "no")]
for t, held, k, er, es in six:
    got = key(rate_now(3, [F(x) for x in t], q, W, k)), ("yes" if held + k <= 3 else "no"); assert got == (er, es), (t, got)
print("Dexagon's six examples reproduce: 6 of 6")
