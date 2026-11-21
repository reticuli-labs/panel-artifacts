"""audit_isolation.py <items.json> [--json=out.json]: does the key of each item depend on the STATEMENT, or can it be had from the
shared world facts alone? Offline, read-only.

The class (Dexagon's retractions of 2026-10-11 and 2026-11-07 on mean-outcome / likeliest-outcome; Saturnia's check of 2026-10-10):
both arms of an item share one world and one x; the arms differ only in the wording of one statement; if a rule that never reads
that statement recovers the key, the item cannot show whether the statement was understood.

Everything is parsed from the ENGLISH ARM'S TEXT up to the word 'Statement:' (the part both arms share), never from the stored
oracle, so the audit reads what a reader was shown. The stored oracle is used once, at the end, as a cross-check of my parser.

Three measures over the real (non-calibration) items:
  A. counterfactual dependence: with the same world and x, would the key differ if the statement asserted the OTHER statistic?
     Items where it would not are statement-independent by construction.
  B. the fixed rule named in Dexagon's audit: claim true if x is the mean OR x is a most probable value; other flags from the world.
  C. the best statement-blind rule over the world features (x is mean, x is a mode, x is the only mode, x possible, x certain):
     for each feature cell the most common key. No rule that reads only those features can score higher.
PLANT=1 runs the same code on a planted bank where every key depends on the statement, and must report dependence on all of it."""
import collections, json, os, re, sys
from fractions import Fraction as F

YN = lambda b: "yes" if b else "no"


def opt(flags):
    return "Claim true: %s; x possible: %s; x unique most probable: %s; next result guaranteed x: %s." % tuple(YN(b) for b in flags)


def parse(shared):
    """World and x from the text both arms share."""
    paths = [(int(v), F(m)) for v, m in re.findall(r"value (-?\d+) units with mass (\d+/\d+|\d+)", shared)]
    assert paths and sum(m for _, m in paths) == 1, shared[-300:]
    xm = re.findall(r"Here x = (-?\d+(?:/\d+)?) units\.", shared); assert len(xm) == 1, xm
    agg = collections.OrderedDict()
    for v, m in paths: agg[v] = agg.get(v, 0) + m
    mean = sum(F(v) * m for v, m in agg.items()); top = max(agg.values()); modes = sorted(v for v, m in agg.items() if m == top)
    return agg, mean, modes, F(xm[0])


def world_flags(agg, mean, modes, x):
    possible = x.denominator == 1 and int(x) in agg
    return possible, (len(modes) == 1 and possible and int(x) == modes[0]), (possible and agg[int(x)] == 1)


def key(stratum, agg, mean, modes, x):
    claim = (x == mean) if stratum == "mean-outcome" else (x in [F(m) for m in modes])
    return opt((claim,) + world_flags(agg, mean, modes, x))


def audit(items):
    real = [i for i in items if not i.get("calibration")]
    rows = []
    for i in real:
        en, ai = i["english"], i["ainglish"]
        assert en.count("Statement: ") == 1 and ai.count("Statement: ") == 1
        shared, st_en = en.split("Statement: "); shared_ai, st_ai = ai.split("Statement: ")
        assert shared == shared_ai, "the arms differ before the statement: " + i["id"]
        agg, mean, modes, x = parse(shared)
        # which statistic the statement asserts, read from the statement alone
        s_en = "mean-outcome" if "probability-weighted mean is" in st_en else "likeliest-outcome" if "highest outcome probability" in st_en else None
        s_ai = "mean-outcome" if "is mean-outcome(" in st_ai else "likeliest-outcome" if "is likeliest-outcome(" in st_ai else None
        assert s_en and s_en == s_ai == i["settlement_stratum"], i["id"]
        k = key(s_en, agg, mean, modes, x); assert k == i["answer"], ("my parser disagrees with the stored key", i["id"])
        other = "likeliest-outcome" if s_en == "mean-outcome" else "mean-outcome"
        k_other = key(other, agg, mean, modes, x)
        feats = (x == mean, x in [F(m) for m in modes]) + world_flags(agg, mean, modes, x)
        rule_b = opt(((x == mean) or (x in [F(m) for m in modes]),) + world_flags(agg, mean, modes, x))
        rows.append({"id": i["id"], "stratum": s_en, "variant": i.get("variant"), "boundary": i.get("boundary"), "key": k, "key_if_other_statistic": k_other,
                     "depends_on_statement": k != k_other, "rule_b": rule_b, "rule_b_right": rule_b == k, "features": [bool(f) for f in feats]})
    n = len(rows); dep = [r for r in rows if r["depends_on_statement"]]
    cells = collections.defaultdict(collections.Counter)
    for r in rows: cells[tuple(r["features"])][r["key"]] += 1
    best = sum(c.most_common(1)[0][1] for c in cells.values())
    cells_dep = collections.defaultdict(collections.Counter)
    for r in dep: cells_dep[tuple(r["features"])][r["key"]] += 1
    best_dep = sum(c.most_common(1)[0][1] for c in cells_dep.values())
    out = {"real_items": n, "A_key_depends_on_statement": len(dep), "A_key_independent_of_statement": n - len(dep),
           "A_by_variant": {str(v): [sum(1 for r in rows if r["variant"] == v and r["depends_on_statement"]), sum(1 for r in rows if r["variant"] == v)] for v in sorted({r["variant"] for r in rows}, key=str)},
           "A_by_stratum": {s: [sum(1 for r in rows if r["stratum"] == s and r["depends_on_statement"]), sum(1 for r in rows if r["stratum"] == s)] for s in sorted({r["stratum"] for r in rows})},
           "B_rule_mean_or_mode_right": sum(r["rule_b_right"] for r in rows), "B_right_among_dependent": sum(r["rule_b_right"] for r in dep),
           "C_best_statement_blind_rule_right": best, "C_feature_cells": len(cells), "C_right_among_dependent": best_dep,
           "C_mixed_cells": {" ".join(YN(f) for f in k): dict(v) for k, v in cells.items() if len(v) > 1}}
    return out, rows


def planted(items):
    """A bank where EVERY key depends on the statement: every x is the mean and not a mode, or a mode and not the mean."""
    out = []
    for n, i in enumerate(x for x in items if not x.get("calibration")):
        shared = i["english"].split("Statement: ")[0]; agg, mean, modes, x = parse(shared)
        if mean == F(modes[0]) or (mean.denominator == 1 and int(mean) in modes): continue
        stratum = ("mean-outcome", "likeliest-outcome")[n % 2]; xx = mean if n % 4 < 2 else F(modes[0])
        sh = re.sub(r"Here x = (-?\d+(?:/\d+)?) units\.", "Here x = %s units." % (xx if xx.denominator > 1 else xx.numerator), shared)
        st_en = "Under M, the probability-weighted mean is x units." if stratum == "mean-outcome" else "Under M, x units has the highest outcome probability, ties allowed."
        st_ai = "x units is %s(M)." % stratum
        out.append({"id": "plant-%d" % n, "english": sh + "Statement: " + st_en, "ainglish": sh + "Statement: " + st_ai, "settlement_stratum": stratum, "variant": "plant", "boundary": i.get("boundary"),
                    "answer": key(stratum, agg, mean, modes, xx)})
    return out


if __name__ == "__main__":
    items = json.load(open(sys.argv[1], encoding="utf-8")); items = items.get("items", items) if isinstance(items, dict) else items
    if os.environ.get("PLANT") == "1":
        p = planted(items); o, rows = audit(p)
        assert o["real_items"] == len(p) > 50 and o["A_key_depends_on_statement"] == len(p), o
        assert o["C_best_statement_blind_rule_right"] < len(p), o
        print("PLANT ok: %d planted items, key depends on the statement in %d, best statement-blind rule %d" % (len(p), o["A_key_depends_on_statement"], o["C_best_statement_blind_rule_right"]))
        sys.exit(0)
    o, rows = audit(items)
    print(json.dumps(o, indent=1))
    for a in sys.argv[2:]:
        if a.startswith("--json="): json.dump({"summary": o, "rows": rows}, open(a.split("=", 1)[1], "w", encoding="utf-8"), indent=1)
