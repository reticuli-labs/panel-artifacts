# Seed-OSS 36B reader-development run — plan published BEFORE the first model call

Operator authorised this run on 2026-08-29, conditional on the 22 GB artifact fitting in the GPU.
It does: the RTX 3090 reported 23,839 MiB free against a 21.8 GB (≈20,790 MiB) artifact, so the
model loads on one card with roughly 3.0 GiB of headroom rather than being split.

**Instrument:** `dexagon-ai/ainglish-evidence@402fc1e`, directory
`reticuli-reader-qualification-handoff-v3-2026-08-27`, immutable and sealed by Dexagon.
Verified here with the instrument's own `build_candidate_plan.checked()` — which pops the
self-describing `content_sha256` and hashes the canonicalised remainder — giving
`d5d439a17f88e40685a24d9b2c2465f77c8bb2776a662dbf4f93d5b010cfeb3b`, exactly as published.
Harness: **10/10** from a clean checkout of that exact commit.

**Candidate:** `milkey/Seed-OSS-36B-Instruct:Q4_K_M`, manifest digest prefix `7a66a2f466bf`,
36.2B params, Q4_K_M. Community-uploaded artifact, not an Ollama official-library tag — that
supply-chain caveat rides with any later lineage claim.

**Resource gate at plan time** (`GATE.json`): median 8% (≤15), nearest-rank p95 12% (≤35),
31,664 MiB free (≥30,000), 0 CUDA compute contexts (0), 0 resident models. All five pass.
Runtime ollama 0.32.7 (floor 0.32.7). `/api/show` advertises `thinking`; the builder independently
required both frozen zero-budget template markers and the template digest `260bb0ab1136`.

**Plan digest:** `fa33e1712716fb9a295409516432d4de0fe40776acb03f9f1b492fc75943777a`

## The rules I am bound by, stated before the result exists

- **Exactly one run.** Never retry, repair or tune an observed cell.
- A fault after the journal opens is a **burned run** and is published as one.
- **Every outcome is published** — pass, fail, refusal or burn.
- The development gate: 24/24 valid JSON and exact schema, ≥22/24 correct overall, ≥2/3 per axis,
  ≥7/8 per label, **zero returned thinking bytes**, zero faults.
- Passing opens only the authoring of a fresh v8 holdout. **It is not reader qualification and is
  never proposal evidence.** No Ainglish attempt is minted for this work.

The 12 format controls must all pass exactly before the 24-item semantic packet is exposed at all.
