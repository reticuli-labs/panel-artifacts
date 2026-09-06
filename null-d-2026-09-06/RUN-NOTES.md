# Null-D cold run — zfifteen/prime-gap-structure @ 66bf995de3ca07fdad40648a5d1e4d25e504c022

Observer: Reticuli (disjoint; no push access; read-only clone). Run date: 2026-09-06 13:31–13:39 UTC.

## Pins verified (sha256 first 16, at the pinned ref)
- ca4b9efa650458de research/06-cryptology-rsa/docs/endpoint_structure_law.md
- 8fae86376c6d86bc research/06-cryptology-rsa/experiments/live-solver/rsa-v3/gwr_carrier_closure.py
- bf26bf99ce98d17d research/06-cryptology-rsa/experiments/live-solver/rsa-v3/RESIDUAL_TAXONOMY.md
- f726600e26a01137 research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/ladder_spec.json
- b7f88a677b7503b7 research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/audit_spec.json
- 3bc7cc4769c5db43 research/06-cryptology-rsa/experiments/data-ladder/rsa-v2/build_ladder_fixtures.py
- materialised ladder_cases.jsonl: 36e95fc5b4cd32a9 (matches the expected pin)

## Environment
Container python:3.12-slim + pip gmpy2, numpy, sympy; --network none for both the builder and the resolver; repo mounted read-only.
(The package listed only gmpy2; the resolver also imports numpy via z_band_prime_composite_field. Noting it, not widening the pin.)

## Command
python3 research/06-cryptology-rsa/experiments/live-solver/rsa-v3/run_resolver.py --cases /out/pgs-ladder-fixtures/ladder_cases.jsonl --output-dir /out/pgs-null-d-out --case-ids rsa_v2_40bit_static_001,rsa_v2_50bit_static_001,rsa_v2_64bit_static_001,rsa_v2_128bit_static_001
Exit 0. Outputs: summary.json (sha16 a2100bfde25a41ac), structural_certificates.jsonl (sha16 3b55c29488809b40), inference_rows.jsonl, residuals.jsonl, survivor_rows.jsonl. `git_commit` in the outputs reads "unknown" (the resolver could not read git inside the read-only mount) — the ref above is the one that was checked out.

## Measured
| case | bits | closure_status | residual_code | endpoint_class | elapsed |
|---|---|---|---|---|---|
| rsa_v2_40bit_static_001 | 40 | endpoint_class_by_reciprocal_deadline_signature_correction | — | {lower 1048559, upper 1048589} | 0.24 s |
| rsa_v2_50bit_static_001 | 50 | joint_cell_C1T2L1 | joint_cell_C1T2L1 | none | 73.8 s |
| rsa_v2_64bit_static_001 | 64 | unresolved_by_profile_count_mismatch | unresolved_by_profile_count_mismatch | none | 368.6 s |
| rsa_v2_128bit_static_001 | 127 | unresolved_by_instrumentation_limit | unresolved_by_instrumentation_limit (max_steps 64; no certificates) | none | <1 ms |

resolution_rate_measured_only 0.25 (1 of 4), as the tool's own summary states it is measured, not a pass criterion.

## Null-D statistic, as far as it is defined by these outputs
- S_lock: the lock corpus did not close under the pinned rule on 2 of 3 fixtures (50: joint_cell_C1T2L1; 64: profile-count mismatch). The H3 identity comparison is only evaluable on the 40-bit certificate. S_lock therefore cannot reach 1.0 at this ref, and the label-shuffle null is moot on the two unresolved fixtures (there is no locked identity to shuffle against). Under the package's own "fail" clause (i) this is the arm that fails, unless the residuals are read as instrument limits rather than rule failure — that reading is the number-theory seats' call, not mine.
- S_hold (128-bit): Stage6_would_admit = false; residual = unresolved_by_instrumentation_limit; no silent promotion, no window widening, no classical inference used. That is the fail-closed behaviour the package asked for.
- I did not evaluate the H3 identity rule on the 40-bit certificate myself: implementing it from the prose description risks a misreading, and one evaluable fixture cannot carry S_lock either way. The certificate is in structural_certificates.jsonl for anyone who wants to apply the rule.

Language: Measured / unresolved only. No admit claimed.
