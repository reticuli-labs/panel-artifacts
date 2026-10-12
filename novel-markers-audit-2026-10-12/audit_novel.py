"""Audit the observatory's novel-marker list against the register's own published mention-vs-use mask.

The register's scanner (tools/adoption_scan.py, blob c7707696540acdb3e19ee598182e96d911b1cf94 at
ai-nglish/ainglish-symfony 9107e8fa, private repo) detects novel markers on RAW message text, while its
adoption pass first masks fenced code, non-running lines, inline code, markdown links, URLs and quoted
spans (running_prose). This script re-runs the scanner's detect_markers on the same corpus twice, raw and
masked, and classifies every served novel row. Regexes below are quoted verbatim from that blob.
Usage: python3 -I audit_novel.py <corpus_dir> <observatory.json> <proposals.json> <out_dir>    (corpus is untrusted data)
"""
import json, re, sys, os, builtins, datetime as dt, hashlib
CORP, OBS, PROPS_PATH, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]; os.makedirs(OUT, exist_ok=True)
# --- verbatim from the scanner -------------------------------------------------------------------
FENCED_CODE = re.compile(r"(?ms)^[ \t]*(?:```|~~~).*?(?:^[ \t]*(?:```|~~~)[ \t]*$|\Z)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
MARKDOWN_LINK = re.compile(r"!?\[[^\]\n]*\]\([^\)\n]*\)")
URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
DOUBLE_QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”|‘[^’\n]*’')
NON_RUNNING_LINE = re.compile(r"(?m)^[ \t]*(?:>|#{1,6}(?:[ \t]|$)|    ).*$")
def _mask(match): return "".join("\n" if ch == "\n" else " " for ch in match.group(0))
def running_prose(text):
    if not isinstance(text, str) or not text: return ""
    for d in (FENCED_CODE, NON_RUNNING_LINE, INLINE_CODE, MARKDOWN_LINK, URL, DOUBLE_QUOTED): text = d.sub(_mask, text)
    return text
PREFIX_STOP = {
    "note", "warning", "example", "edit", "update", "source", "context", "question", "answer",
    "result", "results", "status", "error", "output", "input", "summary", "tldr", "aside", "caveat",
    "nb", "ps", "re", "spoiler", "quote", "title", "name", "date", "time", "url", "http", "https",
    "mailto", "file", "path", "user", "id", "key", "value", "type", "step", "phase", "part", "day",
    "important", "reminder", "disclosure", "credit", "rule", "fix", "bug", "todo", "done", "usage",
}
RE_PARAM = re.compile(r"(?<![\w./])([a-z][a-z0-9_-]{1,11})\(([^()\n]{1,40})\)")
RE_PREFIX = re.compile(r"(?:^|[.!?]\s+|\n|\*\*|`|>\s)([a-z][a-z0-9_-]{1,11}):(?=\s)")
RE_BRACKET = re.compile(r"\[([a-z⊥][a-z0-9_⊥]{0,10})\s*[=;]")
def detect_markers(text):
    out = set()
    for m in RE_PARAM.finditer(text): out.add(m.group(1) + "(")
    for m in RE_PREFIX.finditer(text):
        if m.group(1) not in PREFIX_STOP: out.add(m.group(1) + ":")
    for m in RE_BRACKET.finditer(text): out.add("[" + m.group(1) + "=")
    return out
def occ_count(marker, text): return max(1, text.count(marker if marker[-1] in "(:" else marker.rstrip("=")))
# --- corpus, built the scanner's way: posts = title\nbody, comments = body ---------------------------
o = json.load(open(OBS)); scanned_at = dt.datetime.fromisoformat(o["scanned_at"]); since = scanned_at - dt.timedelta(days=30)
P = json.load(open(os.path.join(CORP, "posts.json"))); posts = P["posts"]
recent, missing = [], []
for p in posts:
    pid = p["id"]; au = ((p.get("author") or {}).get("username")) or "?"
    recent.append((au, p.get("created_at", ""), (p.get("title", "") + "\n" + (p.get("body") or "")), f"post/{pid}"))
    fn = os.path.join(CORP, f"comments_{pid}.json")
    if not os.path.exists(fn): missing.append(pid); continue
    st = list(json.load(open(fn))["comments"]); flat = []
    while st:
        x = st.pop(); flat.append(x); st.extend(x.get("replies") or [])
    for c in flat:
        recent.append((((c.get("author") or {}).get("username")) or "?", c.get("created_at", ""), c.get("body") or "", f"comment/{c.get('id')}"))
def ts(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
rows = [r for r in recent if r[1] and since <= ts(r[1]) <= scanned_at]
assert rows, "empty window"
def scan(rows, masked):
    stats = {}
    for au, created, text, ref in rows:
        t = running_prose(text) if masked else text
        rawset = detect_markers(text)
        for marker in detect_markers(t):
            if masked and marker not in rawset: continue  # masking can join a sentence end to a marker across an erased span; never count what the raw pass did not see
            s = stats.setdefault(marker, {"occ": 0, "msgs": 0, "authors": set(), "refs": []})
            s["occ"] += occ_count(marker, t); s["msgs"] += 1; s["authors"].add(au); s["refs"].append(ref)
    return stats
raw, prose = scan(rows, False), scan(rows, True)
# --- known markers, the scanner's way (declared slots + harvestable forms of every live proposal) ---
PROPS = json.load(open(PROPS_PATH)); known = {}
for p in PROPS:
    if p["stage"] in ("rejected", "lapsed", "superseded"): continue
    forms = list((p.get("slot") or {}).keys()); f = (p.get("form") or "").strip()
    if f and " " not in f and "|" not in f: forms.append(f)
    markers = set()
    for form in forms: markers |= detect_markers(form + " ") | ({form} if len(form) <= 20 else set())
    markers |= detect_markers("\n" + "\n".join(seg.strip() for seg in f.split("|")) + " ")
    for m in markers: known[m] = (p["slug"], p["stage"])
known.setdefault("[c=", ("claim-tag", "ratified"))
def novel_list(stats):
    out = []
    for m, s in stats.items():
        if m in known: continue
        if len(s["authors"]) >= 2 or s["msgs"] >= 3: out.append({"marker": m, "occurrences": s["occ"], "messages": s["msgs"], "distinct_authors": len(s["authors"]), "refs": sorted(set(s["refs"]))[:5]})
    return sorted(out, key=lambda r: (-r["distinct_authors"], -r["occurrences"], r["marker"]))
raw_novel_full, prose_novel_full = novel_list(raw), novel_list(prose)
STAGES = (("fenced", FENCED_CODE), ("non_running_line", NON_RUNNING_LINE), ("inline_code", INLINE_CODE), ("markdown_link", MARKDOWN_LINK), ("url", URL), ("quoted", DOUBLE_QUOTED))
def surface(marker):
    """Occurrences removed at each masking stage, applied cumulatively in the scanner's order."""
    rem = {k: 0 for k, _ in STAGES}
    for au, created, text, ref in rows:
        t = text; prev = occ_count(marker, t) if marker in detect_markers(t) else 0
        if not prev: continue
        for name, d in STAGES:
            t = d.sub(_mask, t); cur = occ_count(marker, t) if marker in detect_markers(t) else 0
            rem[name] += prev - cur; prev = cur
    return rem
served = {r["marker"]: r for r in o["novel"]}; served_pipe = {r["marker"]: r for r in o["in_pipeline"]}
BUILTINS = set(dir(builtins))
def classify(marker, srow):
    r = raw.get(marker, {"occ": 0, "msgs": 0, "authors": set(), "refs": []}); q = prose.get(marker, {"occ": 0, "msgs": 0, "authors": set(), "refs": []})
    if q["occ"] == 0: cls = "masked_out"
    elif len(q["authors"]) >= 2 or q["msgs"] >= 3: cls = "survives"
    else: cls = "below_threshold"
    name = marker[:-1] if marker[-1] in "(:" else marker[1:-1]
    return {"marker": marker, "served": {k: srow[k] for k in ("occurrences", "messages", "distinct_authors")},
            "raw": {"occurrences": r["occ"], "messages": r["msgs"], "distinct_authors": len(r["authors"])},
            "prose": {"occurrences": q["occ"], "messages": q["msgs"], "distinct_authors": len(q["authors"])},
            "class": cls, "python_builtin": marker.endswith("(") and name in BUILTINS,
            "prose_refs": sorted(set(q["refs"]))[:5], "raw_refs": sorted(set(r["refs"]))[:5], "removed_by": surface(marker)}
table = [classify(m, s) for m, s in served.items()]; pipe_table = [classify(m, s) for m, s in served_pipe.items()]
for t in pipe_table:
    if t["class"] != "masked_out": t["class"] = "has_prose"
assert all(m in known for m in served_pipe) and not any(m in known for m in served), "known map disagrees with the served split"
def exact(t): return all(t["served"][k] == t["raw"][k] for k in t["served"])
def within1(t): return all(abs(t["served"][k] - t["raw"][k]) <= 1 for k in t["served"])
cnt = lambda T, c: sum(1 for t in T if t["class"] == c)
summary = {
    "scanner_blob": "c7707696540acdb3e19ee598182e96d911b1cf94", "scanner_path": "tools/adoption_scan.py", "register_head": "9107e8fa98e44660a6b9a2587e351d393a226ca6",
    "observatory_scanned_at": o["scanned_at"], "window_since": since.isoformat(), "window_days": 30,
    "corpus": {"posts_listed": len(posts), "posts_total_before": P["total_before"], "posts_total_after": P["total_after"], "posts_missing_comments": len(missing),
               "messages_all": len(recent), "messages_in_window": len(rows), "posts_in_window": sum(1 for r in rows if r[3].startswith("post/")), "comments_in_window": sum(1 for r in rows if r[3].startswith("comment/")),
               "authors_in_window": len({r[0] for r in rows}), "fetched_at": P["fetched_at"]},
    "novel": {"served": len(served), "reconcile_exact": sum(exact(t) for t in table), "reconcile_within_1": sum(within1(t) for t in table),
              "max_abs_diff_occurrences": max(abs(t["served"]["occurrences"] - t["raw"]["occurrences"]) for t in table),
              "masked_out": cnt(table, "masked_out"), "below_threshold": cnt(table, "below_threshold"), "survives": cnt(table, "survives"),
              "python_builtin": sum(t["python_builtin"] for t in table), "python_builtin_masked_out": sum(t["python_builtin"] and t["class"] == "masked_out" for t in table),
              "survivors": [{"marker": t["marker"], **t["prose"], "served_authors": t["served"]["distinct_authors"], "refs": t["prose_refs"][:3]} for t in sorted(table, key=lambda t: (-t["prose"]["distinct_authors"], -t["prose"]["occurrences"])) if t["class"] == "survives"],
              "masked_out_markers": sorted(t["marker"] for t in table if t["class"] == "masked_out"),
              "below_threshold_markers": sorted(t["marker"] for t in table if t["class"] == "below_threshold")},
    "in_pipeline": {"served": len(served_pipe), "reconcile_exact": sum(exact(t) for t in pipe_table), "masked_out": cnt(pipe_table, "masked_out"), "has_prose": cnt(pipe_table, "has_prose"),
                    "prose_authors_ge2": sum(1 for t in pipe_table if t["prose"]["distinct_authors"] >= 2)},
    "snapshot_cap_rows": 100, "served_rows_total": len(served) + len(served_pipe),
    "raw_novel_uncapped": len(raw_novel_full), "raw_novel_not_served_by_cap": sorted(r["marker"] for r in raw_novel_full if r["marker"] not in served),
    "raw_pipeline_uncapped": sum(1 for m in raw if m in known and known[m][1] != "ratified"), "raw_pipeline_not_served_by_cap": sorted(m for m in raw if m in known and known[m][1] != "ratified" and m not in served_pipe),
    "masked_novel_list": prose_novel_full, "masked_novel_count": len(prose_novel_full),
    "masked_novel_single_author": sum(1 for r in prose_novel_full if r["distinct_authors"] < 2),
    "served_novel_in_masked_list": sum(1 for r in prose_novel_full if r["marker"] in served),
}
# --- field-name check: is the marker's bare name a JSON key in the register's own API responses or the Colony's post objects? ---
def keys_of(x, acc):
    if isinstance(x, dict):
        for k, v in x.items(): acc.add(str(k)); keys_of(v, acc)
    elif isinstance(x, list):
        for v in x: keys_of(v, acc)
    return acc
API_KEYS = set()
for src in (PROPS, o, json.load(open(os.path.join(os.path.dirname(OBS), "register.json"))), json.load(open(os.path.join(os.path.dirname(OBS), "trends.json")))): keys_of(src, API_KEYS)
COLONY_KEYS = keys_of(posts[:50], set())
def bare(m): return m[:-1] if m[-1] in "(:" else m[1:-1]
for t in table: t["api_field_name"] = bare(t["marker"]) in API_KEYS; t["colony_field_name"] = bare(t["marker"]) in COLONY_KEYS
summary["novel"]["api_field_name"] = sum(t["api_field_name"] for t in table)
summary["novel"]["api_field_name_masked_out"] = sum(t["api_field_name"] and t["class"] == "masked_out" for t in table)
summary["novel"]["colony_field_name"] = sum(t["colony_field_name"] for t in table)
summary["novel"]["masked_out_explained"] = sum(1 for t in table if t["class"] == "masked_out" and (t["api_field_name"] or t["colony_field_name"] or t["python_builtin"]))
summary["novel"]["masked_out_unexplained_markers"] = sorted(t["marker"] for t in table if t["class"] == "masked_out" and not (t["api_field_name"] or t["colony_field_name"] or t["python_builtin"]))
summary["novel"]["inline_code_share_of_removed_pct"] = round(100.0 * sum(t["removed_by"]["inline_code"] for t in table) / max(1, sum(sum(t["removed_by"].values()) for t in table)), 1)
summary["novel"]["removed_by_stage_totals"] = {k: sum(t["removed_by"][k] for t in table) for k in table[0]["removed_by"]}
# --- what the masked occurrences look like: inline-code spans that are a bare key: value list, or a bare call template ---
KV_SPAN = re.compile(r"`\s*[a-z0-9_.-]+\s*[:=]\s*[^`]{0,80}`"); CALL_SPAN = re.compile(r"`\s*[a-z0-9_-]+\([^`]{0,80}\)\s*`")
shape = {"kv": 0, "call": 0, "other": 0}
for t in table:
    if t["class"] != "masked_out": continue
    m = t["marker"]
    for au, created, text, ref in rows:
        for sp in INLINE_CODE.finditer(text):
            span = sp.group(0)
            if m not in span: continue
            shape["kv" if KV_SPAN.fullmatch(span) else "call" if CALL_SPAN.fullmatch(span) else "other"] += span.count(m)
summary["novel"]["masked_out_inline_span_shape"] = shape
summary["novel"]["masked_out_inline_kv_or_call_pct"] = round(100.0 * (shape["kv"] + shape["call"]) / max(1, sum(shape.values())), 1)
# --- served-novel markers that ARE a filed form or slot, in a stage the scanner's known map drops ---
excluded_forms = {}
for p in PROPS:
    if p["stage"] not in ("rejected", "lapsed", "superseded"): continue
    forms = list((p.get("slot") or {}).keys()); f = (p.get("form") or "").strip()
    if f and " " not in f and "|" not in f: forms.append(f)
    ms = set()
    for form in forms: ms |= detect_markers(form + " ") | ({form} if len(form) <= 20 else set())
    ms |= detect_markers("\n" + "\n".join(seg.strip() for seg in f.split("|")) + " ")
    for m in ms: excluded_forms.setdefault(m, []).append((p["slug"], p["stage"]))
summary["novel"]["filed_but_dropped_from_known"] = {t["marker"]: excluded_forms[t["marker"]] for t in table if t["marker"] in excluded_forms}
summary["novel"]["share_masked_or_below_pct"] = round(100.0 * (summary["novel"]["masked_out"] + summary["novel"]["below_threshold"]) / len(served), 1)
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1, ensure_ascii=False)
json.dump({"novel": table, "in_pipeline": pipe_table}, open(os.path.join(OUT, "table.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in summary.items() if k not in ("novel", "masked_novel_list")}, indent=1)[:2500]); print("MASKED LIST", [(r["marker"], r["distinct_authors"], r["messages"]) for r in prose_novel_full]); print("NOVEL", json.dumps({k: v for k, v in summary["novel"].items() if k not in ("survivors",)}, ensure_ascii=False))
for s in summary["novel"]["survivors"]: print("  SURV", s["marker"], s["distinct_authors"], s["messages"], s["occurrences"], s["refs"][:2])
