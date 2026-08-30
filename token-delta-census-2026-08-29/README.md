
## Decomposition by roster (added 2026-08-30, after @dantic)

The 52% headline is a blend of two populations, and publishing it as one number is the same pooling
error this census criticises elsewhere:

```
SAME roster throughout      re-run  29   >=1 disagreement   8 (28%)   deadlocked   7 (24%)
MIXED rosters               re-run  74   >=1 disagreement  46 (62%)   deadlocked  33 (45%)
----------------------------------------------------------------------------------------------
all multi-row (headline)    re-run 103   >=1 disagreement  54 (52%)   deadlocked  40 (39%)
```

**Roster heterogeneity more than doubles the disagreement rate.** Re-derive with `decompose.py`.

The 28% single-roster figure is an **upper bound on genuine contest**, not a measurement of it:
roster is one of three components in the proposed estimand key, and `comparator_genre` and
`slot_rendering` need per-manifest reads the row index does not carry. What survives all three keys
is the number that deserves to be called disagreement.
