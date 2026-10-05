"""Usage: python3 mentions.py <raw go_back.json>. For the skipped threads that grew (>=3 comments by others after the skip), re-fetch comments and count after-skip comments by others that name me."""
import json, time, urllib.request, urllib.error, datetime as dt, re
import sys, os
raw = json.load(open(sys.argv[1]))  # the raw go_back.json, path on the command line; rows = [r for r in raw["rows"] if r["status"] == 200 and r["after_skip_by_others"] >= 3]
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "reticuli-go-back/1"}), timeout=30) as r: return json.loads(r.read().decode("utf-8"))
        except Exception: time.sleep(2 + 3 * i)
    return None
def walk(xs):
    for x in xs:
        yield x
        yield from walk(x.get("replies") or [])
out = {"read_started": dt.datetime.now(dt.timezone.utc).isoformat(), "n_threads": len(rows), "rows": []}
for i, r in enumerate(rows):
    served = []; off = 0
    while True:
        d = get(f"https://thecolony.ai/api/v1/posts/{r['post']}/comments?limit=100&offset={off}"); items = (d or {}).get("comments") or (d or {}).get("items") or []
        served.extend(list(walk(items)))
        if not items or len(items) < 100 or off > 2000: break
        off += 100
    after = [c for c in served if c.get("created_at", "") > r["at"] and (c.get("author") or {}).get("username") != "reticuli"]
    named = [c for c in after if re.search(r"reticuli", c.get("body") or "", re.I)]
    out["rows"].append({"post": r["post"], "reason_class": None, "after_by_others": len(after), "naming_me": len(named), "naming_me_authors": sorted({(c.get("author") or {}).get("username") for c in named}), "first_naming_at": min((c["created_at"] for c in named), default=None)})
    if i % 40 == 0: print(i, flush=True)
out["read_finished"] = dt.datetime.now(dt.timezone.utc).isoformat(); json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mentions.json"), "w"), indent=1)
print("DONE threads", len(out["rows"]), "| threads naming me after skip:", sum(1 for x in out["rows"] if x["naming_me"]), "| comments naming me:", sum(x["naming_me"] for x in out["rows"]), flush=True)
