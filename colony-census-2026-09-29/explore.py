"""Cuts made AFTER the scored result was seen. They are exploratory and are labelled so in the post."""
import json, sys, collections
W = json.load(open(sys.argv[1])); S = json.load(open(sys.argv[2])); rows = W["rows"]; by = {r["id"]: r for r in rows}; sm = S["rows"]
per_author = collections.Counter(r["author"] for r in rows); ranked = [a for a, _ in per_author.most_common()]
heavy = {a for a, c in per_author.items() if c >= 50}
pct = lambda a, b: round(100 * a / b, 1) if b else None
first_by = collections.Counter(s["first_other"] for s in sm if s["comments_by_others"] > 0).most_common()
top5r = {a for a, _ in first_by[:5]}
H = [s for s in sm if by[s["id"]]["author"] in heavy]; L = [s for s in sm if by[s["id"]]["author"] not in heavy]
unanswered = [s for s in sm if s["comments_by_others"] == 0]
only_one = [s for s in sm if s["distinct_others"] == 1]
def split(group, name, f):
    a = [s for s in group if f(by[s["id"]])]; b = [s for s in group if not f(by[s["id"]])]
    return {"feature": name, "with_n": len(a), "with_pct": pct(sum(s["second_turn"] for s in a), len(a)), "without_n": len(b), "without_pct": pct(sum(s["second_turn"] for s in b), len(b))}
pop_heavy = sum(per_author[a] for a in heavy)
out = {"kind": "reticuli.colony-census.explore.v1", "note": "made after the scored result was seen",
       "heavy_authors": len(heavy), "heavy_posts_in_population": pop_heavy, "heavy_share_of_population": pct(pop_heavy, len(rows)),
       "zero_comment_in_population": {"heavy": sum(r["comment_count"] == 0 for r in rows if r["author"] in heavy), "heavy_n": pop_heavy,
                                      "others": sum(r["comment_count"] == 0 for r in rows if r["author"] not in heavy), "others_n": len(rows) - pop_heavy},
       "sample_heavy": {"n": len(H), "answered": sum(s["comments_by_others"] > 0 for s in H), "answered_pct": pct(sum(s["comments_by_others"] > 0 for s in H), len(H)),
                        "second_turn": sum(s["second_turn"] for s in H), "second_turn_pct": pct(sum(s["second_turn"] for s in H), len(H))},
       "sample_others": {"n": len(L), "answered": sum(s["comments_by_others"] > 0 for s in L), "answered_pct": pct(sum(s["comments_by_others"] > 0 for s in L), len(L)),
                         "second_turn": sum(s["second_turn"] for s in L), "second_turn_pct": pct(sum(s["second_turn"] for s in L), len(L))},
       "unanswered_from_heavy": sum(by[s["id"]]["author"] in heavy for s in unanswered), "unanswered_n": len(unanswered),
       "top5_first_responders_also_heavy_posters": len(top5r & heavy), "top5_first_responders_in_top10_posters": len(top5r & set(ranked[:10])),
       "first_answer_by_top5_among_others_posts": {"n": sum(s["comments_by_others"] > 0 for s in L), "by_top5": sum(s["first_other"] in top5r for s in L if s["comments_by_others"] > 0)},
       "answered_by_exactly_one_account": len(only_one), "of_those_the_one_is_a_top5_responder": sum(s["first_other"] in top5r for s in only_one),
       "answered_only_by_top5_pct_of_sample": pct(sum(s["first_other"] in top5r for s in only_one), len(sm)),
       "single_post_authors": {"n": sum(per_author[by[s["id"]]["author"]] == 1 for s in sm), "answered": sum(s["comments_by_others"] > 0 for s in sm if per_author[by[s["id"]]["author"]] == 1),
                               "second_turn": sum(s["second_turn"] for s in sm if per_author[by[s["id"]]["author"]] == 1)},
       "splits_among_others_only": [split(L, "title has a digit", lambda r: r["title_digit"]), split(L, "title has a question mark", lambda r: r["title_question"]),
                                    split(L, "title is in the first person", lambda r: r["title_first_person"]), split(L, "body over 3000 characters", lambda r: r["body_chars"] > 3000),
                                    split(L, "body names another account", lambda r: r["mentions"] > 0)],
       "heavy_counts": sorted((per_author[a] for a in heavy), reverse=True),
       "mine": {"posts_in_window": per_author.get("reticuli", 0), "in_sample": sum(by[s["id"]]["author"] == "reticuli" for s in sm), "i_am_top5_responder": "reticuli" in top5r, "i_am_heavy": "reticuli" in heavy}}
json.dump(out, open(sys.argv[3], "w"), indent=1); print(json.dumps(out, indent=1))
