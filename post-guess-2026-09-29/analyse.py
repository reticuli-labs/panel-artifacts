"""Read my eight 300-cycle runs and their published files. Writes findings.json. Counts nothing by hand."""
import json, glob, os, sys
theirs = json.load(open("repo/results/CM-BAT-R12-conductivity.json"))
base = json.load(open("repo/results/CM-BAT-R12b-baseline.json"))
mine = {}
for f in sorted(glob.glob("runs300/direct_kappa*_N300.json")):
    d = json.load(open(f)); mine[(d["conductivity_scale_set"], d["tau"])] = d
need = [(s, t) for s in (0.125, 0.5, 2.0, 8.0) for t in (1.2, 1.8)]
missing = [k for k in need if k not in mine]
if missing: print("missing", missing); sys.exit(1)
for k, d in mine.items():
    assert d["error"] is None and d["cycles_completed"] == 300, (k, d["error"], d["cycles_completed"])
    assert d["conductivity_scale_seen_by_process_model"] == [k[0]], (k, d["conductivity_scale_seen_by_process_model"])
S = lambda d, n: d["summary_at_end"][n]
def row(d):
    caps = d["caps_at_cycles"]; c1, cN = caps["1"], caps["300"]
    return {"cap1_Ah": c1, "cap300_Ah": cN, "loss_Ah": c1 - cN, "retention_pct": 100 * cN / c1,
            "plating_Ah": S(d, "Loss of capacity to negative lithium plating [A.h]"), "sei_Ah": S(d, "Loss of capacity to negative SEI [A.h]"),
            "sei_on_cracks_Ah": S(d, "Loss of capacity to negative SEI on cracks [A.h]"), "side_reactions_total_Ah": S(d, "Total capacity lost to side reactions [A.h]"),
            "lli_pct": S(d, "Loss of lithium inventory [%]"), "lam_neg_pct": S(d, "Loss of active material in negative electrode [%]"),
            "theoretical_capacity_end_Ah": S(d, "Capacity [A.h]")}
T = {f"x{s:g}_tau{t:g}": row(mine[(s, t)]) for s, t in need}
# 1. reproduction: their labelled x0.5 / x2 against my direct x0.125 / x8, and against my direct x0.5 / x2
rep = {}
for label, ran, named in (("kappa0.5", 0.125, 0.5), ("kappa2", 8.0, 2.0)):
    for t in (1.2, 1.8):
        th = theirs[f"{label}_tau{t}"]
        a, b = mine[(ran, t)], mine[(named, t)]
        rep[f"{label}_tau{t}"] = {"their_retention": th["retention"], "their_plating_Ah": th["LLI_plating_Ah"], "their_sei_Ah": th["LLI_SEI_Ah"],
            f"mine_at_x{ran:g}": {"retention": a["retention"], "plating_Ah": S(a, "Loss of capacity to negative lithium plating [A.h]"), "sei_Ah": S(a, "Loss of capacity to negative SEI [A.h]")},
            f"mine_at_x{named:g}": {"retention": b["retention"], "plating_Ah": S(b, "Loss of capacity to negative lithium plating [A.h]"), "sei_Ah": S(b, "Loss of capacity to negative SEI [A.h]")},
            "rel_diff_plating_at_scale_that_ran": abs(S(a, "Loss of capacity to negative lithium plating [A.h]") - th["LLI_plating_Ah"]) / th["LLI_plating_Ah"],
            "abs_diff_retention_at_scale_that_ran": abs(a["retention"] - th["retention"])}
# 2. the table at each scale: penalty = tau 1.8 minus tau 1.2
def pen(lo, hi): return {"plating_penalty_mAh": 1000 * (hi["plating_Ah"] - lo["plating_Ah"]), "retention_penalty_pt": lo["retention_pct"] - hi["retention_pct"],
                         "plating_ratio": hi["plating_Ah"] / lo["plating_Ah"]}
bl = {t: base[f"kappa1_tau{t}"] for t in (1.2, 1.8)}
b_row = {t: {"plating_Ah": bl[t]["LLI_plating_Ah"], "retention_pct": 100 * bl[t]["retention"]} for t in bl}
pens = {f"x{s:g}": pen(T[f"x{s:g}_tau1.2"], T[f"x{s:g}_tau1.8"]) for s in (0.125, 0.5, 2.0, 8.0)}
pens["x1_their_R12b"] = pen(b_row[1.2], b_row[1.8])
# 3. budget: how much of the capacity lost is each recorded channel
bud = {k: {"loss_Ah": r["loss_Ah"], "plating_share": r["plating_Ah"] / r["loss_Ah"], "sei_share": r["sei_Ah"] / r["loss_Ah"], "sei_on_cracks_share": r["sei_on_cracks_Ah"] / r["loss_Ah"],
           "side_reactions_share": r["side_reactions_total_Ah"] / r["loss_Ah"]} for k, r in T.items()}
out = {"kind": "reticuli.cm-bat-r12.findings.v1", "their_repo_head": open("repo/head.txt").read().strip(), "pybamm_wheel_sha256": "b5977b7867f7159d2a3fe84fe1669ef9ae36312cfe234daf4681569a5c960289",
       "scale_probe": json.load(open("scale_probe.json"))["arms"], "reproduction": rep, "cells": T, "penalties": pens, "budget": bud,
       "seconds_per_run": {f"x{k[0]:g}_tau{k[1]:g}": d["seconds"] for k, d in mine.items()}}
json.dump(out, open("findings.json", "w"), indent=1)
print(json.dumps({"reproduction": rep, "penalties": pens, "budget": bud}, indent=1))
