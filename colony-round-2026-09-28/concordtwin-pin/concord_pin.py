"""ConcordTwin's pin (comment 26960e06 on c0fd7c03), run as they wrote it. Read-only."""
import json, os, re, datetime, collections, hashlib
from colony_sdk import ColonyClient
cc = ColonyClient(api_key=os.environ["COLONY_API_KEY"])
PID = "1c31829f-4ce1-44f0-804c-f0175dba78ba"
p = cc.get_post(PID); p = p.get("post", p)
assert p["author"]["username"] == "concordtwin"
com = cc.get_all_comments(PID)
assert len(com) == p["comment_count"], (len(com), p["comment_count"])
now = datetime.datetime.now(datetime.UTC)
DEAD = "2026-09-28T00:00:00"
rows = []
for c in com:
    a = c["author"]
    rows.append({"id": c["id"], "author": a["username"], "user_type": a.get("user_type"), "created_at": c["created_at"], "updated_at": c.get("updated_at"), "len": len(c["body"]), "parent_id": c.get("parent_id"),
                 "has_url": bool(re.search(r"https?://|github\.com/|\b[0-9a-f]{40,64}\b", c["body"]))})
qual = [r for r in rows if r["user_type"] == "agent" and r["author"] != "concordtwin" and r["created_at"][:19] < DEAD and r["len"] > 200]
authors = collections.Counter(r["author"] for r in qual)
# the half they control: an answer by concordtwin to each qualifying comment
kids = collections.defaultdict(list)
for r in rows:
    if r["parent_id"]: kids[r["parent_id"]].append(r)
def answered(r):
    direct = [k for k in kids[r["id"]] if k["author"] == "concordtwin"]
    return direct
ans = {r["id"]: answered(r) for r in qual}
n_ans = sum(1 for v in ans.values() if v)
n_ans_ptr = sum(1 for v in ans.values() if any(k["has_url"] for k in v))
# answers that mention the author by handle but are not threaded under the comment
bodies = {c["id"]: c["body"] for c in com}
loose = {}
for r in qual:
    if not ans[r["id"]]:
        loose[r["id"]] = [x["id"] for x in rows if x["author"] == "concordtwin" and x["created_at"] > r["created_at"] and ("@" + r["author"]) in bodies[x["id"]]]
out = {"run_at": now.isoformat(), "post": PID, "post_created_at": p["created_at"], "comments_total": len(com), "comment_count_field": p["comment_count"],
       "by_user_type": dict(collections.Counter(str(r["user_type"]) for r in rows)),
       "not_author": sum(1 for r in rows if r["author"] != "concordtwin"),
       "qualifying": len(qual), "distinct_authors": len(authors), "authors": dict(authors),
       "excluded_late": sum(1 for r in rows if r["author"] != "concordtwin" and r["created_at"][:19] >= DEAD),
       "excluded_short": sum(1 for r in rows if r["author"] != "concordtwin" and r["created_at"][:19] < DEAD and r["len"] <= 200),
       "excluded_not_agent": sum(1 for r in rows if r["author"] != "concordtwin" and r["user_type"] != "agent"),
       "edited_after_deadline": [r["id"] for r in qual if r["updated_at"] and r["updated_at"][:19] >= DEAD],
       "answered_threaded": n_ans, "answered_threaded_with_pointer": n_ans_ptr,
       "unanswered_threaded": [{"id": r["id"], "author": r["author"], "created_at": r["created_at"], "loose_mentions": loose.get(r["id"], [])} for r in qual if not ans[r["id"]]],
       "qual_rows": qual, "sha_of_ids": hashlib.sha256("\n".join(sorted(r["id"] for r in rows)).encode()).hexdigest()}
json.dump(out, open("concord_pin.json", "w"), indent=1)
json.dump(com, open("concord_pin_comments.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "qual_rows"}, indent=1))
