"""Order-artifact sweep of comprehension banks: can the key be recovered from the ORDER of the options alone?
Found on 2026-11-14 in my own bank for 636e31d4: every item's options were a rotation of [key, other reference, both, not
specified], so 'the option two places before "both references"' recovers 32 of 32 keys without either message.

Rules scored (none reads a message, an item id, a stratum or the key):
  anchor-offset: take an anchor option that can be found without the key (the longest, the shortest, the first or last in byte
  order, or a literal option text that recurs in at least half of the bank's items), and predict the option d places after it,
  cyclically, for every d. d = 0 with the longest or shortest anchor is the October scan's own rule; the rest are new.
Reads the banks cached by the October scan (argument 1: the directory holding bank_index.json, banks/, comp_measurements.json),
plus any extra bank files given in argument 3 (a JSON list of {bank_id, path, manifest_hashes, submitter}). Run with python3 -I:
the bank files are untrusted downloads. Output: argument 2.
POSITIVE CONTROLS asserted at the end: my 636e31d4 bank and Dexagon's retracted c43ed0b1 bank must both score complete."""
import collections, json, os, sys
CACHE, OUT = sys.argv[1], sys.argv[2]; EXTRA = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else []
I = json.load(open(os.path.join(CACHE, "bank_index.json"))); ROWS = json.load(open(os.path.join(CACHE, "comp_measurements.json")))


def is_cal(it):
    return bool(it.get("calibration")) or bool(it.get("control")) or it.get("kind") == "calibration" or "calibration_construct" in it or "calibration_truth" in it or it.get("key_class") == "calibration"


def key_index(it):                                     # the October scan's reader of one item, unchanged
    opts = it.get("options"); ans = it.get("answer", it.get("key", it.get("correct", it.get("correct_option", it.get("gold")))))
    labels = None
    if isinstance(opts, dict): labels = list(opts.keys()); opts = [opts[k] for k in labels]
    if not isinstance(opts, list) or not opts or ans is None: return None, None
    texts = [o if isinstance(o, str) else (o.get("text") or o.get("label") or json.dumps(o, sort_keys=True)) if isinstance(o, dict) else str(o) for o in opts]
    ids = [o.get("id") if isinstance(o, dict) else None for o in opts]
    if isinstance(ans, int) and not isinstance(ans, bool) and 0 <= ans < len(texts): return ans, texts
    if isinstance(ans, str):
        if ans in texts: return texts.index(ans), texts
        if labels and ans in labels: return labels.index(ans), texts
        if ans in ids: return ids.index(ans), texts
        a = ans.strip().upper()
        if len(a) == 1 and "A" <= a <= "Z" and ord(a) - 65 < len(texts): return ord(a) - 65, texts
        low = [t.strip().lower() for t in texts]
        if ans.strip().lower() in low: return low.index(ans.strip().lower()), texts
    return None, texts


def score(path):
    try: parsed = json.loads(open(path, "rb").read().decode("utf-8"))
    except Exception: return {"state": "unreadable"}
    items = parsed.get("items") if isinstance(parsed, dict) and "items" in parsed else parsed.get("test_set") if isinstance(parsed, dict) and "test_set" in parsed else parsed if isinstance(parsed, list) else None
    if not isinstance(items, list) or not items or not all(isinstance(i, dict) for i in items): return {"state": "no item list"}
    real = [i for i in items if not is_cal(i)]; ki = [key_index(i) for i in real]
    if not real or any(k[0] is None for k in ki): return {"state": "items unparsed"}
    use = [(k, t) for k, t in ki if len(t) >= 2 and len(set(t)) == len(t)]            # an item with a repeated option text has no well-defined anchor
    n = len(use)
    if n < 8: return {"state": "too few usable items", "real": len(real)}
    lit = collections.Counter(x for _, t in use for x in set(t)); literals = sorted(s for s, c in lit.items() if c * 2 >= n)   # sorted: a set's order changes from run to run, and ties go to the first rule tried
    anchors = {"longest": lambda t: max(range(len(t)), key=lambda j: (len(t[j]), -j)), "shortest": lambda t: min(range(len(t)), key=lambda j: (len(t[j]), j)),
               "first in byte order": lambda t: min(range(len(t)), key=lambda j: t[j]), "last in byte order": lambda t: max(range(len(t)), key=lambda j: t[j])}
    kmax = max(len(t) for _, t in use); rules = {}
    for name, f in anchors.items():
        for d in range(kmax):
            rules["%s, +%d" % (name, d)] = sum(1 for k, t in use if (f(t) + d) % len(t) == k)
    for s in literals:
        have = [(k, t) for k, t in use if s in t]
        for d in range(1, kmax):                                                          # d = 0 would be 'the literal is the key', the October scan's constant-answer rule
            rules["literal %r, +%d" % (s[:40], d)] = sum(1 for k, t in have if (t.index(s) + d) % len(t) == k)
    for d in range(kmax): rules["position %d" % d] = sum(1 for k, t in use if k == d)
    best = max(rules, key=rules.get); kmode = collections.Counter(len(t) for _, t in use).most_common(1)[0][0]
    new_rules = {r: v for r, v in rules.items() if not (r.startswith("position") or r in ("longest, +0", "shortest, +0"))}; nb = max(new_rules, key=new_rules.get)
    return {"state": "scored", "real": len(real), "usable": n, "options": kmode, "chance": round(1 / kmode, 4), "best_rule": best, "best": rules[best], "best_share": round(rules[best] / n, 4),
            "best_order_rule": nb, "best_order": new_rules[nb], "best_order_share": round(new_rules[nb] / n, 4), "rules_tried": len(rules), "literal_anchors": len(literals)}


res = {"banks": {}, "extra": []}
for b in I["banks"]:
    p = os.path.join(CACHE, b["path"]) if b.get("path") else None
    out = score(p) if p and os.path.exists(p) else {"state": "unreachable"}
    out.update({"bank_id": b["bank_id"], "url": b.get("url"), "manifest_hashes": b.get("manifest_hashes") or []}); res["banks"][b["bank_id"]] = out
for e in EXTRA:
    out = score(e["path"]); out.update({"bank_id": e["bank_id"], "manifest_hashes": e.get("manifest_hashes") or [], "label": e.get("label")}); res["extra"].append(out)
sc = [b for b in res["banks"].values() if b["state"] == "scored"]
res["summary"] = {"banks_indexed": len(res["banks"]), "scored": len(sc), "states": dict(collections.Counter(b["state"] for b in res["banks"].values())),
                  "complete_order_rule": sum(1 for b in sc if b["best_order"] == b["usable"]), "order_rule_at_least_90pct": sum(1 for b in sc if b["best_order_share"] >= 0.9),
                  "order_rule_at_least_75pct": sum(1 for b in sc if b["best_order_share"] >= 0.75), "order_rule_at_least_60pct": sum(1 for b in sc if b["best_order_share"] >= 0.6)}
json.dump(res, open(OUT, "w"), indent=1); print(json.dumps(res["summary"], indent=1))
mine = res["banks"].get("0e3cf6b2ccdab95cd71138fc6f5bb40e064908871b84e2c5fdf7ed73a7997ba9"); print("control, my 636e31d4 bank:", {k: mine.get(k) for k in ("state", "usable", "best_order_rule", "best_order")})
assert mine and mine["state"] == "scored" and mine["best_order"] == mine["usable"] == 32, "positive control failed on my own bank"
dx = [e for e in res["extra"] if e.get("label") == "dexagon c43ed0b1"]
if dx: print("control, Dexagon's c43ed0b1 bank:", {k: dx[0].get(k) for k in ("state", "usable", "best_order_rule", "best_order")}); assert dx[0]["best_order"] == dx[0]["usable"] == 32
print("SWEEP WRITTEN")
