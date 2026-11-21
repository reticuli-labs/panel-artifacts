"""rescore_cells.py <isolation.json> <cells.json>: a POST-HOC reading of the saved reader answers of my filed replication f139083d,
split by whether the item's key depends on the statement (audit_isolation.py). Offline, read-only. Nothing here is a new
measurement and nothing is filed: no key is changed, the split was chosen after the answers were known, and the numbers are a
diagnostic of the instrument.

For each reader and arm: cells, share fully correct, and the share with the CLAIM flag right, on the statement-dependent items and
on the others. On the dependent items where the statement-blind rule (claim true if x is the mean or a most probable value) gives
the wrong claim flag, it counts how often a reader's claim flag follows the key and how often it follows that rule: a reader who
reads the statement follows the key."""
import collections, json, re, sys

iso = json.load(open(sys.argv[1])); rows = {r["id"]: r for r in iso["rows"]}
cells = json.load(open(sys.argv[2]))["rows"]
flag = lambda s: re.match(r"Claim true: (yes|no);", s or "").group(1) if re.match(r"Claim true: (yes|no);", s or "") else None
assert len(cells) == 480 and all(c["item_id"] in rows for c in cells) and all(c["expected"] == rows[c["item_id"]]["key"] for c in cells)
assert all(c["correct"] == (c["answer"] == c["expected"]) for c in cells), "a stored correct flag is not answer == expected"
out = {"cells": len(cells), "by_reader_arm": {}, "pooled_by_arm": {}, "follow": {}}
for dep in (True, False):
    name = "statement_dependent" if dep else "statement_independent"
    for rd in sorted({c["reader"] for c in cells}) + ["ALL"]:
        for arm in ("english", "ainglish"):
            cs = [c for c in cells if rows[c["item_id"]]["depends_on_statement"] == dep and c["arm"] == arm and (rd == "ALL" or c["reader"] == rd)]
            full = sum(c["correct"] for c in cs); cl = sum(flag(c["answer"]) == flag(c["expected"]) for c in cs); unparsed = sum(flag(c["answer"]) is None for c in cs)
            out["by_reader_arm"]["%s | %s | %s" % (name, rd, arm)] = {"cells": len(cs), "fully_correct": full, "share": round(full / len(cs), 4), "claim_flag_right": cl, "claim_share": round(cl / len(cs), 4), "answer_not_an_option": unparsed}
    for rd in sorted({c["reader"] for c in cells}) + ["ALL"]:
        a = out["by_reader_arm"]["%s | %s | ainglish" % (name, rd)]; e = out["by_reader_arm"]["%s | %s | english" % (name, rd)]
        out["pooled_by_arm"]["%s | %s" % (name, rd)] = {"marked_minus_english_full_pp": round(100 * (a["share"] - e["share"]), 2), "marked_minus_english_claim_flag_pp": round(100 * (a["claim_share"] - e["claim_share"]), 2)}
# where the statement-blind rule's claim flag is wrong
bad = {i for i, r in rows.items() if r["depends_on_statement"] and flag(r["rule_b"]) != flag(r["key"])}
good = {i for i, r in rows.items() if r["depends_on_statement"] and flag(r["rule_b"]) == flag(r["key"])}
out["dependent_items_where_blind_rule_claim_wrong"] = len(bad); out["dependent_items_where_blind_rule_claim_right"] = len(good)
for rd in sorted({c["reader"] for c in cells}):
    for arm in ("english", "ainglish"):
        cs = [c for c in cells if c["item_id"] in bad and c["reader"] == rd and c["arm"] == arm]
        k = sum(flag(c["answer"]) == flag(c["expected"]) for c in cs); b = sum(flag(c["answer"]) == flag(rows[c["item_id"]]["rule_b"]) for c in cs)
        cg = [c for c in cells if c["item_id"] in good and c["reader"] == rd and c["arm"] == arm]; kg = sum(flag(c["answer"]) == flag(c["expected"]) for c in cg)
        out["follow"]["%s | %s" % (rd, arm)] = {"cells_where_rule_wrong": len(cs), "claim_follows_key": k, "claim_follows_blind_rule": b, "cells_where_rule_right": len(cg), "claim_right_there": kg}
# the FILED formula (equal weight over the two settlement strata; within a stratum, cells pooled by arm), on all cells and on each subset.
# On all cells it must give the filed +3.885: that is the check that this script reads the cells the way the harness scored them.
def filed_formula(cs):
    d = []
    for s in ("mean-outcome", "likeliest-outcome"):
        acc = {}
        for arm in ("english", "ainglish"):
            x = [c for c in cs if rows[c["item_id"]]["stratum"] == s and c["arm"] == arm]; acc[arm] = sum(c["correct"] for c in x) / len(x)
        d.append(acc["ainglish"] - acc["english"])
    return round(100 * sum(d) / 2, 3)
allv = filed_formula(cells); assert abs(allv - 3.885) < 0.006, ("the filed value is not reproduced from the cells", allv)
out["filed_formula_pp"] = {"all_240_items": allv, "statement_dependent_112": filed_formula([c for c in cells if rows[c["item_id"]]["depends_on_statement"]]),
                           "statement_independent_128": filed_formula([c for c in cells if not rows[c["item_id"]]["depends_on_statement"]])}
print(json.dumps(out, indent=1))
if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1)
