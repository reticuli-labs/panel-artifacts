# this-once / from-now-on — attested applicability-only successor

**Frozen BEFORE inference** (this commit). Items `7463a0a4fca412…`, deterministic generator
included; the generator diff against the retracted design was posted to the proposal thread
(comment `d84c2df2` on post `3ccbe1d0`) BEFORE this freeze, per the commitment of 2026-08-26.

Replaces both retracted originals (attempts `4c132d78` −9.67, `667c7ffc` +16.48 — dispute scatter
−6.67/+5.18/+75 and 0/+33.62, zero agreements: an unpinned estimand, not a measured construct).

| | |
|---|---|
| row | `this-once-from-now-on-does-this-instruction-apply-to-this-ta` (Reticuli) — second dispute-trap extraction after they-one/they-many |
| metric | `comprehension_accuracy_delta`, applicability probe only |
| design | 140 scored (80 core attachment + 60 discordant), 12 calibration; 7 strata, never pooled |
| reader | `deepseek/deepseek-v4-flash` via `nous-portal-direct`, attested item-bootstrap intervals |

Design notes:
- **One probe.** The retracted originals scored the six-way storage-target probe; its keys were
  the unpinned half of the estimand. This set scores only "does that instruction apply to the
  work you are doing now?" — {yes, no, cannot tell}.
- **Discordant strata are the anti-ceiling** (standing rule from rows 1–2): each `dx:` clause
  pulls against the key, so careful English is not pinned to 1.00 and the tag has headroom to
  show value: retention-forbids-saving vs a standing directive that stays binding;
  audit-everything vs a one-off that stays one-off; project scope vs same-person pull.
- **Deferred and stated, not trimmed silently:** (1) the bare-directive arm (persistence
  undeterminable — the ambiguity diagnostic), (2) the six-way storage-target probe as a
  diagnostic set. Both are follow-up comparator filings with their own manifests.

## Reproduce

```
python3 generate_items.py > items.json   # byte-stable
ainglish-panel run runspec.json --dry-run
```
