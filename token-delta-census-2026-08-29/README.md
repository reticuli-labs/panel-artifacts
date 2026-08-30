
## Decomposition by roster (added 2026-08-30, after @dantic)

The 52% headline is a blend of two populations, and publishing it as one number is the same pooling
error this census criticises elsewhere:

```
SAME roster throughout      re-run  29   >=1 disagreement   8 (28%)   deadlocked   7 (24%)
MIXED rosters               re-run  74   >=1 disagreement  46 (62%)   deadlocked  33 (45%)
----------------------------------------------------------------------------------------------
all multi-row (headline)    re-run 103   >=1 disagreement  54 (52%)   deadlocked  40 (39%)
```

**RETRACTED 2026-08-30 — the roster reading does not survive conditioning.** @dantic predicted
this gap was confounded by proposal size: roster mixing needs multiple rows to be visible at all,
so "mixed roster" is largely a proxy for "more rows". His pre-specified test — condition on row
count, check whether roster still adds disagreement within strata — was run with `confound.py`:

```
 rows       SAME roster      MIXED roster   difference
    2      2/19  ( 11%)      0/7   (  0%)    -10.5pp
    3      2/4   ( 50%)      4/6   ( 67%)    +16.7pp
   4+      4/6   ( 67%)     42/61  ( 69%)     +2.2pp
------------------------------------------------------------
 pool      8/29  ( 28%)     46/74  ( 62%)    +34.6pp  (unadjusted)
                         row-count-adjusted     -0.1pp
```

**Row-count-adjusted, the roster effect is -0.1pp — it is gone.** The 34.6pp pooled gap is
confounding: same-roster rows sit mostly in 2-row proposals (19 of 29), mixed-roster rows mostly in
4+-row proposals (61 of 74). What actually moves is proposal size, and it moves a lot:

```
Per-ROW disagreement rate by proposal size (roster ignored):
  rows=2     2/26  (  8%)
  rows=3     6/10  ( 60%)
  rows=4+   46/67  ( 69%)
```

So the correct statement is **"rows in larger proposals attract disagreement far more often"**, with
roster as the visible proxy — which is what @dantic said would be the case. The earlier claim on
this page was a pooled comparison across a non-homogeneous population, i.e. exactly the error the
census criticises elsewhere, committed one section further down the same document.

Two honest limits on the correction itself: several strata are small (rows=3 has 4 and 6 rows;
rows=4+ same-roster has 6), and rows are clustered within proposals, so the adjusted estimate is
less precise than its single number suggests. It does not establish that roster never matters. It
establishes that this population does not support the claim that it does, and the burden was on the
claim. Re-derive with `decompose.py` (pooled) and `confound.py` (stratified).

The 28% single-roster figure is an **upper bound on genuine contest**, not a measurement of it:
roster is one of three components in the proposed estimand key, and `comparator_genre` and
`slot_rendering` need per-manifest reads the row index does not carry. What survives all three keys
is the number that deserves to be called disagreement.
