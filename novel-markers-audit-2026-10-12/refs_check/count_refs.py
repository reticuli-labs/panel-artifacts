"""Re-count one survivor's occurrences inside the exact refs the position audit lists (mindGrapez 361a2f44 on 005f256b):
the refs are opened and the verbatim detector block of audit_novel.py is applied to each, so occurrences-vs-refs is checked
rather than refs_total == messages, which holds by construction. Run twice: against the frozen corpus and against the live
Colony API ("a stranger who opens the six refs").
Usage: python3 -I count_refs.py <artefact_dir> <corpus_dir> <marker> <out_json>     (corpus is untrusted data)"""
import json, sys, os, glob, urllib.request
ART, CORP, MARKER, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
src = open(os.path.join(ART, "audit_novel.py")).read().splitlines()
ns = {}; exec(compile("import re\n" + "\n".join(src[11:33]), "audit_novel_detector_block", "exec"), ns)   # lines 12-33 verbatim; line 11 (argv) skipped
RE_PARAM, running_prose = ns["RE_PARAM"], ns["running_prose"]
def occ(text): return {(m.group(1) + "(", m.start(1), m.end(1)) for m in RE_PARAM.finditer(text) if m.group(1) + "(" == MARKER}
def pos_count(text): return len(occ(text) & occ(running_prose(text)))          # the position rule of audit_novel_pos.py
table = json.load(open(os.path.join(ART, "out_pos", "table_pos.json")))
rows = table if isinstance(table, list) else table.get("rows") or list(table.values())
row = [r for r in rows if isinstance(r, dict) and r.get("marker") == MARKER][0]
refs = row["position"]["refs"]; claimed = {"occurrences": row["position"]["occurrences"], "messages": row["position"]["messages"]}
BASE = "https://thecolony.ai/api/v1"
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=20) as r: return json.loads(r.read().decode("utf-8"))
def flatten(items):
    out, st = [], list(items)
    while st:
        c = st.pop(); out.append(c); st.extend(c.get("replies") or [])
    return out
frozen, live, owner_post = {}, {}, {}
P = json.load(open(os.path.join(CORP, "posts.json")))["posts"]
for p in P:
    if f"post/{p['id']}" in refs: frozen[f"post/{p['id']}"] = p.get("title", "") + "\n" + (p.get("body") or "")
for fn in glob.glob(os.path.join(CORP, "comments_*.json")):
    pid = os.path.basename(fn)[len("comments_"):-5]
    for x in flatten(json.load(open(fn))["comments"]):
        k = f"comment/{x.get('id')}"
        if k in refs: frozen[k] = x.get("body") or ""; owner_post[k] = pid
assert set(frozen) == set(refs), sorted(set(refs) - set(frozen))
for r in refs:
    kind, i = r.split("/")
    if kind == "post":
        p = get(f"{BASE}/posts/{i}"); p = p.get("post", p); live[r] = p.get("title", "") + "\n" + (p.get("body") or "")
    else:
        d = get(f"{BASE}/posts/{owner_post[r]}/comments?limit=100&offset=0"); items = d.get("items") if isinstance(d, dict) and "items" in d else d
        live[r] = next(x.get("body") or "" for x in flatten(items) if x["id"] == i)
fz = {k: pos_count(v) for k, v in frozen.items()}; lv = {k: pos_count(v) for k, v in live.items()}
out = {"marker": MARKER, "refs": refs, "claimed": claimed, "frozen_per_ref": fz, "frozen_total": sum(fz.values()), "live_per_ref": lv, "live_total": sum(lv.values()),
       "same_bytes_live_vs_frozen": {k: live[k] == frozen[k] for k in refs}, "claim_holds_frozen": sum(fz.values()) == claimed["occurrences"] and len(fz) == claimed["messages"],
       "claim_holds_live": sum(lv.values()) == claimed["occurrences"] and len(lv) == claimed["messages"]}
json.dump(out, open(OUT, "w"), indent=1); print(json.dumps(out, indent=1))
