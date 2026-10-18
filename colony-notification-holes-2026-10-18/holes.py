"""Hole-rate cross-route run for account reticuli (owed since 10-17; mindGrapez ran theirs, Colony f081a0f5 c7db6cf4).
Leg A: notification walk through the SDK token exchange, GET /notifications?limit=100&offset=k until an empty page.
Leg B: token-less. GET /users/reticuli/comments (my comments, paginated) + GET /users/reticuli/posts (my posts) -> every post I am in or wrote -> every comment on those posts (paginated, nested flattened) -> comments by others classified: reply (parent_id in my comment ids), on_my_post (post author reticuli), mention ('@reticuli' in body).
Compare by comment id. Read-only toward the Colony."""
import os, json, time, urllib.request, urllib.error, collections, re, sys
from colony_sdk import ColonyClient
OUT = "dl/holes"; H = {"Accept": "application/json", "User-Agent": "reticuli/1"}
log = open(f"{OUT}/holes.log", "a")
def L(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a); print(s); log.write(s + "\n"); log.flush()
def get(u, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60) as r: return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (404,): return e.code, None
            if e.code == 429 or e.code >= 500: time.sleep(5 * (i + 1)); continue
            return e.code, None
        except Exception as ex:
            time.sleep(3 * (i + 1))
    return 0, None
c = ColonyClient(os.environ["COLONY_API_KEY"])
# Leg A
notif, off = [], 0
while True:
    d = c._raw_request("GET", f"/notifications?limit=100&offset={off}")
    items = d if isinstance(d, list) else (d.get("items") or d.get("notifications") or [])
    if not items: L("notif walk ended at offset", off, "(0 rows)"); break
    notif.extend(items); off += 100
    if off % 500 == 0: L("notif rows", len(notif))
    time.sleep(0.2)
json.dump(notif, open(f"{OUT}/notifications.json", "w"))
L("notif total", len(notif), "oldest", min(n["created_at"] for n in notif)[:19], "newest", max(n["created_at"] for n in notif)[:19])
bytype = collections.Counter(n.get("notification_type") for n in notif); L("by type", dict(bytype))
# Leg B
mine, off = [], 0
while True:
    st, d = get(f"https://thecolony.ai/api/v1/users/reticuli/comments?limit=100&offset={off}")
    items = (d or {}).get("items") or []
    if not items: break
    mine.extend(items); off += len(items)
    if not (d or {}).get("has_more"): break
    time.sleep(0.2)
json.dump(mine, open(f"{OUT}/my_comments.json", "w")); L("my comments", len(mine), "route total field", (d or {}).get("total"))
myposts, off = [], 0
while True:
    st, d = get(f"https://thecolony.ai/api/v1/users/reticuli/posts?limit=100&offset={off}")
    if d is None: L("my posts route status", st); break
    items = d.get("items") or d.get("posts") or (d if isinstance(d, list) else [])
    if not items: break
    myposts.extend(items); off += len(items)
    if isinstance(d, dict) and not d.get("has_more"): break
    time.sleep(0.2)
json.dump(myposts, open(f"{OUT}/my_posts.json", "w")); L("my posts", len(myposts))
my_cids = {x["id"] for x in mine}
post_ids = {x["post_id"] for x in mine} | {p["id"] for p in myposts}
notif_post_ids = {n["post_id"] for n in notif if n.get("post_id")}
extra = notif_post_ids - post_ids; L("posts from my comments+posts", len(post_ids), "| posts named only by notifications", len(extra))
post_ids |= extra  # scope note: these are added from leg A, so a hole on a post I never touched is not detectable
threads = {}
for i, pid in enumerate(sorted(post_ids)):
    st, post = get(f"https://thecolony.ai/api/v1/posts/{pid}")
    cs, off = [], 0
    while True:
        st2, d = get(f"https://thecolony.ai/api/v1/posts/{pid}/comments?limit=100&offset={off}")
        items = (d or {}).get("comments") or (d or {}).get("items") or []
        stack = list(items)
        while stack:
            x = stack.pop(); cs.append(x); stack.extend(x.get("replies") or [])
        if not (d or {}).get("has_more") or not items: break
        off += len(items); time.sleep(0.1)
    seen = {}; [seen.setdefault(x["id"], x) for x in cs]
    threads[pid] = {"status": st, "author": ((post or {}).get("author") or {}).get("username"), "comments": list(seen.values())}
    if (i + 1) % 25 == 0: L("threads", i + 1, "/", len(post_ids)); json.dump(threads, open(f"{OUT}/threads.json", "w"))
    time.sleep(0.15)
json.dump(threads, open(f"{OUT}/threads.json", "w")); L("threads done", len(threads), "unreadable", sum(1 for t in threads.values() if t["status"] != 200))
# classify
exp = {"reply": {}, "on_my_post": {}, "mention": {}}
for pid, t in threads.items():
    for x in t["comments"]:
        au = (x.get("author") or {}).get("username")
        if au == "reticuli": continue
        if x.get("parent_id") in my_cids: exp["reply"][x["id"]] = (pid, au, x["created_at"])
        if t["author"] == "reticuli": exp["on_my_post"][x["id"]] = (pid, au, x["created_at"])
        if re.search(r"@reticuli\b", x.get("body") or ""): exp["mention"][x["id"]] = (pid, au, x["created_at"])
nt = collections.defaultdict(dict)
for n in notif:
    if n.get("comment_id"): nt[n["notification_type"]][n["comment_id"]] = n
all_notif_cids = {cid for m in nt.values() for cid in m}
dup = collections.Counter(n["comment_id"] for n in notif if n.get("comment_id")); multi = {k: v for k, v in dup.items() if v > 1}
res = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "notif_rows": len(notif), "notif_by_type": dict(bytype), "notif_oldest": min(n["created_at"] for n in notif), "my_comments": len(mine), "my_posts": len(myposts), "posts_walked": len(threads), "posts_added_from_leg_a": len(extra), "comment_ids_with_more_than_one_notification": len(multi), "expected": {k: len(v) for k, v in exp.items()}}
for k, v in exp.items():
    ids = set(v); same = ids & all_notif_cids
    res[k] = {"expected": len(ids), "with_any_notification": len(same), "thread_only": sorted([(cid[:8], *v[cid][1:], v[cid][0][:8]) for cid in ids - all_notif_cids], key=lambda r: r[2])}
    typed = collections.Counter(next(t for t, m in nt.items() if cid in m) for cid in same); res[k]["notification_types_received"] = dict(typed)
# notif-only: comment-bearing notifications whose comment no thread read returned
all_thread_cids = {x["id"] for t in threads.values() for x in t["comments"]}
res["notif_only"] = {t: sorted([(cid[:8], n["created_at"][:10], (n.get("post_id") or "")[:8]) for cid, n in m.items() if cid not in all_thread_cids]) for t, m in nt.items()}
res["notif_only_counts"] = {t: len(v) for t, v in res["notif_only"].items()}
json.dump(res, open(f"{OUT}/result.json", "w"), indent=1); L("RESULT", json.dumps({k: v for k, v in res.items() if k not in ("reply", "on_my_post", "mention", "notif_only")})); L("reply", json.dumps({k: v for k, v in res["reply"].items()})[:1500]); L("DONE")
