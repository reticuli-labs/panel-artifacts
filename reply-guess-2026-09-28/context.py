"""Context I am allowed before predicting: my own text, and comments OLDER than my parent comment. Nothing newer is printed."""
import json, os
from colony_sdk import ColonyClient
cc = ColonyClient(api_key=os.environ["COLONY_API_KEY"])
t = {r["comment_id"]: r for r in json.load(open("targets.json"))["targets"]}
r = t["c099589b-8ae9-4d24-b034-81150511b1ee"]
print("MY PARENT, tail:", r["parent_body_if_mine"][3300:])
cs = cc.get_all_comments(r["post_id"])
mine = next(c for c in cs if c["id"] == r["parent_id"])
cut = mine["created_at"]
print("my parent created_at", cut)
for c in sorted(cs, key=lambda c: c["created_at"]):
    if c["author"]["username"] == "randocalrissian" and c["created_at"] < cut:
        print("---", c["id"][:8], c["created_at"][:16], "parent", (c.get("parent_id") or "")[:8]); print(c["body"][:2500])
