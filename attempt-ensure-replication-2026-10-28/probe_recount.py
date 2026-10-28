"""Recount Saturnia's fb7a6ca7 table from my frozen cells: attempt items, per probe, per arm, correct/total; and where each attempt stratum's delta sits by probe."""
import json, collections
import os; B = os.path.dirname(os.path.abspath(__file__))  # run from anywhere; reads items.json and run/cells.json beside this file
items = {i["id"]: i for i in json.load(open(f"{B}/items.json"))}
rows = json.load(open(f"{B}/run/cells.json"))["rows"]; assert len(rows) == 512
real = [r for r in rows if r["item_id"] in items and items[r["item_id"]].get("form") in ("attempt", "ensure")]
print("rows", len(rows), "real rows", len(real), "arms", collections.Counter(r["arm"] for r in real))
def tally(pred):
    t = collections.defaultdict(lambda: [0, 0])
    for r in real:
        if pred(r):
            k = r["arm"]; t[k][1] += 1; t[k][0] += (r["correct"] is True or r["correct"] == "True")
    return dict(t)
print("\nATTEMPT items, per probe (marked=ainglish arm, english arm): correct/total")
out = {}
for probe in ("failure-completion", "outcome-required", "failure-unreported", "no-effort", "success", "failure-is-not-success", "retry-authority", "escalation-authority"):
    t = tally(lambda r: items[r["item_id"]]["form"] == "attempt" and items[r["item_id"]]["probe"] == probe)
    a, e = t.get("ainglish", [0, 0]), t.get("english", [0, 0]); out[probe] = (a, e)
    print(f"  {probe:24} marked {a[0]:2}/{a[1]:2}   english {e[0]:2}/{e[1]:2}")
print("\nATTEMPT strata x probe: marked acc - english acc (pp), with counts")
for st in ("retry-allowed", "retry-forbidden", "budget-exhausted", "irreversible"):
    line = []
    for probe in ("failure-completion", "outcome-required", "failure-unreported", "no-effort", "success", "failure-is-not-success", "retry-authority", "escalation-authority"):
        t = tally(lambda r: items[r["item_id"]]["form"] == "attempt" and items[r["item_id"]]["context"] == st and items[r["item_id"]]["probe"] == probe)
        a, e = t.get("ainglish", [0, 0]), t.get("english", [0, 0])
        da = (a[0] / a[1] if a[1] else float("nan")) - (e[0] / e[1] if e[1] else float("nan"))
        line.append(f"{probe[:12]} {a[0]}/{a[1]} vs {e[0]}/{e[1]} ({da*100:+.0f})")
    print(f"  attempt-{st}:\n    " + "\n    ".join(line))
json.dump({"attempt_probe_counts": out}, open(os.path.join(B, "probe_recount.json"), "w"), indent=1)
