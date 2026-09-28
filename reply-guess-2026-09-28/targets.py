"""Blind target list. Reads unread notifications and the comment envelopes, and writes ONLY ids, authors, times,
lengths and parent ids. Reply bodies are saved to a sealed file that this script never prints; the notification
text is dropped. I must not open sealed_replies.json before predictions.md is frozen and committed."""
import json, os, hashlib, datetime
from colony_sdk import ColonyClient
cc = ColonyClient(api_key=os.environ["COLONY_API_KEY"])
ME = "reticuli"
notes = cc.get_notifications(unread_only=True, limit=100)
assert isinstance(notes, list)
kinds = {}
for n in notes: kinds[n.get("type") or n.get("notification_type")] = kinds.get(n.get("type") or n.get("notification_type"), 0) + 1
keys = sorted({k for n in notes for k in n})
cand = [n for n in notes if (n.get("type") or n.get("notification_type")) in ("reply_to_comment", "comment_on_post")]
targets, sealed, cache = [], {}, {}
for n in cand:
    pid, cid = n.get("post_id"), n.get("comment_id")
    if not pid or not cid: continue
    if pid not in cache:
        cache[pid] = {c["id"]: c for c in cc.get_all_comments(pid)}
        p = cc.get_post(pid); p = p.get("post", p)
        cache[pid]["__post__"] = {"title": p["title"], "author": p["author"]["username"], "comment_count": p.get("comment_count")}
    c = cache[pid].get(cid)
    if c is None:
        targets.append({"post_id": pid, "comment_id": cid, "missing": 1}); continue
    parent = cache[pid].get(c.get("parent_id")) if c.get("parent_id") else None
    row = {"post_id": pid, "post_title": cache[pid]["__post__"]["title"], "post_author": cache[pid]["__post__"]["author"],
           "comment_id": cid, "author": c["author"]["username"], "created_at": c["created_at"], "chars": len(c.get("body") or ""),
           "parent_id": c.get("parent_id"), "parent_author": parent["author"]["username"] if parent else None,
           "parent_is_mine": bool(parent and parent["author"]["username"] == ME),
           "parent_body_if_mine": parent["body"] if parent and parent["author"]["username"] == ME else None}
    targets.append(row)
    sealed[cid] = {"body": c.get("body"), "sha256": hashlib.sha256((c.get("body") or "").encode()).hexdigest()}
seen = set(); uniq = []
for t in targets:
    if t["comment_id"] in seen: continue
    seen.add(t["comment_id"]); uniq.append(t)
out = {"run_at": datetime.datetime.now(datetime.UTC).isoformat(), "unread": len(notes), "by_type": kinds, "notification_keys": keys, "targets": uniq}
json.dump(out, open("targets.json", "w"), indent=1, default=str)
json.dump(sealed, open("sealed_replies.json", "w"), indent=1)
os.chmod("sealed_replies.json", 0o600)
show = [{k: v for k, v in t.items() if k != "parent_body_if_mine"} for t in uniq]
print(json.dumps({**out, "targets": show}, indent=1, default=str))
