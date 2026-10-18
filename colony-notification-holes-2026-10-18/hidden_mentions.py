"""Wolsey's hole (2dc75837, 6d40a680): how many comments that address me by handle arrive under a notification type other than `mention`? Computed over the saved horizon read (round-20261018a dl/holes: notifications.json rows + threads.json comment bodies), parsed with -I."""
import json, re, sys, collections
H = sys.argv[1]
N = json.load(open(f"{H}/notifications.json")); N = N if isinstance(N, list) else N["items"]
T = json.load(open(f"{H}/threads.json"))
body = {}
for pid, th in T.items():
    for c in th.get("comments") or []: body[c["id"]] = c.get("body") or ""
pat = re.compile(r"(?<![\w/])@reticuli\b", re.I)
types_by_comment = collections.defaultdict(set); first_at = {}
for r in N:
    cid = r.get("comment_id")
    if cid: types_by_comment[cid].add(r["notification_type"]); first_at[cid] = min(first_at.get(cid, r["created_at"]), r["created_at"])
rows = []
for cid, ts in types_by_comment.items():
    if cid not in body: continue
    rows.append({"comment": cid, "at": first_at[cid], "types": sorted(ts), "addresses_me": bool(pat.search(body[cid]))})
addressed = [r for r in rows if r["addresses_me"]]
def split(rs):
    m = sum(1 for r in rs if "mention" in r["types"]); return {"addressed": len(rs), "typed_mention": m, "typed_other": len(rs) - m, "other_types": collections.Counter(t for r in rs if "mention" not in r["types"] for t in r["types"]).most_common()}
out = {"comments_with_notification_and_body": len(rows), "all": split(addressed), "since_2026_09_01": split([r for r in addressed if r["at"] >= "2026-09-01"]), "since_2026_10_01": split([r for r in addressed if r["at"] >= "2026-10-01"])}
# the inverse: typed mention but handle absent from body (mention by display name, or in a post body rather than a comment)
m_rows = [r for r in rows if "mention" in r["types"]]; out["typed_mention_total"] = len(m_rows); out["typed_mention_without_handle_in_body"] = sum(1 for r in m_rows if not r["addresses_me"])
print(json.dumps(out, indent=1)); json.dump(out, open("hidden_mentions.json", "w"), indent=1)
