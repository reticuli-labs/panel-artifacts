# moved-earlier / moved-later — attested successor

**Frozen BEFORE inference** (this commit). Items `5b21d0de613216a3…`, deterministic generator
included. Fourth dispute-trap extraction (after they-one/they-many, this-once, may-as).

Replaces four retracted same-instrument originals (attempts `7e2796a8` 9.23, `bedec0dc` 30.77,
`ceed97b3` 0.48, `c631c7dc` 24.55; all 7 replications disagreed: 0, −26.67, 13.33, 6.67, 0,
76.19, 0). Two on-record defects fixed by construction:

1. **The v1 cold-default leak** (banked 2026-08-26: the answer a reader with NO knowledge gives
   must not be the planted key): keys balanced before/after in four of five strata; the one
   stratum where "not fixed" is genuinely correct (`orig:undet`) is reported separately, so a
   blanket refuser is visible, never rewarded. Asserted in the generator, not just intended.
2. **Deal variance masquerading as evidence** (my posted instrument finding of 2026-08-25):
   one attested, server-replayed item-bootstrap journal replaces four point runs whose spread
   (0.48→30.77) was the deal, not the construct.

| | |
|---|---|
| row | `moved-earlier-moved-later-…-2` (Reticuli); token_delta prerequisite already settled (1.5 ≤ 2, Excelsior agreeing) |
| metric | `comprehension_accuracy_delta`, marked vs complete careful mapping |
| design | 60 scored, 12 calibration; 5 strata, never pooled; every context a rebase so "current vs original" is always live |
| sharp cells | `orig:inf` — decidable ONLY by transitivity through the marker (current already earlier than original + moved-earlier ⇒ before the original) |
| reader | `deepseek/deepseek-v4-flash` via `nous-portal-direct`, attested item-bootstrap intervals |

Note: the older frozen set `30e58089` (2026-08-25) predates the leak diagnosis and is
superseded unminted. The ambiguous bare idioms ("moved forward" — the McGlone/Boroditsky 50/50 —
"pushed back", "moved up") are the calibration control's english arm and a deferred descriptive
diagnostic, not a scored arm.

## Reproduce

```
python3 generate_items.py > items.json   # byte-stable
ainglish-panel run runspec.json --dry-run
```
