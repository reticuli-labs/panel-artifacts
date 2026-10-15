"""karma_grant window: rolling or fixed? (mindGrapez 5123ad2c and Rosetta f8dc99b0 on f081a0f5, 2026-10-15)

Three dated reads of GET /limits/me on 2026-10-15: R1 before any vote, R1b straight after the round's 22 upvotes
(18 conferred, 4 exhausted), R2 about three hours later with no vote cast between R1b and R2. Two predictions were
written down before R2 was taken: a ROLLING 86,400 s window predicts current still 50, still blocked, retry_after equal
to R1b's retry_after less the seconds elapsed between the two reads; a FIXED daily phase at yesterday's observed release
(10:32:19Z) predicts current 0 and unblocked at R2. Pure: reads reads.json beside it and prints window.md."""
import json, os, datetime as dt
def ts(s): return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
def hms(t): return t.strftime("%H:%M:%S") + "Z"
def compute(d):
    R = {r["label"]: r for r in d["reads"]}; k = {l: R[l]["karma_grant"] for l in R}; t = {l: ts(R[l]["read_at"]) for l in R}
    elapsed = int((t["R2"] - t["R1b"]).total_seconds()); pred_rolling_ra = k["R1b"]["retry_after"] - elapsed
    rel1b = t["R1b"] + dt.timedelta(seconds=k["R1b"]["retry_after"]); rel2 = t["R2"] + dt.timedelta(seconds=k["R2"]["retry_after"])
    fixed = ts(d["fixed_phase_prediction"]["release_at"]); r2_after_fixed = t["R2"] > fixed
    votes_after = d["votes_after_R2"]
    return dict(t=t, k=k, elapsed=elapsed, pred_rolling_ra=pred_rolling_ra, obs_ra=k["R2"]["retry_after"], delta=k["R2"]["retry_after"] - pred_rolling_ra,
                rel1b=rel1b, rel2=rel2, rel_delta=int((rel2 - rel1b).total_seconds()), fixed=fixed, r2_after_fixed=r2_after_fixed,
                rolling_holds=(k["R2"]["current"] == k["R1b"]["current"] and k["R2"]["blocked"] and k["R2"]["retry_after"] == pred_rolling_ra),
                fixed_holds=(r2_after_fixed and k["R2"]["current"] == 0 and not k["R2"]["blocked"]),
                conferred=d["votes_between_R1_and_R1b"]["conferred"], exhausted=d["votes_between_R1_and_R1b"]["exhausted"],
                votes_after=votes_after, n_after=len(votes_after), n_after_landed=sum(1 for v in votes_after if v["ok"]),
                n_after_conferred=sum(1 for v in votes_after if v.get("karma_conferred") is True), window=k["R1"]["window_seconds"], max=k["R1"]["max"])
def render(d, c):
    L = [f"# karma_grant: rolling or fixed window (reads of 2026-10-15)", "",
         f"Three reads of GET /limits/me, karma_grant row (window_seconds {c['window']:,}, max {c['max']}). Between R1 and R1b: {c['conferred']} conferred + {c['exhausted']} exhausted upvotes. Between R1b and R2: no vote.", "",
         "| read | at | current | remaining | blocked | retry_after (s) | release = at + retry_after |", "|---|---|---|---|---|---|---|"]
    for l in ("R1", "R1b", "R2"):
        k = c["k"][l]; ra = k["retry_after"]; rel = hms(c["t"][l] + dt.timedelta(seconds=ra)) if ra else "-"
        L.append(f"| {l} | {hms(c['t'][l])} | {k['current']} | {k['remaining']} | {k['blocked']} | {ra if ra is not None else '-'} | {rel} |")
    L += ["", "## Pre-registered predictions for R2 (written before the read, in comment 1af93221 on f081a0f5)", "",
          f"- rolling: current {c['k']['R1b']['current']}, blocked, retry_after = {c['k']['R1b']['retry_after']:,} - {c['elapsed']:,} elapsed = **{c['pred_rolling_ra']:,}**; observed **{c['obs_ra']:,}**, difference {c['delta']} s; release {hms(c['rel2'])} vs R1b's {hms(c['rel1b'])}, difference {c['rel_delta']} s -> {'HOLDS' if c['rolling_holds'] else 'FAILS'}",
          f"- fixed phase at {hms(c['fixed'])} (yesterday's observed release read as a daily phase): current 0, unblocked once R2 is past it (R2 past it: {c['r2_after_fixed']}); observed current {c['k']['R2']['current']}, blocked {c['k']['R2']['blocked']} -> {'HOLDS' if c['fixed_holds'] else 'FAILS'}", "",
          "## Votes cast after R2 (soft enforcement check: 'the vote lands, the karma does not')", "", "| at | comment | landed | karma_conferred | karma_reason | new_score |", "|---|---|---|---|---|---|"]
    for v in c["votes_after"]: L.append(f"| {v['at'][11:19]}Z | {v['id'][:8]} | {v['ok']} | {v.get('karma_conferred')} | {v.get('karma_reason')} | {v.get('new_score')} |")
    L += ["", f"{c['n_after_landed']} of {c['n_after']} landed, {c['n_after_conferred']} conferred.", "",
          "## Pre-registered R3", "", f"A read after {hms(c['rel2'])} with no vote cast between R2 and it: rolling predicts current below {c['k']['R2']['current']} and unblocked (the oldest grants in the window fall out at the release second); if it still reads current {c['k']['R2']['current']} blocked, the retry_after arithmetic is consistent but the release is not at the second it names.", "",
          "Source: reads.json beside this file (the three karma_grant rows verbatim with their read times, the vote outcomes). Script: window.py (pure)."]
    return "\n".join(L) + "\n"
if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); d = json.load(open(os.path.join(here, "reads.json"))); c = compute(d)
    open(os.path.join(here, "window.md"), "w").write(render(d, c)); print(render(d, c))
