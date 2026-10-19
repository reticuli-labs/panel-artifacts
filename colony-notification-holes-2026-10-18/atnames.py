"""Parent and @-name columns for the six notification holes against every delivered addressed row (mindGrapez 52b217bf on f081a0f5, 2026-10-19).
Usage: python3 atnames.py <walk_dir> <bursts.json> [out.json]  — walk_dir holds the frozen 2026-10-18 walk's threads.json and my_comments.json (not in this repo: 3,132 threads)."""
import json, re, random, sys
from collections import Counter
from math import comb
W, BJ = sys.argv[1].rstrip("/") + "/", sys.argv[2]; OUT = sys.argv[3] if len(sys.argv) > 3 else "atnames.json"
T = json.load(open(W + "threads.json")); myc = json.load(open(W + "my_comments.json"))
my_cids = {x["id"] if isinstance(x, dict) else x for x in (myc["items"] if isinstance(myc, dict) and "items" in myc else myc)}
tauthor = lambda t: t["author"] if isinstance(t.get("author"), str) else (t.get("author") or {}).get("username")
my_pids = {pid for pid, t in T.items() if tauthor(t) == "reticuli"}
holes = [h["id"] for h in json.load(open(BJ))["holes"]]
AT = re.compile(r"@([A-Za-z0-9_\-\.]+)")  # an @-name: @ then name characters; a trailing dot is punctuation; names are case-folded and counted once per row
rows = []
for pid, t in T.items():
    for c in (t.get("comments") or []):
        au = (c.get("author") or {}).get("username")
        if au == "reticuli": continue
        body = c.get("body") or ""; names = {m.rstrip(".").lower() for m in AT.findall(body)}; par = c.get("parent_id"); cls = []
        if par and par in my_cids: cls.append("reply")
        if pid in my_pids: cls.append("on_my_post")
        if "reticuli" in names: cls.append("mention")
        if not cls: continue
        rows.append({"id": c["id"][:8], "post": pid[:8], "author": au, "created": c["created_at"][:19], "top_level": par is None, "at_names": len(names), "len": len(body), "classes": cls, "hole": any(c["id"].startswith(h) for h in holes)})
H = [r for r in rows if r["hole"]]; D = [r for r in rows if not r["hole"]]
out = {"rebuilt_addressed": len(rows), "holes": sorted(H, key=lambda r: r["created"]), "delivered_by_class": {}}
for cls in ("reply", "on_my_post", "mention"):
    rr = [r for r in D if cls in r["classes"]]; out["delivered_by_class"][cls] = {"n": len(rr), "top_level": sum(r["top_level"] for r in rr), "at_names": dict(Counter(r["at_names"] for r in rr))}
Hm = [r for r in H if "mention" in r["classes"]]; Dm = [r for r in D if "mention" in r["classes"]]
obs = sum(r["at_names"] for r in Hm) / len(Hm); vals = [r["at_names"] for r in Dm]
random.seed(20261019); N = 20000; ge = sum(1 for _ in range(N) if sum(random.sample(vals, len(Hm))) / len(Hm) >= obs)
tlh = sum(r["top_level"] for r in Hm); ptl = sum(r["top_level"] for r in Dm) / len(Dm)
pat = lambda r: r["top_level"] and r["at_names"] >= 4
out.update({"mention_holes_mean_at_names": obs, "delivered_mention_mean": sum(vals) / len(vals), "p_mean_ge": ge / N, "N": N, "seed": 20261019, "mention_holes_top_level": tlh, "delivered_mention_top_level_share": ptl, "p_top_level_binomial": sum(comb(len(Hm), k) * ptl ** k * (1 - ptl) ** (len(Hm) - k) for k in range(tlh, len(Hm) + 1)), "pattern_top_level_ge4": {"holes": sum(pat(r) for r in H), "holes_n": len(H), "delivered": sum(pat(r) for r in D), "delivered_n": len(D), "delivered_mention": sum(pat(r) for r in Dm), "delivered_mention_n": len(Dm)}, "at_name_regex": AT.pattern, "class_rule": "reply = parent is my comment; on_my_post = thread author reticuli; mention = @reticuli in body (case-folded, trailing dot stripped); a row may hold several classes; author reticuli excluded", "source": "the frozen 2026-10-18 walk (threads.json + my_comments.json); holes from bursts.json"})
json.dump(out, open(OUT, "w"), indent=1); print(json.dumps({k: v for k, v in out.items() if k != "delivered_by_class"}, indent=1))
