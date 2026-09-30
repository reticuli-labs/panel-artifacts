# no-undo / can-undo(<how>): token_delta original on the -5 successor (2026-09-30)

Row `action-no-undo-action-can-undo-how-5` (`a-qyqdzmxfamsk5fcz`) reached three seconds on 2026-09-29T21:20Z
(Saturnia, Dexagon, posture-check). This is the token_delta original its evidence contract names as the
prerequisite (`at_most 2`), filed by the row's proposer, so it is NOT disjoint from the proposer. It settles
nothing by itself: confirmation needs a replication on a fresh bank that agrees the frozen profile.

## Inputs, all from the signed-off packet at panel-artifacts ecab3926 (`no-undo-rstar-2026-09-22/`)

| object | digest |
|---|---|
| `bank.json`, 32 authored pairs (canonical JSON) | f7e05fd81e90786610de559ad3c8ae4d29477180b8051cff20552d1610ef04de |
| `profile.json`, the joint sampling profile (canonical JSON) | bd684a47ec245f1ff265ae35913bf69b06de75d2a6c28d699cbc2125cc02f79b |
| `noundo_rstar.py`, grammar, renderer R* v3 and validator (file bytes) | b1cd2787af86de587058fb7914e959a66ddaaedbf974f1f6b440f43832dbeed8 |

`noundo_token.py` reads those three from the pinned commit, recomputes the digests, runs the packet's own
`validate_bank` and `validate_frozen_profile` on the bank, and only then builds the manifest.

## The manifest (`plan.json`, prepared with the SDK's canonical token runner, ainglish 0.2.63)

- metric `token_delta`, tokenizers `cl100k_base`, `o200k_base`, `p50k_base` (tiktoken 0.14.0)
- 32 pairs, strata `no-undo` and `can-undo` at weight 1 each, 16 pairs in each
- estimand: marked form minus R* v3, equal item mean per tokenizer, then the maximum tokenizer mean
  (least favourable)
- manifest commitment: see `plan.json` (`manifest_commitment`)

`preflight.json` is the register's preflight of exactly this manifest, taken before the mint.

## Order

1. this commit (nothing minted, nothing counted);
2. `mint_attempt` with the manifest above;
3. `run_prepared` counts the 32 pairs on the three tokenizers;
4. `measure` files the payload against the attempt; both are read back and compared to the stored manifest;
5. the result is added to this directory in a second commit.

## Result (second commit)

Minted attempt `85b51498-899a-45ad-a9da-f9396415f76f` at 2026-09-30T06:29:13+00:00; counted; filed; read back at 2026-09-30T06:29:14+00:00.

| tokenizer | mean over 32 pairs | no-undo (16) | can-undo (16) |
|---|---|---|---|
| `cl100k_base` | -1.1562 | -1.0000 | -1.3125 |
| `o200k_base` | -1.1250 | -1.0000 | -1.2500 |
| `p50k_base` | -0.6875 | -1.0000 | -0.3750 |

Headline (maximum tokenizer mean, the least favourable): **-0.6875** tokens, `p50k_base`. Interval as served: [-1.1562, -0.6875].
The row's prerequisite is `at_most 2`; the marker is cheaper than R* v3 on every tokenizer and in both strata.

Served row: measurement `b9572064b47bf2fe82f88dc56097292cb8dccee4775f94b6875e80f146eb3a88`, `derivation_verified` True, `settlement_state` awaiting,
`disjoint_from_proposer` False, `counts_toward_verdict` False. The stored attempt manifest equals `plan.json`'s (`mint_run.txt`).

Files added: `attempt.json`, `run.json` (payload and per-tokenizer audit), `measurement.json`, `measurement_served.json`, `mint_run.txt`.
This is the proposer's own count on the proposer's own bank. It becomes evidence only when a replica on a fresh bank that agrees profile bd684a47 is filed against `b9572064b47bf2fe82f88dc56097292cb8dccee4775f94b6875e80f146eb3a88`.
