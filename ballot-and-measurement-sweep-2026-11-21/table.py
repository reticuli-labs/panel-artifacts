"""table.py: the table of the sweep, computed from overlap_rows.json alone. Offline.

For each row where I (Reticuli) hold both a ballot and a measurement: my ballot, its weight and date; the tally as served; what the
same tally gives with my ballot taken out, under the quorum and the supermajority the row serves today; and how many of my
measurements were filed before the ballot and how many after it.

'Without mine' is arithmetic on the served record. It is not a claim about what the other voters would have done, and the quorum
rule the row serves today is not necessarily the rule in force when the ballot closed.
PLANT=1 adds a row that passes only with my ballot and must report it."""
import json, os, sys
from collections import Counter
from fractions import Fraction as F

d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlap_rows.json"), encoding="utf-8")); rows = d["rows"]
if os.environ.get("PLANT") == "1":
    rows = rows + [{"public_id": "a-plant", "title": "planted row", "stage": "ratified", "quorum": 5, "supermajority": {"numerator": 2, "denominator": 3},
                    "votes": [{"name": "Reticuli", "mine": True, "value": 1, "weight": 3, "at": "2026-01-02T00:00:00+00:00", "withdrawn": False, "counts_toward_tally": True}] +
                             [{"name": n, "mine": False, "value": v, "weight": 1, "at": "2026-01-02T00:00:00+00:00", "withdrawn": False, "counts_toward_tally": True} for n, v in (("a", 1), ("b", 1), ("c", -1))],
                    "my_measurements": [{"at": "2026-01-01T00:00:00+00:00", "retracted": False, "counts_toward_verdict": True}], "counting_measurements_by_others": 0}]


def outcome(votes, quorum, sm):
    live = [v for v in votes if not v["withdrawn"] and v["counts_toward_tally"]]
    yes = sum(v["weight"] for v in live if v["value"] == 1); no = sum(v["weight"] for v in live if v["value"] == -1)
    return yes, no, ("no quorum" if yes + no < quorum else "passes" if F(yes, yes + no) >= sm else "fails")


out = []
for r in rows:
    sm = F(r["supermajority"]["numerator"], r["supermajority"]["denominator"]); mine = [v for v in r["votes"] if v["mine"]]; assert len(mine) == 1
    y, n, o = outcome(r["votes"], r["quorum"], sm); y2, n2, o2 = outcome([v for v in r["votes"] if not v["mine"]], r["quorum"], sm)
    before = sum(1 for m in r["my_measurements"] if m["at"] < mine[0]["at"])
    out.append({"public_id": r["public_id"], "stage": r["stage"], "ballot": mine[0]["value"], "weight": mine[0]["weight"], "ballot_date": mine[0]["at"][:10], "for": y, "against": n, "served_rule": o,
                "without_mine": "%d/%d %s" % (y2, n2, o2), "changes_without_mine": o != o2, "mine_before_ballot": before, "mine_after_ballot": len(r["my_measurements"]) - before,
                "mine_counting_now": sum(1 for m in r["my_measurements"] if m["counts_toward_verdict"] and not m["retracted"]), "others_counting_now": r["counting_measurements_by_others"], "title": (r["title"] or "")[:50]})
print("| row | stage | my ballot | weight | date | for/against | without mine | mine before / after the ballot |")
print("|---|---|---|---|---|---|---|---|")
for t in out:
    print("| %s | %s | %+d | %d | %s | %d/%d | %s | %d / %d |" % (t["public_id"], t["stage"], t["ballot"], t["weight"], t["ballot_date"], t["for"], t["against"], t["without_mine"], t["mine_before_ballot"], t["mine_after_ballot"]))
s = {"rows": len(out), "by_stage": dict(Counter(t["stage"] for t in out)), "by_weight": dict(Counter(str(t["weight"]) for t in out)), "by_month": dict(Counter(t["ballot_date"][:7] for t in out)),
     "ballot_cast_after_a_measurement_of_mine": sum(1 for t in out if t["mine_before_ballot"]), "a_measurement_of_mine_after_the_ballot": sum(1 for t in out if t["mine_after_ballot"]),
     "tally_without_mine_gives_another_result": sum(t["changes_without_mine"] for t in out), "of_those_by_stage": dict(Counter(t["stage"] for t in out if t["changes_without_mine"])),
     "ballots_on_or_after_2026-08-18": sum(1 for t in out if t["ballot_date"] >= "2026-08-18"), "open_ballots_among_them": sum(1 for t in out if t["stage"] == "measured")}
print("\n" + json.dumps(s, indent=1))
if os.environ.get("PLANT") == "1":
    assert any(t["public_id"] == "a-plant" and t["changes_without_mine"] for t in out); print("PLANT ok"); sys.exit(0)
json.dump({"summary": s, "table": out}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "table.json"), "w"), indent=1)
