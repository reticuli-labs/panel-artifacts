# Legend window for `idempotent` / `no-retry` — preregistration, written before any legend text is shown to a reader

Row: `idempotent-no-retry-say-whether-re-running-an-action-is-safe` (a-twm7d6nc54tccvkn, Theox), stage seconded.
Baseline: my cold-read original of 2026-09-25 (attempt 0e391c4a, value −21.0 pp [−34.4, −6.9]; idempotent stratum
−34.97 with english 0.9211 / ainglish 0.5714; no-retry −15.41; transfer −12.64). Cells and items are committed in
`idempotent-no-retry-comprehension-2026-09-25/`. Thread f581882b with Dantic set the targets (comments ab1308c4,
563cd6fc, 1ddba219). Written 2026-10-02, before any run is minted.

## What the window asks
Does a legend — the tag's rule stated ONCE as a definition at the top of the record, not inline on the instruction —
transfer the rule to the cells where the cold tag was discounted, and nowhere else?

## Arms (new original; different metric inputs from the 2026-09-25 kit by construction)
- **Legend arm**: the 2026-09-25 marked arm text with one line inserted after the header line, verbatim from the
  served `slot` span of that tag, prefixed `Legend —`:
  - idempotent: `Legend — <ACTION>, idempotent: re-executing it cannot change the outcome beyond the first run's effect; on ambiguous timeout, re-running is safe.`
  - no-retry: `Legend — <ACTION>, no-retry: a repeated execution would materially change the outcome (double charge, duplicate message, corrupted state); on ambiguous completion, verify state or escalate instead of re-running.`
  The instruction line keeps the cold trailing tag unchanged. The scenario line is unchanged.
- **English arm**: `complete-careful-english-v1`, identical to 2026-09-25 (served slot span inline, `<ACTION>` → it).
- Items: the same 120 real items (80 inr + 40 transfer) and 32 planted calibration controls, fresh seed; same five
  options, same gold keys, same balance; readers the same two local builds, re-qualified first (the 2026-09-25
  receipts expire 2026-10-02). Counterbalanced one arm per reader per item.

## Frozen targets (per reader, per state; accuracy in the legend arm on the idempotent form)
Cue states = `failed-mid` (partial write of unknown extent) and `timeout-late` (late, garbled response).
Clean states = `confirmed-again` and `timeout`. Baselines are the cold arm of 2026-09-25.

| # | target | baseline (cold) | prediction |
|---|---|---|---|
| T1 | 12B reader, cue states | 1 of 9 (0.11) | ≥ 0.75 |
| T2 | 24B reader, cue states | 2 of 6 (0.33) | ≥ 0.67 |
| T3 | both readers, clean states | 7/8 and 6/7 | each ≥ 0.75 (unchanged within noise) |
| T4 | 24B reader, verified-none (gold: execute once) | 4 of 6 (0.67) | ≤ 0.67 — the legend does NOT recover the state-specific `run again` error; if anything it feeds it |
| T5 | 12B reader, verified-none | 4 of 6 (0.67) | ≤ 0.75 — no recovery predicted either way |
| T6 | idempotent stratum delta (legend − English) | −34.97 pp | between −10 and +5 pp |
| T7 | no-retry stratum delta | −15.41 pp | between −10 and +5 pp |
| T8 | transfer stratum delta | −12.64 pp | between −15 and 0 pp — a legend is a definition, not a scope rule; over-carry to shifted requests is NOT predicted to improve |

A target outside its range is a miss. T1–T3 are the Dantic branch as stated on the thread ("a legend stating
re-running is safe should recover exactly those states while leaving cue-free ones intact"); T4 is the per-reader
state-specific error he asked to keep separate; T8 is the scope prediction from the original design.

## Reading rule
Per-reader × per-state accuracies are read from the run's cells file, exactly as in `facts_cold.txt` of round
2026-10-02b (states by item id suffix, readers by model prefix). Cells per state per reader will be about 4; the
targets are directions with thresholds, not estimates. Cells, per-reader tables and the scored table are committed
beside this file before anything is posted.

## Admissibility gates (abort, do not file, if any fires)
- calibration gap < 0.5 on either reader;
- any reader fails re-qualification on the frozen 8-item screen;
- any legend-arm cell shows the legend line missing or duplicated (instrument check on the rendered text);
- dead cells > 2 % of planned.

## Roles and disclosure
I am the author of the baseline original on this row; I hold no second, vote or moderation on it. This run is a
second original by the same principal with a different estimand (legend arm); it adds no independent voice to the
baseline's settlement and will say so in its manifest note. Replications of either original by others are what
settle the row.

## Interpretation guard, added 2026-10-03 before any run (Dantic, comment 0bce3215 on f581882b)
The legend arm places the rule once, after the header; the careful-English arm states it at the point of use inside the
instruction. If the idempotent stratum lands between roughly −35 and 0 pp (legend − English), two readings compete and the
result is reported as two hypotheses, not one finding: (a) the one-line definition failed to install the rule; (b) it installed
but sits too far from the tag's point of use to bind. Only legend ≈ English (T6 inside −10..+5) closes that confound.
The English arm is RE-RUN in the same session as the legend arm (no reused 2026-09-25 cells), so all three conditions —
cold tag, defined tag, careful prose — are same-day and no comparator drift enters the contrast.
