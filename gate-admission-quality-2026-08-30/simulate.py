#!/usr/bin/env python3
"""False-admit and false-refuse rates for both calibration gates, under KNOWN mechanisms.

@excelsior's point on the protocol thread: the row contains two claims, and its declared evidence
establishes only the first.

  1. COMPATIBILITY -- the headroom rule is monotone with respect to the old default, so previously
     admitted work cannot silently flip. Settled by algebra plus the zero-flip blast table.
  2. ADMISSION QUALITY -- panels NEWLY admitted by the relative rule deserve admission.
     `unclaimed_verdict_flips = 0` cannot establish this, because it only observes the OLD
     population. The 23.4% of panels the new rule newly admits are exactly the ones it says
     nothing about.

This measures claim 2 by simulation, because the failure mechanisms can be constructed rather than
guessed at. Every reader here has a known generative truth, so "should this panel have been
admitted?" is decidable rather than a judgement call.

  GROUND TRUTH: a panel deserves admission iff the marker actually changes the reader's behaviour,
  i.e. the generating p_marked differs from the generating p_bare. A reader whose two arms are
  driven by the SAME probability is detecting nothing, however its sample happens to land.

  false admit  = gate admits a panel whose generating arms are identical
  false refuse = gate refuses a panel whose marker carries the reader from its bare rate to ~1.0

No network, no credential, no cost. Uses the SHIPPED gate, imported, never a local restatement.
"""
import argparse
import json
import random
import statistics
import sys

from ainglish.panel import calibration_verdict, CALIBRATION_MIN_GAP, CALIBRATION_MIN_RECOVERED

OLD_MIN_GAP = 0.5  # the superseded constant-gap default


def old_gate(planted, bare):
    return (planted - bare) >= OLD_MIN_GAP


def new_gate(planted, bare):
    return calibration_verdict(planted, bare)["passed"]


def sample_arm(p, n, rng):
    """n independent scored cells at true rate p -> the observed accuracy."""
    return sum(1 for _ in range(n) if rng.random() < p) / n


MECHANISMS = {
    # name: (p_bare, p_marked_or_None, deserves_admission)
    # -- NO MARKER EFFECT: both arms driven by one rate. Admission is always an error.
    "uniform guessing (chance both arms)": ("chance", "chance", False),
    "skewed guessing (biased, both arms)": (0.62, 0.62, False),
    "context fully recoverable (both arms high)": (0.95, 0.95, False),
    # -- REAL MARKER EFFECT: the marker carries the reader to near-certainty. Refusal is an error.
    "true detector off a chance floor": ("chance", 0.98, True),
    "true detector off a leaky floor": (0.50, 0.98, True),
    "true detector off a high floor": (0.80, 0.98, True),
}


def run(trials, seed):
    rng = random.Random(seed)
    rows = []
    for n_items in (4, 8, 12, 24):
        for n_options in (2, 3, 4):
            chance = 1.0 / n_options
            for name, (bare_p, marked_p, deserves) in MECHANISMS.items():
                bare_p = chance if bare_p == "chance" else bare_p
                marked_p = chance if marked_p == "chance" else marked_p
                old_admits = new_admits = 0
                for _ in range(trials):
                    bare = sample_arm(bare_p, n_items, rng)
                    marked = sample_arm(marked_p, n_items, rng)
                    old_admits += old_gate(marked, bare)
                    new_admits += new_gate(marked, bare)
                rows.append({
                    "items": n_items, "options": n_options, "chance": round(chance, 4),
                    "mechanism": name, "deserves_admission": deserves,
                    "old_admit_rate": old_admits / trials,
                    "new_admit_rate": new_admits / trials,
                })
    return rows


def summarise(rows):
    out = {}
    for gate in ("old", "new"):
        key = "%s_admit_rate" % gate
        false_admit = [r[key] for r in rows if not r["deserves_admission"]]
        false_refuse = [1 - r[key] for r in rows if r["deserves_admission"]]
        out[gate] = {
            "false_admit_mean": round(statistics.mean(false_admit), 4),
            "false_admit_max": round(max(false_admit), 4),
            "false_refuse_mean": round(statistics.mean(false_refuse), 4),
            "false_refuse_max": round(max(false_refuse), 4),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=20260830)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = run(args.trials, args.seed)
    summary = summarise(rows)
    report = {
        "kind": "ainglish.gate-admission-quality.v1",
        "trials_per_cell": args.trials, "seed": args.seed,
        "old_gate": {"rule": "gap >= %s" % OLD_MIN_GAP},
        "new_gate": {"rule": "gap >= %s and recovered >= %s"
                             % (CALIBRATION_MIN_GAP, CALIBRATION_MIN_RECOVERED)},
        "summary": summary, "cells": rows,
    }
    if args.json:
        print(json.dumps(report, indent=1))
        return 0

    print("FALSE ADMIT — gate admits a panel whose two arms are driven by the SAME rate")
    print(f"{'items':>5} {'opts':>5}  {'mechanism':<44} {'old':>7} {'new':>7}")
    for r in rows:
        if r["deserves_admission"]:
            continue
        print(f"{r['items']:5} {r['options']:5}  {r['mechanism']:<44} "
              f"{r['old_admit_rate']:7.3f} {r['new_admit_rate']:7.3f}")
    print()
    print("FALSE REFUSE — gate refuses a panel whose marker carries the reader to ~1.0")
    print(f"{'items':>5} {'opts':>5}  {'mechanism':<44} {'old':>7} {'new':>7}")
    for r in rows:
        if not r["deserves_admission"]:
            continue
        print(f"{r['items']:5} {r['options']:5}  {r['mechanism']:<44} "
              f"{1-r['old_admit_rate']:7.3f} {1-r['new_admit_rate']:7.3f}")
    print()
    for gate in ("old", "new"):
        s = summary[gate]
        print(f"{gate:>4} gate: false-admit mean {s['false_admit_mean']:.4f} "
              f"(max {s['false_admit_max']:.4f})   false-refuse mean {s['false_refuse_mean']:.4f} "
              f"(max {s['false_refuse_max']:.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
