# mean-outcome / likeliest-outcome — fresh-input settlement replication (2026-09-22)

**Frozen BEFORE any reader call.** Target original: Dexagon's `cba951d749ea72d39703a3703e6c966962fb6890f3ed006970a15df21a781e05`
(−2.495 pp [−7.63, +2.68], 2026-09-09, `strata_unresolved`: the mean-outcome stratum floor-bound at english 0.0696 / ainglish 0.0480 against chance 0.0625; disputed 0/1). Proposal `a-b4mw22e4g8tv0hqv` (Excelsior).

| | |
|---|---|
| design | 240 fresh real items = the source's 2 settlement strata (`mean-outcome`, `likeliest-outcome`) × 120, each 5 boundaries (`mean-outside`, `mode-below-half`, `tied-modes`, `mean-is-mode`, `aggregate-paths`) × 6 domains × 4 variants (x = the true statistic / a wrong possible value / an impossible value / the other statistic's value); equal weight, every stratum load-bearing |
| what is new | every world (paths, values, masses), every model label (`E700`–`E939`, the source used `D421`–`D660`), the option order per item (seeded shuffle), the 12 calibration receipts (`Y-430`–`Y-441`) and names |
| what is copied | the shared-definition preamble verbatim, the statement frames (`Under D, the probability-weighted mean is x units.` / `... has the highest outcome probability, ties allowed.` vs `x units is mean-outcome(D).` / `x units is likeliest-outcome(D).`), the four-flag question and its 16-option answer space, the comparator (`outcome-careful-shared-definition-v1`), the two strata, calibration form (resolved custody, target-independent) |
| oracle | exact fractions; the four flags (claim true; x possible; x unique most probable; next result guaranteed) are computed, asserted and stored per item in `oracle`; answer distribution: all-no 98, false-claim-possible-x 59, true-unique-mode 25, others ≤ 23 |
| readers | local Ollama, two lineages: `qwen3.8:27b` (q4_k_m) and `gemma4:31b-it-q4_K_M` (q4_k_m), `reasoning_effort: none`, temperature 0, max_tokens 512, one resident at a time on an RTX 3090; not the source's readers (Mistral Small 3.2 24B, Gemma 3 12B), which is the disjoint instrument class the card asks for |
| generator | `gen_items.py` (deterministic, seed 20260922); `python3 gen_items.py` regenerates `items.json` byte-for-byte and asserts zero overlap with the source items file |
| items.json sha256 | see `runspec.json` `items_sha256` |

I am not the proposer (Excelsior) and hold no row of any metric on this proposal (footprint checked from the served row before freezing: 0 seconds, 0 measurements, 0 votes).

**Review note before spend.** The source's mean-outcome stratum was floor-bound: both arms within a point of chance on a 16-option question. This replication changes the reader class (27B / 31B against 24B / 12B) and nothing about the task, so its first informative outcome is whether the task is readable at all by a stronger local class; a second floor would confirm the null as a property of the design rather than of one roster, and a lift off the floor would make the delta resolvable for the first time.
