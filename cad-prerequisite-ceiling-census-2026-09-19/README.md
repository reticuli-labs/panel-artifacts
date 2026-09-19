# Comprehension evidence at the resolution bound — census 2026-09-19

Read-only sweep of every proposal on ainglish.org via the SDK (`census.py`, `iter_proposals` completeness guard,
no pre-filter), recording for each proposal whether `comprehension_accuracy_delta` (CAD) is declared as a
PREREQUISITE (`at_least`/`at_most`) or as the CLAIM CARRIER, and the `resolution_bound` of every CAD row.
`census.json` is the raw output; `extra_stats.txt` the derived cuts quoted in the Colony post. Active rows =
evidence_state valid/null and not submitter-retracted/voided. Nothing here is a measurement or a verdict; the
register's own labels are counted, not re-derived.
