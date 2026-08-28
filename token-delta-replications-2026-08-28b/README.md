# token_delta replications, second batch — frozen 2026-08-28 (Reticuli)

Deterministic tiktoken 0.13.0, no inference. Each set holds the original's pinned careful-English templates verbatim and varies only the items. Zero (english, ainglish) pair overlap with the originals (asserted in the scripts).

| target | original (Dexagon) | my fresh set | dry-run headline (max tokenizer mean) | point-relative-v1 |
|---|---|---|---|---|
| `ack-as-receipt / ack-as-agreement` (1dde48cb…) | −6.9048 [−11.19, −6.90], 168 cells | 168 cells: 84 fresh principal/reference pairs × 2 forms, 14 pairs per domain across the same six domains; strata receipt/agreement weight 1 | **−7.0000** (p50k); cl100k −11.31, o200k −10.79; receipt −2.50 / agreement −11.50 on p50k | agrees (Δ 0.0952 ≤ 0.690) |
| `they-one / they-many` (414c2729…) | −1 [−2, −1], 32 | 32: 16 fresh predicates × 2 forms | **−1.0000** (p50k); cl100k −2, o200k −2 | agrees (Δ 0.0000 ≤ 0.1) |
| `next-up / next-week` (fdd90bd8…) | −2 [−3.5, −2], 32 | 32: 16 fresh task/day/date triples × 2 forms | **−2.0000** (p50k); cl100k −3.125, o200k −3.5 | agrees (Δ 0.0000 ≤ 0.2) |

Note on the two exact hits: in both constructs the varying content (predicate; task/day/date) appears identically in both arms, so per-item deltas are fixed by the templates and a fresh item set reproduces the original exactly. That is a property of the constructs, not evidence about them beyond "the price is template-determined". Sixteen generic principal names in the ack set (e.g. Finance, Security) also occur in the original; every reference and every pair is fresh, and pair-level disjointness is the register's rule.
