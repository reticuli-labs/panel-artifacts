"""build_blind.py: from every item bank in this repository, make the BLIND form of each item: the text both arms share, with every
stretch where the two arms differ replaced by a gap. A reader of the blind form has not seen the form under test nor its careful
English wording. Reads only files of this repository (the parent directory). Writes, beside itself:
  banks.json          per bank file: its directory, path, canonical SHA-256 of the item list, and the ids of its items here
  blind_items.jsonl   one line per DISTINCT item (the same item in two files is read once): id, blind text, question, options,
                      answer, calibration flag, number of gaps, whether the arms are identical
  controls.jsonl      the control reads (see PLAN.md): planted and sighted, drawn with the fixed seed below
  not_read.json       items that are not in the two-arm shape, by file, with the reason
An item id here is the first 16 hex characters of the SHA-256 of its five fields (both arm texts, question, options, answer).
PLANT=1 instead writes the same files for a small planted bank under planted/ (see PLAN.md, "the instrument's own controls")."""
import collections, difflib, glob, hashlib, json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
GAP = "[…]"; MIN_BLOCK = 3; SEED = 20261121
KEYS = {"key", "answer", "gold", "correct", "expected", "truth"}; TEXTS = {"prompt", "text", "question", "arms", "marked", "careful", "stem", "passage", "sentence", "context", "world", "options", "a", "b"}
ABSTAIN = re.compile(r"(?i)not determined|cannot determine|cannot be determined|can't be determined|not established|not stated|not specified|not recorded|unknown|no way to tell|not enough information|unclear from")


def canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def blind_text(marked, careful):
    """The careful-English arm with every stretch that differs from the marked arm replaced by GAP. Words are compared; a shared
    stretch shorter than MIN_BLOCK words that stands between two differences is folded into the gap, so that no fragment of the
    wording under test is left standing. Returns (text, number of gaps)."""
    if marked == careful: return careful, 0
    tok = re.split(r"(\s+)", careful); words_c = tok[0::2]; words_m = re.split(r"\s+", marked)
    sm = difflib.SequenceMatcher(None, words_c, words_m, autojunk=False); keep = [b for b in sm.get_matching_blocks() if b.size >= MIN_BLOCK]
    out, pos_c, pos_m, gaps = [], 0, 0, 0
    for b in keep:
        if b.a > pos_c or b.b > pos_m: out.append(GAP); gaps += 1            # something differs before this shared stretch, in either arm
        out.append("".join(tok[2 * b.a: 2 * (b.a + b.size) - 1])); pos_c, pos_m = b.a + b.size, b.b + b.size
    if pos_c < len(words_c) or pos_m < len(words_m): out.append(GAP); gaps += 1
    return " ".join(out), gaps


def item_id(it):
    return hashlib.sha256(canon([it["ainglish"], it["english"], it["question"], it["options"], it["answer"]]).encode("utf-8")).hexdigest()[:16]


def shape_problem(it):
    for k in ("ainglish", "english", "question", "options", "answer"):
        if k not in it: return "no field " + k
    if not (isinstance(it["ainglish"], str) and isinstance(it["english"], str) and isinstance(it["question"], str)): return "an arm or the question is not text"
    if not (isinstance(it["options"], list) and 2 <= len(it["options"]) <= 26 and all(isinstance(o, str) for o in it["options"])): return "options are not a list of 2 to 26 texts"
    if it["answer"] not in it["options"] or it["options"].count(it["answer"]) != 1: return "the answer is not exactly one of the options"
    return None


def bank_files():
    """Every JSON file here that holds a list of items with some text field and a key field (the survey rule of 2026-11-21)."""
    for d in sorted(os.listdir(REPO)):
        p = os.path.join(REPO, d)
        if not os.path.isdir(p) or d.startswith(".") or os.path.abspath(p) == HERE: continue
        for f in sorted(glob.glob(os.path.join(p, "**", "*.json"), recursive=True)):
            if os.path.getsize(f) > 30_000_000: continue
            try: j = json.load(open(f, encoding="utf-8"))
            except Exception: continue
            items = j if isinstance(j, list) else (j.get("items") if isinstance(j, dict) and isinstance(j.get("items"), list) else None)
            if not items or not all(isinstance(x, dict) for x in items): continue
            ks = {k for x in items for k in x}
            if ks & KEYS and ks & TEXTS: yield d, os.path.relpath(f, p), items


def build(banks_iter, outdir):
    os.makedirs(outdir, exist_ok=True); banks, items, not_read = [], {}, []
    for d, f, its in banks_iter:
        ids, skipped = [], collections.Counter()
        for it in its:
            why = shape_problem(it)
            if why: skipped[why] += 1; continue
            i = item_id(it); ids.append(i)
            if i not in items:
                text, gaps = blind_text(it["ainglish"], it["english"])
                items[i] = {"id": i, "blind": text, "question": it["question"], "options": it["options"], "answer": it["answer"], "calibration": bool(it.get("calibration")), "gaps": gaps,
                            "identical_arms": it["ainglish"] == it["english"], "abstain_key": bool(ABSTAIN.search(it["answer"])), "english": it["english"]}
        banks.append({"dir": d, "file": f, "items_in_file": len(its), "item_ids": ids, "sha256_items": hashlib.sha256(canon(its).encode("utf-8")).hexdigest()})
        if skipped: not_read.append({"dir": d, "file": f, "reasons": dict(skipped)})
    rng = random.Random(SEED); real = sorted(i for i, v in items.items() if not v["calibration"] and not v["identical_arms"])
    planted = rng.sample(real, min(200, len(real))); sighted = rng.sample(real, min(300, len(real))); controls = []
    for i in planted:                                   # known present: the answer is written into what the blind reader sees
        v = items[i]; controls.append({"id": "planted:" + i, "kind": "planted", "of": i, "text": v["blind"] + "\n\nNote from the examiner: the correct choice is: " + v["answer"], "question": v["question"], "options": v["options"], "answer": v["answer"]})
    for i in sighted:                                   # the same reader with the careful-English arm whole
        v = items[i]; controls.append({"id": "sighted:" + i, "kind": "sighted", "of": i, "text": v["english"], "question": v["question"], "options": v["options"], "answer": v["answer"]})
    with open(os.path.join(outdir, "blind_items.jsonl"), "w", encoding="utf-8") as f:
        for i in sorted(items): f.write(canon({k: v for k, v in items[i].items() if k != "english"}) + "\n")
    with open(os.path.join(outdir, "controls.jsonl"), "w", encoding="utf-8") as f:
        for c in controls: f.write(canon(c) + "\n")
    json.dump(banks, open(os.path.join(outdir, "banks.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(not_read, open(os.path.join(outdir, "not_read.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    n = len(items); print("bank files %d | distinct banks %d | distinct items %d (real %d, calibration %d) | identical arms %d | no gap made %d | items not in the two-arm shape %d in %d files | controls %d" % (
        len(banks), len({b["sha256_items"] for b in banks}), n, sum(not v["calibration"] for v in items.values()), sum(v["calibration"] for v in items.values()),
        sum(v["identical_arms"] for v in items.values()), sum(v["gaps"] == 0 for v in items.values()), sum(sum(x["reasons"].values()) for x in not_read), len(not_read), len(controls)))


def planted_bank():
    """A bank whose right answers are known by construction: 40 items whose key stands ONLY in the stretch that differs (blind
    must be at chance), and 40 whose key stands in the shared text (blind must find it)."""
    rng = random.Random(SEED); names = ["Ilka", "Joss", "Kemi", "Lior", "Mira", "Noor", "Oren", "Pia"]; its = []
    for k in range(40):
        opts = rng.sample(names, 4); key = rng.choice(opts); other = rng.choice([o for o in opts if o != key])
        its.append({"id": "gap-only-%02d" % k, "english": "Shipment log %d was opened on a weekday at the north dock. The person who signed for crate %d was %s, as the ledger shows. The dock was dry." % (700 + k, k, key),
                    "ainglish": "Shipment log %d was opened on a weekday at the north dock. Crate %d: signed-by(%s). The dock was dry." % (700 + k, k, key),
                    "question": "Who signed for crate %d?" % k, "options": opts, "answer": key, "planted_class": "key only in the gap"})
        opts = rng.sample(names, 4); key = rng.choice(opts)
        its.append({"id": "shared-%02d" % k, "english": "Shipment log %d: %s signed for crate %d at the north dock on a weekday. The crate was weighed afterwards, and the weight was entered in the ledger as checked." % (800 + k, key, k),
                    "ainglish": "Shipment log %d: %s signed for crate %d at the north dock on a weekday. Crate weighed after; weight: ledger-checked." % (800 + k, key, k),
                    "question": "Who signed for crate %d?" % k, "options": opts, "answer": key, "planted_class": "key in the shared text"})
    return its


if __name__ == "__main__":
    if os.environ.get("PLANT") == "1":
        its = planted_bank(); os.makedirs(os.path.join(HERE, "planted"), exist_ok=True); json.dump(its, open(os.path.join(HERE, "planted", "items.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        build([("planted", "items.json", its)], os.path.join(HERE, "planted"))
    else: build(bank_files(), HERE)
