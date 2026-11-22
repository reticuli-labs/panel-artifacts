"""after_the_results.py --sweep DIR --results FILE --out FILE: written AFTER results.json existed, to read it against yesterday's
sweep. Nothing here was fixed in PLAN.md, so every figure it adds is a second look and no test. Reads the sweep's files and FILE
(results.json); writes --out and nothing else; calls no reader. It adds:
  flagged          per flagged bank and rule: the score, the share of the bank's sorted ceiling it reaches, and what yesterday's
                   blind reader scored on the same bank (with yesterday's null, p and flag)
  one_position     banks whose key sits in one position in every real item, with yesterday's figures: the cases in which
                   yesterday's null equals the reader's score by construction
  null_demo        yesterday's permutation function on two made-up readers of 40 items with 4 options
  twin_banks       banks in which at least 90 in 100 real items have a twin (same blind text, question and option set, another
                   key): in how many twin groups the options are LISTED in the same order, and the position rules on them
  my_measurements  my filed measurements on a bank with a flagged rule, as the register served them on 2026-11-21"""
import argparse, collections, json, os, sys
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--sweep", required=True); ap.add_argument("--results", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    S = a.sweep; jl = lambda n: [json.loads(l) for l in open(os.path.join(S, n), encoding="utf-8") if l.strip()]; js = lambda n: json.load(open(os.path.join(S, n), encoding="utf-8"))
    res = json.load(open(a.results, encoding="utf-8")); items = {r["id"]: r for r in jl("blind_items.jsonl")}; reads = {r["id"]: r for r in jl("reads.jsonl")}
    yest = {r["sha256_items"]: r for r in js("results.json")["rows"]}; contrast = {o["sha256_items"]: o for o in js("contrast.json")}; banks = {}
    for b in js("banks.json"): banks.setdefault(b["sha256_items"], b)
    real = lambda sha: [i for i in banks[sha]["item_ids"] if not items[i]["calibration"] and not items[i]["identical_arms"]]
    y = lambda sha: {"blind": yest[sha]["blind"], "n": yest[sha]["n"], "null": yest[sha]["null_mean"], "p": round(yest[sha]["p"], 5), "flagged": yest[sha]["flagged"]}
    out = {"what": __doc__.split("\n")[0], "flagged": [], "one_position": [], "twin_banks": [], "my_measurements": []}
    for b in res["rows"]:
        for r in b["flagged_rules"]:
            q = b["rules"][r]; cap = b["ceiling_sorted"] if r in ("longest", "shortest", "echo") else None
            out["flagged"].append({"bank": b["bank"], "sweep_class": b["sweep_class"], "n": b["n"], "rule": r, "right": q["right"], "decided": q["decided"], "expected": q["expected"], "complete": q["right"] == q["decided"],
                                   "decides_every_item": q["decided"] == b["n"], "ceiling_sorted": b["ceiling_sorted"],
                                   "at_the_sorted_ceiling": bool(cap is not None and cap < 0.999 and q["decided"] == b["n"] and abs(q["right"] / b["n"] - cap) < 0.005), "yesterday": y(b["sha256_items"])})
        if len(b["key_position"]) == 1: out["one_position"].append({"bank": b["bank"], "n": b["n"], "key_position": next(iter(b["key_position"])), "yesterday": y(b["sha256_items"])})
    # yesterday's null on two made-up readers
    sys.path.insert(0, S); import analyse as A
    rng = np.random.default_rng(A.SEED)
    o1 = A.permutation([(4, 0, 0)] * 40, rng); o2 = A.permutation([(4, i % 4, i % 4) for i in range(40)], rng)
    out["null_demo"] = {"key always first, reader always answers the first": {"right": o1[0], "null_mean": o1[1], "p": o1[2]},
                        "key in each position equally often, reader finds it every time": {"right": o2[0], "null_mean": o2[1], "p": o2[2]}}
    # twin banks
    for sha, o in contrast.items():
        if o["contrast_share"] < 0.9: continue
        ids = real(sha); g = collections.defaultdict(list)
        for i in ids: g[(items[i]["blind"], items[i]["question"], tuple(sorted(items[i]["options"])))].append(i)
        tw = [v for v in g.values() if len({items[i]["answer"] for i in v}) > 1]; rb = next(b for b in res["rows"] if b["sha256_items"] == sha)
        out["twin_banks"].append({"bank": o["bank"], "n": len(ids), "flagged_yesterday": o["flagged"], "twin_groups": len(tw), "group_sizes": sorted({len(v) for v in tw}),
                                  "groups_listed_in_one_order": sum(len({tuple(items[i]["options"]) for i in v}) == 1 for v in tw), "content_ceiling": o["ceiling"], "blind": sum(reads.get(i, {}).get("picked") == items[i]["answer"] for i in ids),
                                  "blind_picks_one_option_for_the_whole_group": sum(len({reads.get(i, {}).get("picked") for i in v}) == 1 for v in tw), "key_position": rb["key_position"],
                                  "first": [rb["rules"]["first"]["right"], rb["rules"]["first"]["decided"], rb["rules"]["first"]["expected"]], "last": [rb["rules"]["last"]["right"], rb["rules"]["last"]["decided"], rb["rules"]["last"]["expected"]],
                                  "flagged_rules_today": rb["flagged_rules"]})
    # my measurements
    by = {b["sha256_items"]: b for b in res["rows"]}
    for m in js("my_measurements.json")["measurements"]:
        b = by.get(m.get("bank"))
        if b is None or not b["flagged_rules"]: continue
        out["my_measurements"].append({"row": m["row"], "slug": m["slug"], "stage": m["stage"], "manifest_hash": m["manifest_hash"], "metric": m["metric"], "value": m["value"], "at": m["at"], "is_replication": m["is_replication"],
                                       "retracted": m["retracted"], "counts_toward_verdict": bool(m["counts_toward_verdict"]) and not m["retracted"], "bank": b["bank"], "sweep_class": b["sweep_class"],
                                       "rules": {r: [b["rules"][r]["right"], b["rules"][r]["decided"]] for r in b["flagged_rules"]}})
    mm = out["my_measurements"]; fl = out["flagged"]; tb = out["twin_banks"]
    out["counts"] = {"flagged_pairs": len(fl), "complete_pairs": sum(f["complete"] for f in fl), "banks_with_a_complete_rule": len({f["bank"] for f in fl if f["complete"]}),
                     "pairs_at_the_sorted_ceiling": sum(f["at_the_sorted_ceiling"] for f in fl), "banks_flagged_today_not_yesterday": len({f["bank"] for f in fl if not f["yesterday"]["flagged"]}),
                     "banks_with_one_key_position": len(out["one_position"]), "twin_banks": len(tb), "twin_banks_listed_in_one_order": sum(t["groups_listed_in_one_order"] == t["twin_groups"] for t in tb),
                     "twin_banks_flagged_yesterday": sum(t["flagged_yesterday"] for t in tb), "twin_banks_flagged_yesterday_listed_in_one_order": sum(t["flagged_yesterday"] and t["groups_listed_in_one_order"] == t["twin_groups"] for t in tb),
                     "my_measurements_on_flagged_banks": len(mm), "of_them_retracted_before_today": sum(m["retracted"] for m in mm), "of_them_not_retracted": sum(not m["retracted"] for m in mm),
                     "of_them_counting_toward_a_verdict": sum(m["counts_toward_verdict"] for m in mm), "directories_with_a_flagged_bank": len({f["bank"].split("/")[0] for f in fl})}
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1)); print(json.dumps(out["null_demo"], indent=1)); print("one position:", json.dumps(out["one_position"]))
    for t in tb: print("twin %-58s n=%3d groups=%3d one order in %3d | ceiling %.2f blind %3d | first %s last %s | %s %s" % (t["bank"][:58], t["n"], t["twin_groups"], t["groups_listed_in_one_order"], t["content_ceiling"], t["blind"], t["first"], t["last"], "flagged yesterday" if t["flagged_yesterday"] else "", t["flagged_rules_today"]))
    for f in fl:
        if f["at_the_sorted_ceiling"]: print("at the ceiling:", f["bank"][:60], f["rule"], f["right"], "of", f["decided"], "ceiling", f["ceiling_sorted"])


if __name__ == "__main__":
    main()
