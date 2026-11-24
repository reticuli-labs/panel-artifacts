"""taught.py --sweep DIR --out FILE: taught lookups over every item bank of the statement-isolation sweep. A lookup is shown half
of a bank WITH its keys, then scored on the other half, and the halves are swapped. It never sees the wording under test: its key
is built from the options, or from an identifier in the part of the message that both arms share. Reads banks.json and
blind_items.jsonl in DIR; writes FILE and nothing else. Calls no reader. The lookups, the null and the flag are in PLAN.md."""
import argparse, collections, json, math, os, random, re
import numpy as np
RULES = ("menu", "options", "label0", "label1", "label2"); MIN_N = 10; FAMILY_ALPHA = 0.05
IDENT = re.compile(r"\b(?=[A-Za-z0-9_-]*[A-Za-z])(?=[A-Za-z0-9_-]*\d\d)[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*\b")
num = lambda t: re.sub(r"\d+", "#", t)
CODED = re.compile(r"\b([A-H]) = (.*?)(?=\. [A-H] = |\.?$)"); FOLDS = 4; SPLIT_SEED = 20261124


def shown(v):
    """The option texts a reader is shown, in order. Where a bank lists bare codes (A, B, C, D) and prints the texts in the question,
    the texts are taken from the question (amendment of 2026-11-24); otherwise the listed options are the texts."""
    o = v["options"]
    if all(len(x) == 1 for x in o):
        m = CODED.findall(v["question"])
        if [k for k, _ in m] == list(o): return [t for _, t in m]
    return list(o)


def key(rule, v):
    """What the lookup may see of one item for this rule, or None when the item has no such thing."""
    if rule == "menu": return tuple(num(o) for o in shown(v))
    if rule == "options": return tuple(sorted(num(o) for o in shown(v)))
    m = IDENT.search(v.get("blind") or "")
    if not m: return None
    tok = m.group(0); digits = re.sub(r"\D", "", tok); p = int(rule[-1])
    if p >= len(digits): return None
    return (re.sub(r"[a-z]", "a", re.sub(r"[A-Z]", "A", re.sub(r"\d", "9", tok))), p, digits[p])


def target(rule, v):
    pos = v["options"].index(v["answer"]); return pos if rule == "menu" else num(shown(v)[pos])


def predict(rule, table, v):
    k = key(rule, v)
    if k is None or len(table.get(k, ())) != 1: return None
    t = next(iter(table[k]))
    if rule == "menu": return t if t < len(v["options"]) else None
    hit = [i for i, o in enumerate(shown(v)) if num(o) == t]
    return hit[0] if len(hit) == 1 else None


def tail(ks, right):
    """P(X >= right), X = number right for a reader that is right on an item with k options with probability 1/k, items independent."""
    dist = np.array([1.0])
    for k, n in sorted(collections.Counter(ks).items()):
        p = 1.0 / k; lp, lq = math.log(p), math.log(1.0 - p)
        pmf = np.array([math.exp(math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq) for j in range(n + 1)])
        dist = np.convolve(dist, pmf)
    return float(min(1.0, dist[right:].sum()))


def score_rule(rule, rows):
    """Four folds drawn by a seeded shuffle of the bank's items (amendment of 2026-11-24; the plan's split by parity is in run 1):
    each item is scored by a lookup taught on the three other quarters."""
    ks, right, wrong = [], 0, 0; order = list(range(len(rows))); random.Random(SPLIT_SEED).shuffle(order); part = {i: n % FOLDS for n, i in enumerate(order)}
    for fold in range(FOLDS):
        table = collections.defaultdict(set)
        for i, v in enumerate(rows):
            if part[i] != fold and key(rule, v) is not None: table[key(rule, v)].add(target(rule, v))
        for i, v in enumerate(rows):
            if part[i] != fold: continue
            pos = predict(rule, table, v)
            if pos is None: continue
            ks.append(len(v["options"])); ok = v["options"][pos] == v["answer"]; right += ok; wrong += not ok
    n = len(ks); exp = sum(1.0 / k for k in ks)
    return {"decided": n, "right": right, "wrong": wrong, "abstain": len(rows) - n, "expected": round(exp, 2), "p": tail(ks, right) if n else 1.0}


def analyse(banks, items):
    real = lambda v: not v.get("calibration") and not v.get("identical_arms"); out = []
    for name, sha, ids in banks:
        rows = [items[i] for i in ids if real(items[i])]
        if len(rows) < MIN_N: continue
        out.append({"bank": name, "sha256_items": sha, "n": len(rows), "rules": {r: score_rule(r, rows) for r in RULES}})
    tests = [(b, r) for b in out for r in RULES if b["rules"][r]["decided"] >= MIN_N]; alpha = FAMILY_ALPHA / max(1, len(tests))
    for b in out:
        for r in RULES: b["rules"][r]["flagged"] = bool(b["rules"][r]["decided"] >= MIN_N and b["rules"][r]["p"] < alpha)
        b["flagged_rules"] = [r for r in RULES if b["rules"][r]["flagged"]]
    return {"banks_tested": len(out), "tests": len(tests), "alpha_per_test": alpha, "min_decided": MIN_N, "rules": list(RULES),
            "banks_with_a_flagged_rule": sum(bool(b["flagged_rules"]) for b in out), "flagged_banks_per_rule": {r: sum(b["rules"][r]["flagged"] for b in out) for r in RULES},
            "rows": sorted(out, key=lambda b: (-max([x["right"] / b["n"] for x in b["rules"].values() if x["flagged"]] or [0.0]), b["bank"]))}


def load(sweep):
    items = {}
    for l in open(os.path.join(sweep, "blind_items.jsonl"), encoding="utf-8"):
        if l.strip(): r = json.loads(l); items[r["id"]] = r
    by_sha = collections.OrderedDict()
    for b in json.load(open(os.path.join(sweep, "banks.json"), encoding="utf-8")): by_sha.setdefault(b["sha256_items"], []).append(b)
    return [(f[0]["dir"] + "/" + f[0]["file"], sha, f[0]["item_ids"]) for sha, f in by_sha.items()], items


def rekeyed(items, seed=20261124):
    """The negative control: every item gets a key drawn at random among its own options, so nothing an item shows can name it."""
    rnd = random.Random(seed); out = {}
    for i in sorted(items):
        v = dict(items[i]); v["answer"] = v["options"][rnd.randrange(len(v["options"]))]; out[i] = v
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--sweep", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    banks, items = load(a.sweep); res = analyse(banks, items); ctl = analyse(banks, rekeyed(items))
    res["control_keys_drawn_at_random"] = {k: ctl[k] for k in ("banks_tested", "tests", "banks_with_a_flagged_rule", "flagged_banks_per_rule")}
    find = lambda part, rule: [(b["bank"], b["rules"][rule]["right"], b["rules"][rule]["wrong"], b["rules"][rule]["decided"], b["rules"][rule]["flagged"]) for b in res["rows"] if part in b["bank"]]
    res["known_cases"] = {"send-snapshot replica, menu": find("send-snapshot-comprehension-replica-2026-09-25/items.json", "menu"), "frozen pool seats, label0": find("hh-mm-z-frozen-pool-2026-09-26/seat-", "label0")}
    json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1, ensure_ascii=False))
    print("\n%-66s %4s  %s" % ("bank", "n", "flagged lookups: right, wrong of decided (expected by chance)"))
    for b in res["rows"]:
        if b["flagged_rules"]: print("%-66s %4d  %s" % (b["bank"][:66], b["n"], "; ".join("%s %d, %d of %d (%.1f)" % (r, b["rules"][r]["right"], b["rules"][r]["wrong"], b["rules"][r]["decided"], b["rules"][r]["expected"]) for r in b["flagged_rules"])))


if __name__ == "__main__":
    main()
