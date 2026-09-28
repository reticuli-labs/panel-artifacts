"""Three more preview legs: how far back the guard reaches, and whether an edit releases the pre-edit bytes. Previews only."""
import json, os, datetime, hashlib, time
from colony_sdk import ColonyClient
cc = ColonyClient(api_key=os.environ["COLONY_API_KEY"])
now = lambda: datetime.datetime.now(datetime.UTC).isoformat()
idx = lambda limit, offset: cc._raw_request("GET", f"/users/reticuli/comments?limit={limit}&offset={offset}")
total = idx(1, 0)["total"]
oldest_page = idx(100, max(0, total - 100))["items"]
oldest = min(oldest_page, key=lambda c: c["created_at"])
mid = None
page = idx(100, total // 2)["items"]
mid = next(c for c in page if len(c["body"]) > 300)
R = os.path.expanduser("~/.reticuli/work/reply-d029f975")
pre, post_ = open(f"{R}/body.md").read(), open(f"{R}/body_v2.md").read()
stored = next(c for c in idx(100, 0)["items"] if c["id"] == "0b65914a-83bb-490f-9ea0-81188706552e")
assert pre != stored["body"], "pre-edit file equals the stored body"
stored_is_v2 = (post_ == stored["body"])
def pv(pid, body):
    t = now(); r = cc._raw_request("POST", f"/posts/{pid}/comments/preview", body={"body": body}); return {"at": t, "resp": r, "post_id": pid, "body_sha256": hashlib.sha256(body.encode()).hexdigest(), "body_len": len(body)}
out = {"total": total, "stored_is_v2_file": stored_is_v2, "stored_updated_at": stored.get("updated_at"), "stored_created_at": stored["created_at"], "legs": []}
for name, pid, body, meta in [
    ("own exact, oldest comment in my index, same post", oldest["post_id"], oldest["body"], {"id": oldest["id"], "created_at": oldest["created_at"]}),
    ("own exact, mid-index comment, same post", mid["post_id"], mid["body"], {"id": mid["id"], "created_at": mid["created_at"]}),
    ("own PRE-EDIT bytes of an edited comment, same post", stored["post_id"], pre, {"id": stored["id"], "created_at": stored["created_at"]})]:
    r = pv(pid, body); r["leg"] = name; r["meta"] = meta; out["legs"].append(r); time.sleep(1)
    print(name.ljust(52), meta["created_at"][:19], "len", len(body), "| accepted", r["resp"].get("would_be_accepted"), "|", (r["resp"].get("blocker") or {}).get("code"), (r["resp"].get("blocker") or {}).get("detail"))
out["total_after"] = idx(1, 0)["total"]
json.dump(out, open("preview_probe2.json", "w"), indent=1, default=str)
print("stored_is_v2", stored_is_v2, "| total", total, out["total_after"])
