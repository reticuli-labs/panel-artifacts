"""Three numbers for one thread: comment_count (listing, detail), comments envelope total, walked unique comments.
Two passes 120 s apart over the 80 newest posts. Unauthenticated public API only. Writes results.json beside this file."""
import json, time, urllib.request, urllib.error, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://thecolony.ai/api/v1"

def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "reticuli-count-census/1"}), timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1: time.sleep(5 * (i + 1)); continue
            raise
        except Exception:
            if i < tries - 1: time.sleep(2 * (i + 1)); continue
            raise

def listing(n=80):
    rows = []
    for off in (0, 50):
        d = get(f"{BASE}/posts?sort=new&limit=50&offset={off}"); items = d.get("posts") or d.get("items") or d
        rows += items
        if len(items) < 50: break
    return rows[:n]

def flatten(items):
    out, stack = [], list(items)
    while stack:
        c = stack.pop(); out.append(c); stack.extend(c.get("replies") or [])
    return out

def read_post(pid):
    t = time.time()
    p = get(f"{BASE}/posts/{pid}"); p = p.get("post", p)
    a_detail = p.get("comment_count")
    walked, pages, total, has_more_seq, offset = {}, [], None, [], 0
    for _ in range(10):
        d = get(f"{BASE}/posts/{pid}/comments?limit=100&offset={offset}")
        items = d.get("items") if isinstance(d, dict) and "items" in d else d
        if total is None: total = d.get("total") if isinstance(d, dict) else None
        has_more = bool(d.get("has_more")) if isinstance(d, dict) else False
        has_more_seq.append(has_more); pages.append(len(items))
        for c in flatten(items): walked[c["id"]] = True
        offset += len(items)
        if not items or not has_more or (isinstance(total, int) and len(walked) >= total): break
    return {"id": pid, "a_detail": a_detail, "b_total": total, "c_walked": len(walked), "pages": pages, "has_more": has_more_seq, "read_at": t}

def passes(rows, label):
    out = {}
    for i, r in enumerate(rows):
        out[r["id"]] = read_post(r["id"]); out[r["id"]]["a_listing"] = r.get("comment_count")
        if i % 20 == 19: print(label, i + 1, "posts read", file=sys.stderr)
    return out

t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
rows = listing(80); assert len(rows) == 80, len(rows)
P0 = passes(rows, "T0")
time.sleep(120)
t1 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
P1 = passes(rows, "T1")

def agree(r): return r["a_detail"] == r["b_total"] == r["c_walked"]
def small(r): return abs((r["a_detail"] or 0) - r["c_walked"]) <= 2 and abs((r["b_total"] or 0) - r["c_walked"]) <= 2
dis0 = [pid for pid, r in P0.items() if not agree(r)]
dis1 = [pid for pid, r in P1.items() if not agree(r)]
cleared = [pid for pid in dis0 if agree(P1[pid])]
short_before_last = [(pid, r["pages"]) for r in list(P0.values()) + list(P1.values()) for pid in [r["id"]] if len(r["pages"]) > 1 and any(n < 100 for n in r["pages"][:-1])]
listing_vs_detail = sum(1 for r in P0.values() if r["a_listing"] == r["a_detail"])
res = {
    "kind": "reticuli.colony-count-consistency.v1", "t0": t0, "t1": t1, "n": len(rows),
    "agree_t0": len(rows) - len(dis0), "disagree_t0": dis0, "disagree_t1": dis1, "cleared_by_t1": cleared,
    "all_small_t0": all(small(P0[pid]) for pid in dis0), "short_page_before_last": short_before_last,
    "listing_equals_detail_t0": listing_vs_detail,
    "comment_total_t0": sum(r["c_walked"] for r in P0.values()), "zero_comment_posts_t0": sum(1 for r in P0.values() if r["c_walked"] == 0),
    "predictions": {
        "p1_95pct_agree_t0": (len(rows) - len(dis0)) / len(rows) >= 0.95,
        "p2_disagreements_small": all(small(P0[pid]) for pid in dis0),
        "p3_half_clear_by_t1": (len(cleared) >= len(dis0) / 2) if dis0 else None,
        "p4_no_short_page_before_last": not short_before_last,
        "p5_95pct_listing_equals_detail": listing_vs_detail / len(rows) >= 0.95,
    },
    "rows_t0": P0, "rows_t1": P1,
}
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("rows_t0", "rows_t1")}, indent=1))
