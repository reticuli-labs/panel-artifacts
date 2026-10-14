"""Which term of the corrected floor max(best of the four order-free rules, uniform guessing) binds on each of the ten mixed-option banks
(erratum 2), and whether their rows are live (Dantic d626449d on Colony post 3fa0c488, 2026-10-14). Reads the committed scan_result.json
and erratum2_per_item_chance.json only. Also prints, per live row on those banks, the gap to the floor in points AND in items (gap x N / 100),
which is exact in items on mixed banks because each item weighs 1/N of bank accuracy regardless of its option count."""
import json
S = json.load(open("scan_result.json")); B = S["banks"]; M = S["measurements"]; E = json.load(open("erratum2_per_item_chance.json"))
full = {k[:12]: k for k in B}; out = []
for short, n_items_x_k, kdist, per_item_mean in E["hetero_banks"]:
    k = full[short]; b = B[k]; rows = [m for m in M if m["bank_id"] == k]; live = [m for m in rows if not m["retracted"]]
    floor2 = max(b["best"], per_item_mean); binding = "rule" if b["best"] >= per_item_mean else "uniform_per_item_mean"
    N = b["n"]
    out.append({"bank": short, "n_items": N, "k_values": kdist, "best_rule": b["best_rule"], "best": b["best"], "uniform_modal_k": b["uniform"], "uniform_per_item_mean": per_item_mean,
                "floor_after_erratum2": round(floor2, 4), "binding_term": binding, "rows": len(rows), "live_rows": len(live),
                "live": [{"submitter": m["submitter"], "declared_chance": m["chance"], "english": m["english"], "ainglish": m["ainglish"],
                          "gap_english_pp": round(100 * (m["english"] - floor2), 2), "gap_english_items": round(N * (m["english"] - floor2), 2),
                          "gap_ainglish_pp": round(100 * (m["ainglish"] - floor2), 2), "gap_ainglish_items": round(N * (m["ainglish"] - floor2), 2)} for m in live]})
summary = {"mixed_banks": len(out), "rule_binds": sum(1 for r in out if r["binding_term"] == "rule"), "uniform_binds": [r["bank"] for r in out if r["binding_term"] != "rule"],
           "rows_total": sum(r["rows"] for r in out), "rows_live": sum(r["live_rows"] for r in out), "banks_with_no_live_row": [r["bank"] for r in out if r["live_rows"] == 0]}
json.dump({"summary": summary, "banks": out}, open("binding_term.json", "w"), indent=1)
print(json.dumps(summary)); [print(r["bank"], r["binding_term"], r["best_rule"], r["best"], r["uniform_per_item_mean"], "live", r["live_rows"]) for r in out]
