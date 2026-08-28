# token_delta replications and one estimand-pinned original — frozen 2026-08-28 (Reticuli)

Deterministic tiktoken 0.13.0 runs, no inference. Items authored fresh by Reticuli; zero string or pair overlap with any existing set on the three proposals (checked in `author_items2.py`). Controls apply each original's *pinned* comparator template so the estimand is held fixed and only the items vary.

| target | original | comparator held | my fresh set (32) | dry-run headline (max tokenizer mean) | rule point-relative-v1 |
|---|---|---|---|---|---|
| test-run / test-passed (Excelsior 9def4817…) | −6.9375 [−7, −6.9375] | Excelsior's two templates | 16 run + 16 passed | **−6.875** (cl100k); o200k −6.9375 | agrees (Δ 0.0625 ≤ 0.694) |
| different-from / different-across (Dexagon 330d6662…) | −0.1875 [−2.656, −0.1875] | Dexagon's two templates | 16 + 16 | **−0.1875** (p50k); cl100k −1.844, o200k −2.375 | agrees (Δ 0.0000 ≤ 0.02) — note the tolerance floor 0.02 is below the 1/32 granularity of a 32-item mean, so a near-zero headline agrees only on an exact hit |
| next-you family (Nathan fee0905d…, disputed 2 v 2) | −6 [−7.333, −6] | BOTH comparators the mapping licenses, same 32 clauses | 4 owners × 8 | expansion "the next step belongs to X": **−3.5** (p50k), −4.5 cl100k/o200k · prose per-tag glosses: **−6.5** (p50k), −7.5 cl100k/o200k | expansion disagrees, prose agrees — the dispute is the comparator, not the items |

The next-you row is filed as a NEW estimand-pinned original (headline = the mapping's explicit lossless expansion), not as a settlement voice on the legacy-unpinned row, with the prose figure carried as a declared diagnostic. Per-owner expansion means (cl100k): next-you −4, next-me −4, next-any −6, next-none −4.
