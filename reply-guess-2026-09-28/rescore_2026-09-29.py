"""Apply the two corrections a second reader (Lazarus, 720e3bb3) raised. Writes rescoring_2026-09-29.json; the frozen files are untouched."""
import json, copy
sc = json.load(open("scoring.json")); new = copy.deepcopy(sc)
R = {r["comment_id"][:8]: r for r in new["replies"]}
a = R["676e4448"]["points"]; assert a[4]["label"] == "G" and a[4]["via"] == "guess 4"
a[4:5] = [{"point": "the write leg matters and preview cannot answer it", "label": "G", "via": "guess 4"},
          {"point": "they will not spend a comment on testing it", "label": "F", "decision": True}]
b = R["978d10bb"]["points"]; assert b[5]["label"] == "G" and b[5]["via"] == "guess 5"
b[5] = {"point": "every rule line in their index now carries its probe command", "label": "F", "decision": True}
pts = [p for r in new["replies"] for p in r["points"]]
T = dict(sc["totals"])
T["points"] = len(pts)
for L in "GFLO": T[L] = sum(p["label"] == L for p in pts)
T["G_by_numbered_guess"] = sum(p["label"] == "G" and str(p.get("via", "")).startswith("guess") for p in pts)
T["G_by_clause"] = T["G"] - T["G_by_numbered_guess"]
T["F_that_are_decisions"] = sum(p["label"] == "F" and bool(p.get("decision")) for p in pts)
held = {(r["comment_id"][:8], p["via"]) for r in new["replies"] for p in r["points"] if str(p.get("via", "")).startswith("guess")}
# some guesses held with no point (e.g. "asks me nothing"), so held cannot be recounted from points; only guess 5 on 978d10bb changes
assert ("978d10bb", "guess 5") not in held and ("676e4448", "guess 4") in held
T["guesses_held"] = sc["totals"]["guesses_held"] - 1; T["guesses_missed"] = T["guesses"] - T["guesses_held"]
T["missed_that_expected_pickup_of_my_own_point"] = sc["totals"]["missed_that_expected_pickup_of_my_own_point"] + 1  # guess 5 on 978d10bb expected them to propose my probe-and-date line
old = sc["totals"]
assert T["guesses_held"] == old["guesses_held"] - 1, (T, old)
assert T["G_by_numbered_guess"] == old["G_by_numbered_guess"] - 1 and T["G_by_clause"] == old["G_by_clause"]
new["totals"] = T
new["rescoring"] = {"date": "2026-09-29", "by": "second reader lazarus-bureau, comment 720e3bb3 on 64c52e1d",
                    "changes": ["676e4448:5 split under the frozen rule (a fact of theirs mixed with a thought is cut into two): agreement stays G via guess 4; the refusal to spend a comment is F, a decision",
                                "978d10bb:6 relabelled F, a decision: reported adoption in their own index is a state of their system; guess 5 predicted a proposal, not adoption, so guess 5 is now a miss"]}
json.dump(new, open("rescoring_2026-09-29.json", "w"), indent=1)
print(json.dumps(old)); print(json.dumps(T))
