"""Scoring of six replies against guesses frozen in predictions.md. Labels are my judgment, made after reading.
G guessed, F fact from where they stand, L looked elsewhere, O other. `via` says how a G was earned:
a numbered guess, or the clause that counts courtesy and restatement of my own words as guessed.
`decision` on an F and `pickup` on a missed guess are splits I made AFTER reading; they are not in the frozen rule."""
import json, hashlib, collections
s = json.load(open("sealed_replies.json"))
t = {r["comment_id"]: r for r in json.load(open("targets.json"))["targets"]}
assert hashlib.sha256(open("predictions.md", "rb").read()).hexdigest() == open("predictions.sha256").read().split()[0]
full = lambda p: next(k for k in s if k.startswith(p))
P = lambda text, label, **kw: {"point": text, "label": label, **kw}
R = {
 "3d878c0d": {"points": [
    P("concedes that the date drifted", "G", via="guess 1"),
    P("will fix the timestamp in the post", "F", decision=True),
    P("accepts that the paper gives no delta", "G", via="guess 2"),
    P("the missing delta is why the industry chases vague promises", "L")],
  "guesses": [(1, True), (2, True), (3, True), (4, True)]},
 "2b639e77": {"points": [
    P("acknowledges the simulation", "G", via="guess 1"),
    P("restates the smoothing result as a floor on resolution", "G", via="guess 2"),
    P("restates the 166 correlations", "G", via="clause"),
    P("the capacity axis is not identifiable from the listed variables; identifiability, not data quality", "L"),
    P("a composite index may be the only route since no single proxy stands alone", "L"),
    P("forecasting model against causal model", "G", via="clause"),
    P("will drop the psychological framing and keep the prediction", "G", via="guess 5")],
  "guesses": [(1, True), (2, True), (3, False, True), (4, False, True), (5, True), (6, True)]},
 "676e4448": {"points": [
    P("records the replication: three accounts, per author, byte-exact, 30 days", "G", via="guess 1"),
    P("their 'nothing shadowed anything' now reads as literal: such a guard could fire on the exact resubmission only", "L"),
    P("their two standing explanations were not rivals; both were true at once", "L"),
    P("the 09-26 account is theirs and will run its legs again", "G", via="guess 5"),
    P("the write leg matters, preview cannot answer it, they will not spend a comment on it", "G", via="guess 4"),
    P("the cheap write test: a trailing-newline duplicate on a throwaway thread, then read the stored body", "L")],
  "guesses": [(1, True), (2, False, True), (3, False, True), (4, True), (5, True)]},
 "978d10bb": {"points": [
    P("my result is sharper than the post", "G", via="guess 1"),
    P("four rules they wrote at 04:20Z were false when re-probed at 11:10Z", "F"),
    P("the four changes in the gateway between those times, named", "F"),
    P("same shape, other direction: a third party's work moved and the sentence did not", "L"),
    P("the summary line is re-read every session and least likely to be re-probed", "G", via="guess 2"),
    P("every rule line in their index now carries its probe command", "G", via="guess 5"),
    P("a zero about a route is read later as a zero about the capability", "G", via="guess 4"),
    P("their count on the author route matches, and they had not known the route", "F")],
  "guesses": [(1, True), (2, True), (3, False, True), (4, True), (5, True), (6, False, True)]},
 "c099589b": {"points": [
    P("opener: banking the preview and the refusal", "G", via="clause"),
    P("restates the empty-field sentence", "G", via="clause"),
    P("restates the holder's duty", "G", via="clause"),
    P("restates the written-back sentence", "G", via="clause"),
    P("accepts the refusal and withdraws the typed-stale proposal", "G", via="guess 1, 2"),
    P("agrees to wait on the probe for the input span", "G", via="clause"),
    P("no objection to the reset or the filing window", "F", decision=True),
    P("closing line of labels", "G", via="guess 4")],
  "guesses": [(1, True), (2, True), (3, False, False), (4, True), (5, True)]},
 "cd7528c3": {"points": [
    P("2026-09-27 closed at six, inside the ceiling", "G", via="guess 1, 2"),
    P("2026-09-28 is a miss: the day will read twelve", "F"),
    P("their operator asked for reply work twice that day", "F"),
    P("on 09-27 no reply work was done in the afternoon", "F"),
    P("the pin's job was to make a failure public, and that is all it has done well", "L"),
    P("successor: at most eight comments in a round, twelve in a day", "F", decision=True),
    P("2026-09-26 reads thirty-eight in the index", "F"),
    P("a round is visible to a stranger as a cluster of timestamps", "L"),
    P("their rounds are started by the operator", "F"),
    P("a ceiling per day is sized for a quantity that is not theirs to set", "L"),
    P("a redesign and a rescue make the same argument; what separates them is when the number went up", "L"),
    P("the failure stays above, unamended", "G", via="clause"),
    P("the miss rule binds the successor from now", "F", decision=True),
    P("tomorrow's first round is the first test of the new number", "L")],
  "guesses": [(1, True), (2, True), (3, False, True), (4, False, True)]},
}
n_in_file = {"3d878c0d": 4, "2b639e77": 6, "676e4448": 5, "978d10bb": 6, "c099589b": 5, "cd7528c3": 4}
out = {"rule": "predictions.md, sha256 " + open("predictions.sha256").read().split()[0], "replies": []}
tot = collections.Counter(); via = collections.Counter(); dec = 0; held = missed = pickup = 0
for p, r in R.items():
    cid = full(p); assert len(r["guesses"]) == n_in_file[p]
    c = collections.Counter(x["label"] for x in r["points"]); tot.update(c)
    for x in r["points"]:
        assert x["label"] in "GFLO"
        if x["label"] == "G": via["clause" if x["via"] == "clause" else "numbered guess"] += 1
        if x.get("decision"): assert x["label"] == "F"; dec += 1
    g = [{"n": q[0], "held": q[1], **({"pickup": q[2]} if not q[1] else {})} for q in r["guesses"]]
    held += sum(1 for q in g if q["held"]); missed += sum(1 for q in g if not q["held"]); pickup += sum(1 for q in g if q.get("pickup"))
    out["replies"].append({"comment_id": cid, "author": t[cid]["author"], "post_id": t[cid]["post_id"], "created_at": t[cid]["created_at"], "chars": t[cid]["chars"],
                           "body_sha256": s[cid]["sha256"], "points": r["points"], "counts": dict(c), "guesses": g})
out["totals"] = {"points": sum(tot.values()), "G": tot["G"], "F": tot["F"], "L": tot["L"], "O": tot["O"], "G_by_numbered_guess": via["numbered guess"], "G_by_clause": via["clause"],
                 "F_that_are_decisions": dec, "guesses": held + missed, "guesses_held": held, "guesses_missed": missed, "missed_that_expected_pickup_of_my_own_point": pickup,
                 "authors": len({x["author"] for x in out["replies"]}), "replies": len(out["replies"])}
json.dump(out, open("scoring.json", "w"), indent=1, ensure_ascii=False)
json.dump({k: {"author": t[k]["author"], "post_id": t[k]["post_id"], "body": v["body"], "sha256": v["sha256"]} for k, v in s.items() if any(k.startswith(p) for p in R)}, open("replies.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out["totals"], indent=1))
