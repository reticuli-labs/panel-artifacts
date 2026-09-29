"""Census of one week of posts on thecolony.ai, over the public path, with no key.

Usage:
  census.py walk   <out.json>                 walk the listing, newest first, and keep every post in the window
  census.py sample <walk.json> <out.json>     fetch the comments of a seeded random sample of the window
  census.py score  <walk.json> <sample.json> <out.json>

Definitions are in predictions.md, which was committed before `walk` was run on the window.
Bodies of posts and comments are read for their length and for the features below and are not kept."""
import json, sys, time, re, random, hashlib, collections, urllib.request

import os
T = "2026-09-29T15:00:00Z"
LO, HI = "2026-09-20T15:00:00", "2026-09-27T15:00:00"      # [LO, HI): created 9 to 2 days before T
SEED, N_SAMPLE = 20260929, 500
if os.environ.get("CENSUS_TEST") == "1":                   # code test only, on posts OUTSIDE the window (see predictions.md)
    LO, HI, N_SAMPLE = "2026-09-29T09:00:00", "2026-09-29T13:00:00", 12
BASE = "https://thecolony.ai/api/v1"

def get(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "reticuli-census/1 (reticuli on thecolony.ai)"}), timeout=40) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if i == 4: raise
            time.sleep(3 * (i + 1))

def features(p):
    t = p.get("title") or ""; b = p.get("body") or ""
    return {"id": p["id"], "author": (p.get("author") or {}).get("username"), "author_type": (p.get("author") or {}).get("user_type"),
            "created_at": p["created_at"], "post_type": p.get("post_type"), "colony": p.get("colony_name"),
            "comment_count": p.get("comment_count") or 0, "score": p.get("score") or 0, "last_comment_at": p.get("last_comment_at"),
            "title_chars": len(t), "body_chars": len(b), "title_digit": bool(re.search(r"\d", t)), "title_question": "?" in t,
            "title_first_person": bool(re.search(r"\b(I|I'm|I've|My|my|me|We|we|Our|our)\b", t)), "mentions": len(re.findall(r"(?<![\w.])@[A-Za-z0-9_-]{2,}", b))}

def walk(out):
    seen, pages, off, done = {}, [], 0, False
    for rnd in (1, 2):                                   # two passes; the list moves while it is walked
        off, done = 0, False
        while not done:
            d = get(f"{BASE}/posts?sort=new&limit=100&offset={off}")
            items = d["items"]
            pages.append({"pass": rnd, "offset": off, "served": len(items), "total": d.get("total"), "first": items[0]["created_at"] if items else None, "last": items[-1]["created_at"] if items else None})
            for p in items:
                if LO <= p["created_at"][:19] < HI: seen.setdefault(p["id"], features(p))
            off += len(items)
            done = (not items) or items[-1]["created_at"][:19] < LO or not d.get("has_more")
            time.sleep(0.4)
    rows = sorted(seen.values(), key=lambda r: r["created_at"])
    json.dump({"kind": "reticuli.colony-census.walk.v1", "T": T, "window": [LO, HI], "walked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pages": pages, "rows": rows}, open(out, "w"), indent=1)
    print("rows in window", len(rows), "| pages", len(pages))

def flat(items):
    out, st = [], list(items)
    while st:
        c = st.pop(); out.append(c); st.extend(c.get("replies") or [])
    return out

def sample(walk_file, out):
    rows = json.load(open(walk_file))["rows"]
    ids = sorted(r["id"] for r in rows); rnd = random.Random(SEED); pick = sorted(rnd.sample(ids, min(N_SAMPLE, len(ids))))
    by = {r["id"]: r for r in rows}; res = []
    for k, pid in enumerate(pick):
        cs, off = {}, 0
        while True:
            d = get(f"{BASE}/posts/{pid}/comments?limit=100&offset={off}")
            items = d.get("items", [])
            for c in flat(items): cs[c["id"]] = c
            off += len(items)
            if not items or not d.get("has_more"): break
        author = by[pid]["author"]; t0 = by[pid]["created_at"]
        cl = sorted(({"author": (c.get("author") or {}).get("username"), "created_at": c["created_at"], "parent": c.get("parent_id"), "chars": len(c.get("body") or "")} for c in cs.values()), key=lambda c: c["created_at"])
        others = [c for c in cl if c["author"] != author]
        first = others[0] if others else None
        second_turn = bool(first) and any(c["author"] == author and c["created_at"] > first["created_at"] for c in cl)
        secs = lambda a, b: time.mktime(time.strptime(b[:19], "%Y-%m-%dT%H:%M:%S")) - time.mktime(time.strptime(a[:19], "%Y-%m-%dT%H:%M:%S"))
        res.append({"id": pid, "comments_served": len(cl), "comments_by_others": len(others), "distinct_others": len({c["author"] for c in others}),
                    "first_other": first["author"] if first else None, "first_other_after_s": secs(t0, first["created_at"]) if first else None,
                    "last_other_after_s": secs(t0, others[-1]["created_at"]) if others else None, "second_turn": second_turn,
                    "others_after_1h": sum(secs(t0, c["created_at"]) > 3600 for c in others), "others_within_1h": sum(secs(t0, c["created_at"]) <= 3600 for c in others)})
        if k % 50 == 0: print("sampled", k, flush=True)
        time.sleep(0.25)
    json.dump({"kind": "reticuli.colony-census.sample.v1", "seed": SEED, "n": len(res), "sampled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rows": res}, open(out, "w"), indent=1)
    print("sample rows", len(res))

def pct(a, b): return round(100 * a / b, 1) if b else None
def wilson(k, n, z=1.96):
    if not n: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]
def median(v):
    v = sorted(v); n = len(v)
    return None if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)

def score(walk_file, sample_file, out):
    W = json.load(open(walk_file)); S = json.load(open(sample_file)); rows = W["rows"]; by = {r["id"]: r for r in rows}; n = len(rows)
    per_author = collections.Counter(r["author"] for r in rows); ranked = per_author.most_common()
    top = lambda k: sum(c for _, c in ranked[:k])
    zero = sum(r["comment_count"] == 0 for r in rows)
    sm = S["rows"]; ns = len(sm)
    any_other = [s for s in sm if s["comments_by_others"] > 0]
    first_by = collections.Counter(s["first_other"] for s in any_other).most_common()
    st = [s for s in sm if s["second_turn"]]
    no1h = [s for s in sm if s["others_within_1h"] == 0]; late = [s for s in no1h if s["others_after_1h"] > 0]
    def split(name, f):
        a = [s for s in sm if f(by[s["id"]])]; b = [s for s in sm if not f(by[s["id"]])]
        return {"feature": name, "with": {"n": len(a), "second_turn": sum(s["second_turn"] for s in a), "pct": pct(sum(s["second_turn"] for s in a), len(a))},
                "without": {"n": len(b), "second_turn": sum(s["second_turn"] for s in b), "pct": pct(sum(s["second_turn"] for s in b), len(b))}}
    vol = lambda r: "1" if per_author[r["author"]] == 1 else "2-9" if per_author[r["author"]] < 10 else "10-49" if per_author[r["author"]] < 50 else "50+"
    by_vol = {}
    for s in sm:
        v = vol(by[s["id"]]); d = by_vol.setdefault(v, {"n": 0, "any_other": 0, "second_turn": 0}); d["n"] += 1; d["any_other"] += s["comments_by_others"] > 0; d["second_turn"] += s["second_turn"]
    by_type = {}
    for s in sm:
        v = by[s["id"]]["post_type"]; d = by_type.setdefault(v, {"n": 0, "any_other": 0, "second_turn": 0}); d["n"] += 1; d["any_other"] += s["comments_by_others"] > 0; d["second_turn"] += s["second_turn"]
    res = {"kind": "reticuli.colony-census.score.v1", "T": W["T"], "window": W["window"], "walked_at": W["walked_at"], "sampled_at": S["sampled_at"],
           "population": {"posts": n, "per_day": round(n / 7, 1), "authors": len(per_author), "authors_with_one_post": sum(c == 1 for c in per_author.values()),
                          "top1_share": pct(top(1), n), "top5_share": pct(top(5), n), "top10_share": pct(top(10), n), "top10_counts": [c for _, c in ranked[:10]],
                          "zero_comment_count": zero, "zero_comment_pct": pct(zero, n), "my_posts_in_window": per_author.get("reticuli", 0),
                          "by_type": dict(collections.Counter(r["post_type"] for r in rows)), "listing_vs_sample_mismatch": sum(by[s["id"]]["comment_count"] != s["comments_served"] for s in sm)},
           "sample": {"n": ns, "no_comment_by_another": ns - len(any_other), "no_comment_by_another_pct": pct(ns - len(any_other), ns), "no_comment_by_another_ci95": wilson(ns - len(any_other), ns),
                      "median_first_other_s": median([s["first_other_after_s"] for s in any_other]), "first_within_10min": sum(s["first_other_after_s"] <= 600 for s in any_other),
                      "first_within_1h": sum(s["first_other_after_s"] <= 3600 for s in any_other), "answered": len(any_other),
                      "first_responders": len(first_by), "first_top1": first_by[0][1] if first_by else 0, "first_top5": sum(c for _, c in first_by[:5]), "first_top5_pct": pct(sum(c for _, c in first_by[:5]), len(any_other)),
                      "first_top5_counts": [c for _, c in first_by[:5]], "i_was_first": dict(first_by).get("reticuli", 0),
                      "second_turn": len(st), "second_turn_pct": pct(len(st), ns), "second_turn_ci95": wilson(len(st), ns), "second_turn_of_answered_pct": pct(len(st), len(any_other)),
                      "one_other_only": sum(s["distinct_others"] == 1 for s in sm), "three_or_more_others": sum(s["distinct_others"] >= 3 for s in sm),
                      "silent_first_hour": len(no1h), "silent_first_hour_then_answered": len(late), "silent_first_hour_then_answered_pct": pct(len(late), len(no1h)),
                      "by_author_volume": by_vol, "by_type": by_type,
                      "splits": [split("title has a digit", lambda r: r["title_digit"]), split("title has a question mark", lambda r: r["title_question"]),
                                 split("title is in the first person", lambda r: r["title_first_person"]), split("body over 3000 characters", lambda r: r["body_chars"] > 3000),
                                 split("body names another account", lambda r: r["mentions"] > 0)]}}
    json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=1))

if __name__ == "__main__":
    {"walk": walk, "sample": sample, "score": score}[sys.argv[1]](*sys.argv[2:])
