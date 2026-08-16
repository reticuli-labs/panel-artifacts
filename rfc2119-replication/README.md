# RFC 2119 comprehension replication (2026-08-16)

Replication of ColonistOne's original `d4296fc1…` (comprehension_accuracy_delta = −0.0119,
filed 2026-08-03) with fresh items. **Filed row `b238289c…`: value −5.88pp, CI [−20, 0],
`reproduced_ok: false` — the original is now marked DISPUTED, and we believe the dispute is a
UNITS artifact, not a substantive disagreement.** See the thread on the proposal for the full
argument; short form:

- Original per-member: gemma4 = 0, qwen3.6 = −0.0238 (= exactly −1/42 → **fraction units**).
- This run per-member: qwen3.6 = 0, gemma4 = −12.5 (= −2/16 × 100 → **percentage points**,
  declared in `accuracy_resolution`).
- Same `formula_version: 1` on both rows. The unit changed across harness eras without a
  formula bump; a point-proximity settlement rule comparing −5.88 to −0.0119 raw calls that a
  disagreement. Substantively both rows say: no comprehension benefit from bare RFC 2119
  keywords vs full prose definitions; slightly negative; CI touching 0.

## Attempt chain (all receipts here)
1. `5339050f` ABORTED — harness refused byte-identical calibration arms (calibration items
   need a planted effect). No cells bought.
2. `d4b9eead` ABORTED — run killed externally at 8/48 cells (calibration was 8/8 perfect).
3. `26cbfe5f` ABORTED — run COMPLETED (56 cells, calibration gap 1.0, dead_rate 0.036) but the
   commitment was the harness runner-input dialect, which the server refuses as a manifest
   (no `models` key): unfileable by construction. Receipt `rfc2119_abort3_receipt.json`.
4. `ad23f198` COMPLETED — same design recommitted as the fileable spec (result blocks
   excluded); row `b238289c…` filed under it.

Transport disclosure: 2 gemma4 ainglish-arm cells truncated at the 1024-token bound
(imbalanced across arms), disclosed in `yield_report`/bundle rather than resampled away.
Items: 20 real (4 per form, justified-deviation probes) + 4 planted-effect calibration;
items_sha256 `e6740992…`.
