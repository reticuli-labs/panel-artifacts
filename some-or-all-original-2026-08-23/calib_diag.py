#!/usr/bin/env python3
"""Calibration items (planted_arm=ainglish: marked form vs bare 'some' — answer derivable
only from the marked arm) and the bare-'some' diagnostics block (NOT part of the carrier)."""
import json, sys
sys.path.insert(0, ".")
from banks import SC
from build import claims, answer, lint_item, content_words, TMAP, YES, NO, CT

NEUTRAL_LOC = ["at this point", "as things stand", "among them", "right now"]
def neutral(s, idx):
    return dict(s, loc=NEUTRAL_LOC[idx % 4],
                sa=s["sa"].replace("every ", "each "), sn=s["sn"].replace("every ", "each "),
                pi=s["pi"].replace("every ", "each "), ni=s["ni"].replace("every ", "each "))

# 8 calibration scenarios: first of each domain + one extra (index 28)
CAL_IDX = [0, 8, 16, 24, 32, 40, 48, 28]
def build_cal(form):
    out, fails = [], []
    for k, si in enumerate(CAL_IDX):
        s = neutral(SC[si], si)
        ain_claim, _ = claims(s, form)
        bare = f"Some {s['np']} {s['vp']}."
        if form == "sba":
            q = TMAP["M_GNP"][1][k % 3](s)      # guarantee of a non-P member: derivable=yes from sba
        else:
            q = TMAP["M_CONS_ALLP"][1][k % 2](s) # compatible with all-case: derivable=yes from soa
        item = {"id": f"cal-{form}-{k}", "calibration": True,
                "english": f"{s['lead']} {bare}",
                "ainglish": f"{s['lead']} {ain_claim}",
                "question": q, "options": ["yes", "cannot tell"], "answer": "yes"}
        bad = lint_item(item)
        if bad: fails.append((item["id"], bad))
        out.append(item)
    return out, fails

# diagnostics: bare-'some' arm with LICENSED keys (lower-bound-as-worded = SOA bounds)
def build_diag():
    real = json.load(open("soa_items.json"))
    out = []
    for i in real:
        s_meta = i["meta"]
        out.append({"id": i["id"].replace("soa-", "bare-"),
                    "claim": i["ainglish"].replace(
                        # replace the marked clause with bare 'some'
                        "Some-or-all", "Some"),
                    "question": i["question"], "options": i["options"],
                    "licensed_answer": i["answer"],
                    "note": "licensed key = as-worded lower-bound semantics (k in [1,N]); divergence from readers' answers measures unlicensed implicature uptake",
                    "meta": s_meta})
    return out

if __name__ == "__main__":
    total_fail = 0
    for form in ("soa", "sba"):
        cal, fails = build_cal(form)
        total_fail += len(fails)
        for f in fails: print("CAL LINT FAIL:", f)
        json.dump(cal, open(f"{form}_calibration.json", "w"), indent=1, ensure_ascii=False)
        print(f"[{form}] calibration: {len(cal)} items")
    diag = build_diag()
    json.dump(diag, open("diagnostics_bare_some.json", "w"), indent=1, ensure_ascii=False)
    print(f"diagnostics: {len(diag)} bare-some items (licensed keys)")
    print("CAL LINT FAILURES:", total_fail)
    # show one calibration pair per form
    for form in ("soa", "sba"):
        c = json.load(open(f"{form}_calibration.json"))[0]
        print(f"--- {c['id']}\n AIN: {c['ainglish']}\n ENG: {c['english']}\n Q: {c['question']} -> {c['answer']}")
