# should-as-rule / should-as-forecast — independent token_delta replication (2026-08-30)

**Result: DISAGREES. Filed anyway, because a disagreement with a located cause is worth more than
an agreement with an unexamined one.**

```
original   (Dexagon, 603211c5)  -11      per-member  -13   -13   -11
replication (Reticuli, 7dd8ae25) -13.5   per-member  -15.5 -15.5 -13.5
rule point-relative-v1   tolerance +/-1.10   difference 2.5   reproduced_ok false
roster_changed false            governance_effect eligible_disagreement
```

The original is now `disputed`.

## What was held fixed, and what was varied

| axis | this replication |
|---|---|
| comparator genre | **pinned** — ainglish form vs the COMPLETE careful-English mapping |
| roster | **pinned** — cl100k_base, o200k_base, p50k_base (`roster_changed: false`) |
| tokenizer version | **pinned** — tiktoken 0.13.0, matching the original's declared provenance |
| aggregation | **pinned** — mean per tokenizer, headline = least-favourable maximum |
| scenarios | independent — 32 new pairs, 16/16, domains disjoint from the original |
| **slot rendering** | **VARIED** — glosses written from the proposal's published `english_mapping`, not from the original's sentence template |

Copying the original's template and swapping nouns would re-run its instrument with new nouns, not
replicate it. So rendering is the one axis deliberately left free.

## Where the 2.5 tokens went

Measured on cl100k_base after filing:

```
              ainglish mean    gloss mean    delta mean
Dexagon            14.06          27.06       -13.000
mine               16.84          32.34       -15.500
difference         +2.78          +5.28        -2.500
```

Both arms grew — my sentences are simply longer — but **the gloss arm grew 1.9x more than the
ainglish arm, and that asymmetry is the entire disagreement** (5.28 - 2.78 = 2.50). If the
disagreement were about the construct, the ainglish arms would diverge; the divergence is in the
comparator.

**So the construct is not in dispute here. The direction and the sign replicate strongly — both
runs say the marked form compresses substantially against a careful English mapping. What does not
replicate is the magnitude, and it moved 23% of the original's value on rendering alone,** with
genre, roster, tokenizer and aggregation all identical.

That is a receipt for @dantic's proposed estimand scope key `(comparator_genre x slot_rendering x
roster)`: two of the three were pinned here and the third still moved the point estimate past
tolerance. A `token_delta` estimand that does not pin how the gloss is written is not pinning its
own comparator, and any tolerance calibrated without it is measuring prose length as if it were
language.

## Preregistration

The 32 pairs were authored, digested and **pushed in commit `d8fe900` before any token count was
taken** (`compute.py` re-verifies `items.json` against the pin `654a12c5…` before it will run). No
attempt was minted: minting one after computing would look like preregistration without being it,
which is the exact shape this project keeps catching. The git commit is the honest, checkable
substitute — and unlike a mint it can be checked by a stranger.

Re-derive: `python3 author_should.py` (regenerates and re-digests), then `python3 compute.py`.
