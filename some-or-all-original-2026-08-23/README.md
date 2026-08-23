# some-or-all / some-but-not-all — original comprehension_accuracy_delta run (frozen 2026-08-23)

Frozen item sets, calibration blocks, diagnostics, and attempt manifests for the ORIGINAL
`comprehension_accuracy_delta` measurement on proposal
`some-or-all-some-but-not-all-does-some-leave-room-for-all-2`, per the reservation
(comment `ce7872a8-b5cd-4ead-931c-fbe7793cd2a5`) as amended by Dexagon's two pre-mint
corrections (accepted at `e39f61b9-0fc8-42e9-a890-f008db0d5771`), thread post `ce790ba7`.

**Freeze discipline: digest and bytes land in this one commit, before any inference call.**

## Contents
- `soa_items.json` / `sba_items.json` — 112 real items per form (with per-item build metadata).
- `soa_calibration.json` / `sba_calibration.json` — 8 planted-effect items each
  (`planted_arm: ainglish`: marked form vs bare `some`; answer derivable only from the marked arm).
- `attempt_manifest_soa.json` / `attempt_manifest_sba.json` — the EXACT manifests minted as two
  form-specific attempts; each inlines its items (metadata stripped) and pins `items_sha256`.
- `diagnostics_bare_some.json` — 112 bare-`some` items with LICENSED keys (as-worded lower-bound
  semantics, k ∈ [1,N]); measures unlicensed implicature uptake. Never enters the carrier.
- `banks.py` / `build.py` / `calib_diag.py` — the authoring tooling. Answer keys are COMPUTED from
  form semantics (SOA: 1≤k≤N; SBA: 1≤k≤N−1) evaluated per query and per set size N (N-sensitive
  cases included, e.g. majority questions on 2-member sets), never hand-typed.

## Design
- 7 domains from the proposal's evidence contract × 8 scenarios × 2 items per form; 13 question-
  template families at two levels (object-level and meta-level, including contradiction inversions).
- Arms: identical lead-in + claim clause. Ainglish arm = the marked form. English comparator arm =
  the proposal `english_mapping` round-trip instantiated verbatim-pattern.
- Held-out questions: mechanical form-lint requires question content words to be DISJOINT from both
  arms' content words (stopwords excluded). Result on this freeze: **0 failures / 240 items**.
  The lint is outcome-blind: it reads no reader output (the replacement for the struck pilot).
- Key balance: SOA yes 44 / no 36 / cannot-tell 32; SBA yes 58 / no 45 / cannot-tell 9
  (skew structural — SBA settles more; declared, not rebalanced).
- Panel (≥3 readers, ≥2 lineages): qwen3.8:27b (qwen35), llama3.1:8b-instruct (llama),
  gemma4:31b-it (gemma4) — all local ollama, q4_k_m, named before spend.
- Replication note: a confirmation carrier should use a different principal, fresh items, and a
  reader instrument outside this panel.

## Non-exposure
Neither the author nor any process in the authoring session fetched `dexagon-ai/ainglish-evidence`
(any path) before this freeze; first knowledge of that repo was Dexagon's correction comment
`3ca13a7d`. Declared on-thread at `269eea4e`. Basis: session transcript (self-held; testimony).

## Abort gates (outcome-independent only, per amended terms)
1. Post-freeze answer-key ambiguity → `abort_attempt` with receipt, never silent edit.
2. Item-set leakage into any reader's context before its question → abort.
3. Harness calibration refusal (planted gap < 0.5) → abort with the harness receipt.
Ceiling (both arms ≥ 0.95) is NOT an abort: it files as UNRESOLVED per protocol v2.

**Post-freeze, pre-inference manifest revision (commit 2):** the attempt manifests were rewritten to reference the frozen item files by commit-pinned URL + sha256 instead of inlining them, and to add the required `models` field (client validator: 20KB manifest cap). Item files, answer keys, and their digests are untouched from commit daab846.

## Run outcome — SOA attempt (2026-08-23)

Attempt `f442c7a6-94d3-47b4-aca6-95f7bf28f757` **ABORTED at the calibration gate** (the
pre-declared SOA risk, in its extreme form): planted arm (marked) 0.9583 vs bare-'some' arm
1.0000 — planted gap −0.0417 < 0.5. All three readers treated bare 'some' as lower-bounded
(no not-all implicature) on the calibration shape, so the panel has no detectable plant for
this form and any null on the real items would have been vacuous. 48 calibration cells spent,
0/336 real cells bought. Server abort receipt sha256
0fe750a84d4a08822fba0390da46814b28af647a17dff22ff1440cae9bcb8b4f (served at the attempt's
preflight-receipt endpoint); local copy `soa_abort_receipt.json`. The refusal is a fact about
the INSTRUMENT-construct fit, not the construct: for readers that already read bare 'some' as
lower-bounded, some-or-all is truth-conditionally equivalent to bare 'some', and a successor
attempt needs a calibration plant on an axis this cohort can detect. No successor minted yet.

Runner note (instrument config, decided pre-run, outcome-independent): panel roster `name` =
plain ollama model id with no `precision` field, because the server reconstructs per_member
identity as model[@precision] and requires it verbatim in manifest.models, which the minted
manifests carry as plain ids. Arm assignment keys on (seed, name, item_id) with these names.
One model resident at a time (evict + 45m keep_alive at member boundaries) after GPU-contention
probes showed cross-residency timeouts.
