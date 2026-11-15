"""consequence_sweep.py: read-only, no network. Run with python3 -I (the bank files are downloads).
For every reader-panel measurement of MINE (the 57 of my_rows_sweep.json, 2026-11-14), load its pinned bank from the October
cache or from yesterday's extra banks and print what the scored items ASK: the question stems with their counts, whether an
abstaining option (cannot tell, not specified, ...) is offered and how often it is the key, and one sample item.
It classifies nothing by itself. The class looked for (found on 2026-11-15 in my bank for 7200b173, after Dexagon's correction of
396935c2): a question about a resulting state of the world whose key is a concrete state that the messages do not establish,
with an abstaining option offered and never keyed. The judgement is made by reading this output; the reading is in sweep_read.json.
Arguments: 1 = the October cache directory, 2 = yesterday's round directory, 3 = output json."""
import collections, json, os, re, sys
CACHE, Y, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
I = json.load(open(os.path.join(CACHE, "bank_index.json"))); paths = {b["bank_id"]: os.path.join(CACHE, b["path"]) for b in I["banks"] if b.get("path")}
for f in ("sweep_extra.json", "sweep_extra2.json"):
    for e in json.load(open(os.path.join(Y, f))): paths[e["bank_id"]] = e["path"]
MINE = json.load(open(os.path.join(Y, "my_rows_sweep.json")))["mine"]; assert len(MINE) == 57
ROWS = {r["manifest_hash"]: r for r in json.load(open(os.path.join(CACHE, "comp_measurements.json")))}
ABST = re.compile(r"cannot tell|can't tell|not specified|unspecified|not stated|does not say|doesn't say|cannot be determined|not determinable|unclear|not enough information|no way to know|leaves .* open|unknown", re.I)


def is_cal(it): return bool(it.get("calibration")) or bool(it.get("control")) or it.get("kind") == "calibration" or "calibration_construct" in it or "calibration_truth" in it or it.get("key_class") == "calibration"
def stem(q): return re.sub(r"\s+", " ", re.sub(r"[“”\"'‘’`].*?[“”\"'‘’`]", "<q>", re.sub(r"\b[A-Z][a-z]+\b|\d[\d:.\-]*|\b[a-z]+-[0-9a-f]{3,}\b", "#", q or ""))).strip()[:110]


def opts(it):
    o = it.get("options") or it.get("choices") or []
    return [x if isinstance(x, str) else (x.get("text") or x.get("label") or json.dumps(x)) for x in (o.values() if isinstance(o, dict) else o)]


def key(it):
    a = it.get("answer", it.get("key", it.get("correct"))); o = opts(it)
    if isinstance(a, int) and 0 <= a < len(o): return o[a]
    if isinstance(a, str) and len(a) == 1 and a.upper() in "ABCDEFGH" and a not in o and ord(a.upper()) - 65 < len(o): return o[ord(a.upper()) - 65]
    return a if isinstance(a, str) else json.dumps(a)


out = []
for r in MINE:
    h, bid = r["measurement"], r.get("bank"); p = paths.get(bid) if bid else None; slug = ((ROWS.get(h) or {}).get("proposal") or {}).get("slug") if isinstance((ROWS.get(h) or {}).get("proposal"), dict) else (ROWS.get(h) or {}).get("proposal_slug")
    row = {"measurement": h, "bank": bid, "slug": slug, "retracted": r.get("retracted"), "is_replication": r.get("is_replication")}
    if not p or not os.path.exists(p): row["state"] = "no bank file"; out.append(row); continue
    try: J = json.load(open(p, encoding="utf-8"))
    except Exception as e: row["state"] = "unreadable: %s" % type(e).__name__; out.append(row); continue
    items = J if isinstance(J, list) else (J.get("items") or J.get("bank") or J.get("pairs") or [])
    if not items or not isinstance(items[0], dict): row["state"] = "no item list"; out.append(row); continue
    real = [i for i in items if not is_cal(i)]; q = [i.get("question") or i.get("prompt") or i.get("q") or "" for i in real]
    ab_off = sum(any(ABST.search(o) for o in opts(i)) for i in real); ab_key = sum(bool(ABST.search(str(key(i)))) for i in real)
    s = real[0] if real else {}
    row.update(state="read", real=len(real), cal=len(items) - len(real), fields=sorted(s.keys())[:14], stems=collections.Counter(stem(x) for x in q).most_common(4), distinct_questions=len(set(q)),
               abstain_offered=ab_off, abstain_keyed=ab_key, sample={"question": q[0] if q else None, "options": opts(s), "key": key(s), "english": str(s.get("english") or s.get("baseline") or s.get("message_english") or "")[:420]})
    out.append(row)
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print("measurements", len(out), collections.Counter(r["state"] for r in out))
for r in out:
    if r["state"] != "read": print("\n%s | %s | %s" % (r["measurement"][:8], r["state"], r["slug"])); continue
    print("\n%s | %s | real %d cal %d | abstain offered %d keyed %d | distinct questions %d | retracted %s | replication %s" % (r["measurement"][:8], (r["slug"] or "")[:60], r["real"], r["cal"], r["abstain_offered"], r["abstain_keyed"], r["distinct_questions"], r["retracted"], r["is_replication"]))
    for st, n in r["stems"]: print("     %3d  %s" % (n, st))
    print("     e.g. EN: %s\n          Q: %s | OPT %s | KEY %s" % (r["sample"]["english"][:300], r["sample"]["question"], json.dumps(r["sample"]["options"], ensure_ascii=False)[:330], str(r["sample"]["key"])[:120]))
