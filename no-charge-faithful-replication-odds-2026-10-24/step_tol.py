"""Step versus tolerance for Dexagon's no-charge/available-now original 3ce6e06b: from the served stratum arms and the bank's 72 items per stratum, recover the per-arm cell counts (k/n with n_e+n_a = 144), the one-cell step of each arm, the settlement tolerance max(0.02, 0.1*|v|), and the probability that a faithful replication (same n per arm, same true arm accuracies, binomial cells) lands inside tolerance on each stratum and on all four. Writes step_tol.json. No network."""
import json, hashlib, math
from fractions import Fraction
m = json.load(open("m_3ce6e06b.json"))["result"]; man = m["manifest"]
items = json.load(open("items.json")); assert hashlib.sha256(json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest() == man["items_sha256"]
real = [it for it in items if it.get("settlement_stratum")]; strata = [s["id"] for s in man["settlement_strata"]]
per = {s: sum(1 for it in real if it["settlement_stratum"] == s) for s in strata}; assert all(v == 72 for v in per.values()) and len(real) == 288 and len(items) - len(real) == 10
readers = len(man["readers"]); assert readers == 2; cells = 72 * readers  # each item read once per reader, in one arm
def recover(acc, total):
    """all (k, n) with n in 1..total and k/n rounding to acc at 4 dp"""
    return [(k, n) for n in range(1, total + 1) for k in range(0, n + 1) if round(k / n, 4) == acc]
def tol(v): return max(0.02, 0.1 * abs(v))
def binom_pmf(n, p):
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]
out = {"source": m["manifest_hash"], "items_sha256": man["items_sha256"], "items_per_stratum": 72, "readers": readers, "cells_per_stratum": cells, "tolerance_rule": "max(0.02, 0.1*|value|) percentage points on the stratum value", "strata": []}
p_all_same = 1.0; p_all_bal = 1.0
for sr in m["stratum_results"]:
    e, a, v = sr["arms"]["english"], sr["arms"]["ainglish"], sr["value"]
    pairs = [(ke, ne, ka, na) for ke, ne in recover(e, cells) for ka, na in recover(a, cells) if ne + na == cells]
    assert len(pairs) == 1, (sr["id"], pairs); ke, ne, ka, na = pairs[0]
    assert abs(100 * (ka / na - ke / ne) - v) < 0.006, (sr["id"], 100 * (ka / na - ke / ne), v)
    t = tol(v); step_e, step_a = 100 / ne, 100 / na
    def p_within(ne_, na_):
        pe = binom_pmf(ne_, ke / ne); pa = binom_pmf(na_, ka / na); tot = 0.0
        for i, pi in enumerate(pe):
            for j, pj in enumerate(pa):
                if abs(100 * (j / na_ - i / ne_) - v) <= t + 1e-9: tot += pi * pj
        return tot
    ps, pb = p_within(ne, na), p_within(72, 72); p_all_same *= ps; p_all_bal *= pb
    grid_bal = sorted({round(100 * (j - i) / 72, 3) for i in range(73) for j in range(73)}); hits_bal = [g for g in grid_bal if abs(g - v) <= t + 1e-9]
    out["strata"].append({"id": sr["id"], "value": v, "english": [ke, ne], "ainglish": [ka, na], "step_english_pp": round(step_e, 3), "step_ainglish_pp": round(step_a, 3), "tolerance_pp": round(t, 3), "tolerance_below_both_steps": t < min(step_e, step_a), "p_within_tolerance_same_split": round(ps, 4), "p_within_tolerance_balanced_72_72": round(pb, 4), "balanced_grid_points_within_tolerance": [round(g, 3) for g in hits_bal]})
out["p_all_four_same_split"] = round(p_all_same, 6); out["p_all_four_balanced"] = round(p_all_bal, 6)
agg_cells = sum(1 for _ in real) * readers // 2
out["aggregate"] = {"value": m["value"], "tolerance_pp": round(tol(m["value"]), 3), "note": "aggregate = mean of the four stratum values (equal weights); its tolerance is wider than any stratum's step"}
# aggregate: mean of the four stratum deltas; distribution by convolution of the four stratum delta pmfs on a 0.01 pp grid
import numpy as np
R = 100; G = 2 * R * 100 + 1  # -100..+100 pp at 0.01
def delta_pmf(ke, ne, ka, na):
    arr = np.zeros(G); pe = binom_pmf(ne, ke / ne); pa = binom_pmf(na, ka / na)
    for i, pi in enumerate(pe):
        for j, pj in enumerate(pa): arr[int(round((100 * (j / na - i / ne) + R) * 100))] += pi * pj
    return arr
pm = None
for sr, st in zip(m["stratum_results"], out["strata"]):
    ke, ne = st["english"]; ka, na = st["ainglish"]; arr = delta_pmf(ke, ne, ka, na)
    pm = arr if pm is None else np.convolve(pm, arr)  # sum of deltas; index offset accumulates R per term
k = len(out["strata"]); offs = k * R * 100  # index of sum == 0
sums = (np.arange(len(pm)) - offs) / 100.0 / k  # mean delta in pp
va = m["value"]; ta = tol(va); p_agg = float(pm[np.abs(sums - va) <= ta + 1e-9].sum()); assert abs(pm.sum() - 1) < 1e-6
out["aggregate"]["p_within_tolerance_same_split"] = round(p_agg, 4)
out["aggregate"]["sd_of_replication_mean_pp"] = round(float(np.sqrt((pm * (sums - (pm * sums).sum()) ** 2).sum())), 3)
out["p_all_four_and_aggregate_same_split_upper_bound"] = round(min(p_all_same, p_agg), 6)
out["model"] = "faithful replication: same readers, same 72 items per stratum split into arms as the source was, each arm's cells binomial at the source's observed arm accuracy; strata independent; settlement = every stratum and the aggregate within tolerance (strata_effect required_all)"
json.dump(out, open("step_tol.json", "w"), indent=1); print(json.dumps(out, indent=1))
