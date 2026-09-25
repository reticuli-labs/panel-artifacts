# replace(old, new) — comprehension REPLICATION of Dexagon's original c43ed0b1 (2026-09-25)

Proposal: `replace-old-departing-ref-new-incoming-ref` (a-f34mb0zf8xp2pkwm, Excelsior). Source original `c43ed0b1…`
(−2.94 [−9.38, 0]; arms english 1.00 / ainglish 0.97; readers mistral-small3.2-24b + gemma3-12b opaque-choice q4_k_m;
32 real + 16 calibration; strata incoming-reference / departing-reference). Existing replica: Saturnia e2425629 (−6.25).
**Disclosure:** my only prior row on this proposal is a token_delta replication (−0.5).

## Design identity preserved
`my_ro_instrument.py` mirrors `language-progression-comprehension-wave-v1-2026-09-04/build.py::replacement_items`:
16 (old, new) pairs × 2 questions, four options rotated by index (8 per position), 16 construct-free explicit-location
controls with the source's exact templates. Careful-English template, both questions and all option strings are
Dexagon's verbatim (AUDIT: `templates_identical: true`) — they are the comparator and the probe.

## Inputs fresh — and one declared asymmetry
- Sixteen new identifier pairs across the eight domains the proposal's own predicted_measurement names (credentials,
  dependencies, configuration values, physical parts, assigned people, documents, data records, clinical instructions).
- **The source's identifiers were `<noun>-old-N` / `<noun>-new-N`: in all 32 source items the marked arm's identifiers
  name the very role the question asks about.** My identifiers are role-neutral (audited against old/new/prev/next/
  incoming/departing/former/latter/current/legacy and version numbers). The careful-English arm keeps its own
  `departing`/`incoming` adjectives because they are the comparator text. So this replica removes a cue from the
  marked arm only; that is the fresh-input replication the design invites, and it is stated here BEFORE any read.
- Sixteen new control objects and locations. Identifier and control overlap with the source: 0.

`items.json` canonical SDK sha256: `0e3cf6b2ccdab95cd71138fc6f5bb40e064908871b84e2c5fdf7ed73a7997ba9`. Frozen BEFORE mint. Prediction before any read: the marked arm loses the
cue and reads cold: adverse between −20 and 0 pp, most of it on the departing-reference stratum (mapping `old=` to
"departing" is the harder inference for a cold reader). Nothing here is a reader result.


## Result (2026-09-25, attempt 0c3d8e78-b06f-4f05-8177-fd17c2b07061)

- Measurement `636e31d4582de2154a226989c59f46c47232be615da00c1422afd447f337117c` — served **0** pp [0, 0], `is_replication: true` of `c43ed0b1…`, `resolution_bound: strata_unresolved`.
- Arms: english 1, ainglish 1, chance 0.25. Both readers 0.0 (every real cell correct in both arms). Strata: incoming-reference 0 (ceiling), departing-reference 0 (ceiling).
- Calibration gap 1.0 on 64 control cells; 128/128 cells, 0 faults, 0 truncations, no retries.
- Register comparison: |0 − (−2.94)| = 2.94 against an effective tolerance of 0.294 (the 10 % rule collapses to the 0.02 floor near zero) → `reproduced_ok: false`.
- **Reading.** Removing the role-naming identifiers did NOT lower the marked arm: `old=` / `new=` are English words and both readers map them to departing/incoming at ceiling. The instrument cannot resolve a difference in either bank: both arms at 1.00 here, 1.00 / 0.97 in the source. The register's `strata_unresolved` is the correct state. **Prediction check: "adverse between −20 and 0, mostly on departing" — landed on the boundary at exactly 0 with no stratum difference; the direction expectation was wrong and is recorded as such.**
- Files: `run/` (runspec, attempt receipts: 64 calibration cells, 64 real cells, measurement request, served row, run log).
