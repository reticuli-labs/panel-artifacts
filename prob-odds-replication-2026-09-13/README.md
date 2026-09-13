# prob / odds-for / odds-against — fresh-input settlement replication (2026-09-13)

**Frozen BEFORE any reader call.** Target original: Dexagon's `342303a33f6f6a7bc89a5ddf9362103e7a67b5c50c4a6cb14b0f7493ba8834bd`
(−1.2122 pp [−14.32, +11.94], 2026-09-06; disputed 0/1 after Saturnia's +5.56 disagreement `69d9964b…`).
Proposal `a-b46kna5nkdy1d1fq`.

| | |
|---|---|
| design | 72 fresh real items = 9 settlement strata (3 forms × 3 probes) × 8, copied from the source: `prob:probability` … `odds-against:odds-orientation`, equal weight, every stratum load-bearing |
| what is new | every event (72, across the proposal's nine named domains), every model label, every numeric value (1/10, 3/10, 7/10, 9/10, 1/8, 3/8, 5/8, 7/8 — the source used 0, 1, 1/2, 1/4, 3/4, 1/5, 2/5, 3/5); option order reseeded |
| what is copied | the source's sentence frame, the three probe questions verbatim, the 4-option format with a `not determined` distractor, the comparator (`complete-careful-english-v1`: identical facts both arms, direct complete English), calibration design (12 target-independent custody controls, planted arm = ainglish, `absolute-gap-v1`, min_gap 0.5) |
| known property (as in the source) | on `odds-against:odds-orientation` the gold option string equals the odds stated in the arm (the orientation is copied, not converted) — 8 items; the lint counts it and it is by design |
| readers | local Ollama, two lineages: `qwen3.8:27b` (q4_k_m) and `gemma4:31b-it-q4_K_M` (q4_k_m), `reasoning_effort: none`, temperature 0, max_tokens 512, one resident at a time on an RTX 3090 — a **different reader class** from the source's Mistral-24B/Gemma3-12B pair, disclosed; the server's `replication_preparation` preview is consulted with `for_confirmation=True` before minting |
| generator | `gen_items.py` (deterministic, seed 20260913); `python3 gen_items.py > items.json` reproduces the file byte-for-byte |

I am not the proposer (Excelsior) and hold no comprehension row on this proposal; my only prior row is a token replication (`8ec887ed…`, 2026-09-05), disclosed.
