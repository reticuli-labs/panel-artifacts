"""erfu 1028641a: (a) the window start = first graded (route-column) row; (b) do fires follow the gaps? Permutation test on the exposure log: statistic = mean log10(gap seconds) before fired rows; gaps permuted among rows, labels fixed. Read-only."""
import datetime as dt, math, random, json
rows = [l.split() for l in open("rounds-exposure.log") if l.strip()]
ts = [dt.datetime.strptime(r[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc) for r in rows]; fired = ["fired=True" in " ".join(r) for r in rows]; graded = [any(x.startswith("route=") for x in r) for r in rows]
first_graded = next(r[0] for r, g in zip(rows, graded) if g); n = len(rows)
gaps = [None] + [(ts[i] - ts[i - 1]).total_seconds() for i in range(1, n)]
idx = [i for i in range(1, n)]; lg = [math.log10(max(gaps[i], 1)) for i in idx]; f = [fired[i] for i in idx]
fires = [i for i in idx if fired[i]]; print("rows", n, "fired", sum(fired), "graded", sum(graded), "pre-route", n - sum(graded), "| first graded row", first_graded, "| fires at", [rows[i][0] for i in fires])
print("gaps before fires (h):", [round(gaps[i] / 3600, 1) for i in fires]); print("median gap all (h):", round(sorted(gaps[1:])[n // 2] / 3600, 2), "quiet-row gaps ≥8.9h:", sum(1 for i in idx if not fired[i] and gaps[i] >= 8.9 * 3600), "of", sum(1 for i in idx if not fired[i]))
stat = lambda L, F: sum(l for l, x in zip(L, F) if x) / sum(F)
obs = stat(lg, f); random.seed(20261019); N = 20000; ge = 0
for _ in range(N):
    P = lg[:]; random.shuffle(P); ge += stat(P, f) >= obs
print(f"observed mean log10 gap before fires {obs:.3f} (={10**obs/3600:.1f} h); mean over quiet rows {sum(l for l, x in zip(lg, f) if not x)/sum(1 for x in f if not x):.3f}; permutation p (gap-shuffle, one-sided, N={N}) = {ge/N:.4f}")
# the fires are all pre-route rows; also report within pre-route rows only
pre = [i for i in idx if not graded[i]]; lgp = [math.log10(max(gaps[i], 1)) for i in pre]; fp = [fired[i] for i in pre]
obs2 = stat(lgp, fp); ge2 = 0
for _ in range(N):
    P = lgp[:]; random.shuffle(P); ge2 += stat(P, fp) >= obs2
print(f"pre-route rows only: {len(pre)} rows, {sum(fp)} fired, observed {obs2:.3f}, p = {ge2/N:.4f}")
json.dump({"rows": n, "fired": sum(fired), "graded": sum(graded), "first_graded_row": first_graded, "fires": [rows[i][0] for i in fires], "gaps_before_fires_h": [round(gaps[i] / 3600, 2) for i in fires], "obs_mean_log10_gap_fired": obs, "p_all": ge / N, "pre_rows": len(pre), "pre_fired": sum(fp), "p_pre": ge2 / N, "N": N, "seed": 20261019}, open("exposure_perm.json", "w"), indent=1)
