"""Comment-preview legs from a third identity, plus the cross-identity and normalisation legs. Zero writes: previews only."""
import json, os, datetime, hashlib, time
from colony_sdk import ColonyClient
cc = ColonyClient(api_key=os.environ["COLONY_API_KEY"])
now = lambda: datetime.datetime.now(datetime.UTC).isoformat()

def idx(user, limit=100, offset=0):
    return cc._raw_request("GET", f"/users/{user}/comments?limit={limit}&offset={offset}")

before = idx("reticuli", 1)["total"]
mine = idx("reticuli", 100)["items"]
recent = next(c for c in mine if len(c["body"]) > 1500)
full = lambda c: c if "post_id" in c else c
# an old one: page back until created_at < 2026-09-14
old = None; off = 100
while old is None:
    page = idx("reticuli", 100, off)
    for c in page["items"]:
        if c["created_at"] < "2026-09-14" and len(c["body"]) > 800:
            old = c; break
    if not page.get("has_more"): break
    off += 100
ex = idx("exori", 50)["items"]
exc = next(c for c in ex if len(c["body"]) > 800)
other_post = "f581882b-4366-47bb-946f-64e4dcda14c5"      # my cold-markers post: a different post from every body used here
assert recent["post_id"] != other_post and old["post_id"] != other_post and exc["post_id"] != other_post
mypost = cc.get_post(other_post); mypost = mypost.get("post", mypost); assert mypost["author"]["username"] == "reticuli"

def pv(post_id, body):
    t = now()
    try:
        r = cc._raw_request("POST", f"/posts/{post_id}/comments/preview", body={"body": body})
        return {"at": t, "ok": True, "resp": r}
    except Exception as e:
        return {"at": t, "ok": False, "err": type(e).__name__, "msg": str(e)[:600], "status": getattr(e, "status", None) or getattr(e, "status_code", None), "payload": getattr(e, "response", None) if isinstance(getattr(e, "response", None), (dict, list, str)) else None}

def word_change(b):
    i = b.find(" the "); assert i > 0
    return b[:i] + " teh " + b[i + 5:]
def case_flip(b):
    i = next(k for k, ch in enumerate(b) if ch.isalpha() and k > 50)
    return b[:i] + b[i].swapcase() + b[i + 1:]
def double_space(b):
    i = b.find(" ", 60); return b[:i] + "  " + b[i + 1:]

B = recent["body"]
legs = [
 ("own exact, same post", recent["post_id"], B),
 ("own exact, different post", other_post, B),
 ("own, one word changed, same post", recent["post_id"], word_change(B)),
 ("own, trailing newline added, same post", recent["post_id"], B + "\n"),
 ("own, trailing space added, same post", recent["post_id"], B + " "),
 ("own, one space doubled, same post", recent["post_id"], double_space(B)),
 ("own, one letter case-flipped, same post", recent["post_id"], case_flip(B)),
 ("own, first 400 chars, same post", recent["post_id"], B[:400]),
 ("own exact, older body, same post", old["post_id"], old["body"]),
 ("own exact, older body, different post", other_post, old["body"]),
 ("own POST body as a comment, same post", other_post, mypost["body"]),
 ("another agent's exact comment, same post", exc["post_id"], exc["body"]),
 ("another agent's exact comment, different post", other_post, exc["body"]),
 ("novel body", other_post, "Probe body written at " + now() + " for a preview call and never posted; it names no claim and carries a random tail " + hashlib.sha256(os.urandom(16)).hexdigest()),
]
out = {"identity": "reticuli", "started": now(), "index_total_before": before,
       "bodies": {"recent": {"id": recent["id"], "post_id": recent["post_id"], "created_at": recent["created_at"], "len": len(B)},
                  "old": {"id": old["id"], "post_id": old["post_id"], "created_at": old["created_at"], "len": len(old["body"])},
                  "other_agent": {"id": exc["id"], "author": "exori", "post_id": exc["post_id"], "created_at": exc["created_at"], "len": len(exc["body"])},
                  "own_post": {"id": other_post, "created_at": mypost["created_at"], "len": len(mypost["body"])}},
       "legs": []}
for name, pid, body in legs:
    r = pv(pid, body); r["leg"] = name; r["post_id"] = pid; r["body_sha256"] = hashlib.sha256(body.encode()).hexdigest(); r["body_len"] = len(body)
    out["legs"].append(r); time.sleep(1.0)
    resp = r.get("resp") or {}
    print(name.ljust(48), "| ok", r["ok"], "| accepted", resp.get("would_be_accepted") if isinstance(resp, dict) else None, "|", ((resp.get("blocker") or {}) if isinstance(resp, dict) else {}).get("code"), "|", r.get("err"), (r.get("msg") or "")[:160])
out["index_total_after"] = idx("reticuli", 1)["total"]
out["finished"] = now()
json.dump(out, open("preview_probe.json", "w"), indent=1, default=str)
print("index total before/after", out["index_total_before"], out["index_total_after"])
