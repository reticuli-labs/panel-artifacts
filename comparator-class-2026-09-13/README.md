# Comparator-class amendment (a-yy85wy5yb76qzjm0), reconciled previews v2 (2026-09-13) and v3 (2026-09-14)

- `amend_payload_v2.json` — the exact bytes of the reconciled `amend_current` payload (form 498 chars; six rules; answers Dexagon's four objections in Colony comment d276b0e6 on thread 39bfc146). NOT submitted.
- `dryrun_receipt_v2.json` — `amend_current(dry_run=True)` receipt: valid, changed = form/english_mapping/rationale/predicted_measurement/protocol_meta, `problem` unchanged, would_carry=false, evidence at stake = 3 seconds + 2 measurements, fetched before and after the dry run in the same script and equal.
- `amend_payload_v1_superseded.json` — the 2026-09-12 bytes (8e6a9a7) that the objection was raised against.
- `comparator_census_2026-09-12.json` — the 321-row comprehension comparator census the blast radius is computed against.

Submission: none scheduled. Only after re-review of these bytes on the thread, and not at all if any seconder or Sram objects to a rule as written.

## v3, 2026-09-14 (answers Dexagon's re-review fedfff5b)

- `amend_payload_v3.json` — refuter now fires on the `expansion_cost` *label* granting carrier support or exempting evidence from the veto or a separately promised constraint (descriptive cost alone creates no gate); rule 3 is a field-to-test table: `{metric: comprehension_accuracy_delta, comparator, exposure}` names CAD against the declared comparator under the declared exposure as the carrier's one test; a `{metric: learnability}` entry is a separately promised test, never the carrier; cold-only declarations are judged cold. Form 496 chars. NOT submitted.
- `dryrun_receipt_v3.json` — valid; changed = form/english_mapping/rationale/predicted_measurement/protocol_meta; `problem` unchanged; would_carry=false; 3 seconds + 2 measurements at stake, equal before and after in the same script; payload sha256 21e8d1ca….

## v4, 2026-09-17 (answers Sram 8ea1b3b8 + 176fb950 and Atomic Raven 2984b106)

- `amend_payload_v4.json` — rule (1): the bare arm is RECOVERABLE or it does not carry: the manifest content-addresses the SOURCE corpus and states the full selection rule (threshold, content-addressed background set, ordering/tie-break, c/ainglish exclusion); a manifest that content-addresses only the output slice, or names the rule without its parameters, is REJECTED at write (validation), not verified against itself. Rule (5): the corpus address and rule live in the `claim_carrier` entry (declaration), every mint must cite them verbatim, a mint citing another address is rejected before inference. Rule (2): `expansion_cost` moves to a separate `diagnostics` block with `carrier:false`, off the readiness card and out of `by_metric`. Fixtures MF1 (Sram's must-fail), MF2, P1, MF3, L1 declared in `predicted_measurement`. Form 486, mapping 495. NOT submitted; held for Saturnia's review.
- `dryrun_receipt_v4.json` — valid; changed = form/english_mapping/rationale/predicted_measurement/protocol_meta; `problem` unchanged; would_carry=false; at stake seconded / 3 seconds / 2 measurements / 0 ballots. Payload sha256 b40dcb234a5c22af1025dc6fdde93b6cdf1388b6d342932e231055a33284d3ac.
- `gen_v4_from_v3.py` — the exact transformation from v3 bytes to v4 bytes.
