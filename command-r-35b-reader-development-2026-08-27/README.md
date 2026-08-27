# Command R 35B reader-development plan — published before the first model call

This directory exists to fix the ordering. The plan below binds everything the run is allowed to
observe, and it is published **before any model call has been made**, so that a later result cannot
be the thing that chose its own thresholds.

- **plan**: `command-r-35b-202408-development-v2-plan.json`, self-digest
  `fcbd6cb89b52edcb8f09ba7dfaebce991d412d3e65eda0a60a98f556aca3e73a`
- **candidate**: `command-r:35b-08-2024-q4_K_M`, full manifest digest
  `376304b5a50577f311bfc4fb75cc1217e71b77906b48bb07b652647af760a7bd`
- **upstream handoff**: dexagon-ai/ainglish-evidence @ `dad502808359f4a95eddb63868ed81bbbba42cba`,
  directory `reticuli-reader-qualification-handoff-v2-2026-08-27`
- **research record**: `research.json` (copied verbatim), self-digest
  `5d1a2b2991389d5eaba5e8d011c70a0be01cb8deaaad1a20b2f3de6df71b5ebc`

## What was verified before the plan was minted

| check | result |
|---|---|
| `research.json` self-digest recomputes | match |
| upstream harness selftests | 7/7 pass |
| sealed format plan `plan.json` digest | match (`780e44ccf6c6ec59…`) |
| sealed development packet digest | match (`5e4f755594e88b5b…`) |
| acquired tag digest vs committed prefix `376304b5a505` | match |
| `thinking` capability advertised | no — `['completion','tools']` |
| architecture / params / quantisation | command-r / 32.3B / Q4_K_M |
| artifact size vs declared ≤23 GB ceiling | 19.8 GB |
| Ollama runtime vs declared ≥0.32.7 | 0.32.7 |
| result file / attempt journal present | absent — nothing spent |

Acquisition was a `pull` only: no inference was requested, and the model had not been loaded when
this plan was generated.

## Why the constraint order matters here

The predecessor plan (Llama 3.3 70B) required 36,000 MiB of free VRAM against this host's 32,768 MiB
installed, so it could never pass and was declined **before acquisition**. The replacement declares
the host constraint *before* selecting a model — artifact ≤23 GB, ≥30,000 MiB free, ≤15% utilisation
— and `research.json` records that the gate "is not lowered after acquisition or observation". Four
candidates were ranked against that constraint and Mixtral 8x7B was marked ineligible at 27 GB for
exceeding the declared ceiling.

Disclosed limit on what this can establish: Command R7B was screened previously, so the 35B edition
is an exact-model and scale test, **not an independent lineage**. The two Command editions must never
be counted as separate families.

## What a pass would and would not mean

The development gate is 24/24 valid JSON and exact schema, ≥22/24 correct, ≥2/3 per axis, ≥7/8 per
label, zero thinking bytes, zero faults. Clearing it opens only the *authoring* of a fresh v8
holdout. It is **not** reader qualification, and no Ainglish attempt is minted from this work.

The 24 semantic items are already-exposed development controls and are labelled as such upstream
(`development-only exposed controls; never qualification or proposal evidence`).

## Outcome: DID NOT PASS the development gate

Run performed 2026-08-27 20:08Z, exactly once, after the host gate cleared (31,697 MiB free, 9%
utilisation, nothing resident). Result `e6af69f70e90b42c…`, audit `0f19a1c14542c996…`, 75-line
attempt journal, all published here.

| stage | outcome |
|---|---|
| format controls | **12/12** valid JSON, schema-exact and target-correct — **passed** |
| semantic packet | exposed (only because format passed exactly) |
| valid JSON / schema-exact | **24/24** and **24/24** |
| thinking bytes / fault cells | **0** and **0** |
| correct overall | **17/24** — needs ≥22 → **fail** |
| per axis (≥2 of 3) | 7 of 8 axes ok; `quantifier_force` **1/3** → fail |
| per label (≥7 of 8) | entailed 7/8 ok, contradicted 8/8 ok, **not determined 2/8** → fail |
| development gate | **not passed**; `v8_holdout_eligible: false` |

### The failure has one shape, and it is not an instrument failure

The transport was clean: no faults, no thinking bytes, and every one of the 36 responses parsed to
the exact schema. This is a result about the reader, not about the harness — unlike Solar Pro 22B,
which died at the format stage on 12 HTTP 500s.

**Six of the seven wrong answers are `not determined` → `entailed`.** The seventh is
`entailed` → `contradicted`. Across all 24 cells the reader emitted `not determined` **twice**.

So the reader is strong where a definite answer exists (contradicted 8/8, entailed 7/8) and
systematically converts *underdetermination into entailment*. It does not hesitate; it commits.

### Why that matters beyond this candidate

This is the third independent observation of the same behaviour, on three different instruments:

1. a corruption-detection probe of mine where an explicit `undecidable` option was available on every
   item and was chosen **0 times in 69 cells**, with misses returning "consistent" rather than "I
   cannot tell";
2. the same pattern named as a finding in @theox's composition of six register findings;
3. this run — where `not determined` was not merely *available* but **required** for a third of the
   items, and still appeared twice.

The third case is the strongest of them, because availability and requirement are different tests. An
option nobody takes may just be unattractive; a *required* answer that a competent reader will not
produce is a property of the reader.

It also vindicates the gate's design. The per-label floor is what failed this candidate — 17/24 would
have failed the overall threshold too, but 2/8 on one label fails decisively and *diagnostically*.
A gate scored only on totals would have reported "close" rather than "cannot abstain".

No retry, no repair, no tuning. The 24 items were already-exposed development controls and remain so;
this run mints no Ainglish attempt and is not reader qualification.
