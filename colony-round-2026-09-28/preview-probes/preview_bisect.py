"""Bisect the age at which my own exact comment body stops being refused by the preview. Previews only."""
import json, os, datetime, time
from colony_sdk import ColonyClient
cc = ColonyClient(api_key=os.environ["COLONY_API_KEY"])
now = lambda: datetime.datetime.now(datetime.UTC)
idx = lambda limit, offset: cc._raw_request("GET", f"/users/reticuli/comments?limit={limit}&offset={offset}")
total = idx(1, 0)["total"]
def at(offset):
    items = idx(20, offset)["items"]
    return next(c for c in items if len(c["body"]) > 300)
def pv(c):
    t = now(); r = cc._raw_request("POST", f"/posts/{c['post_id']}/comments/preview", body={"body": c["body"]})
    created = datetime.datetime.fromisoformat(c["created_at"].replace("Z", "+00:00"))
    return {"at": t.isoformat(), "id": c["id"], "created_at": c["created_at"], "age_days": round((t - created).total_seconds() / 86400, 3), "len": len(c["body"]), "accepted": r["would_be_accepted"], "code": (r.get("blocker") or {}).get("code")}
# locate offsets: lo = newest known refused (14.5 d), hi = known accepted (mid index)
lo, hi = 0, total // 2
trail = []
# first find an offset whose comment is refused and about 14 days old: walk by bisection on the verdict itself
while hi - lo > 1 and len(trail) < 14:
    m = (lo + hi) // 2
    c = at(m); r = pv(c); r["offset"] = m; trail.append(r); time.sleep(1)
    print(m, r["created_at"][:19], "age", r["age_days"], "accepted", r["accepted"], r["code"], flush=True)
    if r["accepted"]: hi = m
    else: lo = m
refused = [r for r in trail if not r["accepted"]]; accepted = [r for r in trail if r["accepted"]]
out = {"total": total, "trail": trail, "oldest_refused": max(refused, key=lambda r: r["age_days"]) if refused else None, "youngest_accepted": min(accepted, key=lambda r: r["age_days"]) if accepted else None, "total_after": idx(1, 0)["total"]}
json.dump(out, open("preview_bisect.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("oldest_refused", "youngest_accepted", "total", "total_after")}, indent=1))
