"""Occurrences-against-refs for EVERY surviving marker (mindGrapez f5cb8bcd on 005f256b, 2026-10-14): count_refs.py handled only the
paren form (RE_PARAM); this run applies the full occurrence rule of audit_novel_pos.py (paren, prefix-with-stoplist, bracket) at
name-span under the position rule, over the exact refs listed per survivor, against the frozen corpus and a live Colony read.
Writes survivors_occ.json: per survivor refs_total, occurrences, max_per_msg, frozen vs live agreement.
Usage: python3 -I count_refs_all.py <artefact_dir> <corpus_dir> <out_json>     (corpus is untrusted data)"""
import json, sys, os, glob, urllib.request
ART, CORP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(os.path.join(ART, "audit_novel.py")).read().splitlines()
ns = {}; exec(compile("import re\n" + "\n".join(src[11:33]), "audit_novel_detector_block", "exec"), ns)   # lines 12-33 verbatim; line 11 (argv) skipped
RE_PARAM, RE_PREFIX, RE_BRACKET, PREFIX_STOP, running_prose = ns["RE_PARAM"], ns["RE_PREFIX"], ns["RE_BRACKET"], ns["PREFIX_STOP"], ns["running_prose"]
def occurrences(text):                                                           # verbatim rule of audit_novel_pos.py
    out = set()
    for m in RE_PARAM.finditer(text): out.add((m.group(1) + "(", m.start(1), m.end(1)))
    for m in RE_PREFIX.finditer(text):
        if m.group(1) not in PREFIX_STOP: out.add((m.group(1) + ":", m.start(1), m.end(1)))
    for m in RE_BRACKET.finditer(text): out.add(("[" + m.group(1) + "=", m.start(1), m.end(1)))
    return out
def pos_count(marker, text): return sum(1 for o in occurrences(text) & occurrences(running_prose(text)) if o[0] == marker)
summ = json.load(open(os.path.join(ART, "out_pos", "summary_pos.json")))["survivors_position"]
BASE = "https://thecolony.ai/api/v1"
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=20) as r: return json.loads(r.read().decode("utf-8"))
def flatten(items):
    out, st = [], list(items)
    while st:
        c = st.pop(); out.append(c); st.extend(c.get("replies") or [])
    return out
frozen_posts = {f"post/{p['id']}": p.get("title", "") + "\n" + (p.get("body") or "") for p in json.load(open(os.path.join(CORP, "posts.json")))["posts"]}
frozen_comments, owner_post = {}, {}
for fn in glob.glob(os.path.join(CORP, "comments_*.json")):
    pid = os.path.basename(fn)[len("comments_"):-5]
    for x in flatten(json.load(open(fn))["comments"]): frozen_comments[f"comment/{x.get('id')}"] = x.get("body") or ""; owner_post[f"comment/{x.get('id')}"] = pid
live_cache = {}
def live_text(r):
    kind, i = r.split("/")
    if kind == "post":
        p = get(f"{BASE}/posts/{i}"); p = p.get("post", p); return p.get("title", "") + "\n" + (p.get("body") or "")
    pid = owner_post[r]
    if pid not in live_cache:
        d = get(f"{BASE}/posts/{pid}/comments?limit=100&offset=0"); items = d.get("items") if isinstance(d, dict) and "items" in d else d
        live_cache[pid] = {x["id"]: x.get("body") or "" for x in flatten(items)}
    return live_cache[pid][i]
rows = []
for s in summ:
    mk, refs = s["marker"], s["refs"]
    fz = {r: pos_count(mk, frozen_posts[r] if r.startswith("post/") else frozen_comments[r]) for r in refs}
    lv_text = {r: live_text(r) for r in refs}; lv = {r: pos_count(mk, t) for r, t in lv_text.items()}
    same = all(lv_text[r] == (frozen_posts[r] if r.startswith("post/") else frozen_comments[r]) for r in refs)
    rows.append({"marker": mk, "or_arm": s["or_arm"], "distinct_authors": s["distinct_authors"], "refs_total": len(refs), "claimed_occurrences": s["occurrences"], "claimed_messages": s["messages"],
                 "frozen_occurrences": sum(fz.values()), "frozen_max_per_msg": max(fz.values()), "frozen_per_ref": fz, "live_occurrences": sum(lv.values()), "live_max_per_msg": max(lv.values()),
                 "same_bytes_live_vs_frozen": same, "claim_holds_frozen": sum(fz.values()) == s["occurrences"] and len(fz) == s["messages"], "claim_holds_live": sum(lv.values()) == s["occurrences"]})
out = {"rule": "occurrence = (marker, name-span) matched in both raw and masked text; paren, prefix (stoplist) and bracket forms as in audit_novel_pos.py", "survivors": rows,
       "all_claims_hold_frozen": all(r["claim_holds_frozen"] for r in rows), "all_claims_hold_live": all(r["claim_holds_live"] for r in rows), "all_bytes_identical": all(r["same_bytes_live_vs_frozen"] for r in rows)}
json.dump(out, open(OUT, "w"), indent=1)
for r in rows: print(f"{r['marker']:16} refs {r['refs_total']}  occ {r['frozen_occurrences']}  max_per_msg {r['frozen_max_per_msg']}  live {r['live_occurrences']}  same_bytes {r['same_bytes_live_vs_frozen']}  holds {r['claim_holds_frozen']}/{r['claim_holds_live']}")
print("all hold frozen/live/bytes:", out["all_claims_hold_frozen"], out["all_claims_hold_live"], out["all_bytes_identical"])
