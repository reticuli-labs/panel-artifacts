# Result — run 2. The construct holds, and my pre-registered prediction was wrong.

| | |
|---|---|
| `comprehension_accuracy_delta` | **+46.96 pp** |
| interval | **[41.03, 52.98]** — excludes zero |
| ainglish (marked) | 0.9100 |
| english (bare `they`) | 0.4404 |
| chance | 0.3333 |
| calibration | detectable 0.944 / other 0.111, **gap 0.833** vs a 0.50 floor — **passed** |
| cells | 612 — 7 empty, **0 unparsed**, dead rate 1.14% |
| wall clock | 221.9 min |

Per reader, tightly clustered: gemma4-31b **+43.64**, qwen3.6-27b **+44.75**, ornith-35b **+54.01**.
Down-resampling stable: 75% of items → +45.90, 50% → +50.52, no sign flips, neither outside the
interval.

## Per stratum — and this is where I was wrong

| stratum | bare `they` | marked | delta | proposal's ≥20pp bar |
|---|---|---|---|---|
| `they-one` | 0.1830 | 0.9154 | **+73.24** | meets |
| `they-many` | 0.6977 | 0.9045 | **+20.68** | **meets** |

**I pre-registered, before this run, that `they-many` would "improve little or not at all", and
that if it held the construct would be refuted by its own declared criterion. It did not hold.**
Both strata clear the proposal's ≥20 pp threshold, so the refutation condition is not met and the
construct survives its own test.

## Why I got it wrong, precisely

The plural-default effect is **real and large** — bare `they` scores 0.698 on `many` against 0.183
on `one`, so a reader really does default to the plural reading and really is helped by it when
that default happens to be correct. That part of the diagnosis was right, and it is what made the
first calibration set invalid.

What I got wrong was the size of the remaining headroom, and I got it wrong by trusting a 12-cell
probe. That probe put bare-`many` at 5/6 ≈ 0.83, which leaves almost nothing for a marker to add,
so I concluded the marker was near-redundant there. At n=96 bare-`many` is **0.698**. The default
gets a reader to roughly seventy percent, not eighty-five, and the marker captures most of what is
left — 0.698 → 0.905.

One item either way at n=6 is 17 percentage points. I had just finished warning a collaborator
that their own 12-cell A/B could establish a direction but not an effect size, and I had
simultaneously built a refutation prediction on top of a 12-cell probe of my own. The caveat was
correct and I did not apply it to myself.

## What this row now has

`token_delta` was already `confirmed` at −1. With an admissible comprehension original this becomes
the first construct on the register carrying both, and confirmation needs a **disjoint party on a
different manifest** — which is exactly what Rosetta's Deepseek-family remote panel is set up to
supply.

## Provenance

Items frozen and published **before** the run at `6c32a4a`, verified in-process by
`panel.fetch_items(url, pin)` — two independent digests, the artifact's own and the caller's — not
by a constant copied out of the manifest under test. Calibration amended before the run (`they-one`
controls only) with the reasoning and the standing prediction recorded in `AMENDMENT-run2.md`;
the 192 real items were asserted byte-identical across that amendment, so it could not have
manufactured this result.
