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

## Outcome

Every direction gets published here — supportive, null, adverse, a transport failure, or a refusal by
the host gate — with the result, the fsynced attempt journal and the audit. No observed cell is
retried, repaired or tuned.

At publication time the run has not been performed.
