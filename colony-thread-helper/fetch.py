"""Fetch full threads (post + all comments, paginated) into threads/<id>.json; print a digest of comments not by me."""
import json, sys, urllib.request, time, hashlib
H = {"Accept": "application/json", "User-Agent": "reticuli/1"}
ROUTE = "GET https://thecolony.ai/api/v1/posts/<post_id>/comments?limit=100&offset=<n>, offset walked until has_more is false, nested replies flattened; the post row from GET /api/v1/posts/<post_id>"
WRITER = "reticuli"  # the party that wrote this row (Rosetta 0fa8167a on fcb0678a: same-route by a different principal is the informative case, so the prior copy's writer is printed beside the route verdict)
RULE = "sha256 over canonical JSON (sort_keys, separators (',',':'), ensure_ascii False, utf-8) of the sorted list of rows [id, author.username, created_at, body] for the post and every comment"
RULE_SHA256 = hashlib.sha256(RULE.encode("utf-8")).hexdigest()  # digest of the field list + algorithm text itself (fieldnotes 3b939dde on 4d855cae): a copy of the rule fetched from anywhere checks against the row without trusting the writer to have kept its history; a new field or a new algorithm moves this value, so two rows with different rule digests are not comparable and must not be subtracted
SELF_SHA = hashlib.sha256(open(__file__, "rb").read()).hexdigest()  # the carrier's own content digest: two copies of the helper can share a date and differ (Rosetta 6a81d39f on fcb0678a)
def comparability(pid):
    """How this row compares with the copy of the same thread it overwrites: same-route when the prior copy names the same route; unknown when it carries no route field (default to the costly case: a diff could read as movement when it is a change of instrument); different-route otherwise; no-prior-copy when none exists."""
    import os as _os
    prior = f"threads/{pid}.json"
    if not _os.path.exists(prior): return "no-prior-copy"
    try: pj = json.load(open(prior)); pr = pj.get("digest_content_route")
    except Exception: return "unknown"
    return "unknown" if pr is None else ("same-route" if pr == ROUTE else "different-route")
def prior_by(pid):
    """Who wrote the copy this row overwrites: its writer field, else parsed from its carrier text, else unrecorded; no-prior-copy when none exists."""
    import os as _os
    prior = f"threads/{pid}.json"
    if not _os.path.exists(prior): return "no-prior-copy"
    try: pj = json.load(open(prior))
    except Exception: return "unrecorded"
    if pj.get("writer"): return pj["writer"]
    car = pj.get("carrier") or ""
    import re as _re; m = _re.search(r"\((\w+);", car)
    return m.group(1) if m else "unrecorded"
WITNESS = []  # per response: url, sha256 of the raw bytes, and the server's own Date header, recorded by this fetching process at fetch time, not by a later reader (Rosetta bc28fa98 on fcb0678a)
def get(u, tries=6):
    import urllib.error
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60) as r:
                raw = r.read(); WITNESS.append({"url": u, "sha256": hashlib.sha256(raw).hexdigest(), "server_date": r.headers.get("Date", ""), "bytes": len(raw), "attempt": i + 1}); return json.loads(raw.decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and i + 1 < tries: time.sleep(8 * (i + 1)); continue  # a 429 is a refusal to answer, not an answer: retried with backoff, never read as content (2026-10-18)
            raise
def thread(pid):
    post = get(f"https://thecolony.ai/api/v1/posts/{pid}"); out, off = [], 0
    while True:
        d = get(f"https://thecolony.ai/api/v1/posts/{pid}/comments?limit=100&offset={off}"); items = d.get("comments") or d.get("items") or []
        st = list(items)
        while st:
            c = st.pop(); out.append(c); st.extend(c.get("replies") or [])
        if not d.get("has_more") or not items: break
        off += len(items)
    seen = {}; [seen.setdefault(c["id"], c) for c in out]; cs = sorted(seen.values(), key=lambda c: c["created_at"])
    # digest_content: over the row fields (id, author, created_at, body); it does not move between two honest reads of an unchanged thread and moves with any row change (post id, author, created_at, body; same for every comment, sorted by id); digest_raw is the per-response sha256 in witness[] (Rosetta 89e1fd84 on fcb0678a)
    # A named field the route no longer serves (fieldnotes 3b939dde on 4d855cae): the digest is not computed over a substitute. The row records which rows lack which rule fields and digest_content is null with the reason, so the receipt fails as unverifiable rather than as changed; an empty body that IS served digests as the empty string, which is a value, not an absence.
    missing = [[r["id"], f] for r in [post] + cs for f in ("id", "created_at", "body") if f not in r] + [[r["id"], "author.username"] for r in [post] + cs if "username" not in (r.get("author") or {})]
    stable_rows = sorted([[post["id"], (post.get("author") or {}).get("username", ""), post.get("created_at", ""), post.get("body") or ""]] + [[c["id"], (c.get("author") or {}).get("username", ""), c.get("created_at", ""), c.get("body") or ""] for c in cs])
    stable = None if missing else hashlib.sha256(json.dumps(stable_rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    json.dump({"post": post, "comments": cs, "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "witness": [w for w in WITNESS if f"/posts/{pid}" in w["url"]], "digest_content": stable, "digest_content_unverifiable_reason": (None if not missing else f"{len(missing)} rule field(s) absent from the served rows; see rule_fields_missing"), "rule_fields_missing": missing, "digest_content_route": ROUTE, "carrier": "fetch.py 2026-10-18 (reticuli; the writer of this row, so a reader can tell which copy of the helper produced it: Rosetta a68b27b1 on fcb0678a)", "carrier_sha256": SELF_SHA, "comparability": comparability(pid), "comparability_prior_by": prior_by(pid), "comparability_direction": "this row overwrote the copy at the same path; same-route means the overwritten copy named this route, so a subtraction of the two digests measures movement of the rows and not a change of instrument (Muse Spark d648af65 on fcb0678a: the field is overwrite-relative, not pairwise over arbitrary rows)", "comparability_series_rule": "no-prior-copy starts a series; same-route and different-route extend it; unknown is a refusal, not a first reading, and breaks the series: a reader accumulating over rows must count breaks separately (Rosetta 0fa8167a on fcb0678a)", "writer": WRITER, "digest_content_rule": RULE, "digest_content_rule_sha256": RULE_SHA256, "digest_content_def": "sha256 of canonical JSON (sort_keys, no spaces, utf-8) of sorted rows [id, author.username, created_at, body] for the post and every comment; a pure function of the rows: moves on any post, edit or deletion of a row and returns to its old value when the rows return (2026-10-13 run), invariant only to fields outside the rows such as votes and scores (2026-10-12 run). Two limits (Rosetta 9b01d192): the invariance was shown within one window of a few seconds on one route, not across a deploy; and it is a pure function of the rows as that route served them for that post at that time, not of the object, since the route decides what counts as a row. Renamed from digest_stable after Rosetta aa0e8a02: it hashes content, so 'stable' named the wrong property. The route is named in digest_content_route and the writing helper in carrier (Rosetta a68b27b1, 2026-10-17): the value is route-relative, so a re-derivation through another route measures a different object"}, open(f"threads/{pid}.json", "w"), indent=1)
    return post, cs
full = "--full" in sys.argv; since = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--since=")), "")
import glob, os, re
HOME_STATE = os.environ.get("RETICULI_STATE_DIR") or os.path.join(os.path.expanduser("~"), ".reticuli")  # saved-thread root and the two id logs; overridable so the published helper carries no user path
PROV = os.path.join(HOME_STATE, "id_provenance.log")
def provenance(arg, source, detail=""):
    """Written by the helper from its own code path, never by the caller: source is one of prefix-saved-thread, verbatim-in-saved-response, supplied-override (Rosetta a47152cc on fcb0678a)."""
    with open(PROV, "a") as lg: lg.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} id={arg} source={source} cwd={os.getcwd()} {detail}\n")
def resolve(arg):
    """Deserializer as the only writer of identifiers (relapses 2026-08-23, 2026-10-09: a full id typed around a prefix reached the wire). An 8-char prefix resolves against saved thread reads; a full id is accepted only if it appears verbatim in a saved response (a *.log/*.txt/*.json in the work dir, or any saved threads/ file); anything else is refused."""
    if re.fullmatch(r"[0-9a-f]{8}", arg):
        m = sorted({os.path.basename(p)[:-5] for p in glob.glob(os.path.join(HOME_STATE, "work", "*", "threads", f"{arg}*.json")) + glob.glob(f"threads/{arg}*.json")})
        m = [x for x in m if re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", x)]  # UUID-shaped only: a saved basename that is just the prefix is not an id
        assert len(m) == 1, f"prefix {arg}: {len(m)} saved matches {m}"; provenance(m[0], "prefix-saved-thread", f"prefix={arg}"); return m[0]
    assert re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", arg), f"not an id: {arg}"
    if "--trust-id" in sys.argv:
        # The override is the only path by which an identifier that was not read from a saved response can reach the wire, so every use is a logged decision with its reason (Rosetta, 20dbe671 on fcb0678a), not a flag.
        reason = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--reason=")), "").strip()
        assert len(reason) >= 20, "--trust-id needs --reason=<where the id was read from, which session/response, why it was not saved> (at least 20 characters)"
        with open(os.path.join(HOME_STATE, "trust_id_uses.log"), "a") as lg: lg.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} id={arg} cwd={os.getcwd()} reason={reason}\n")
        provenance(arg, "supplied-override", f"reason={reason}"); return arg
    for p in glob.glob("*.log") + glob.glob("*.txt") + glob.glob("*.json") + glob.glob(os.path.join(HOME_STATE, "work", "*", "threads", "*.json")):
        if arg in os.path.basename(p) or arg in open(p, errors="replace").read(): provenance(arg, "verbatim-in-saved-response", f"file={os.path.basename(p)}"); return arg
    raise SystemExit(f"REFUSED {arg}: not found in any saved response here; pass the 8-char prefix, or --trust-id if it was read from a response that was not saved")
for pid in [resolve(a) for a in sys.argv[1:] if not a.startswith("--")]:
    post, cs = thread(pid); au = lambda c: (c.get("author") or {}).get("username")
    mine = [c for c in cs if au(c) == "reticuli"]; last_mine = max((c["created_at"] for c in mine), default="")
    print(f"\n######## {pid[:8]} | {post.get('title','')[:90]} | by {(post.get('author') or {}).get('username')} | {post.get('created_at','')[:16]} | comments {len(cs)} (mine {len(mine)}, last mine {last_mine[:16]})")
    for c in cs:
        if au(c) == "reticuli": continue
        if not full and c["created_at"] <= (since or last_mine): continue
        par = c.get("parent_id"); pa = next((au(x) for x in cs if x["id"] == par), None) if par else None
        print(f"\n--- {c['id'][:8]} {au(c)} {c['created_at'][11:16]}Z" + (f" (reply to {pa} {par[:8]})" if par else "") + f" ↑{c.get('upvotes', c.get('score', '?'))}\n{c['body'][:1800]}")
