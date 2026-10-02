# Re-deriving 32 un-rederived token rows — result (2026-10-02)

Plan and sample frozen first (`plan.md`, `sample.json`, commit fc95bc5). Then `rederive.py` (rev 2 — the first run read the
wrong result key, `value` instead of `floor`, and did not normalise legacy encoding names such as `tiktoken/cl100k_base`,
`cl100k_base@0.13.0`, `cl100k_base@vocab`; the rule was not changed; the first run's output is not used).

## Result (`results.json`)
- **match 31**, mismatch 0, not derivable 1 (manifest has no usable `test_set`; keys ['construct', 'environment', 'estimand', 'formula_version', 'item_counts', 'items_sha256', 'items_url', 'method', 'metric', 'models', 'seed', 'settlement_strata', 'source', 'test_set_note']).
- Of the 31 matches, 25 are exact and 6 agree only to the filed rounding (filed values carry 3–4 decimals; the
  SDK derives the exact dyadic/repeating value). At the register's own tolerance of 1e-12 those 6 would read as
  mismatches for rounding alone — which is why the rule here used 0.01.
- Submitters in the sample: 9 distinct; 8 rows by me. `attempt.backfilled`: {'True': 16, 'False': 16}.
- Wilson 95% interval on 0 of 31 mismatching: -0.0–11.0 percent of the derivable legacy population.

## Prediction scored
I predicted 2–8 mismatches of 32. **Miss** (0). The hand sweeps of early September already removed the mismatching rows
from `valid` (57 are `result_invalid`), so what remains valid and un-rederived re-derives, at least in this sample.

## What this does and does not say
It bounds the mismatch rate of the *current* un-rederived valid population; it says nothing about deterrence, since the
marked and unmarked populations were not randomly assigned — the unmarked one has been hand-audited for a month.
