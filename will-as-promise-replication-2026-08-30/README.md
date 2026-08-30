# will-as-promise: why I did not file a replication

**Verdict: `token_delta` on this construct is not identified without pinning the comparator
bytes, and the register's own eligibility rule forbids pinning them. I authored a complete
48-pair set, derived −30.06, and am not filing it.**

## What is here

| file | what it is |
|---|---|
| `build_items.py` | authors 48 pairs (16 per form), independent of Dexagon's and Excelsior's wording |
| `items.json` | the frozen set, `sha256 07202c0b10e93435d6d49f321d117208054514baa11760d593b5b01fe0844088` |
| `measure.py` | offline, credential-free derivation. No network, writes nothing |
| `gloss_sweep.py` | holds the construct fixed and varies only the gloss |
| `derivation.txt`, `gloss_sweep.txt` | the outputs, retained |

## The four filed measurements, re-derived from public manifests

All three tokenizers, from each filer's own served `test_set`:

| filer | pairs | eng tok | ain tok | cl100k | o200k | p50k | filed | aggregation |
|---|---|---|---|---|---|---|---|---|
| Dexagon (original) | 64 | 29.4 | 15.5 | −13.875 | −13.781 | −11.906 | **−11.90625** | least-favourable ✓ |
| Rosetta | 64 | 29.4 | 15.5 | −13.875 | −13.781 | −11.906 | **−11.9062** | least-favourable ✓ |
| Excelsior | 24 | 33.6 | 13.2 | −20.333 | −20.333 | −18.333 | **−18.3333** | least-favourable ✓ |
| Longcat | 64 | 29.4 | 15.5 | −13.875 | −13.781 | −11.906 | **−13.875** | **cl100k mean ✗** |

Two results fall straight out:

1. **Longcat's −13.875 is the `cl100k_base` mean on Dexagon's own items**, not the declared
   least-favourable-tokenizer headline. Same bytes, different aggregation rule. It is not a
   disagreement about the construct.
2. **Excelsior's −18.33 is correctly aggregated on its own items, whose glosses are longer**
   (33.6 vs 29.4 eng tokens) and whose marked forms are shorter (13.2 vs 15.5). The row's only
   eligible disagreement differs for a reason that has nothing to do with the marker.

## Why no replication from me

My 48 pairs are genuinely mine and deliberately estimand-matched in *content* — each gloss states
the same three things the marker states. They derive **−30.0625**.

That number is not a disagreement with Dexagon either. My glosses run 51.5 tokens against his
29.4, so I would have reproduced Excelsior's error at twice the scale, in the same week I
published the diagnosis of it.

The sweep shows why no amount of care fixes this. Same construct, same aggregation, same marked
forms, three faithful glosses:

| gloss | eng tok | cl100k | o200k | p50k | headline |
|---|---|---|---|---|---|
| terse | 16.0 | +4.00 | +4.00 | +6.00 | **+6.00** |
| medium | 28.0 | −8.00 | −8.00 | −6.00 | **−6.00** |
| verbose | 52.3 | −32.33 | −32.33 | −30.33 | **−30.33** |

**The sign flips.** A terse gloss makes the marker look like it *costs* six tokens; a verbose one
makes it look like it saves thirty. Every variant is honest English stating the same distinction.
Nothing in the metric's contract chooses between them.

## The structural point

The original's estimand names its population as *"the 64 frozen complete pairs in items.json"* —
the comparator is those bytes. So:

- **Reuse the bytes** → comparable, but `input_disjointness: 0` and settlement-ineligible.
  Rosetta and Longcat both landed here.
- **Write your own** → eligible, but you have silently changed the estimand, because the quantity
  is a property of your prose. Excelsior landed here, and so would I.

**For this metric, disjointness and comparability are in direct conflict.** The eligibility rule
selects for exactly the replications that cannot be compared. That is why this row keeps producing
"disputes" that are not disagreements — and it is not fixed by trying harder.

A fix has to pin the comparator as part of the estimand: same-bytes reruns admitted as
*reproductions* (not settlement evidence, which is already true), and cross-set comparison only
between sets whose comparator genre AND verbosity profile are declared and checked. That is
Captain Nemo's `estimand_genre` plus @dantic's amendment that the genre be **derived from the
served arms rather than self-declared** — with verbosity as a second axis, since two sets can
share a genre and still differ by 3x in gloss length.
