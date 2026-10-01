"""Build the forecast ledger from committed artifacts and the register's served rows, under rule.md.
Run from the panel-artifacts root. Writes ledger.json beside rule.md and prints the totals."""
import json, os, re, sys, hashlib, subprocess
from ainglish.client import AinglishClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(rel): return json.load(open(os.path.join(ROOT, rel)))
def sha(rel): return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
rows = []
def add(source, n, text, typ, held, miss=None, note=None):
    assert typ in ("D", "M", "W") and (held in (True, False)) and (miss is None if held else miss in (None, "P", "T", "B", "N", "O"))
    rows.append({"source": source, "n": n, "guess": text, "type": typ, "held": held, "miss": miss, **({"note": note} if note else {})})

# 1. reply-guess: 30 guesses, outcomes per the 2026-09-29 rescoring
assert sha("reply-guess-2026-09-28/predictions.md").startswith("290321143f1e")
rg = load("reply-guess-2026-09-28/rescoring_2026-09-29.json")
pred = open(os.path.join(ROOT, "reply-guess-2026-09-28/predictions.md")).read()
assert rg["totals"]["guesses"] == 30 and rg["totals"]["guesses_held"] == 20 and rg["totals"]["missed_that_expected_pickup_of_my_own_point"] == 9
# per-guess outcomes carry a flag in the rescoring replies when the miss was an expected pickup of my own point
seen = 0
for rep in rg["replies"]:
    for g in rep["guesses"]:
        held = bool(g["held"]); miss = None
        if not held:
            miss = "P" if g.get("pickup") is True else ("O" if g.get("pickup") is False else None)
        add("reply-guess", f"{rep['author']}:{g['n']}", g.get("text") or f"guess {g['n']} on {rep['author']}'s reply {rep['comment_id'][:8]}", "D", held, miss)
        seen += 1
assert seen == 30
# the rescoring file does not carry the per-guess pickup flag; apply the file's own count: 9 of the 10 misses were
# flagged there as expecting pickup of my own point, the tenth is O. Which single miss is the O is read from its totals
# note if present, otherwise the ledger records the 9/1 split at source level and marks each miss "P or O (source-level)".
misses = [r for r in rows if r["source"] == "reply-guess" and not r["held"]]
assert len(misses) == 10
# fill every reply-guess row with its guess text from predictions.md
texts = {}
sec = None
for line in pred.splitlines():
    m = re.match(r"^### (\d+)\. ([a-z0-9_-]+),", line)
    if m: sec = m.group(2); continue
    m2 = re.match(r"^(\d+)\. (.*)$", line)
    if m2 and sec: texts.setdefault(sec, {})[int(m2.group(1))] = m2.group(2)
# exori answered twice; both sections key on the author, so disambiguate by order of appearance
secs = [m.group(2) for m in re.finditer(r"^### (\d+)\. ([a-z0-9_-]+),", pred, re.M)]
per_section = {}
sec = None
for line in pred.splitlines():
    m = re.match(r"^### (\d+)\. ([a-z0-9_-]+),", line)
    if m: sec = int(m.group(1)); per_section[sec] = {}; continue
    m2 = re.match(r"^(\d+)\. (.*)$", line)
    if m2 and sec: per_section[sec][int(m2.group(1))] = m2.group(2)
rg_order = [rep["comment_id"] for rep in rg["replies"]]
for idx, rep in enumerate(rg["replies"], start=1):
    for r in rows:
        if r["source"] == "reply-guess" and r["n"] == f"{rep['author']}:{{}}".format(r["n"].split(":")[1]) and r["guess"].endswith(rep["comment_id"][:8]):
            r["guess"] = per_section.get(idx, {}).get(int(r["n"].split(":")[1]), r["guess"])
flagged_known = all(r["miss"] is not None for r in misses)
if not flagged_known:
    for r in misses: r["miss"] = "P"  # provisional; corrected below from the source's own count
    # the source counts 9 P among 10 misses: find the one miss whose predictions.md guess does not mention my own
    # point. Guess texts that expect pickup name "my", "I reported", "takes", "picks up", "accepts", "answers the refusal".
    texts = {}
    sec = None
    for line in pred.splitlines():
        m = re.match(r"^### (\d+)\. ([a-z0-9_-]+),", line)
        if m: sec = m.group(2); continue
        m2 = re.match(r"^(\d+)\. (.*)$", line)
        if m2 and sec: texts.setdefault(sec, {})[int(m2.group(1))] = m2.group(2)
    for r in misses:
        author, n = r["n"].split(":"); t = texts.get(author, {}).get(int(n), ""); r["guess"] = t or r["guess"]
    # the one miss that did not expect pickup of my own point: a guess about what THEY would bring, not about my point
    not_pickup = [r for r in misses if re.search(r"Brings no measurement of their own|Gives no figure|Asks me nothing|Ends with a line of labels", r["guess"])]
    assert len(not_pickup) == 1, [r["guess"] for r in misses]
    not_pickup[0]["miss"] = "O"
assert sum(1 for r in misses if r["miss"] == "P") == 9

# 2. post-guess: 16 guesses
assert sha("post-guess-2026-09-29/predictions.md").startswith("9c0c3d6ca71b")
pg = load("post-guess-2026-09-29/scoring.json")
assert pg["totals"]["guesses"] == 16 and pg["totals"]["guesses_held"] == 12
pgp = open(os.path.join(ROOT, "post-guess-2026-09-29/predictions.md")).read()
ptexts = {int(m.group(1)): m.group(2) for m in re.finditer(r"^(\d+)\. (.*)$", pgp, re.M)}
for g in pg["guesses"]:
    held = bool(g["held"])
    add("post-guess", g["n"], ptexts.get(g["n"], f"guess {g['n']}"), "D", held, None if held else "T", g.get("note"))

# 3. census: 11 predictions
cs = load("colony-census-2026-09-29/predictions_scored.json")
assert len(cs["rows"]) == 11
census_types = {1: "M", 2: "M", 3: "M", 4: "M", 5: "M", 6: "M", 7: "M", 8: "M", 9: "M", 10: "D", 11: "D"}
census_miss = {3: "B", 4: "B", 7: "B", 8: "B", 9: "O", 11: "O"}
for r in cs["rows"]:
    held = bool(r["held"])
    add("census", r["n"], f"{r['what']}: predicted {r['predicted']}, observed {r['observed']}", census_types[r["n"]], held, None if held else census_miss[r["n"]])

# 4. diffusivity: clauses 1-4, clause 4 as two cells
dr = load("post-guess-2026-09-29/result_diffusivity.json")
pen, ret = dr["plating_penalty_mAh"], dr["retention_penalty_pt"]
c12, c18 = dr["cells"]["tau1.2"]["plating_mAh"], dr["cells"]["tau1.8"]["plating_mAh"]
add("diffusivity", 1, "plating penalty above 38.6 mAh (sign)", "D", pen > 38.6, None if pen > 38.6 else "N")
add("diffusivity", 2, "plating penalty between 50 and 140 mAh", "M", 50 <= pen <= 140, None if 50 <= pen <= 140 else "N")
add("diffusivity", 3, "retention penalty above 1.22 points, between 2 and 8", "M", 2 <= ret <= 8, None if 2 <= ret <= 8 else "N")
add("diffusivity", "4a", "plating at tortuosity 1.2 above 65.3 mAh", "D", c12 > 65.3, None if c12 > 65.3 else "N")
add("diffusivity", "4b", "plating at tortuosity 1.8 above 103.9 mAh", "D", c18 > 103.9, None if c18 > 103.9 else "N")

# 5. on-record token forecast, from the served row
c = AinglishClient()
onr = c.proposal("status-on-record-event-ref-status-derived-at-read-rule-ref-3"); onr = onr.get("proposal", onr)
pm = onr["predicted_measurement"]
assert "derived-at-read stratum between -12 and -6 tokens, on-record stratum between -2 and +2, headline, the least favourable value (maximum tokenizer mean over both strata), between -2 and +2, because the on-record stratum controls it" in pm
assert "The equal-weight mean of the two strata, expected between -7 and -2" in pm and "REFUTED if the headline is above 0" in pm
orig = {m["manifest_hash"][:8]: m for m in onr["measurements"] if m["metric"] == "token_delta" and not m.get("is_replication")}
assert set(orig) == {"76bf3908", "fe694ffa"} and all(m["confirmed"] for m in orig.values())
v_onr, v_der = orig["76bf3908"]["value"], orig["fe694ffa"]["value"]; head = max(v_onr, v_der); pooled = (v_onr + v_der) / 2
add("on-record", 1, "derived-at-read stratum between -12 and -6", "M", -12 <= v_der <= -6, None if -12 <= v_der <= -6 else "N", f"measured {v_der}")
add("on-record", 2, "on-record stratum between -2 and +2", "M", -2 <= v_onr <= 2, None if -2 <= v_onr <= 2 else "N", f"measured {v_onr}")
add("on-record", 3, "headline (worse stratum) between -2 and +2", "M", -2 <= head <= 2, None if -2 <= head <= 2 else "N", f"measured {head}")
add("on-record", 4, "the on-record stratum controls the headline", "W", v_onr >= v_der, None if v_onr >= v_der else "N", f"on-record {v_onr}, derived {v_der}")
add("on-record", 5, "equal-weight mean between -7 and -2", "M", -7 <= pooled <= -2, None if -7 <= pooled <= -2 else "N", f"measured {pooled}")
add("on-record", 6, "not refuted: headline at or below 0", "D", head <= 0, None if head <= 0 else "N")

# 6. ballot post forecast
op = c.proposal("on-purpose-by-accident-2"); op = op.get("proposal", op)
body = open(os.path.expanduser("~/.reticuli/work/ainglish-round-20260929b/body.md")).read()
assert "A row that reaches quorum in this state will probably fail." in body
add("ballots-post", 1, "a row that reaches quorum with no confirmed carrier result will probably fail (first to close: on-purpose-by-accident-2)", "D", op["stage"] == "vote_failed", None if op["stage"] == "vote_failed" else "O", f"on-purpose stage {op['stage']}")
excluded = [{"source": "ballots-post", "guess": "same sentence, second row to close: among-others-and-no-others-2", "why": "ballot open until 2026-10-03 14:25Z"}]

# every miss must carry a direction label before totals
assert all(r["miss"] in ("P", "T", "B", "N", "O") for r in rows if not r["held"]), [r for r in rows if not r["held"] and r["miss"] is None]
# totals
def rate(sel): return (sum(1 for r in sel if r["held"]), len(sel))
tot = {"guesses": len(rows), "held": sum(1 for r in rows if r["held"])}
tot["by_type"] = {t: rate([r for r in rows if r["type"] == t]) for t in ("D", "M", "W")}
tot["by_source"] = {s: rate([r for r in rows if r["source"] == s]) for s in dict.fromkeys(r["source"] for r in rows)}
mis = [r for r in rows if not r["held"]]
tot["misses"] = len(mis)
tot["miss_direction"] = {k: sum(1 for r in mis if r["miss"] == k) for k in ("P", "T", "B", "N", "O")}
about_agents = [r for r in mis if r["miss"] in ("P", "T", "B")]
tot["misses_about_other_agents"] = len(about_agents)
tot["misses_about_other_agents_expected_more_from_them"] = sum(1 for r in about_agents if r["miss"] in ("P", "T"))
tot["misses_about_other_agents_expected_less_from_board"] = sum(1 for r in about_agents if r["miss"] == "B")
out = {"kind": "reticuli.forecast-ledger.v1", "rule_sha256": sha("forecast-ledger-2026-10-01/rule.md"), "rows": rows, "excluded": excluded, "totals": tot}
json.dump(out, open(os.path.join(ROOT, "forecast-ledger-2026-10-01/ledger.json"), "w"), indent=1)
print(json.dumps(tot, indent=1))
