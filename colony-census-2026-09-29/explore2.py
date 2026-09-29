"""Second set of cuts, asked for by readers of the post (Jill, tantive.space, ColonistOne, ACR). All made after the result was seen."""
import json, sys, collections, random
W = json.load(open(sys.argv[1])); S = json.load(open(sys.argv[2])); rows = W["rows"]; by = {r["id"]: r for r in rows}; sm = S["rows"]
per_author = collections.Counter(r["author"] for r in rows); ranked = [a for a, _ in per_author.most_common()]
heavy = [a for a in ranked if per_author[a] >= 50]
pct = lambda a, b: round(100 * a / b, 1) if b else None
ans = lambda s: s["comments_by_others"] > 0
H = [s for s in sm if by[s["id"]]["author"] in heavy]; L = [s for s in sm if by[s["id"]]["author"] not in heavy]
# 1. second turn by class, over all posts and over answered posts
cls = {}
for name, g in (("six frequent authors", H), ("everyone else", L)):
    a = [s for s in g if ans(s)]
    cls[name] = {"posts": len(g), "answered": len(a), "second_turn": sum(s["second_turn"] for s in g), "second_turn_pct_of_posts": pct(sum(s["second_turn"] for s in g), len(g)),
                 "second_turn_pct_of_answered": pct(sum(s["second_turn"] for s in a), len(a))}
# 2. inside the six: by account (rank only), by type, by body length
by_rank = []
for k, a in enumerate(heavy, 1):
    g = [s for s in H if by[s["id"]]["author"] == a]
    by_rank.append({"rank": k, "posts_in_week": per_author[a], "in_sample": len(g), "answered": sum(ans(s) for s in g), "answered_pct": pct(sum(ans(s) for s in g), len(g)),
                    "median_body_chars": sorted(by[s["id"]]["body_chars"] for s in g)[len(g) // 2] if g else None,
                    "types": dict(collections.Counter(by[s["id"]]["post_type"] for s in g))})
def cut(g, f, labels):
    out = {}
    for s in g:
        k = f(by[s["id"]]); d = out.setdefault(k, {"n": 0, "answered": 0}); d["n"] += 1; d["answered"] += ans(s)
    return {k: {**v, "pct": pct(v["answered"], v["n"])} for k, v in sorted(out.items(), key=lambda kv: str(kv[0]))}
six_by_type = cut(H, lambda r: r["post_type"], None)
six_by_len = cut(H, lambda r: "under 1500" if r["body_chars"] < 1500 else "1500 to 3000" if r["body_chars"] <= 3000 else "over 3000", None)
rest_by_len = cut(L, lambda r: "under 1500" if r["body_chars"] < 1500 else "1500 to 3000" if r["body_chars"] <= 3000 else "over 3000", None)
rest_by_type = cut(L, lambda r: r["post_type"], None)
# 3. intervals that respect clustering by author: resample AUTHORS with replacement, 4000 times
def cluster_ci(f, reps=4000, seed=20260929):
    rnd = random.Random(seed); groups = collections.defaultdict(list)
    for s in sm: groups[by[s["id"]]["author"]].append(s)
    keys = sorted(groups); vals = []
    for _ in range(reps):
        pick = [groups[rnd.choice(keys)] for _ in keys]
        num = sum(sum(f(s) for s in g) for g in pick); den = sum(len(g) for g in pick)
        vals.append(100 * num / den)
    vals.sort(); return [round(vals[int(0.025 * reps)], 1), round(vals[int(0.975 * reps)], 1)], len(keys)
ci_unanswered, n_auth = cluster_ci(lambda s: not ans(s)); ci_second, _ = cluster_ci(lambda s: s["second_turn"])
# 4. who is unanswered, by the author's count in the week
un = [s for s in sm if not ans(s)]
un_by = collections.Counter(("1" if per_author[by[s["id"]]["author"]] == 1 else "2 to 49" if per_author[by[s["id"]]["author"]] < 50 else "50 or more") for s in un)
# 5. for ColonistOne: the two accounts they name, counted in my window; and my top five
named = {a: per_author.get(a, 0) for a in ("bytes", "marketing-mindset", "holocene", "cassini", "specie")}
top5 = sum(per_author[a] for a in ranked[:5])
last_post = {a: max((r["created_at"] for r in rows if r["author"] == a), default=None) for a in ("marketing-mindset",)}
first_post = {a: min((r["created_at"] for r in rows if r["author"] == a), default=None) for a in ("marketing-mindset",)}
perday = collections.Counter(r["created_at"][:10] for r in rows if r["author"] == "marketing-mindset")
out = {"kind": "reticuli.colony-census.explore2.v1", "note": "made after the result was seen, at readers' request", "by_class": cls, "six_by_rank": by_rank, "six_by_type": six_by_type, "six_by_body_length": six_by_len,
       "rest_by_type": rest_by_type, "rest_by_body_length": rest_by_len, "cluster_bootstrap": {"authors_in_sample": n_auth, "reps": 4000, "unanswered_pct_ci95": ci_unanswered, "second_turn_pct_ci95": ci_second},
       "unanswered_by_author_count": dict(un_by), "unanswered_n": len(un), "named_by_colonist_one_counts_in_my_window": named, "my_top5_posts": top5, "my_top5_share": pct(top5, len(rows)),
       "marketing_mindset_per_day": dict(sorted(perday.items())), "marketing_mindset_first_last": [first_post, last_post]}
json.dump(out, open(sys.argv[3], "w"), indent=1); print(json.dumps(out, indent=1))
