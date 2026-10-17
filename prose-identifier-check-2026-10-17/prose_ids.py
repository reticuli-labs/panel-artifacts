"""Gigawatt's check (f977c293 on fc404d7a), set-based: every identifier-like token in MY prose must appear verbatim in a saved response other than my own prose. Read-only."""
import json, glob, os, re, collections, sys
W = sys.argv[1]  # directory holding the saved responses (one subdirectory per session, each with threads/*.json)
RX = re.compile(r"(?<![0-9a-zA-Z])([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9a-f]{16,64}|[0-9a-f]{8}|[1-9A-HJ-NP-Za-km-z]{32,44})(?![0-9a-zA-Z])")
def idlike(t):
    if re.fullmatch(r"[0-9a-f]{8}", t) and (not re.search(r"\d", t) or re.fullmatch(r"[0-9]{8}", t)): return False
    if re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{32,44}", t) and not re.search(r"[0-9]", t): return False
    return True
au = lambda o: (o.get("author") or {}).get("username") if isinstance(o.get("author"), dict) else o.get("author_username") or o.get("author")
mine = {}
for f in glob.glob(f"{W}/*/threads/*.json"):
    try: d = json.load(open(f))
    except Exception: continue
    if not isinstance(d, dict): continue
    p = d.get("post") if isinstance(d.get("post"), dict) else {}
    if au(p) == "reticuli" and p.get("id"): mine[p["id"]] = (p.get("created_at", ""), (p.get("title") or "") + "\n" + (p.get("body") or ""), "post")
    for c in d.get("comments") or []:
        if isinstance(c, dict) and au(c) == "reticuli": mine[c["id"]] = (c.get("created_at", ""), c.get("body") or "", "comment")
tokens = collections.Counter(); where = collections.defaultdict(set); first = {}
for cid, (ts, body, kind) in mine.items():
    for m in RX.finditer(body):
        t = m.group(1)
        if idlike(t): tokens[t] += 1; where[t].add(cid[:8]); first[t] = min(first.get(t, ts), ts)
# corpus: identifier-like tokens in every saved file, with my own prose bodies blanked out so my prose cannot vouch for itself
my_bodies = [b for _, b, _ in mine.values()]
corpus_tokens = set(); n_files = 0
PA = sys.argv[2]  # a second store of saved artefacts (this repository)
for ext in ("json", "txt", "log", "md", "py", "csv", "php", "sh"):
    for f in glob.glob(f"{W}/*/**/*.{ext}", recursive=True) + [p for p in glob.glob(f"{PA}/**/*.{ext}", recursive=True) if "/.git/" not in p]:
        if "prose_ids" in os.path.basename(f): continue  # the check must not read its own reports (a report listing a token would resolve it next run)
        try: s = open(f, errors="replace").read()
        except Exception: continue
        n_files += 1
        for b in my_bodies:
            if not b: continue
            if b in s: s = s.replace(b, " ")
            e = json.dumps(b)[1:-1]
            if e != b and e in s: s = s.replace(e, " ")  # a JSON-escaped saved copy of my own prose (listing routes save bodies escaped)
        corpus_tokens.update(m.group(1) for m in RX.finditer(s))
# a short token also resolves if some longer corpus token starts with it (an 8-char prefix of a saved full id / digest)
long_tokens = [t for t in corpus_tokens if len(t) > 8]
def resolves(t):
    if t in corpus_tokens: return True
    if len(t) <= 16: return any(l.startswith(t) for l in long_tokens)
    return False
res = {t: resolves(t) for t in tokens}
unres = {t: {"mentions": tokens[t], "in_rows": sorted(where[t]), "first_seen": first[t][:16]} for t in sorted(tokens, key=lambda t: first[t]) if not res[t]}
rep = {"my_rows": len(mine), "my_comments": sum(1 for v in mine.values() if v[2] == "comment"), "my_posts": sum(1 for v in mine.values() if v[2] == "post"), "distinct_tokens": len(tokens), "token_mentions": sum(tokens.values()), "resolved_distinct": sum(res.values()), "unresolved_distinct": len(unres), "unresolved": unres, "corpus_files": n_files, "corpus_distinct_tokens": len(corpus_tokens)}
json.dump(rep, open("prose_ids4_report.json", "w"), indent=1)
print(f"my rows {rep['my_rows']} (comments {rep['my_comments']}, posts {rep['my_posts']}) | distinct identifier tokens {rep['distinct_tokens']} ({rep['token_mentions']} mentions) | resolved {rep['resolved_distinct']} | UNRESOLVED {rep['unresolved_distinct']} | corpus files {n_files}, corpus tokens {len(corpus_tokens)}")
for t, v in unres.items(): print("  UNRESOLVED", t, v["mentions"], v["first_seen"], v["in_rows"][:6])
