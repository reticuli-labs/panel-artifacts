# Result — run 2

**The positive control passed and the effect is not distinguishable from zero.**

| | |
|---|---|
| `comprehension_accuracy_delta` | **+6.33 pp** |
| interval | **[−10.91, +23.86]** — **includes zero** |
| ainglish (marked) arm | 0.7397 |
| english (bare) arm | 0.6765 |
| chance | 0.3333 |
| panel agreement | 0.7612 |
| cells | 180 — 3 empty, **0 unparsed**, dead rate 1.67% |

## Calibration (positive control)

`planted_arm: ainglish`, detectable **0.8889** vs other **0.2778**, gap **0.6111** against a `min_gap` of 0.50 — **passed**. The instrument can see a planted effect at this bound, so the wide interval below is a statement about the items and readers, not about a broken harness.

## Why the headline is the interval, not the point estimate

+6.33 pp is the point estimate. The interval spans zero comfortably in both directions, so **this panel does not establish that the marking improves comprehension.** It also does not establish that it doesn't. Reporting "marking helps by 6.33 pp" from this table would be one step stronger than the table supports.

The per-reader spread is where the width comes from:

| reader | delta |
|---|---|
| command-r-35b | +3.48 |
| gemma4-31b | +2.27 |
| qwen3.6-27b | **+13.59** |

All three agree on the **sign**, which is a weak consistency signal worth stating. But the magnitudes differ by about 6×, and a single reader carries most of the effect. Sign agreement across three readers is not the same quantity as a settled effect size, and pooling them into one scalar is what makes the interval honest rather than what makes it wide.

Down-resampling is stable — 75% of items → +8.84, 50% → +4.84, no sign flips, neither outside the interval — so the result is not an artifact of a few items. Stability of an indistinguishable-from-zero estimate is still indistinguishable from zero.

## Pre-registered conditions

- **withdraw-if-bare ≥ 0.85** — **not triggered.** The bare arm scored **0.6765**, so the unmarked form does not already carry the information and the construct is not redundant on this evidence.
- **amend-if-flip ≥ 15%** — does not apply to this metric; that condition attaches to `unclaimed_verdict_flips`, not to a comprehension panel.

## Provenance

Item set frozen at `3c3da66` and asserted byte-identical by the runner before any cell was bought (`sha256(items)[:16] == b96205495729d261`). Run 1 refused at the calibration gate with zero real cells; the refusal envelope, the amendment and its probe table were committed at `c7f2b0b` **before** run 2 started. Transport bounds for this run: `max_tokens 3072`, `timeout_s 400`, uniform across all three readers.
