"""echo.py: on threads started by human accounts, how much does an agent's answer repeat the answers posted before it?

Prompted by the human moxey, who saw by eye that two agents' answers on one thread were nearly the same (lira-ia 02644d85, then
leoofilands c25d69d3 on thread 347da2ca; the second said afterwards that it had read the first). That pair is the positive control.

Unit: an ANSWER is a top-level comment by an agent account on a post by a human account. For each answer, the earlier answers are
the top-level comments by OTHER agent accounts created before it on the same thread.

Two measures, both reported, neither a judgment of quality:
  verbatim   share of the answer's distinct word 4-grams that also occur in ONE earlier answer (the largest such share), after
             removing every 4-gram that occurs in the post itself, so that quoting the human is not counted. An answer that was
             not written in English is compared in a local English translation (translate.py), because the control pair is
             an English answer repeated in German and shares no word sequence at all in the original
  embedding  cosine between the answer and each earlier answer under a local embedding model (nomic-embed-text through Ollama,
             inputs prefixed 'clustering: ', first 6,000 characters); the largest is kept

Two comparisons that try to separate echo from a shared topic:
  near/far   same-thread pairs created within 120 s of each other (the later one can hardly have been written after reading the
             earlier one) against same-thread pairs more than 600 s apart
  cross      pairs of answers from different threads

Reads threads/*.json saved by the round kit. Writes results.json: ids, account names of agents, times and numbers. No comment or
post text is written out. Usage: python3 echo.py [--no-embed]"""
import collections, glob, hashlib, itertools, json, math, os, random, re, sys, urllib.request
# Accounts whose answers are counted and also reported apart: one username per line in linkfarm.txt beside this script.
FARM = {ln.split()[0].lstrip("@").lower() for ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "linkfarm.txt"), encoding="utf-8") if ln.strip() and not ln.startswith("#")}
CONTROL = ("347da2ca", "02644d85", "c25d69d3")          # thread, earlier answer, later answer
N, NEAR, FAR, CAP = 4, 120, 600, 6000
ENG = {k: v["english"] for k, v in json.load(open("dl/english.json", encoding="utf-8")).items()} if os.path.exists("dl/english.json") else {}

ENGP = {k: v["english"] for k, v in json.load(open("dl/english_posts.json", encoding="utf-8")).items()} if os.path.exists("dl/english_posts.json") else {}

def text(c):
    """The answer in English: the local translation where the answer was not written in English (translate.py), else the body."""
    return ENG.get(c["id"], c["body"])
WORD = re.compile(r"\w+", re.UNICODE)


def grams(text):
    w = [x.lower() for x in WORD.findall(text)]
    return {tuple(w[i:i + N]) for i in range(len(w) - N + 1)}


def ts(s):
    import datetime as dt
    return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp()


def embed(texts):
    cache_f = "dl/emb_cache.json"; cache = json.load(open(cache_f)) if os.path.exists(cache_f) else {}
    keys = [hashlib.sha256(("clustering: " + t[:CAP]).encode()).hexdigest() for t in texts]
    todo = [(k, t) for k, t in dict(zip(keys, texts)).items() if k not in cache]
    for i in range(0, len(todo), 16):
        body = {"model": "nomic-embed-text", "input": ["clustering: " + t[:CAP] for _, t in todo[i:i + 16]], "truncate": True, "options": {"num_ctx": 8192}}
        req = urllib.request.Request("http://localhost:11434/api/embed", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r: out = json.loads(r.read().decode())["embeddings"]
        for (k, _), v in zip(todo[i:i + 16], out): cache[k] = v
        json.dump(cache, open(cache_f, "w"))
    return [cache[k] for k in keys]


def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def q(xs, p):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None


threads = []
for f in sorted(glob.glob("threads/*.json")):
    j = json.load(open(f, encoding="utf-8")); post = j["post"]
    if (post.get("author") or {}).get("user_type") != "human": continue
    ans = [c for c in j["comments"] if not c.get("parent_id") and (c.get("author") or {}).get("user_type") == "agent" and (c.get("body") or "").strip()]
    ans.sort(key=lambda c: c["created_at"])
    threads.append({"id": post["id"], "post": post, "answers": ans, "all": j["comments"], "fetched": j["fetched"]})
answers = [(t, c) for t in threads for c in t["answers"]]
farm = [c for _, c in answers if c["author"]["username"].lower() in FARM]
use_embed = "--no-embed" not in sys.argv
E = {}
if use_embed:
    vecs = embed([text(c) for _, c in answers] + [(t["post"].get("title") or "") + "\n\n" + (t["post"].get("body") or "") for t in threads])
    for (_, c), v in zip(answers, vecs): E[c["id"]] = v
    for t, v in zip(threads, vecs[len(answers):]): E[t["id"]] = v
rows, pairs = [], []
for t in threads:
    pg = grams((t["post"].get("title") or "") + " " + (t["post"].get("body") or "")) | grams(ENGP.get(t["id"], ""))
    G = {c["id"]: grams(text(c)) - pg for c in t["answers"]}
    for i, c in enumerate(t["answers"]):
        earlier = [e for e in t["answers"][:i] if e["author"]["username"] != c["author"]["username"]]
        row = {"thread": t["id"][:8], "answer": c["id"][:8], "author": c["author"]["username"], "created_at": c["created_at"][:19], "position": i + 1, "earlier_answers": len(earlier),
               "words": len(WORD.findall(c["body"])), "translated_for_comparison": c["id"] in ENG, "link_farm_account": c["author"]["username"].lower() in FARM}
        best_v = best_e = None
        for e in earlier:
            v = len(G[c["id"]] & G[e["id"]]) / len(G[c["id"]]) if G[c["id"]] else 0.0
            s = cos(E[c["id"]], E[e["id"]]) if use_embed else None
            dt = ts(c["created_at"]) - ts(e["created_at"])
            pairs.append({"thread": t["id"][:8], "earlier": e["id"][:8], "later": c["id"][:8], "earlier_author": e["author"]["username"], "later_author": c["author"]["username"], "seconds_apart": round(dt), "verbatim": round(v, 4), "cosine": (round(s, 4) if s is not None else None)})
            if best_v is None or v > best_v[0]: best_v = (v, e["id"][:8])
            if s is not None and (best_e is None or s > best_e[0]): best_e = (s, e["id"][:8])
        row.update(verbatim_max=(round(best_v[0], 4) if best_v else None), verbatim_with=(best_v[1] if best_v else None), cosine_max=(round(best_e[0], 4) if best_e else None), cosine_with=(best_e[1] if best_e else None),
                   cosine_to_post=(round(cos(E[c["id"]], E[t["id"]]), 4) if use_embed else None))
        rows.append(row)
have = [r for r in rows if r["earlier_answers"] > 0]
ctl = [p for p in pairs if (p["thread"], p["earlier"], p["later"]) == CONTROL]; assert len(ctl) == 1, "the control pair is not in the sample"
ctl = ctl[0]
out = {"sample": {"threads_by_humans": len(threads), "threads_with_two_or_more_agent_answers": sum(1 for t in threads if len({c["author"]["username"] for c in t["answers"]}) >= 2),
                  "agent_answers": len(rows), "answers_with_an_earlier_answer_by_another_agent": len(have), "answers_by_link_farm_accounts": len(farm), "distinct_agent_accounts": len({r["author"] for r in rows}),
                  "posts_created_from": min(t["post"]["created_at"] for t in threads)[:19], "posts_created_to": max(t["post"]["created_at"] for t in threads)[:19], "threads_read_from": min(t["fetched"] for t in threads), "threads_read_to": max(t["fetched"] for t in threads)},
       "definitions": {"ngram": N, "answers_compared_in_translation": sum(1 for _, c in answers if c["id"] in ENG), "near_seconds": NEAR, "far_seconds": FAR, "embedding_model": "nomic-embed-text (Ollama), prefix 'clustering: ', first %d characters" % CAP},
       "control_pair": ctl}
vm = [r["verbatim_max"] for r in have]
out["verbatim"] = {"control_rank_from_top": 1 + sum(v > ctl["verbatim"] for v in vm), "median": q(vm, .5), "p90": q(vm, .9), "max": max(vm), "answers_at_or_above_0.05": sum(v >= .05 for v in vm), "answers_at_or_above_0.10": sum(v >= .10 for v in vm), "answers_at_or_above_0.25": sum(v >= .25 for v in vm),
                   "answers_at_or_above_control": sum(v >= ctl["verbatim"] for v in vm), "answers_with_zero_shared_ngrams": sum(v == 0 for v in vm)}
# pairs that can hardly be one answer written after reading the other: the same measure on them is the floor for coincidence
nearv = [p["verbatim"] for p in pairs if p["seconds_apart"] <= NEAR]; farv = [p["verbatim"] for p in pairs if p["seconds_apart"] > FAR]
out["verbatim"].update(answers_at_or_above_0_03=sum(v >= .03 for v in vm), near_pairs=len(nearv), near_pairs_max=(max(nearv) if nearv else None), near_pairs_at_or_above_0_03=sum(v >= .03 for v in nearv),
                       near_pairs_with_zero=sum(v == 0 for v in nearv), far_pairs=len(farv), far_pairs_at_or_above_0_03=sum(v >= .03 for v in farv), far_pairs_with_zero=sum(v == 0 for v in farv),
                       answers_by_accounts_outside_the_link_farm_list=sum(1 for r in have if not r["link_farm_account"]))
if use_embed:
    cm = [r["cosine_max"] for r in have]
    near = [p["cosine"] for p in pairs if p["seconds_apart"] <= NEAR]; far = [p["cosine"] for p in pairs if p["seconds_apart"] > FAR]
    rnd = random.Random(20261113); ids = [(t["id"][:8], c["id"]) for t, c in answers]; cross = []
    while len(cross) < 4000:
        (ta, a), (tb, b) = rnd.sample(ids, 2)
        if ta != tb: cross.append(cos(E[a], E[b]))
    out["embedding"] = {"control_rank_from_top": 1 + sum(v > ctl["cosine"] for v in cm), "cosine_max_median": q(cm, .5), "cosine_max_p90": q(cm, .9), "answers_at_or_above_control": sum(v >= ctl["cosine"] for v in cm),
                        "pairs_same_thread": len(pairs), "near_pairs": len(near), "near_median": q(near, .5), "near_p90": q(near, .9), "far_pairs": len(far), "far_median": q(far, .5), "far_p90": q(far, .9),
                        "cross_thread_pairs_sampled": len(cross), "cross_median": q(cross, .5), "cross_p90": q(cross, .9), "cross_p99": q(cross, .99),
                        "answers_above_cross_p99": sum(v >= q(cross, .99) for v in cm), "median_cosine_to_post": q([r["cosine_to_post"] for r in rows], .5)}
    # the same comparison inside threads that have both kinds of pair, so that a thread's topic cannot make the difference
    by = collections.defaultdict(lambda: {"near": [], "far": []})
    for p in pairs:
        if p["seconds_apart"] <= NEAR: by[p["thread"]]["near"].append(p["cosine"])
        elif p["seconds_apart"] > FAR: by[p["thread"]]["far"].append(p["cosine"])
    both = {k: v for k, v in by.items() if v["near"] and v["far"]}
    diffs = [sum(v["far"]) / len(v["far"]) - sum(v["near"]) / len(v["near"]) for v in both.values()]
    out["embedding"].update(threads_with_near_and_far_pairs=len(both), far_minus_near_mean_within_thread_median=(q(diffs, .5) if diffs else None), threads_where_far_pairs_are_more_alike=sum(d > 0 for d in diffs))
mine = [r for r in rows if r["author"] == "reticuli"]
out["mine"] = mine
per = collections.defaultdict(list)
for r in have: per[r["author"]].append(r)
out["per_account"] = sorted(({"author": a, "answers_with_an_earlier_answer": len(v), "verbatim_at_or_above_0.10": sum(x["verbatim_max"] >= .10 for x in v),
                              "cosine_at_or_above_control": (sum(x["cosine_max"] >= ctl["cosine"] for x in v) if use_embed else None), "link_farm_account": v[0]["link_farm_account"]} for a, v in per.items()),
                            key=lambda x: (-x["answers_with_an_earlier_answer"], x["author"]))
out["top_verbatim_pairs"] = sorted(pairs, key=lambda p: -p["verbatim"])[:15]
out["top_cosine_pairs"] = sorted(pairs, key=lambda p: -(p["cosine"] or 0))[:15] if use_embed else []
out["rows"] = rows
json.dump(out, open("results.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ("sample", "control_pair", "verbatim") + (("embedding",) if use_embed else ())}, indent=1))
print("mine:", [(r["thread"], r["answer"], r["position"], r["earlier_answers"], r["verbatim_max"], r["cosine_max"]) for r in mine])
