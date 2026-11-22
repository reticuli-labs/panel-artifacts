"""selfcheck.py [--module FILE]: the controls of PLAN.md, on planted banks built in memory with a fixed seed. Reads no bank, writes
nothing, calls no reader. Loads the analysis from degenerate.py beside it, or from FILE (so an altered copy can be checked).
Exit code 0 and a count of checks when every check holds; the first one that does not hold stops it."""
import argparse, importlib.util, itertools, os, random
ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--module", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "degenerate.py")); a = ap.parse_args()
spec = importlib.util.spec_from_file_location("degenerate_under_check", a.module); D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)
rng = random.Random(20261122); FILL = ["amber", "birch", "cedar", "delta", "ember", "fjord", "grove", "heron", "inlet", "jetty", "knoll", "larch"]; checks = 0


def text(n_words, avoid=()):
    return " ".join(rng.choice([w for w in FILL if w not in avoid]) for _ in range(n_words))


def item(i, options, key, question=None):
    return {"id": "p%05d" % i, "question": question or "Which one holds in case %d?" % i, "options": options, "answer": key, "calibration": False, "identical_arms": False}


def plant(kind, n=40, k=4):
    """A bank of n items with k options in which the named rule finds every key (or, for clean, no rule finds more than chance)."""
    rows = []
    for i in range(n):
        if kind in ("first", "last", "clean"):
            opts = ["%s %d%s" % (text(rng.randint(2, 6)), i, c) for c in "abcd"[:k]]; key = opts[0]
            if kind == "clean": rng.shuffle(opts)
            elif kind == "last": opts = opts[1:] + [key]
            rows.append(item(i, opts, key))
        elif kind in ("longest", "shortest"):
            sizes = rng.sample(range(2, 9), k); opts = ["%s %d%s" % (text(s), i, c) for s, c in zip(sizes, "abcd")]
            key = (max if kind == "longest" else min)(opts, key=len); assert [len(o) for o in opts].count(len(key)) == 1
            rng.shuffle(opts); rows.append(item(i, opts, key))
        elif kind == "echo":
            opts = ["%s %d%s" % (text(3), i, c) for c in "abcd"[:k]]; key = "zebra quartz " + opts[0]; opts[0] = key
            rng.shuffle(opts); rows.append(item(i, opts, key, "Does Zebra Quartz hold in case %d?" % i))     # capitals: the rule compares in lower case
        else: raise ValueError(kind)
    return rows


def run(banks):
    items = {v["id"]: v for _, rows in banks for v in rows}
    return {b["bank"]: b for b in D.analyse([(name, name, [v["id"] for v in rows]) for name, rows in banks], items)["rows"]}


# 1. each planted rule is found by its own rule, and the clean bank by none
banks = []
for i, kind in enumerate(["first", "last", "longest", "shortest", "echo"]):
    rows = plant(kind)
    for v in rows: v["id"] = kind + v["id"]
    banks.append((kind, rows))
clean = plant("clean", n=400)
for v in clean: v["id"] = "clean" + v["id"]
banks.append(("clean", clean)); res = run(banks)
for kind in ["first", "last", "longest", "shortest", "echo"]:
    r = res[kind]["rules"][kind]; assert r["flagged"] and r["right"] == r["decided"] == 40, (kind, r); checks += 1
assert res["clean"]["flagged_rules"] == [], res["clean"]["flagged_rules"]; checks += 1
assert not res["first"]["rules"]["last"]["flagged"] and not res["last"]["rules"]["first"]["flagged"]; checks += 1
assert res["longest"]["rules"]["shortest"]["right"] == 0 and res["shortest"]["rules"]["longest"]["right"] == 0; checks += 1
assert res["clean"]["rules"]["echo"]["decided"] == 0, res["clean"]["rules"]["echo"]; checks += 1      # no option shares a word with the question: no pick, not a pick of the first
assert D.pick("longest", "q", ["aa", "bb", "c"]) is None and D.pick("shortest", "q", ["a", "b", "cc"]) is None; checks += 1      # a tie is no pick
assert D.pick("longest", "q", ["aa", "bbb", "c"]) == 1 and D.pick("shortest", "q", ["aa", "bbb", "c"]) == 2 and D.pick("last", "q", ["x", "y", "z"]) == 2; checks += 1
assert D.pick("echo", "Is the Valve open?", ["the pump", "the valve is open", "neither"]) == 1 and D.pick("echo", "Is it?", ["yes", "no"]) is None; checks += 1
r = res["first"]["rules"]["first"]; assert r["expected"] == 10.0 and r["excess"] == 1.0 and res["clean"]["chance"] == 0.25, (r, res["clean"]["chance"]); checks += 1

# 2. a rotated bank: the key sits in each position equally often, and the listed order still gives every key away
rot = []
for i in range(48):
    base = ["keep the record", "drop the record", "both of them", "not stated"]; r = i % 4; opts = base[r:] + base[:r]
    rot.append(item(i, opts, opts[1], "What happens to the record?"))                     # the key is always the option after the first
rr = run([("rotated", rot)])["rotated"]
assert rr["key_position"] == {"2 of 4": 48}, rr["key_position"]; checks += 1
rot2 = []
for i in range(48):
    base = ["keep the record", "drop the record", "both of them", "not stated"]; r = i % 4; opts = base[r:] + base[:r]
    rot2.append(item(i, opts, base[0], "What happens to the record?"))                    # one key text, rotated through all four positions
r2 = run([("rotated2", rot2)])["rotated2"]
assert r2["key_position"] == {"1 of 4": 12, "2 of 4": 12, "3 of 4": 12, "4 of 4": 12}, r2["key_position"]; checks += 1
assert not r2["rules"]["first"]["flagged"] and not r2["rules"]["last"]["flagged"] and r2["rules"]["first"]["right"] == 12; checks += 1
rot3 = []
for i in range(48):
    base = ["keep the record", "drop the record", "both of them", "not stated"]; r = i % 4; opts = base[r:] + base[:r]
    rot3.append(item(i, opts, opts[0] if r % 2 == 0 else opts[2], "What happens to the record?"))   # the key follows from the rotation, and from nothing else
r3 = run([("rotated3", rot3)])["rotated3"]
assert r3["ceiling_listed"] == 1.0 and r3["ceiling_sorted"] == 0.25, (r3["ceiling_listed"], r3["ceiling_sorted"]); checks += 1   # the four keys are four texts, 12 items each: as a set, chance
assert r3["chance"] == 0.25; checks += 1

# 3. the exact tail against full enumeration, and against two values worked by hand
ks = [2, 2, 3, 4, 3]
for right in range(len(ks) + 2):
    brute = 0.0
    for hits in itertools.product([0, 1], repeat=len(ks)):
        if sum(hits) >= right:
            p = 1.0
            for h, k in zip(hits, ks): p *= (1.0 / k) if h else (1.0 - 1.0 / k)
            brute += p
    assert abs(D.tail(ks, right) - brute) < 1e-12, (right, D.tail(ks, right), brute); checks += 1
assert abs(D.tail([2] * 10, 10) - 1 / 1024) < 1e-15; checks += 1
assert abs(D.tail([4] * 3, 1) - (1 - 0.75 ** 3)) < 1e-15; checks += 1

# 4. the flag threshold divides by the number of tests, and a rule with fewer than 10 decided items is not tested
small = plant("first", n=9)
for v in small: v["id"] = "small" + v["id"]
rs = D.analyse([("small", "small", [v["id"] for v in small])], {v["id"]: v for v in small}); assert rs["banks_tested"] == 0 and rs["tests"] == 0; checks += 1
full = D.analyse([(name, name, [v["id"] for v in rows]) for name, rows in banks], {v["id"]: v for _, rows in banks for v in rows})
assert abs(full["alpha_per_test"] - 0.05 / full["tests"]) < 1e-15 and full["tests"] >= 20, (full["alpha_per_test"], full["tests"]); checks += 1
assert full["banks_with_a_flagged_rule"] == 5, full["banks_with_a_flagged_rule"]; checks += 1
assert full["all_distinct_real_items"]["n"] == 600; checks += 1
twice = D.analyse([("one", "one", [v["id"] for v in clean]), ("two", "two", [v["id"] for v in clean])], {v["id"]: v for v in clean})
assert twice["banks_tested"] == 2 and twice["all_distinct_real_items"]["n"] == 400, twice["all_distinct_real_items"]["n"]; checks += 1      # an item in two banks is pooled once

# 5. calibration items and items with identical arms are not counted
mixed = plant("first", n=30)
for j, v in enumerate(mixed): v["id"] = "mixed" + v["id"]; v["calibration"] = j < 10; v["identical_arms"] = 10 <= j < 15
rm = D.analyse([("mixed", "mixed", [v["id"] for v in mixed])], {v["id"]: v for v in mixed}); assert rm["rows"][0]["n"] == 15, rm["rows"][0]["n"]; checks += 1
print("selfcheck passed: %d checks" % checks)
