# Reader qualification on hosted readers (Nous inference API) — 2026-09-07

Frozen before any target inference. Screen: 8 target-independent positive controls (ownership, order,
inclusion, day, exception, permission, room, delivery), each with a `detectable` text that fixes the
answer and an `other` text that does not; scoring per the SDK's `ainglish-qualify-reader` (one call per
cell, no retry; passed = detectable recovery ≥ 50% and detectable−other gap ≥ 12.5 pp).
Controls are byte-identical across the three screens, so `screen.sha256 = 717a79b2…` is shared.

| reader (exact catalogue id) | detectable | other | status | note |
|---|---|---|---|---|
| `deepseek/deepseek-v4-flash` | 8/8 | 0/8 | **passed** | valid to 2026-12-06 |
| `qwen/qwen3.6-27b` | 2/8 | 0/8 | **failed** (kept, unedited) | 14 of 16 cells `Absent('truncated')` at max_tokens 32 — the model spends the budget before answering; an instrument-settings failure, not evidence about the target. Not re-run under the same design, per the SDK rule. |
| `meta-llama/llama-3.3-70b-instruct` | 8/8 | 0/8 | **passed** | valid to 2026-12-06 |

`runspec.json` is the frozen replication spec built from these receipts: a disjoint replication of
Dexagon's comprehension original `c9d8d897…` on `quantity-set-to-value-quantity-adjust-by-signed-delta`
(same digest-pinned 200-item kit, same six strata, same comparator and calibration rule; different
readers: DeepSeek V4 Flash + Llama 3.3 70B, lineages disjoint from the original's Mistral Small 3.2 and
Gemma 3 12B). Dry-run: 416-cell plan (384 real, 32 calibration), zero API calls. The real run's
measurement and cell sidecars are added to this directory after the run.
