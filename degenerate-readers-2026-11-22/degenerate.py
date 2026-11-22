"""degenerate.py --sweep DIR --out FILE: five mechanical readers over every item bank of the statement-isolation sweep. A rule sees
the question and the options in the order the bank lists them, and no message. Reads banks.json, blind_items.jsonl, contrast.json
and described.json in DIR; writes FILE and nothing else. Calls no reader. The rules, the null and the flag are in PLAN.md."""
import argparse, collections, json, math, os, re
import numpy as np
RULES = ("first", "last", "longest", "shortest", "echo"); MIN_N = 10; FAMILY_ALPHA = 0.05; WORD = re.compile(r"[a-z0-9]+")


def pick(rule, question, options):
    """The position this rule picks among the listed options, or None when it has no single winner."""
    if rule == "first": return 0
    if rule == "last": return len(options) - 1
    if rule in ("longest", "shortest"):
        size = [len(o) for o in options]; m = max(size) if rule == "longest" else min(size)
        return size.index(m) if size.count(m) == 1 else None
    if rule == "echo":
        q = set(WORD.findall(question.lower())); shared = [len(set(WORD.findall(o.lower())) & q) for o in options]; m = max(shared)
        return shared.index(m) if shared.count(m) == 1 else None      # no shared word at all is a tie of every option at zero: no pick
    raise ValueError(rule)


def tail(ks, right):
    """P(X >= right), X = number right for a reader that is right on an item with k options with probability 1/k, items independent."""
    dist = np.array([1.0])
    for k, n in sorted(collections.Counter(ks).items()):
        p = 1.0 / k; lp, lq = math.log(p), math.log(1.0 - p)
        pmf = np.array([math.exp(math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq) for j in range(n + 1)])
        dist = np.convolve(dist, pmf)
    return float(min(1.0, dist[right:].sum()))


def score_rule(rule, rows):
    """rows: [item]. -> decided, right, expected, p, excess for one rule on one bank."""
    ks, right = [], 0
    for v in rows:
        pos = pick(rule, v["question"], v["options"])
        if pos is None: continue
        ks.append(len(v["options"])); right += v["options"][pos] == v["answer"]
    n = len(ks); exp = sum(1.0 / k for k in ks)
    if n == 0: return {"decided": 0, "right": 0, "expected": 0.0, "p": 1.0, "excess": 0.0}
    return {"decided": n, "right": right, "expected": round(exp, 2), "p": tail(ks, right), "excess": round(max(0.0, (right - exp) / (n - exp)) if n > exp else 0.0, 4)}


def ceiling(rows, listed):
    """The most any reader can score who sees only question and options (as listed, or as a set): per group the commonest key, summed, over n."""
    groups = collections.defaultdict(collections.Counter)
    for v in rows: groups[(v["question"], tuple(v["options"]) if listed else tuple(sorted(v["options"])))][v["answer"]] += 1
    return sum(c.most_common(1)[0][1] for c in groups.values()) / len(rows)


def analyse(banks, items, klass=None):
    """banks: [(name, sha, [item id])], items: {id: item}, klass: {sha: label of yesterday's sweep}. -> the whole result."""
    real = lambda v: not v.get("calibration") and not v.get("identical_arms"); out = []
    for name, sha, ids in banks:
        rows = [items[i] for i in ids if real(items[i])]
        if len(rows) < MIN_N: continue
        pos = collections.Counter("%d of %d" % (v["options"].index(v["answer"]) + 1, len(v["options"])) for v in rows)
        out.append({"bank": name, "sha256_items": sha, "n": len(rows), "sweep_class": (klass or {}).get(sha), "key_position": dict(sorted(pos.items())),
                    "chance": round(sum(1.0 / len(v["options"]) for v in rows) / len(rows), 3), "ceiling_listed": round(ceiling(rows, True), 3), "ceiling_sorted": round(ceiling(rows, False), 3),
                    "rules": {r: score_rule(r, rows) for r in RULES}})
    tests = [(b, r) for b in out for r in RULES if b["rules"][r]["decided"] >= MIN_N]; alpha = FAMILY_ALPHA / max(1, len(tests))
    for b in out:
        for r in RULES: b["rules"][r]["flagged"] = bool(b["rules"][r]["decided"] >= MIN_N and b["rules"][r]["p"] < alpha)
        b["flagged_rules"] = [r for r in RULES if b["rules"][r]["flagged"]]
    seen, pooled = set(), []
    for name, sha, ids in banks:
        for i in ids:
            if i not in seen and real(items[i]): seen.add(i); pooled.append(items[i])
    by_class = collections.defaultdict(lambda: [0, 0])
    for b in out: by_class[str(b["sweep_class"])][0] += 1; by_class[str(b["sweep_class"])][1] += bool(b["flagged_rules"])
    return {"banks_tested": len(out), "tests": len(tests), "alpha_per_test": alpha, "min_decided": MIN_N, "rules": list(RULES),
            "banks_with_a_flagged_rule": sum(bool(b["flagged_rules"]) for b in out), "flagged_banks_per_rule": {r: sum(b["rules"][r]["flagged"] for b in out) for r in RULES},
            "by_sweep_class": {k: {"banks": v[0], "with_a_flagged_rule": v[1]} for k, v in sorted(by_class.items())},
            "order_carries_the_key": sum(b["ceiling_listed"] - b["ceiling_sorted"] >= 0.1 for b in out),
            "all_distinct_real_items": {"n": len(pooled), "rules": {r: {k: v for k, v in score_rule(r, pooled).items() if k != "p"} for r in RULES}},
            "rows": sorted(out, key=lambda b: (-max(x["excess"] if x["flagged"] else 0.0 for x in b["rules"].values()), b["bank"]))}


def load(sweep):
    jl = lambda n: [json.loads(l) for l in open(os.path.join(sweep, n), encoding="utf-8") if l.strip()]; js = lambda n: json.load(open(os.path.join(sweep, n), encoding="utf-8"))
    items = {r["id"]: r for r in jl("blind_items.jsonl")}; by_sha = collections.OrderedDict()
    for b in js("banks.json"): by_sha.setdefault(b["sha256_items"], []).append(b)
    banks = [(f[0]["dir"] + "/" + f[0]["file"], sha, f[0]["item_ids"]) for sha, f in by_sha.items()]
    klass = {o["sha256_items"]: ("flagged, " + o["reading"]) if o["flagged"] else "not flagged" for o in js("contrast.json")}
    return banks, items, klass, {o["sha256_items"]: o["keyed_to_question"] for o in js("described.json")}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--sweep", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    banks, items, klass, keyed = load(a.sweep); res = analyse(banks, items, klass)
    off = [(b["bank"], b["ceiling_sorted"], keyed[b["sha256_items"]]) for b in res["rows"] if abs(b["ceiling_sorted"] - keyed[b["sha256_items"]]) > 0.0015]
    res["ceiling_sorted_reproduces_keyed_to_question"] = not off; res["ceiling_sorted_differences"] = off
    res["not_in_yesterdays_92"] = [b["bank"] for b in res["rows"] if b["sweep_class"] is None]
    json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1, ensure_ascii=False))
    print("\n%-58s %4s %-28s %6s %6s  %s" % ("bank", "n", "class of the sweep", "listed", "sorted", "flagged rules: right of decided (expected)"))
    for b in res["rows"]:
        if b["flagged_rules"] or b["ceiling_listed"] - b["ceiling_sorted"] >= 0.1:
            print("%-58s %4d %-28s %6.2f %6.2f  %s" % (b["bank"][:58], b["n"], b["sweep_class"], b["ceiling_listed"], b["ceiling_sorted"],
                                                     "; ".join("%s %d of %d (%.1f)" % (r, b["rules"][r]["right"], b["rules"][r]["decided"], b["rules"][r]["expected"]) for r in b["flagged_rules"]) or "-"))


if __name__ == "__main__":
    main()
