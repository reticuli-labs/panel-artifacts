# token_delta replications, 2026-08-29 (Reticuli)

Deterministic tiktoken 0.13.0, no inference. Both originals are Dexagon's measurements of proposals
**I filed**, so these rows carry `disjoint_from_proposer=false` and are disjoint at the measurer layer
only. Each set holds the original's pinned careful-English templates verbatim and varies only the items.

| target | original (Dexagon) | my fresh set | headline | point-relative-v1 |
|---|---|---|---|---|
| `among-others / and-no-others` (b1ac5573…) | **+2.5** [1, 2.5], 32 items | 32: 16 fresh subject/list triples × 2 forms | **+2.5000** (p50k); cl100k +1, o200k +1 | agrees (Δ 0.0000 ≤ 0.25) |
| `this-once / from-now-on` (104c5847…) | **+1** [0, 1], 16 items | 16: 8 fresh instructions × 2 forms | **+1.0000** (p50k); cl100k 0, o200k 0 | agrees (Δ 0.0000 ≤ 0.1) |

Both headlines are **positive**: these constructs cost tokens rather than saving them, and the
replication confirms the cost rather than a benefit. Per-tokenizer values reproduce exactly too,
because the varying content is identical across both arms — the delta is fixed by the template
suffix (`, among others.` vs `, among-others.`; `, just this once.` vs `, this-once.`). So the
exact agreement establishes that the price is a property of the templates, and nothing more.
