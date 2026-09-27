"""Same panel at lower frequency: calendar-month means, and one long difference across states."""
import json, numpy as np, pandas as pd
def load(path, daycol):
    d = pd.read_csv(path, na_values=["."], low_memory=False)
    d["date"] = pd.to_datetime(dict(year=d["year"], month=d["month"], day=d[daycol])); return d
sp = load("affinity_state.csv", "day"); sp = sp[sp["date"].dt.dayofweek == 6]
emp = load("Employment_-_State_-_Weekly.csv", "day_endofweek"); ui = load("UI_Claims_-_State_-_Weekly.csv", "day_endofweek"); jp = load("Job_Postings_-_State_-_Weekly.csv", "day_endofweek")
print("job postings non-null by column:", jp[["bg_posts"]].notna().mean().round(3).to_dict(), "| states", jp["statefips"].nunique(), "| first/last", jp["date"].min().date(), jp["date"].max().date())
def monthly(d, cols):
    d = d.copy(); d["ym"] = d["date"].dt.to_period("M")
    return d.groupby(["ym", "statefips"])[cols].mean().reset_index()
S = monthly(sp, ["spend_all", "spend_durables", "spend_hic"])
P = monthly(emp, ["emp", "emp_wage_q1"]).merge(monthly(ui, ["initclaims_rate_regular", "contclaims_rate_regular"]), on=["ym", "statefips"], how="outer").merge(monthly(jp, ["bg_posts"]), on=["ym", "statefips"], how="outer")
M = S.merge(P, on=["ym", "statefips"], how="left")
def wide(col, lo, hi):
    w = M[(M["ym"] >= lo) & (M["ym"] <= hi)].pivot(index="ym", columns="statefips", values=col)
    return w.dropna(axis=1, thresh=int(0.95 * len(w))).dropna(axis=0)
def tw(w): return w.sub(w.mean(axis=1), axis=0).sub(w.mean(axis=0), axis=1).add(w.values.mean())
out = {"monthly": {}, "long_difference": {}}
for pname, (lo, hi) in {"2020-02 to 2021-06": ("2020-02", "2021-06"), "2021-07 to 2024-05": ("2021-07", "2024-05")}.items():
    out["monthly"][pname] = {}
    for tgt in ("spend_all", "spend_durables"):
        ws = wide(tgt, lo, hi)
        for col in ("emp", "emp_wage_q1", "initclaims_rate_regular", "contclaims_rate_regular", "bg_posts"):
            wp = wide(col, lo, hi); cs = ws.columns.intersection(wp.columns); idx = ws.index.intersection(wp.index)
            if len(cs) < 10 or len(idx) < 6:
                out["monthly"][pname][f"{tgt} ~ {col}"] = {"states": int(len(cs)), "months": int(len(idx)), "r": None}; continue
            r = float(np.corrcoef(tw(ws.loc[idx, cs]).values.ravel(), tw(wp.loc[idx, cs]).values.ravel())[0, 1])
            out["monthly"][pname][f"{tgt} ~ {col}"] = {"states": int(len(cs)), "months": int(len(idx)), "r": round(r, 3)}
# long difference across states: change from mid-2021 to mid-2024
def lvl(col, ym): 
    return M[M["ym"] == ym].set_index("statefips")[col]
for tgt in ("spend_all", "spend_durables"):
    dS = lvl(tgt, "2024-05") - lvl(tgt, "2021-07")
    for col in ("emp", "emp_wage_q1", "contclaims_rate_regular"):
        dP = lvl(col, "2024-05") - lvl(col, "2021-07")
        j = pd.concat([dS, dP], axis=1).dropna()
        out["long_difference"][f"{tgt} ~ {col}"] = {"states": int(len(j)), "r": round(float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1]), 3)}
# income-quartile split: the capacity axis the spending file already carries
q = sp[(sp["date"] >= "2020-03-01") & (sp["date"] <= "2020-06-28")].groupby("date")[["spend_all_q1", "spend_all_q4"]].mean()
nat = load("Affinity_-_National_-_Daily.csv", "day"); nat = nat[(nat["date"] >= "2020-03-01") & (nat["date"] <= "2020-08-02") & (nat["date"].dt.dayofweek == 6)]
cols = [c for c in ("spend_all_q1", "spend_all_q4") if c in nat.columns]
tr = nat.set_index("date")[cols]
out["quartiles_2020"] = {"min_q1": [str(tr["spend_all_q1"].idxmin().date()), round(float(tr["spend_all_q1"].min()), 3)], "min_q4": [str(tr["spend_all_q4"].idxmin().date()), round(float(tr["spend_all_q4"].min()), 3)],
                         "q1_on_2020-06-28": round(float(tr.loc["2020-06-28", "spend_all_q1"]), 3), "q4_on_2020-06-28": round(float(tr.loc["2020-06-28", "spend_all_q4"]), 3)}
json.dump(out, open("analysis2.json", "w"), indent=1); print(json.dumps(out, indent=1))
