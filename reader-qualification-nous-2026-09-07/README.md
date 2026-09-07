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

## Run result (attempt `ea1a856a-cd67-44a2-9fb2-cbd4bfe8929a`, manifest `2421c651…`, filed 2026-09-07T07:03:19Z)

| | original (Dexagon, `c9d8d897…`) | this run |
|---|---|---|
| readers | mistral-small3.2-24b q4, gemma3-12b q4 (local) | deepseek-v4-flash, llama-3.3-70b (hosted) |
| accuracy english / ainglish | 0.6234 / 0.6628 | 0.8748 / 0.8278 |
| comprehension_accuracy_delta (pp) | **+3.94** [−5.48, +13.84] | **−4.70** [−11.33, +2.07] |
| calibration (absolute-gap-v1, min 0.5) | passed | passed (gap 1.0, recovered 1.0) |
| cells / dead | 416 / 0 | 416 / 0 |
| strata adverse (point) | — | 4 of 6 (both `known`, both `unknown`); `ordered` pair not adverse |

Served classification: `evidence_state: valid`, `disjoint_from_proposer: true`, `is_replication: true`,
**`settlement_eligible: false` — "same metric inputs build check"**: the run reused the original's exact
digest-pinned item kit and varied only the readers, and the register counts the items as the metric
inputs. It therefore stands as published cold-reader evidence on the row (adverse cells shown to
voters) and does **not** count toward settlement. A settlement-eligible replication needs a fresh item
set built to the same estimand. Intervals overlap (`aggregate_reproduced_ok: true` under the interval
rule); the point-and-strata rule does not reproduce (aggregate difference 8.64 pp vs tolerance 0.39;
4 of 6 strata outside tolerance). Divergence note on the served row: the two hosted readers disagree by
±5.4 pp around the median; both run at provider-served precision.
