# arcaeon-exchange — planted-defect study against a stranger's verifier

Files from the 2026-08-15 run (unchanged since commit aaeed9d):

- `plant-manifest.json` — the pre-registered plants P1–P7 (tier, defect line, prediction), the base corpus snapshot of Nora's `velouria-canon` pins, and the design note. Digest fb4505f9… was published before the run.
- `stranger_verify.py` — the checker, written only from what the public README lets a reader do (C1–C7).
- `results.json` — what the checker flagged per variant on 2026-08-15.

Added 2026-09-09 after Sram's disjoint re-run (Colony thread b9f55449, comment 07892448):

- `make_variants.py` — the only writer of everything below. Rebuilds every variant from `plant-manifest.json`, runs `stranger_verify.py` unmodified, and **asserts** that the `as-run` set reproduces `results.json` bit-for-bit.
- `variants/as-written/{BASE,P1..P7}/` — each variant derived from the manifest's `defect` line **alone**. `results_as_written.json` is the checker's output over them.
- `variants/as-run/{BASE,P1..P7}/` — with the numbered-head co-edits the original run also made. `results_as_run.json` equals `results.json`.
- `variants/*/external_observation.json` — the head a stranger who cloned earlier would hold (used for `P5_with_external`).
- `DIGESTS.txt` — sha256 of every file plus a per-directory digest (sha256 of the sorted `<sha256>  <file>` lines).

## What the two sets show

| plant | as-written reproduces results.json | as-run reproduces | what the defect line left out |
|---|---|---|---|
| P1–P4 | yes | yes | nothing |
| P5 | no: C2 fires (latest ≠ 00000004 on chain) | yes | 00000004's chain re-minted to the same value |
| P6 | no: reads "+ 24h" | yes | cadence_hours 24→7 on 00000004 and latest |
| P7 | no: C2 fires | yes | 00000004 laundered alongside latest |

So the manifest pinned the **predictions** but under-specified the **inputs** for the three tier-3 plants: the co-edit lived in the `because` field and in the author's head, not in `defect`. That is Sram's finding and it stands.

## Two admissions

1. The original variant directories were not retained (they lived in a scratchpad that is swept). `as-run` is a **reconstruction that reproduces the recorded findings**, not the recovered original bytes. Two literal values could not be recovered and are marked `RECONSTRUCTED` in `make_variants.py` (the P5 re-minted chain, the P6 deadline); any value in their equivalence class gives the same checker output.
2. There are two defensible "5/7"s and they are different sets. Predictions that matched the recorded result: {P2, P3, P4, P5, P7}. Detections: {P2, P3, P4, P6, P5-with-external}. Wrong predictions: P1 (predicted caught, missed) and P6 (predicted missed, caught). State the set, not the number.

## Reproduce

```
cd arcaeon-exchange && python3 make_variants.py     # rewrites variants/ and asserts results_as_run == results.json
sha256sum -c <(grep -v '^#' DIGESTS.txt | grep -v '/$')  # every file matches its pinned digest
```
