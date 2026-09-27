"""State-week panel from the Opportunity Insights tracker files as served today.

Three questions, each answered on two-way demeaned data (state effects and week effects removed):
  A. How much of each spending series is state-specific at all?
  B. Which capacity proxy in the same repository tracks spending, and at what lead?
  C. Do categories move against each other inside a state-week?
Nothing here is causal. Series are indices relative to early 2020, not dollars.
"""
import json, datetime
import numpy as np, pandas as pd

def load(path, daycol):
    d = pd.read_csv(path, na_values=["."], low_memory=False)
    d["date"] = pd.to_datetime(dict(year=d["year"], month=d["month"], day=d[daycol]))
    return d

sp = load("affinity_state.csv", "day")
sp = sp[sp["date"].dt.dayofweek == 6].copy()          # Sundays: the 7-day average ending that day, so weeks do not overlap
emp = load("Employment_-_State_-_Weekly.csv", "day_endofweek")
ui = load("UI_Claims_-_State_-_Weekly.csv", "day_endofweek")
jp = load("Job_Postings_-_State_-_Weekly.csv", "day_endofweek")
wk = {name: sorted(set(d["date"].dt.dayofweek)) for name, d in (("spend", sp), ("emp", emp), ("ui", ui), ("jobs", jp))}
def to_sunday(d):
    d = d.copy(); d["date"] = d["date"] + pd.to_timedelta((6 - d["date"].dt.dayofweek) % 7, unit="D"); return d
emp, ui, jp = to_sunday(emp), to_sunday(ui), to_sunday(jp)

SP = ["spend_all", "spend_durables", "spend_hic", "spend_aer", "spend_acf", "spend_grf", "spend_retail_no_grocery"]
PX = {"emp": (emp, "employment, all workers"), "emp_wage_q1": (emp, "employment, lowest wage quartile"),
      "initclaims_rate_regular": (ui, "initial unemployment claims rate"), "contclaims_rate_regular": (ui, "continued unemployment claims rate"),
      "bg_posts": (jp, "job postings")}
panel = sp[["date", "statefips"] + SP + ["spend_all_q1", "spend_all_q4"]]
for col, (d, _) in PX.items():
    panel = panel.merge(d[["date", "statefips", col]], on=["date", "statefips"], how="left")
panel = panel[(panel["date"] >= "2020-01-19") & (panel["date"] <= "2024-06-16")]
out = {"weekdays": wk, "rows": int(len(panel)), "states": int(panel["statefips"].nunique()), "weeks": int(panel["date"].nunique()),
       "first": str(panel["date"].min().date()), "last": str(panel["date"].max().date())}

def wide(col, lo, hi):
    w = panel[(panel["date"] >= lo) & (panel["date"] <= hi)].pivot(index="date", columns="statefips", values=col)
    w = w.dropna(axis=1, thresh=int(0.95 * len(w))).dropna(axis=0)      # balanced block
    return w
def twoway(w):
    return w.sub(w.mean(axis=1), axis=0).sub(w.mean(axis=0), axis=1).add(w.values.mean())

PERIODS = {"2020-01 to 2021-06": ("2020-01-19", "2021-06-27"), "2021-07 to 2024-06": ("2021-07-04", "2024-06-16")}

# A. variance decomposition
A = {}
for pname, (lo, hi) in PERIODS.items():
    A[pname] = {}
    for col in SP:
        w = wide(col, lo, hi); v = w.values; tot = ((v - v.mean()) ** 2).sum()
        week = (((w.mean(axis=1) - v.mean()) ** 2).sum() * w.shape[1]) / tot
        state = (((w.mean(axis=0) - v.mean()) ** 2).sum() * w.shape[0]) / tot
        A[pname][col] = {"states": int(w.shape[1]), "weeks": int(w.shape[0]), "week_share": round(float(week), 3), "state_share": round(float(state), 3), "residual_share": round(float(1 - week - state), 3)}
out["variance"] = A

# B. proxy against spending, residual on residual, proxy leading by k weeks
B = {}
for pname, (lo, hi) in PERIODS.items():
    B[pname] = {}
    for tgt in ("spend_all", "spend_durables"):
        ws = wide(tgt, lo, hi)
        for col, (_, label) in PX.items():
            wp = wide(col, lo, hi)
            common_s = ws.columns.intersection(wp.columns)
            best = None; row = {}
            for k in range(0, 9):
                p = wp[common_s].shift(k)                       # proxy k weeks earlier
                idx = ws.index.intersection(p.dropna().index)
                rs, rp = twoway(ws.loc[idx, common_s]), twoway(p.loc[idx, common_s])
                r = float(np.corrcoef(rs.values.ravel(), rp.values.ravel())[0, 1])
                row[k] = round(r, 3)
                if best is None or abs(r) > abs(best[1]): best = (k, r)
            B[pname][f"{tgt} ~ {col}"] = {"label": label, "states": int(len(common_s)), "weeks": int(len(idx)), "r_at_lead_0": row[0], "best_lead_weeks": best[0], "r_at_best": round(best[1], 3), "by_lead": row}
out["proxy"] = B

# C. category co-movement inside a state-week
C = {}
cats = ["spend_hic", "spend_aer", "spend_acf", "spend_grf", "spend_durables"]
for pname, (lo, hi) in PERIODS.items():
    res = {}
    ws = {c: wide(c, lo, hi) for c in cats}
    cols = None; idx = None
    for c in cats:
        cols = ws[c].columns if cols is None else cols.intersection(ws[c].columns)
        idx = ws[c].index if idx is None else idx.intersection(ws[c].index)
    R = {c: twoway(ws[c].loc[idx, cols]).values.ravel() for c in cats}
    M = np.corrcoef(np.vstack([R[c] for c in cats]))
    C[pname] = {"states": int(len(cols)), "weeks": int(len(idx)), "cats": cats, "corr": [[round(float(x), 3) for x in r] for r in M]}
    C[pname]["negative_pairs"] = int(sum(1 for i in range(len(cats)) for j in range(i + 1, len(cats)) if M[i, j] < 0))
    C[pname]["pairs"] = len(cats) * (len(cats) - 1) // 2
out["comovement"] = C

# D. what the moving average does to a sharp lag: a worked example, not data
rng = np.random.default_rng(20260927)
n = 600; x = np.zeros(n); x[rng.choice(np.arange(20, n - 40), 25, replace=False)] = 1.0     # 25 dated shocks
true_lag = 3
y_daily = np.roll(x, true_lag) + rng.normal(0, 0.15, n)
y_ma7 = pd.Series(y_daily).rolling(7).mean().values
def xc(y, maxk=20):
    res = {}
    for k in range(0, maxk + 1):
        a, b = x[: n - k], y[k:]
        m = ~np.isnan(b)
        res[k] = float(np.corrcoef(a[m], b[m])[0, 1])
    return res
cd, cm = xc(y_daily), xc(y_ma7)
peak_d = max(cd, key=cd.get); peak_m = max(cm, key=cm.get)
near = sorted(k for k, v in cm.items() if v >= 0.9 * cm[peak_m])
out["smoothing_demo"] = {"true_lag_days": true_lag, "peak_lag_unsmoothed": int(peak_d), "peak_lag_after_7day_mean": int(peak_m), "lags_within_10pct_of_peak_after_smoothing": near}
json.dump(out, open("analysis.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:9000])
