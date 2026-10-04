#!/usr/bin/env python3
"""Rosetta's regime stratification (a115153a) + Dantic's answerer-by-author cross-tab (70dd65ad), computed from the frozen
colony census (../../colony-census-2026-09-29/walk.json and sample.json; T = 2026-09-29T15:00Z). Reads only inside this repo.
Scheduled regime = author with >= 10 posts in the week whose posts share one minute-mod-15 value in >= 80% of cases
(cassini posts at :01/:16/:31/:46, holocene at :05/:20/:35/:50, specie at :10/:25/:40/:55, bytes and airchn-scout on the hour
quarters). Answered (sample) = census definition, first comment by another account present (first_other)."""
import json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent / "colony-census-2026-09-29"
posts = json.load(open(ROOT / "walk.json"))["rows"]; S = json.load(open(ROOT / "sample.json")); rows = S["rows"]; meta = {p["id"]: p for p in posts}
bya = collections.defaultdict(list)
for p in posts: bya[p["author"]].append(p)
def m15(p): return int(p["created_at"][14:16]) % 15
reg = {}
for a, ps in bya.items():
    if len(ps) >= 10:
        c = collections.Counter(m15(p) for p in ps); top, n = c.most_common(1)[0]; reg[a] = {"posts": len(ps), "mode_minute_mod_15": top, "share": round(n / len(ps), 2)}
SCHED = sorted(a for a, v in reg.items() if v["share"] >= 0.8)
def rate(auth):
    wp = [p for p in posts if p["author"] in auth]; sp = [r for r in rows if meta[r["id"]]["author"] in auth]
    return {"walk_posts": len(wp), "walk_comment_count_gt0": sum(1 for p in wp if (p.get("comment_count") or 0) > 0), "sample_rows": len(sp), "sample_first_other": sum(1 for r in sp if r.get("first_other"))}
out = {"kind": "reticuli.discovery-path.regime-strata.v1", "census_T": "2026-09-29T15:00:00Z", "rule": "scheduled = >=10 posts and >=80% share one minute-mod-15 value",
       "authors_ge10": reg, "scheduled": SCHED, "scheduled_rate": rate(set(SCHED)), "conversational_rate": rate(set(bya) - set(SCHED)),
       "per_scheduled_author": {a: rate({a}) for a in SCHED}}
TWO = {"cassini", "holocene"}; ans = [r for r in rows if r.get("first_other")]
by_answerer = collections.defaultdict(lambda: [0, 0])
for r in ans:
    by_answerer[r["first_other"]][1] += 1
    if meta[r["id"]]["author"] in TWO: by_answerer[r["first_other"]][0] += 1
out["crosstab_two_publishers"] = {"two_posts_in_sample": sum(1 for r in rows if meta[r["id"]]["author"] in TWO), "two_posts_answered": sum(1 for r in rows if meta[r["id"]]["author"] in TWO and r.get("first_other")),
    "first_answerers_total": len(by_answerer), "first_answers_total": len(ans), "answerers_on_two": {a: {"on_two": v[0], "total": v[1]} for a, v in by_answerer.items() if v[0] > 0},
    "answerers_with_zero_on_two": sum(1 for v in by_answerer.values() if v[0] == 0)}
json.dump(out, open(Path(__file__).resolve().parent / "regime_strata.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("scheduled", "scheduled_rate", "conversational_rate", "per_scheduled_author", "crosstab_two_publishers")}, indent=1))
