"""Retained-cell audit of Dexagon's because / ever since careful-English original 415552aa (attempt 8ab30123, 2026-09-06).

Inputs, all in this directory and all public:
  cells.json             his retained scientific cells  (progression-2026-09-06/since.careful.attempt-8ab30123-….cells.json @ b6fd210)
  calibration.cells.json his retained control cells     (same directory and commit)
  items.json             the frozen bank the manifest pins (items_url @ 9c2685e; canonical sha256 = manifest items_sha256)
  m_415552aa.json        the served measurement row (GET /api/v1/measurements/415552aa…, 2026-10-24)
Writes audit.json and tables.md. No inference, no network, no filing.
"""
import json, re, hashlib, collections, sys, os
H = os.path.dirname(os.path.abspath(__file__))
L = lambda n: json.load(open(os.path.join(H, n)))
cells = L("cells.json"); cal = L("calibration.cells.json"); bank_all = L("items.json"); m = L("m_415552aa.json")["result"]
canon_sha = hashlib.sha256(json.dumps(bank_all, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
assert canon_sha == m["manifest"]["items_sha256"], (canon_sha, m["manifest"]["items_sha256"])
assert cells["attempt_id"] == "8ab30123-7a18-402a-8194-92e859977ed4" and cells["real_cells_recorded"] == 576
rows = cells["rows"]; assert len(rows) == 576
bank = {it["id"]: it for it in bank_all if it.get("settlement_stratum")}; assert len(bank) == 288

def canon(it, letter):
    """Map an answer letter to (reason asserted?, interval asserted?) through the item's own question text."""
    q = it["question"]; s = it["strata"]["answer_options"].get(letter)
    if s is None: return "ABSENT"
    a1, a2 = (x == "yes" for x in re.match(r"1: (yes|no); 2: (yes|no)", s).groups())
    reason_first = q.startswith("1. Does this sentence itself say that the event explains")
    assert reason_first or q.startswith("1. Does it itself assert a condition holding"), q[:80]
    r, i = (a1, a2) if reason_first else (a2, a1)
    return ("Ry" if r else "Rn") + ("Iy" if i else "In")

GOLD = {"reason": "RyIn", "interval": "RnIy", "both": "RyIy", "neither": "RnIn"}
for it in bank.values(): assert canon(it, it["answer"]) == GOLD[it["settlement_stratum"]], it["id"]
for c in rows: assert (canon(bank[c["item_id"]], c["answer"]) == canon(bank[c["item_id"]], c["expected"])) == bool(c["correct"])

# 1. per stratum x arm (x reader): n, correct, answer distribution in canonical terms
dist = collections.defaultdict(collections.Counter); acc = collections.defaultdict(lambda: [0, 0])
for c in rows:
    it = bank[c["item_id"]]; s = it["settlement_stratum"]; r = c["reader"].split("-")[0]
    for k in ((s, c["arm"], "all"), (s, c["arm"], r)):
        dist[k][canon(it, c["answer"])] += 1; acc[k][0] += int(bool(c["correct"])); acc[k][1] += 1
# served stratum arms must equal the recount
served = {s["id"]: s for s in m["stratum_results"]}
for s in GOLD:
    for arm in ("english", "ainglish"):
        ok, n = acc[(s, arm, "all")]; assert abs(ok / n - served[s]["arms"][arm]) < 5e-5, (s, arm, ok, n, served[s]["arms"][arm])

# 2. question-phrase echo
Q_REASON = "explains why"; Q_INT = "from that event"
echo = {}
for s in GOLD:
    for arm in ("english", "ainglish"):
        t = [it[arm] for it in bank.values() if it["settlement_stratum"] == s]
        echo[f"{s}/{arm}"] = {"n": len(t), "has_explains_why": sum(Q_REASON in x for x in t), "has_from_that_event": sum(Q_INT in x for x in t),
                              "has_because": sum(bool(re.search(r"\bbecause\b", x, re.I)) for x in t), "has_ever_since": sum("ever since" in x.lower() for x in t),
                              "has_present_perfect": sum(bool(re.search(r"\b(has|have)\s+\w+", x)) for x in t)}
questions = sorted(set(it["question"] for it in bank.values()))
assert all(Q_REASON in q and "from that event through the review date" in q for q in questions)
neither_identical = sum(it["english"] == it["ainglish"] for it in bank.values() if it["settlement_stratum"] == "neither")

# 3. stratum tolerance vs one item step
step = {}
for s in GOLD:
    v = served[s]["value"]; tol = max(0.02, 0.1 * abs(v))
    n_en, n_ai = acc[(s, "english", "all")][1], acc[(s, "ainglish", "all")][1]
    st = max(100 / n_en, 100 / n_ai)
    step[s] = {"value_pp": v, "tolerance_pp": round(tol, 4), "cells_english": n_en, "cells_ainglish": n_ai, "one_item_step_pp": round(st, 4), "tolerance_below_step": tol < st}

# 4. calibration
calc = collections.Counter((c["arm"], bool(c["correct"])) for c in cal["rows"])
out = {"attempt": cells["attempt_id"], "manifest_hash": m["manifest_hash"], "items_sha256": canon_sha, "served_value_pp": m["value"], "served_interval_pp": [m["value_lo"], m["value_hi"]],
       "questions_distinct": len(questions), "neither_items_identical_arms": neither_identical, "echo": echo, "stratum_step": step,
       "calibration": {f"{a}/{'correct' if ok else 'incorrect'}": n for (a, ok), n in calc.items()},
       "cells": {f"{s}/{arm}/{r}": {"n": acc[(s, arm, r)][1], "correct": acc[(s, arm, r)][0], "accuracy": round(acc[(s, arm, r)][0] / acc[(s, arm, r)][1], 4), "answers": dict(dist[(s, arm, r)])}
                 for (s, arm, r) in sorted(acc)}}
json.dump(out, open(os.path.join(H, "audit.json"), "w"), indent=1, sort_keys=True)

T = ["# Tables (written by audit.py)", "", "## Cells by stratum, arm and reader (Ry/Rn = reason asserted yes/no, Iy/In = interval asserted yes/no; gold: reason RyIn, interval RnIy, both RyIy, neither RnIn)", "",
     "| stratum | arm | reader | cells | correct | accuracy | RyIn | RnIy | RyIy | RnIn |", "|---|---|---|---|---|---|---|---|---|---|"]
for (s, arm, r) in sorted(acc, key=lambda k: (list(GOLD).index(k[0]), k[1], k[2])):
    d = dist[(s, arm, r)]; ok, n = acc[(s, arm, r)]
    T.append(f"| {s} | {arm} | {r} | {n} | {ok} | {ok/n:.3f} | {d.get('RyIn',0)} | {d.get('RnIy',0)} | {d.get('RyIy',0)} | {d.get('RnIn',0)} |")
T += ["", "## Question-phrase echo (count of the stratum's 72 sentences containing the phrase)", "", "| stratum/arm | explains why | from that event | because | ever since | present perfect |", "|---|---|---|---|---|---|"]
for k, e in echo.items(): T.append(f"| {k} | {e['has_explains_why']} | {e['has_from_that_event']} | {e['has_because']} | {e['has_ever_since']} | {e['has_present_perfect']} |")
T += ["", "## Stratum tolerance against one item step", "", "| stratum | served value pp | tolerance pp | cells en / ai | one item step pp | tolerance below step |", "|---|---|---|---|---|---|"]
for s, v in step.items(): T.append(f"| {s} | {v['value_pp']} | {v['tolerance_pp']} | {v['cells_english']} / {v['cells_ainglish']} | {v['one_item_step_pp']} | {'yes' if v['tolerance_below_step'] else 'no'} |")
open(os.path.join(H, "tables.md"), "w").write("\n".join(T) + "\n")
print("\n".join(T)); print("calibration", dict(calc), "| neither identical", neither_identical, "/ 72 | questions", len(questions))
