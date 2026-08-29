# Amendment: transport bounds raised after a calibration refusal

**Status of run 1: REFUSED at the calibration gate. Zero real cells bought (144 saved).**
The refusal envelope is committed verbatim as `REFUSAL-run1.json`.

## What the gate caught

`gemma4-31b` produced **no live answer** on 3 of its 12 calibration cells:
`cal-2/ainglish`, `cal-5/english`, `cal-6/ainglish`. The other two readers passed all 12 each.

The refusal carried `"transport_faults": {}` — nothing failed at the wire. So the reader was
reached, answered, and the answer was unreadable. That points at truncation, not the network.

## The diagnosis, run against the three named cells

Direct probe, same prompts, same temperature 0, only the bound varied:

| cell | max_tokens | wall | finish_reason | output |
|---|---:|---:|---|---|
| cal-2 / ainglish | 1024 | 88.7s | `length` | `''` |
| cal-2 / ainglish | 3072 | 58.4s | `stop` | `'A'` |
| cal-5 / english | 1024 | 40.0s | `length` | `''` |
| cal-5 / english | 3072 | 59.9s | `stop` | `'C'` |
| cal-6 / ainglish | 1024 | 39.0s | `length` | `''` |
| cal-6 / ainglish | 3072 | 48.6s | `stop` | `'A'` |

gemma4 reasons before answering. At 1024 it spent the whole budget thinking and never reached the
option list, so the harness saw an empty completion — the failure mode the module's own comment
names for reasoning readers. This is the third distinct instance in this project of a thinking
reader being silently censored by an answer budget (after Ornith-35B and Seed-OSS, both of which
genuinely exhaust 1024 and stay unusable at it).

## The amendment

`max_tokens` 1024 → **3072** and `timeout_s` 120 → **400**, declared per panel entry in
`gun_manifest_run2.json`, applied **uniformly to all three readers**.

Both bounds move together because they are not independent. gemma4 generated 1024 tokens in 88.7s
(≈11.5 tok/s), so a cell that actually consumed 3072 would take ≈265s and die against the 120s
timeout — raising the answer budget alone would just convert a truncation into a transport fault.

Uniform rather than gemma4-only: an answer budget is an instrument setting, and a bound that
differs across members makes the panel three instruments instead of one. A ceiling only binds when
it is hit, so at temperature 0 the two readers that already answered inside 1024 emit identical
text at 3072; what changes is only that truncation stops censoring the third.

## What is NOT amended

The item set. `sha256(manifest['items'])[:16] == b96205495729d261`, byte-identical to the freeze at
`3c3da66`, asserted in code — `run_gun_panel.py` aborts before buying a cell if it drifts. Items,
arms, seed (29), planted arm (`ainglish`), comparator and answer key are all untouched.

Re-running is legitimate here for one specific reason, and it is worth stating rather than
assuming: **no real cell was ever observed.** The gate fired before the first purchase, so there is
no result to have been shaped by seeing it. Had run 1 produced cells, this amendment would be
result-shaping and the honest move would be to report run 1 and stop.
