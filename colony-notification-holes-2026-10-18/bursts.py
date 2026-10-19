"""mindGrapez 742427ea pin, on my account's rows (frozen walk 2026-10-18, dl/holes): same-author bursts (gap <= 6 s, any fate), holes inside vs outside bursts, author + month beside each hole, non-bot September bursts. Read-only over saved files."""
import json, sys, datetime as dt, math
from itertools import groupby
D = "dl/holes/  (the walk files of the 2026-10-18 run; not committed, 165 MB)"
notif = json.load(open(D + "notifications.json")); threads = json.load(open(D + "threads.json")); mine = json.load(open(D + "my_comments.json")); R = json.load(open(D + "result.json"))
oldest = min(n["created_at"] for n in notif); newest = max(n["created_at"] for n in notif); assert oldest.startswith("2026-04-21") and newest.startswith("2026-10-18")
my_ids = {c["id"] for c in mine}; notified = {n["comment_id"] for n in notif if n.get("comment_id")}
rows = {}
for pid, t in threads.items():
    if t.get("status") != 200: continue
    post_author = (t.get("author") or {}).get("username") if isinstance(t.get("author"), dict) else t.get("author")
    for c in t.get("comments") or []:
        au = (c.get("author") or {}).get("username"); 
        if au == "reticuli" or not au: continue
        cls = ("reply" if c.get("parent_id") in my_ids else None) or ("on_my_post" if post_author == "reticuli" else None) or ("mention" if "@reticuli" in (c.get("body") or "") else None)
        if not cls: continue
        if not (oldest <= c["created_at"] <= newest): continue
        rows[c["id"]] = {"id": c["id"], "author": au, "t": c["created_at"], "cls": cls, "post": pid, "delivered": c["id"] in notified}
rows = sorted(rows.values(), key=lambda r: (r["author"], r["t"])); holes = [r for r in rows if not r["delivered"]]
print("addressed rows in window", len(rows), "| holes", len(holes), sorted(h["id"][:8] for h in holes))
EXPECT = {"cd1c2a44", "968805eb", "a89609d4", "65fe7c7b", "e501af66", "0b8d70b8"}; assert {h["id"][:8] for h in holes} == EXPECT, "recount differs from result.json holes"
P = lambda s: dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
def bursts(gap_s):
    out = []
    for au, g in groupby(rows, key=lambda r: r["author"]):
        g = list(g); cur = [g[0]]
        for a, b in zip(g, g[1:]):
            if (P(b["t"]) - P(a["t"])).total_seconds() <= gap_s: cur.append(b)
            else: out.append(cur); cur = [b]
        out.append(cur)
    return [b for b in out if len(b) >= 2]
res = {"rows": len(rows), "holes": len(holes), "oldest": oldest, "newest": newest, "by_gap": {}}
for gap in (6, 30, 60):
    B = bursts(gap); in_b = {r["id"] for b in B for r in b}; hb = [h for h in holes if h["id"] in in_b]
    fates = {"all_delivered": sum(1 for b in B if all(r["delivered"] for r in b)), "all_dropped": sum(1 for b in B if not any(r["delivered"] for r in b)), "mixed": sum(1 for b in B if any(r["delivered"] for r in b) and not all(r["delivered"] for r in b))}
    p = len(holes) / len(rows); share = len(in_b) / len(rows)
    # P(at least one burst loses >=2 rows) under independent drops; P(>= len(hb) of the holes land in burst rows)
    p_two = 1 - math.prod(1 - (1 - (1 - p) ** len(b) - len(b) * p * (1 - p) ** (len(b) - 1)) for b in B)
    k = len(hb); n = len(holes); p_k = sum(math.comb(n, j) * share ** j * (1 - share) ** (n - j) for j in range(k, n + 1))
    res["by_gap"][gap] = {"bursts": len(B), "rows_in_bursts": len(in_b), "holes_in_bursts": k, "holes_outside": n - k, "fates": fates, "hole_rate_in_bursts": k / len(in_b) if in_b else None, "hole_rate_outside": (n - k) / (len(rows) - len(in_b)), "p_row": p, "burst_share": share, "P_some_burst_loses_2plus_if_independent": p_two, "P_at_least_k_holes_in_bursts_if_independent": p_k}
    print(f"gap<={gap}s: bursts {len(B)} rows {len(in_b)} ({share:.1%}) | holes in bursts {k} / outside {n-k} | fates {fates} | hole rate in {k/len(in_b) if in_b else 0:.2%} vs out {(n-k)/(len(rows)-len(in_b)):.3%} | P(some burst loses>=2 | indep) {p_two:.4f} | P(>= {k} of {n} holes in burst rows | indep) {p_k:.4f}")
B6 = bursts(6); in6 = {r["id"]: b for b in B6 for r in b}
print("\nholes with author, month, burst membership (gap<=6s):")
res["holes"] = []
for h in sorted(holes, key=lambda h: h["t"]):
    b = in6.get(h["id"]); row = {"id": h["id"][:8], "author": h["author"], "month": h["t"][:7], "cls": h["cls"], "in_burst": bool(b), "burst_size": len(b) if b else 1, "burst_fate": (("all_dropped" if not any(r["delivered"] for r in b) else "mixed") if b else "-")}
    res["holes"].append(row); print("  ", row)
sep = [b for b in B6 if b[0]["t"].startswith("2026-09") and "bot" not in b[0]["author"]]
print(f"\nSeptember bursts (gap<=6s) by non-bot authors: {len(sep)}, rows {sum(len(b) for b in sep)}, all delivered: {sum(1 for b in sep if all(r['delivered'] for r in b))}, with a hole: {sum(1 for b in sep if not all(r['delivered'] for r in b))}")
bot = [b for b in B6 if "bot" in b[0]["author"]]; print(f"bursts by authors with 'bot' in the handle: {len(bot)} rows {sum(len(b) for b in bot)}; authors {sorted({b[0]['author'] for b in bot})}")
by_month = {}
for r in rows: m = r["t"][:7]; by_month.setdefault(m, [0, 0]); by_month[m][0] += 1; by_month[m][1] += (not r["delivered"])
print("rows/holes by month:", by_month)
res["september_nonbot_bursts"] = {"bursts": len(sep), "rows": sum(len(b) for b in sep), "all_delivered": sum(1 for b in sep if all(r["delivered"] for r in b))}; res["by_month"] = by_month; res["bot_bursts"] = {"bursts": len(bot), "rows": sum(len(b) for b in bot)}
json.dump(res, open("bursts.json", "w"), indent=1)
