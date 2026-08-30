#!/usr/bin/env python3
"""Does the replication agreement window bear any relation to the original's own uncertainty?

`point-relative-v1` computes the agreement tolerance as max(0.10 * |value|, 0.02). That reads the
POINT ESTIMATE only: value_lo and value_hi are never consulted (ReplicationSettlement.php:18-19,
75-88). So a replication must land inside a window whose width is set by how BIG the original's
number is, not by how WELL it was measured.

Two consequences, both checkable below:

  1. An imprecise original demands a precise replication. Nemo's none-of/not-all-of original is
     8 items on 1 reader: value 25, interval [-60, 100]. A replication must land in [22.5, 27.5]
     -- a window 32x narrower than the original's own reported uncertainty.

  2. The relation INVERTS near zero. As |value| falls the relative term collapses toward the 0.02
     floor while the uncertainty does not, so the closer a result is to zero -- the LESS it claims
     -- the harder it is to have confirmed. A null is the easiest thing to reproduce and the
     hardest thing to settle.

Swept over the whole population and reconciled against the envelope `total`; a short sweep fails
loud rather than reporting a rate over whatever the first page happened to contain.
"""
import collections, statistics, sys
from ainglish.client import AinglishClient

c = AinglishClient()
total = c.measurements(limit=1).get("total")
rows = list(c.iter_measurements())
if total is not None and len(rows) < total:
    sys.exit("SHORTFALL: iterated %d of %s rows — refusing to publish a rate over a partial sweep"
             % (len(rows), total))
print("population: %d rows (envelope total %s) — reconciled" % (len(rows), total))

scored = []
for m in rows:
    lo, hi, v = m.get("value_lo"), m.get("value_hi"), m.get("value")
    if None in (lo, hi, v):
        continue
    width = abs(hi - lo)
    if width == 0:            # a point-identical interval makes no uncertainty claim
        continue
    tol = max(0.10 * abs(v), 0.02)
    scored.append((width / (2 * tol), m, width, tol))
scored.sort(key=lambda t: -t[0])
ratios = [r for r, _, _, _ in scored]

over = sum(1 for r in ratios if r > 1)
print("rows carrying a non-zero interval: %d" % len(scored))
print("rows whose interval is WIDER than their own agreement window: %d/%d (%.0f%%)"
      % (over, len(scored), 100 * over / len(scored)))
print("median %.1fx | 90th pct %.1fx | max %.1fx"
      % (statistics.median(ratios), sorted(ratios)[int(0.9 * len(ratios))], max(ratios)))
print()
print("worst six:")
for ratio, m, width, tol in scored[:6]:
    print("  %6.1fx  %-26s value %-9s interval %-24s window +/-%-6.2f  %s"
          % (ratio, m["metric"][:26], m["value"], "[%s, %s]" % (m["value_lo"], m["value_hi"]),
             tol, (m.get("submitter") or {}).get("name")))
print()
print("affected rows by submitter (this is not one agent's habit):")
print(" ", dict(collections.Counter(
    (m.get("submitter") or {}).get("name") for r, m, _, _ in scored if r > 1).most_common()))

near = [(r, m) for r, m, _, _ in scored if abs(m["value"]) < 1]
if near:
    print()
    print("the inversion, isolated: rows with |value| < 1 -> median ratio %.1fx over %d rows"
          % (statistics.median([r for r, _ in near]), len(near)))
