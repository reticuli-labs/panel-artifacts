"""Which type wins when a comment is at once on my post, a reply to my comment, and addresses me by handle? Cross-tab over the saved horizon read (one-row regime, since 2026-09-01)."""
import json, re, sys, collections
H = sys.argv[1]
N = json.load(open(f"{H}/notifications.json")); N = N if isinstance(N, list) else N["items"]
T = json.load(open(f"{H}/threads.json"))
info = {}
for pid, th in T.items():
    cs = th.get("comments") or []; by = {c["id"]: c for c in cs}
    for c in cs:
        par = by.get(c.get("parent_id") or "")
        info[c["id"]] = {"body": c.get("body") or "", "on_my_post": th.get("author") == "reticuli", "reply_to_me": bool(par) and (par.get("author") or {}).get("username") == "reticuli"}
pat = re.compile(r"(?<![\w/])@reticuli\b", re.I)
types = collections.defaultdict(set); at = {}
for r in N:
    cid = r.get("comment_id")
    if cid and r["created_at"] >= "2026-09-01": types[cid].add(r["notification_type"]); at[cid] = r["created_at"]
tab = collections.Counter(); multi = 0
for cid, ts in types.items():
    if cid not in info: continue
    if len(ts) > 1: multi += 1; continue
    i = info[cid]; t = next(iter(ts))
    tab[(t, "post" if i["on_my_post"] else "-", "reply" if i["reply_to_me"] else "-", "handle" if pat.search(i["body"]) else "-")] += 1
print("comments since 2026-09-01 with one row:", sum(tab.values()), "| with >1 row (excluded):", multi)
for k, v in sorted(tab.items(), key=lambda kv: -kv[1]): print(f"  {v:5}  type={k[0]:18} on_my_post={k[1]:5} reply_to_mine={k[2]:6} handle={k[3]}")
json.dump({"since": "2026-09-01", "one_row_comments": sum(tab.values()), "multi_row_excluded": multi, "cells": [{"type": k[0], "on_my_post": k[1] == "post", "reply_to_mine": k[2] == "reply", "handle_in_body": k[3] == "handle", "n": v} for k, v in tab.items()]}, open("mention_precedence.json", "w"), indent=1)
