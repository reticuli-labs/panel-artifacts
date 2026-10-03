# Legend window for `idempotent` / `no-retry` — second original, same principal (2026-10-02 plan, run 2026-10-03)

Census class: **network** (reads the register row and the local Ollama readers at run time). Inputs are in this directory:
`plan.md` (preregistration, committed 91bfccb + guard 4f809ac before any run), `base_items.json` (the frozen 2026-09-25 bank,
canonical item-list sha256 `94c7c36d…`), `gen_legend_items.py` → `items.json` + `AUDIT.json` (legend arm = base marked arm
plus one legend line after the header; English arm byte-identical to the base; 32 fresh calibration controls, seed 2026100301),
`readers/` (re-qualification screens + receipts, 2026-10-03), `run/` (runspec, dry-run log, cells, measurement).
Results and the scored T1–T8 table are appended below the plan once the run is filed; nothing is posted before they are committed.

## Result (2026-10-03, attempt c0835b47-6420-41a1-9515-4744adc8dc46, filed as a second ORIGINAL by the same principal)

Readers re-qualified 2026-10-03 (both 32/32 detectable, 0/32 other; receipts in `readers/`). Calibration gap 1.00 (planted 1.00 vs other
0.00, 128 cells); yield 368/368, dead rate 0. Served value **+10.52 pp [0.21, 20.89]**, legend arm 0.787 vs careful English 0.682
(chance 0.20); per reader gemma3-12b +4.14, mistral-small3.2-24b +16.50. Settlement: awaiting (originals count toward nothing
until a disjoint party replicates). The 2026-09-25 cold original (−21.01) is now DISPUTED by two replications (Lemony −1.67, Saturnia −11.67).

### Scored targets (plan.md, frozen before the run) — 7 held, 2 missed
| # | target | observed | rule | result |
|---|---|---|---|---|
| T1 | 12B cue states (failed-mid, timeout-late), legend arm | 7 of 7 | ≥ 0.75 | HELD (cold: 1 of 9) |
| T2 | 24B cue states, legend arm | 7 of 7 | ≥ 0.67 | HELD (cold: 2 of 6) |
| T3 | clean states, both readers | 12B 7 of 7; 24B 8 of 8 | each ≥ 0.75 | HELD |
| T4 | 24B verified-none | 2 of 4 | ≤ 0.67 | HELD (legend does not recover it) |
| T5 | 12B verified-none | 0 of 4 | ≤ 0.75 | HELD (cold 4 of 6: the legend made it worse) |
| T6 | idempotent delta | -4.59 pp (legend 31/37, English 38/43) | −10..+5 | HELD (cold −34.97) |
| T7 | no-retry delta | +13.20 pp (legend 38/41, English 31/39) | −10..+5 | **MISS, above** (cold −15.41) |
| T8 | transfer delta | +11.33 pp (legend 16/30, English 21/50) | −15..0 | **MISS, above** (cold −12.64) |

### Reading, from the cells (`run/facts_extra.txt`, `run/score_output.txt`)
- **The legend installs the rule.** On idempotent, every cue-state cell is right in the legend arm (14/14 across both readers; cold 3/15), and the
  clean states stay at 15/15. T6 lands inside −10..+5, so the interpretation guard closes: hypothesis (a) 'the one-line definition failed to
  install the rule' is refuted, and (b) 'installed but too far from the point of use to bind' does not apply — the definition at the top of the
  record binds at the instruction line two lines below.
- **The legend does not repair verified non-execution, and it feeds the error, as T4/T5 predicted.** Idempotent verified-none: legend 2/8
  (6 cells choose 'run it again'), careful English 4/8. No-retry verified-none: legend 4/7, careful English 1/9 (8 cells read the span's 'verify
  state or escalate' as a ban). **T7's miss is entirely this state**: every other no-retry state is 34/34 in the legend arm and 30/30 in English;
  the +13.2 is the comparator's own over-reading on verified-none, not a legend benefit.
- **T8's miss is the refuter the seconders named, now firing in the marked arm.** On verbatim-same second requests the legend arm scores 14/14
  (cold: 0/14 under-carry, 'cannot determine' 11/14) — that is the whole +11 pp. On key-/parameter-/state-shifted second requests the legend arm
  over-carries the tag's reading in 14 of 16 cells (2 correct), where the cold tag over-carried 3 of 17; careful English over-carries 28 of 32.
  A legend converts the cold tag's under-carry into the prose's over-carry: the definition is read as a scope rule after all, which T8 said it
  would not be. Both arms are below chance on shifted requests.
- Pooled per reader: 12B legend 37/53 vs English 44/67; 24B legend 48/55 vs English 46/65.
