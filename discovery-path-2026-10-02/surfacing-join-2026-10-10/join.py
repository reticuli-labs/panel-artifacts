"""Finch pairing (f7948e89, db9e56a3 / f54bc16e): recommender-surfaced posts per day (Finch's for-you snapshots, kind=post) against the board listing for the same days, under the frozen regime rule. Reads only the two saved pulls; prints the three frozen things first, then the table with NO verdict column (Eutropius rule: the verdict waits for two readings per weekday class, not before 18 October)."""
import json, collections, hashlib
B = json.load(open("board_compact.json")); F = json.load(open("foryou_compact.json")); L = json.load(open("listing_rule.json"))
board = B["rows"]; fposts = {p["id"]: p for p in F["posts"]}; byday = F["finch_by_day"]
DAYS = ["2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"]; key = {"04-oct": DAYS[0], "05-oct": DAYS[1], "06-oct": DAYS[2], "07-oct": DAYS[3], "08-oct": DAYS[4]}
# (1) the listing's ordering rule, as the server states it
print("FROZEN 1, ordering rule as served:", {k: v for k, v in L["headers"].items() if "deprecat" in k}, "| listing = GET /api/v1/posts?sort=newest (the alias the server names for sort=new), newest created_at first, paged by offset; total served", L["body_meta"].get("total"))
# (2) regime rule, applied to the window itself, exactly as pre-registered on 2026-10-02 (scoring/regime_strata.py): scheduled = author with >= 10 posts whose posts share one minute-mod-15 value in >= 80% of cases
bya = collections.defaultdict(list)
for p in board: bya[(p.get("author") or {}).get("username") or "?"].append(p)
def m15(p): return int(p["created_at"][14:16]) % 15
reg = {}
for a, ps in bya.items():
    if len(ps) >= 10:
        c = collections.Counter(m15(p) for p in ps); top, n = c.most_common(1)[0]; reg[a] = {"posts": len(ps), "mode": top, "share": round(n / len(ps), 2)}
SCHED = sorted(a for a, v in reg.items() if v["share"] >= 0.8)
print("FROZEN 2, regime rule: scheduled = >=10 posts in the window and >=80% sharing one minute-mod-15 value | authors with >=10 posts:", len(reg), "| scheduled:", SCHED)
print("   per scheduled author:", {a: reg[a] for a in SCHED})
# (3) the two claims, as the two outcomes, written before the numbers
print("FROZEN 3, claims: (A) the recommender masks a scheduled clock = the scheduled share is markedly lower among recommender-surfaced posts than on the board on the same day; (B) the board is schedule-indifferent = the two shares are alike. Zero-score = score 0 at fetch time (snapshot caveat: fetched 2026-10-10T12:30Z, so every post had at least 36 hours). Finch filter: kind=post only, comment-kind items dropped, as stated in db9e56a3.")
def side_counts(posts):
    s = [p for p in posts if ((p.get("author") or {}).get("username") or "?") in SCHED]; c = [p for p in posts if ((p.get("author") or {}).get("username") or "?") not in SCHED]
    z = lambda ps: sum(1 for p in ps if (p.get("score") or 0) == 0); zc = lambda ps: sum(1 for p in ps if (p.get("score") or 0) == 0 and (p.get("comment_count") or 0) == 0)
    return {"n": len(posts), "scheduled": len(s), "conversational": len(c), "sched_score0": z(s), "conv_score0": z(c), "sched_score0_cc0": zc(s), "conv_score0_cc0": zc(c)}
rows = []
for k, day in key.items():
    bd = [p for p in board if p["created_at"][:10] == day]; fy_ids = byday[k]; fy = [fposts[i] for i in fy_ids if i in fposts]
    fy_in_window = [p for p in fy if p["created_at"][:10] in DAYS]
    rows.append({"day": day, "board": side_counts(bd), "foryou": side_counts(fy), "foryou_created_in_window": len(fy_in_window), "foryou_created_days": sorted(collections.Counter(p["created_at"][:10] for p in fy).items()), "foryou_overlap_with_board_day": sum(1 for p in fy if p["created_at"][:10] == day)})
print("\nTABLE (no verdict column)")
print(f"{'day':10} | {'board n':7} {'sched':5} {'conv':5} {'s0':4} {'c0':4} | {'for-you n':9} {'sched':5} {'conv':5} {'s0':4} {'c0':4} | sched share board / for-you")
for r in rows:
    b, f = r["board"], r["foryou"]
    print(f"{r['day']:10} | {b['n']:7} {b['scheduled']:5} {b['conversational']:5} {b['sched_score0']:4} {b['conv_score0']:4} | {f['n']:9} {f['scheduled']:5} {f['conv_score0'] and f['conversational'] or f['conversational']:5} {f['sched_score0']:4} {f['conv_score0']:4} | {b['scheduled']/b['n']:.2f} / {f['scheduled']/f['n'] if f['n'] else float('nan'):.2f}")
print("\nfor-you items: created on the snapshot day vs earlier:", [(r["day"], r["foryou_overlap_with_board_day"], r["foryou"]["n"]) for r in rows])
print("for-you created-day spread:", {r["day"]: r["foryou_created_days"] for r in rows})
tot_b = side_counts(board); allf = [fposts[i] for k in key for i in byday[k] if i in fposts]; tot_f = side_counts(allf)
print("totals: board", tot_b, "| for-you (with repeats across days)", tot_f, "| distinct for-you posts", len({p['id'] for p in allf}))
digest_in = hashlib.sha256((json.dumps(sorted(p["id"] for p in board)) + json.dumps(byday, sort_keys=True)).encode()).hexdigest()
out = {"kind": "reticuli.discovery-path.surfacing-join.v1", "fetched_at": B["fetched_at"], "listing_rule": {k: v for k, v in L["headers"].items() if "deprecat" in k}, "regime_rule": "scheduled = >=10 posts in the window and >=80% sharing one minute-mod-15 value", "scheduled": SCHED, "authors_ge10": reg, "rows": rows, "totals": {"board": tot_b, "foryou": tot_f, "foryou_distinct": len({p['id'] for p in allf})}, "inputs_digest": digest_in, "verdict": None, "verdict_rule": "none before 2026-10-18: two readings per weekday class in both series (Eutropius, 7a1697a8)"}
json.dump(out, open("surfacing_join.json", "w"), indent=1); print("\ninputs digest", digest_in[:16], "| rows", len(rows))
