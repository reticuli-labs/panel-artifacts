#!/usr/bin/env python3
"""Is the roster effect confounded by row count?

@dantic's challenge to the 28%->62% split: roster mixing needs multiple rows to be visible at all,
and rows are also where comparator_genre has room to vary, so part of the 34pp gap may belong to
"more rows" with roster as the visible proxy. His pre-specified test: condition on row count and
check whether mixed roster still adds disagreement WITHIN strata. If it does not, the finding was
really "multi-row proposals disagree more".

Deliberately reports the stratum ns beside every rate: this population is small enough that a
stratified rate can be built on a handful of rows, and a percentage over n=4 is not a base rate.
"""
import collections, json, pathlib, sys

RERUN = ("confirmed", "disputed", "confirmed_contested")


def cell(rows_of_props):
    rerun = [r for _, rows in rows_of_props for r in rows if r.get("settle") in RERUN]
    dis = [r for r in rerun if (r.get("disagree") or 0) >= 1]
    return len(rerun), len(dis)


def fmt(n, d):
    return f"{d:2}/{n:<3} ({100*d/n:3.0f}%)" if n else "     n=0    "


def main(path):
    d = json.load(open(path))
    multi = [(s, r) for s, r in d.items() if len(r) >= 2]
    strata = collections.defaultdict(lambda: {"same": [], "mixed": []})
    for slug, rows in multi:
        k = len(rows) if len(rows) < 4 else "4+"
        same = len({tuple(r["models"] or []) for r in rows}) == 1
        strata[k]["same" if same else "mixed"].append((slug, rows))

    order = [k for k in (2, 3, "4+") if k in strata]
    print(f"{'rows':>5}  {'SAME roster':>16}  {'MIXED roster':>16}   difference")
    print("  " + "-" * 60)
    tot = {"same": [0, 0], "mixed": [0, 0]}
    weighted, weight = 0.0, 0.0
    for k in order:
        ns, ds = cell(strata[k]["same"])
        nm, dm = cell(strata[k]["mixed"])
        tot["same"][0] += ns; tot["same"][1] += ds
        tot["mixed"][0] += nm; tot["mixed"][1] += dm
        diff = ""
        if ns and nm:
            pp = 100 * (dm / nm - ds / ns)
            diff = f"{pp:+6.1f}pp"
            w = (ns * nm) / (ns + nm)          # stratum weight, Mantel-Haenszel style
            weighted += pp * w; weight += w
        print(f"{str(k):>5}  {fmt(ns, ds):>16}  {fmt(nm, dm):>16}   {diff}")
    print("  " + "-" * 60)
    print(f"{'pool':>5}  {fmt(*tot['same']):>16}  {fmt(*tot['mixed']):>16}   "
          f"{100*(tot['mixed'][1]/tot['mixed'][0] - tot['same'][1]/tot['same'][0]):+6.1f}pp  (unadjusted)")
    if weight:
        print(f"{'':>5}  {'':>16}  {'row-count-adjusted':>16}   {weighted/weight:+6.1f}pp")
    print()
    print("Row-count distribution (how much room the confound has):")
    for k in order:
        print(f"  rows={k:<3} same-roster proposals {len(strata[k]['same']):3}   "
              f"mixed-roster {len(strata[k]['mixed']):3}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "census.json")
