"""Message-blind rules on every pinned comprehension bank. Run with python3 -I from this directory; banks/ holds untrusted downloads.
Every bank: verify the pin, drop calibration items, find the key per item, score rules that never read the message:
constant answer text, constant position, longest option, shortest option, constant first word of the key (Dexagon's `Yes;` shortcut generalised).
Then compare each served measurement's arms (english, ainglish, chance) with the best such rule on its bank."""
import json, hashlib, collections, re, sys, os
I = json.load(open("bank_index.json")); rows = json.load(open("comp_measurements.json")); M = json.load(open("manifests.json"))
def canon(x, ascii_): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=ascii_).encode()).hexdigest()
def h(b): return hashlib.sha256(b).hexdigest()
def is_cal(it):
    return bool(it.get("calibration")) or bool(it.get("control")) or it.get("kind") == "calibration" or "calibration_construct" in it or "calibration_truth" in it or it.get("key_class") == "calibration"
def key_index(it):
    opts = it.get("options"); ans = it.get("answer", it.get("key", it.get("correct", it.get("correct_option", it.get("gold")))))
    labels = None
    if isinstance(opts, dict): labels = list(opts.keys()); opts = [opts[k] for k in labels]
    if not isinstance(opts, list) or not opts or ans is None: return None, None, "no options/answer"
    texts = [o if isinstance(o, str) else (o.get("text") or o.get("label") or json.dumps(o, sort_keys=True)) if isinstance(o, dict) else str(o) for o in opts]
    ids = [o.get("id") if isinstance(o, dict) else None for o in opts]
    if isinstance(ans, int) and 0 <= ans < len(texts): return ans, texts, "int"
    if isinstance(ans, str):
        if ans in texts: return texts.index(ans), texts, "text"
        if labels and ans in labels: return labels.index(ans), texts, "label"
        if ans in ids: return ids.index(ans), texts, "id"
        a = ans.strip().upper()
        if len(a) == 1 and "A" <= a <= "Z" and ord(a) - 65 < len(texts): return ord(a) - 65, texts, "letter"
        low = [t.strip().lower() for t in texts]
        if ans.strip().lower() in low: return low.index(ans.strip().lower()), texts, "text-ci"
    return None, texts, "answer not in options"
def first_word(t): 
    m = re.match(r"\W*([A-Za-z0-9']+)", t); return m.group(1).lower() if m else t[:1].lower()
R = {"banks": {}, "measurements": []}
for b in I["banks"]:
    out = {"bank_id": b["bank_id"], "kind": b["kind"], "status": b["status"], "url": b["url"], "manifests": len(b["manifest_hashes"])}
    R["banks"][b["bank_id"]] = out
    p = b.get("path")
    if not p or not os.path.exists(p): out["state"] = "unreachable"; continue
    raw = open(p, "rb").read()
    try: parsed = json.loads(raw.decode("utf-8"))
    except Exception as e: out["state"] = "not json"; continue
    pin = b.get("items_sha256")
    if b["kind"] in ("inline", "test_set"): out["pin"] = "served inline"
    elif pin:
        items0 = parsed.get("items") if isinstance(parsed, dict) else parsed
        cands = {"raw": h(raw), "raw-stripped": h(raw.strip()), "canon-items": canon(items0, False), "canon-items-ascii": canon(items0, True), "canon-doc": canon(parsed, False), "canon-doc-ascii": canon(parsed, True), "field": parsed.get("sha256") if isinstance(parsed, dict) else None}
        out["pin"] = next((k for k, v in cands.items() if v == pin), None)
        if out["pin"] is None: out["state"] = "pin mismatch"; continue
    else: out["pin"] = "no pin"
    items = parsed.get("items") if isinstance(parsed, dict) and "items" in parsed else parsed.get("test_set") if isinstance(parsed, dict) and "test_set" in parsed else parsed if isinstance(parsed, list) else None
    if not isinstance(items, list) or not items or not all(isinstance(i, dict) for i in items): out["state"] = "no item list"; continue
    cal = [i for i in items if is_cal(i)]; real = [i for i in items if not is_cal(i)]
    ki = [key_index(i) for i in real]; bad = [r for r in ki if r[0] is None]
    out.update({"items": len(items), "calibration": len(cal), "real": len(real), "unparsed_items": len(bad), "parse_reasons": dict(collections.Counter(r[2] for r in ki))})
    ic = b.get("item_counts") or {}
    if ic: out["item_counts_match"] = (ic.get("real") == len(real)); out["item_counts_served"] = ic
    if bad or not real: out["state"] = "items unparsed"; continue
    n = len(real); ks = [r[0] for r in ki]; texts = [r[1] for r in ki]
    kcount = collections.Counter(len(t) for t in texts); k = kcount.most_common(1)[0][0]
    keytext = [t[i] for i, t in zip(ks, texts)]
    rules = {}
    rules["constant answer"] = max(collections.Counter(x.strip().lower() for x in keytext).values()) / n
    rules["constant position"] = max(collections.Counter(ks).values()) / n
    rules["longest option"] = sum(1 for i, t in zip(ks, texts) if len(t[i]) > max(len(o) for j, o in enumerate(t) if j != i)) / n
    rules["shortest option"] = sum(1 for i, t in zip(ks, texts) if len(t[i]) < min(len(o) for j, o in enumerate(t) if j != i)) / n
    fw = collections.Counter(first_word(x) for x in keytext); best_fw = 0.0; best_w = None
    for w in fw:
        acc = sum(1 for i, t in zip(ks, texts) if sum(first_word(o) == w for o in t) == 1 and first_word(t[i]) == w) / n
        if acc > best_fw: best_fw, best_w = acc, w
    rules["constant first word"] = best_fw
    ORDER_FREE = ("constant answer", "longest option", "shortest option", "constant first word")  # reader-available whatever order the harness presents
    best = max(ORDER_FREE, key=rules.get); best_any = max(rules, key=rules.get)
    opt_freq = collections.Counter(o.strip().lower() for t in texts for o in t); common = [o for o, c in opt_freq.items() if c >= 0.5 * n]
    never_key = [o for o in common if all(x.strip().lower() != o for x in keytext)]
    out.update({"state": "scored", "n": n, "k": k, "k_dist": dict(kcount), "uniform": round(1 / k, 4), "rules": {r: round(v, 4) for r, v in rules.items()}, "best_rule": best, "best": round(rules[best], 4), "best_any_rule": best_any, "best_any": round(rules[best_any], 4), "position_rule": round(rules["constant position"], 4), "key_always_first_in_file": all(i == 0 for i in ks),
                "key_text_dist": dict(collections.Counter(x.strip().lower() for x in keytext).most_common(6)), "key_position_dist": dict(collections.Counter(ks)), "recurring_options": common, "recurring_options_never_key": never_key, "best_first_word": best_w})
by_m = {}
for b in I["banks"]:
    for mh in b["manifest_hashes"]: by_m[mh] = b["bank_id"]
for m in rows:
    mh = m["manifest_hash"]; bid = by_m.get(mh); bk = R["banks"].get(bid) if bid else None
    arms = m.get("arms") or {}; e, a, c = arms.get("english"), arms.get("ainglish"), arms.get("chance")
    rec = {"manifest_hash": mh, "bank_id": bid, "submitter": (m.get("submitter") or {}).get("name"), "is_replication": bool(m.get("is_replication")), "settlement_state": m.get("settlement_state"), "retracted": bool(m.get("retraction")) or (m.get("settlement_state") or "").startswith("retracted"),
           "value": m.get("value"), "english": e, "ainglish": a, "chance": c, "bank_state": (bk or {}).get("state", "no manifest" if not bid else "?")}
    if bk and bk.get("state") == "scored" and isinstance(e, (int, float)) and isinstance(a, (int, float)):
        best = bk["best"]; rec.update({"best": best, "best_rule": bk["best_rule"], "uniform": bk["uniform"],
            "chance_is_uniform": c is not None and abs(c - bk["uniform"]) < 0.002, "chance_declared": c is not None,
            "chance_below_best_5pp": c is not None and best - c >= 0.05, "english_below_best": e < best, "ainglish_below_best": a < best, "both_below_best": e < best and a < best, "both_below_best_2pp": e < best - 0.02 and a < best - 0.02})
    R["measurements"].append(rec)
json.dump(R, open("scan_result.json", "w"), indent=1, sort_keys=True)
B = R["banks"]; print("banks", len(B), collections.Counter(x.get("state") for x in B.values()), "pins", collections.Counter(x.get("pin") for x in B.values()))
S = [x for x in R["measurements"] if "best" in x]; print("measurements", len(R["measurements"]), "scored", len(S), "bank_state", collections.Counter(x["bank_state"] for x in R["measurements"]))
live = [x for x in S if not x["retracted"]]
for name, L in (("all scored", S), ("live (not retracted)", live)):
    print(name, len(L), "chance declared", sum(x["chance_declared"] for x in L), "chance==1/k", sum(x["chance_is_uniform"] for x in L), "best-chance>=5pp", sum(x["chance_below_best_5pp"] for x in L),
          "eng<best", sum(x["english_below_best"] for x in L), "ain<best", sum(x["ainglish_below_best"] for x in L), "both<best", sum(x["both_below_best"] for x in L), "both<best-2pp", sum(x["both_below_best_2pp"] for x in L))
print("by settlement (live):", collections.Counter((x["settlement_state"], x["both_below_best"]) for x in live))
print("best order-free rule kinds (scored banks):", collections.Counter(x["best_rule"] for x in B.values() if x.get("state") == "scored"), "| any-rule kinds:", collections.Counter(x["best_any_rule"] for x in B.values() if x.get("state") == "scored"))
print("banks key always first in file:", sum(1 for x in B.values() if x.get("key_always_first_in_file")), "banks position rule 1.0:", sum(1 for x in B.values() if x.get("position_rule") == 1.0))
print("banks with a recurring option never the key:", sum(1 for x in B.values() if x.get("recurring_options_never_key")))
for x in sorted((x for x in B.values() if x.get("state") == "scored"), key=lambda x: -x["best"])[:12]:
    print(x["bank_id"][:12], "n", x["n"], "k", x["k"], "uniform", x["uniform"], "best", x["best"], x["best_rule"], "never-key", x["recurring_options_never_key"][:3], "mani", x["manifests"])
print("unparsed banks:", [(x["bank_id"][:12], x.get("state"), x.get("parse_reasons")) for x in B.values() if x.get("state") not in ("scored", "unreachable")][:15])
