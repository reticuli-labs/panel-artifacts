"""Static message-blind audit of one comprehension bank: can the key be recovered from the question and the options alone?
No reader, no network: it reads the frozen bank file given as argument 1 and prints, for a family of predictors that never see
either message, how many of the real (non-calibration) items each recovers, overall and per question. It also runs Dexagon's
predictor of 2026-11-14 (the option containing -new- for the incoming question, -old- for the departing one), and a POSITIVE
CONTROL: the same family on Dexagon's own retracted bank (argument 2) must find the 32-of-32 rule there.
Usage: python3 -I static_audit.py <my items.json> <dexagon items.json>"""
import collections, json, re, sys


def load(path):
    b = json.load(open(path, encoding="utf-8")); items = b["items"] if isinstance(b, dict) else b
    return [i for i in items if not i.get("calibration", False)]


def refs(options):                                    # the options that are references, not the two distractor sentences
    return [o for o in options if not re.search(r"both|not specified|neither|cannot", o, re.I)]


def tail(o): return re.split(r"[-_]", o)[-1]


RULES = {
 "option at position 0": lambda q, o: o[0], "option at position 1": lambda q, o: o[1], "option at position 2": lambda q, o: o[2], "option at position 3": lambda q, o: o[3],
 "shortest option": lambda q, o: min(o, key=len), "longest option": lambda q, o: max(o, key=len),
 "first reference listed": lambda q, o: refs(o)[0], "last reference listed": lambda q, o: refs(o)[-1],
 "smallest reference (byte order)": lambda q, o: min(refs(o)), "largest reference (byte order)": lambda q, o: max(refs(o)),
 "smallest suffix (byte order)": lambda q, o: min(refs(o), key=tail), "largest suffix (byte order)": lambda q, o: max(refs(o), key=tail),
 "reference with more digits": lambda q, o: max(refs(o), key=lambda s: sum(ch.isdigit() for ch in s)), "reference with fewer digits": lambda q, o: min(refs(o), key=lambda s: sum(ch.isdigit() for ch in s)),
 "the 'both' option": lambda q, o: next((x for x in o if re.search("both", x, re.I)), o[0]), "the 'not specified' option": lambda q, o: next((x for x in o if re.search("not specified", x, re.I)), o[0]),
}
CUES = {"Which reference occupies the active slot after the replacement?": "-new-", "Which reference is the departing value removed from the active slot?": "-old-"}


def dexagon(q, o):
    m = [s for s in o if CUES.get(q, "\0") in s]; return m[0] if len(m) == 1 else None


def audit(name, real):
    qs = sorted({i["question"] for i in real}); n = len(real); print("== %s: %d real items, %d questions" % (name, n, len(qs)))
    best = (0, None); out = {}
    def score(label, f, per_question=False):
        nonlocal best
        hit = collections.Counter()
        for i in real:
            try: ok = f(i["question"], i["options"]) == i["answer"]
            except Exception: ok = False
            hit[i["question"]] += ok
        tot = sum(hit.values()); out[label] = tot
        if tot > best[0]: best = (tot, label)
        return tot, [hit[q] for q in qs]
    for label, f in RULES.items():
        tot, per = score(label, f); print("   %-34s %2d of %d   per question %s" % (label, tot, n, per))
    # the best rule PER QUESTION (a predictor may read the question): the ceiling of this family
    ceil = 0; picks = []
    for q in qs:
        sub = [i for i in real if i["question"] == q]; b = max(RULES, key=lambda r: sum(1 for i in sub if _safe(RULES[r], i) == i["answer"]))
        k = sum(1 for i in sub if _safe(RULES[b], i) == i["answer"]); ceil += k; picks.append((b, k, len(sub)))
    print("   best rule chosen per question: %d of %d  %s" % (ceil, n, picks))
    d = sum(1 for i in real if dexagon(i["question"], i["options"]) == i["answer"]); print("   Dexagon's -new-/-old- predictor: %d of %d" % (d, n))
    # identical (question, option set) with different keys: items no message-blind predictor of any kind can all get right
    groups = collections.defaultdict(set)
    for i in real: groups[(i["question"], tuple(sorted(i["options"])))].add(i["answer"])
    clash = sum(1 for i in real if len(groups[(i["question"], tuple(sorted(i["options"])))]) > 1); print("   items whose question and option set recur with another key: %d of %d" % (clash, n))
    pos = collections.Counter(i["options"].index(i["answer"]) for i in real); print("   key positions:", dict(sorted(pos.items())))
    return {"n": n, "rules": out, "best_single_rule": best, "per_question_ceiling": ceil, "dexagon_rule": d, "recurring_with_other_key": clash, "key_positions": dict(pos)}


def _safe(f, i):
    try: return f(i["question"], i["options"])
    except Exception: return None


mine = audit("my bank (636e31d4)", load(sys.argv[1])); ctrl = audit("POSITIVE CONTROL: Dexagon's retracted bank (c43ed0b1)", load(sys.argv[2]))
assert ctrl["dexagon_rule"] == ctrl["n"] == 32, "the control did not reproduce Dexagon's 32 of 32"
json.dump({"mine": mine, "control": ctrl}, open(sys.argv[3], "w"), indent=1); print("AUDIT WRITTEN")
