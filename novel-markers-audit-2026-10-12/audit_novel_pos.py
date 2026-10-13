"""Position-intersection re-run of the novel-marker audit (Saturnia 7f434b6a on 005f256b).
The first audit kept a masked-text match whenever its marker NAME was in the raw detected set; that lets masking
create a new boundary for a name that the raw pass saw elsewhere in the same message. Here an occurrence is
(marker, name-span) and survives only if the same span is matched in both the raw and the masked text (masking
preserves length, so spans are comparable). Usage: python3 -I audit_novel_pos.py <corpus_dir> <observatory.json> <proposals.json> <out_dir>"""
import json, re, sys, os, builtins, datetime as dt
sys.argv, OUT = sys.argv[:1] + sys.argv[1:4] + [None], sys.argv[4]; os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_novel.py")).read()
# reuse the scanner-verbatim block (regexes, mask, PREFIX_STOP, detect_markers) and the corpus/known-map build, without re-running the old scans
head = src.split("def occ_count")[0]; exec(compile(head.replace('CORP, OBS, PROPS_PATH, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]; os.makedirs(OUT, exist_ok=True)', 'CORP, OBS, PROPS_PATH = sys.argv[1], sys.argv[2], sys.argv[3]'), "audit_head", "exec"))
def occurrences(text):
    out = set()
    for m in RE_PARAM.finditer(text): out.add((m.group(1) + "(", m.start(1), m.end(1)))
    for m in RE_PREFIX.finditer(text):
        if m.group(1) not in PREFIX_STOP: out.add((m.group(1) + ":", m.start(1), m.end(1)))
    for m in RE_BRACKET.finditer(text): out.add(("[" + m.group(1) + "=", m.start(1), m.end(1)))
    return out
# --- Saturnia's five-case fixture, asserted before any corpus is read ---------------------------------
def counts(text):
    raw, masked = occurrences(text), occurrences(running_prose(text))
    name_guard = {o for o in masked if o[0] in {r[0] for r in raw}}          # the first audit's rule
    pos = raw & masked                                                            # this audit's rule
    return len(name_guard), len(pos)
witness = "`stance: quoted`\nDone. `aside` stance: neutral"
assert counts("Plain. stance: quoted") == (1, 1), counts("Plain. stance: quoted")
assert counts("`stance: quoted`") == (0, 0)
assert counts("Done. `aside` stance: neutral") == (0, 0), "a new boundary without a same-name raw hit"
assert counts(witness) == (1, 0), counts(witness)
assert counts("Real. stance: quoted\n" + witness) == (2, 1), counts("Real. stance: quoted\n" + witness)
# --- corpus window, exactly as the first audit built it ----------------------------------------------------
o = json.load(open(OBS)); scanned_at = dt.datetime.fromisoformat(o["scanned_at"]); since = scanned_at - dt.timedelta(days=30)
P = json.load(open(os.path.join(CORP, "posts.json"))); posts = P["posts"]; recent = []
for p in posts:
    pid = p["id"]; au = ((p.get("author") or {}).get("username")) or "?"
    recent.append((au, p.get("created_at", ""), (p.get("title", "") + "\n" + (p.get("body") or "")), f"post/{pid}"))
    fn = os.path.join(CORP, f"comments_{pid}.json")
    if not os.path.exists(fn): continue
    st = list(json.load(open(fn))["comments"]); flat = []
    while st:
        x = st.pop(); flat.append(x); st.extend(x.get("replies") or [])
    for c in flat: recent.append((((c.get("author") or {}).get("username")) or "?", c.get("created_at", ""), c.get("body") or "", f"comment/{c.get('id')}"))
ts = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
rows = [r for r in recent if r[1] and since <= ts(r[1]) <= scanned_at]; assert len(rows) == 1667, len(rows)
def scan(rule):
    stats = {}
    for au, created, text, ref in rows:
        raw, masked = occurrences(text), occurrences(running_prose(text))
        if rule == "raw": keep = raw
        elif rule == "name_guard": keep = {o for o in masked if o[0] in {r[0] for r in raw}}
        else: keep = raw & masked
        per = {}
        for mk, a, b in keep: per[mk] = per.get(mk, 0) + 1
        for mk, n in per.items():
            s = stats.setdefault(mk, {"occ": 0, "msgs": 0, "authors": set(), "refs": []}); s["occ"] += n; s["msgs"] += 1; s["authors"].add(au); s["refs"].append(ref)
    return stats
R, G, X = scan("raw"), scan("name_guard"), scan("position")
served = {r["marker"]: r for r in o["novel"]}; BUILTINS = set(dir(builtins))
_pt = json.load(open(os.path.join(os.path.dirname(OUT.rstrip("/")) or ".", "out", "table.json")))
_pt = _pt.get("novel") if isinstance(_pt, dict) else _pt
prev = {t["marker"]: t for t in _pt}
def cls(s):
    if s is None or s["occ"] == 0: return "masked_out"
    return "survives" if (len(s["authors"]) >= 2 or s["msgs"] >= 3) else "below_threshold"
def arm(s):
    a = len(s["authors"]) >= 2; m = s["msgs"] >= 3
    return "both" if a and m else ("authors" if a else ("messages" if m else "none"))
table = []
for mk, srow in served.items():
    g, x, r = G.get(mk), X.get(mk), R.get(mk)
    row = {"marker": mk, "served": {k: srow[k] for k in ("occurrences", "messages", "distinct_authors")},
           "raw_regex": None if r is None else {"occurrences": r["occ"], "messages": r["msgs"], "distinct_authors": len(r["authors"])},
           "name_guard": None if g is None else {"occurrences": g["occ"], "messages": g["msgs"], "distinct_authors": len(g["authors"])},
           "position": None if x is None else {"occurrences": x["occ"], "messages": x["msgs"], "distinct_authors": len(x["authors"]), "or_arm": arm(x), "refs": sorted(set(x["refs"])), "refs_total": len(set(x["refs"]))},
           "class_name_guard": cls(g), "class_position": cls(x), "class_first_audit": prev[mk]["class"], "python_builtin": mk.endswith("(") and mk[:-1] in BUILTINS}
    table.append(row)
changed = [t for t in table if t["class_position"] != t["class_name_guard"]]
guard_vs_first = [t for t in table if t["class_name_guard"] != t["class_first_audit"]]
cnt = lambda key, c: sum(1 for t in table if t[key] == c)
summary = {"rule": "occurrence = (marker, name-span); survives iff matched at the same span in raw and masked text", "fixture": "Saturnia 7f434b6a five cases asserted at start",
           "served": len(table), "messages_in_window": len(rows),
           "name_guard": {"masked_out": cnt("class_name_guard", "masked_out"), "below_threshold": cnt("class_name_guard", "below_threshold"), "survives": cnt("class_name_guard", "survives")},
           "position": {"masked_out": cnt("class_position", "masked_out"), "below_threshold": cnt("class_position", "below_threshold"), "survives": cnt("class_position", "survives")},
           "class_changed_markers": [(t["marker"], t["class_name_guard"], t["class_position"]) for t in changed],
           "name_guard_vs_first_audit_disagreements": [(t["marker"], t["class_first_audit"], t["class_name_guard"]) for t in guard_vs_first],
           "occurrence_definition_note": "the first audit counted occurrences by string count (text.count); this run counts regex matches, so occurrence totals differ while the class only depends on >0 / authors / messages",
           "survivors_position": [{"marker": t["marker"], **t["position"]} for t in table if t["class_position"] == "survives"],
           "occurrences_lost_to_position_rule": sum((t["name_guard"]["occurrences"] if t["name_guard"] else 0) - (t["position"]["occurrences"] if t["position"] else 0) for t in table)}
json.dump(table, open(os.path.join(OUT, "table_pos.json"), "w"), indent=1); json.dump(summary, open(os.path.join(OUT, "summary_pos.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in summary.items() if k != "survivors_position"}, indent=1)); print("survivors:", [(s["marker"], s["distinct_authors"], s["messages"], s["or_arm"]) for s in summary["survivors_position"]])
