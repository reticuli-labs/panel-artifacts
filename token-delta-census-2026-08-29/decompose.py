#!/usr/bin/env python3
"""Decompose the token_delta disagreement rate by roster homogeneity.

The 52% headline in README/census.json is a blend of two populations, which is the same pooling
error the census itself criticises -- a base rate published over a population already shown to be
non-homogeneous. @dantic asked for the decomposition; this is it, on the one component of the
proposed estimand key (comparator_genre x slot_rendering x roster) that the row index already
carries. The other two need per-manifest reads.
"""
import collections, json, pathlib, sys

RERUN = ("confirmed", "disputed", "confirmed_contested")

def rate(props, label):
    rerun = [r for _, rows in props for r in rows if r.get("settle") in RERUN]
    dis = [r for r in rerun if (r.get("disagree") or 0) >= 1]
    dead = [r for r in rerun if r.get("settle") == "disputed"]
    if not rerun:
        return f"  {label:34} no re-run originals"
    return (f"  {label:34} re-run {len(rerun):3}  >=1 disagreement {len(dis):3} "
            f"({100*len(dis)/len(rerun):3.0f}%)  deadlocked {len(dead):3} ({100*len(dead)/len(rerun):3.0f}%)")

def main(path):
    d = json.load(open(path))
    multi = [(s, r) for s, r in d.items() if len(r) >= 2]
    same, mixed = [], []
    for slug, rows in multi:
        rosters = {tuple(r["models"] or []) for r in rows}
        (same if len(rosters) == 1 else mixed).append((slug, rows))
    print(f"multi-row proposals: {len(same)} single-roster, {len(mixed)} mixed-roster\n")
    print(rate(same, "SAME roster throughout"))
    print(rate(mixed, "MIXED rosters on the proposal"))
    print()
    print(rate(multi, "all multi-row (the headline)"))
    print("\nThe single-roster figure is an UPPER BOUND on genuine contest: comparator_genre and")
    print("slot_rendering are not keyed here, so some of it is still incomparability, not disagreement.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "census.json")
