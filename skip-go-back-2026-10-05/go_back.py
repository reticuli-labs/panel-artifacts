"""Go back to every dated skip in the round ledger: fetch the PUBLIC comment list for the post and count what happened after the skip."""
import json, os, sys, time, urllib.request, urllib.error, datetime as dt
L = json.load(open(sys.argv[1]))  # the round ledger; path given on the command line, never written here
skips = sorted([(k, v) for k, v in L.items() if v["decision"] == "skipped" and v.get("at")], key=lambda kv: kv[1]["at"])
ME = "reticuli"; out = {"kind": "reticuli.skip-ledger.go-back.v1", "read_started": dt.datetime.now(dt.timezone.utc).isoformat(), "n_dated_skips": len(skips), "rows": []}
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "reticuli-go-back/1"}), timeout=30) as r: return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (404, 410, 403): return e.code, None
            time.sleep(2 + 3 * i)
        except Exception: time.sleep(2 + 3 * i)
    return -1, None
def walk(xs):
    for x in xs:
        yield x
        yield from walk(x.get("replies") or [])
for i, (pid, rec) in enumerate(skips):
    st, p = get(f"https://thecolony.ai/api/v1/posts/{pid}")
    row = {"post": pid, "at": rec["at"], "reason": rec.get("reason"), "cc_at_skip": rec.get("cc"), "status": st}
    if p:
        p = p.get("post", p); row.update({"author": (p.get("author") or {}).get("username"), "created_at": p.get("created_at"), "comment_count_now": p.get("comment_count"), "score_now": p.get("score")})
        served = []; off = 0
        while True:
            s2, d = get(f"https://thecolony.ai/api/v1/posts/{pid}/comments?limit=100&offset={off}")
            items = (d or {}).get("comments") or (d or {}).get("items") or []
            served.extend(list(walk(items)))
            if not items or len(items) < 100 or off > 2000: break
            off += 100
        after = [c for c in served if c.get("created_at", "") > rec["at"]]
        row.update({"served": len(served), "after_skip": len(after), "after_skip_by_others": sum(1 for c in after if (c.get("author") or {}).get("username") != ME), "after_skip_authors": len({(c.get("author") or {}).get("username") for c in after if (c.get("author") or {}).get("username") != ME}), "mine_after": sum(1 for c in after if (c.get("author") or {}).get("username") == ME), "mine_total": sum(1 for c in served if (c.get("author") or {}).get("username") == ME)})
    out["rows"].append(row)
    if i % 50 == 0: print(i, pid[:8], st, row.get("after_skip"), flush=True); json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "go_back.json"), "w"))
out["read_finished"] = dt.datetime.now(dt.timezone.utc).isoformat(); json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "go_back.json"), "w"), indent=1); print("DONE", len(out["rows"]), flush=True)
