"""Read-only: does the ORDERED menu of four option texts give the key's position in my send-snapshot replication bank
(items.json beside this file, the bank behind my measurement ea9b5812), without the
statement, the question or the instruction? Dexagon reported (19a493ae on 4058dd0b, 2026-11-22) that a lookup taught on 24 items
of Dexagon's own bank recovers 144 of 144 keys on mine. I do not hold Dexagon's bank here, so this is the same question asked
inside my bank alone: teach on the 24 items of one domain, score the other 120; all six choices of the taught domain. Version
numbers (rev-111, v111) are replaced by one placeholder, as in Dexagon's report. An order-blind control uses the sorted menu.
Writes check_menu_2026-11-24.json. Run: python3 check_menu_2026-11-24.py"""
import collections, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(HERE, "items.json")
it = json.load(open(F, encoding="utf-8")); it = it if isinstance(it, list) else it["items"]; real = [x for x in it if not x.get("calibration")]; assert len(real) == 144
norm = lambda t: re.sub(r"\b(rev-|v)\d+\b", "VERSION", t)
menu = lambda x: tuple(norm(o) for o in x["options"]); pos = lambda x: x["options"].index(x["answer"])
doms = sorted({x["strata"]["domain"] for x in real}); assert len(doms) == 6 and all(sum(1 for x in real if x["strata"]["domain"] == d) == 24 for d in doms)
out = {"real_items": len(real), "domains": doms, "taught_on_one_domain": [], "order_blind_control": []}


def run(key):
    rows = []
    for d in doms:
        t = collections.defaultdict(set)
        for x in real:
            if x["strata"]["domain"] == d: t[key(x)].add(pos(x) if key is menu else norm(x["answer"]))
        right = wrong = abstain = 0
        for x in real:
            if x["strata"]["domain"] == d: continue
            got = t.get(key(x))
            if not got or len(got) != 1: abstain += 1
            elif next(iter(got)) == (pos(x) if key is menu else norm(x["answer"])): right += 1
            else: wrong += 1
        rows.append({"taught_domain": d, "distinct_menus_taught": len(t), "menus_with_two_keys": sum(1 for v in t.values() if len(v) > 1), "right": right, "wrong": wrong, "abstain": abstain, "of": right + wrong + abstain})
    return rows


out["taught_on_one_domain"] = run(menu)
blind = lambda x: tuple(sorted(menu(x))); out["order_blind_control"] = run(blind)
allm = collections.defaultdict(set)
for x in real: allm[menu(x)].add(pos(x))
out["whole_bank"] = {"distinct_ordered_menus": len(allm), "ordered_menus_with_two_keys": sum(1 for v in allm.values() if len(v) > 1)}
ab = collections.defaultdict(set)
for x in real: ab[blind(x)].add(norm(x["answer"]))
out["whole_bank"]["distinct_sorted_menus"] = len(ab); out["whole_bank"]["sorted_menus_with_two_keys"] = sum(1 for v in ab.values() if len(v) > 1)
out["key_position_by_form"] = {"%s:%s" % (f, "ABCD"[p]): n for (f, p), n in sorted(collections.Counter((x["strata"]["form"], pos(x)) for x in real).items())}
json.dump(out, open(os.path.join(HERE, "check_menu_2026-11-24.json"), "w"), indent=1, sort_keys=True); print(json.dumps(out, indent=1, sort_keys=True))
