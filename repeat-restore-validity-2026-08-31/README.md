# repeat-event / restore-state — validity + reference-time follow-up

**Frozen BEFORE inference** (this commit). Items `16d7c54de0ea324f…`, deterministic generator
included — a stranger re-derives the exact bytes with `python3 generate_items.py`.

Discharges the commitment declared in `repeat-restore-comp-2026-08-31/README.md` ("Declared and
deferred, not trimmed silently"): the row's 32 restore-state validity fixtures and the
reference-time-attachment axis, each promised "a committed follow-up filing with their own
manifest".

| | |
|---|---|
| row | `repeat-event-restore-state` (Excelsior) |
| metric | `comprehension_accuracy_delta`, follow-up battery — estimand distinct from the primary form×force grid |
| design | 68 scored (32 invalid fixtures + 8 valid controls + 28 reference-time directives), 12 calibration; 7 strata, never pooled |
| reader | `deepseek/deepseek-v4-flash` via `nous-portal-direct` |
| refutation served | "accept more than 5% of invalid state arguments as licensed" — acceptance = choosing the supports option on an invalid fixture, reported per arm from the cells file |

Design notes:
- **Valid controls exist so blanket rejection is visible.** Without them a reader that always
  refuses scores 100% on the 32 invalid fixtures and the audit measures nothing.
- **The three options are mutually exclusive and each factually decidable** (single qualifying
  span / no qualifying span / two conflicting spans): first drafts keyed "ambiguous" against a
  question whose literal reading made "supports" defensible — caught at spot-check, options
  reworded before freeze.
- **Reference time is the row's own mapping**: "before the reference time supplied by the scoped
  clause" — for a directive that is the stated execution time, so a span scheduled between
  utterance and execution qualifies. The careful-English arm states this explicitly; the marked
  arm must derive it from the marker. `rt:none` cells keep a blanket "satisfied" strategy visible.
- **Anti-ceiling** (standing rule from rows 1–2): non-entailed contexts are tempting near-misses
  (a deployed fix with falling error rates is not "ran clean"), so the careful arm is not pinned
  to 1.00.

## Reproduce

```
python3 generate_items.py > items.json   # byte-stable
ainglish-panel run runspec.json --dry-run
```
