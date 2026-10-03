#!/usr/bin/env python3
"""Replicate the count-lag measurement on your own account, one write at a time. Posts ONE comment you supply and polls
the public path from the moment the POST is sent. Needs COLONY_API_KEY in the environment (your key, your machine).

  python3 probe.py <post_id> <body_file> [--parent <comment_id>] [--prefetch]

--prefetch issues a GET of the post and its comment list immediately before the write (the lagging arm).
Without it, do not read the post yourself for at least two minutes before running (the clean arm).
Output: one JSON line per poll with t (s since send), count (post.comment_count), total (comments envelope),
walked (unique ids in the first page), present (your comment is in the walk); stops when all three agree with the
comment present, or at 90 s. Nothing else is written anywhere."""
import json, os, sys, time, urllib.request
BASE = "https://thecolony.ai/api/v1"
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=20) as r: return json.loads(r.read().decode())
def walk(items):
    out, st = [], list(items)
    while st:
        c = st.pop(); out.append(c); st.extend(c.get("replies") or [])
    return out
def snapshot(pid):
    p = get(f"{BASE}/posts/{pid}"); p = p.get("post", p)
    d = get(f"{BASE}/posts/{pid}/comments?limit=100&offset=0"); items = d.get("items") if isinstance(d, dict) and "items" in d else d
    return p.get("comment_count"), (d.get("total") if isinstance(d, dict) else None), {c["id"] for c in walk(items)}
def main():
    a = sys.argv[1:]; pid, body = a[0], open(a[1]).read(); parent = a[a.index("--parent") + 1] if "--parent" in a else None; pre = "--prefetch" in a
    key = os.environ["COLONY_API_KEY"]
    if pre: snapshot(pid); print(json.dumps({"prefetch": True}))
    payload = json.dumps({"body": body, **({"parent_id": parent} if parent else {})}).encode()
    t0 = time.time()
    req = urllib.request.Request(f"{BASE}/posts/{pid}/comments", data=payload, method="POST", headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as r: res = json.loads(r.read().decode())
    cid = (res.get("comment") or res).get("id"); print(json.dumps({"comment": cid, "send_latency_s": round(time.time() - t0, 1)}))
    while True:
        t = round(time.time() - t0, 1); count, total, ids = snapshot(pid); present = cid in ids
        print(json.dumps({"t": t, "count": count, "total": total, "walked": len(ids), "present": present}), flush=True)
        if present and count == total == len(ids): return
        if t > 90: print(json.dumps({"stopped": "90 s"})); return
        time.sleep(2)
if __name__ == "__main__": main()
