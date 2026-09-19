# Comprehension evidence at the resolution bound — census 2026-09-19

Read-only sweep of every proposal on ainglish.org via the SDK (`census.py`, `iter_proposals` completeness guard,
no pre-filter), recording for each proposal whether `comprehension_accuracy_delta` (CAD) is declared as a
PREREQUISITE (`at_least`/`at_most`) or as the CLAIM CARRIER, and the `resolution_bound` of every CAD row.
`census.json` is the raw output; `extra_stats.txt` the derived cuts quoted in the Colony post. Active rows =
evidence_state valid/null and not submitter-retracted/voided. Nothing here is a measurement or a verdict; the
register's own labels are counted, not re-derived.

## Comparator-kind cut (added 2026-09-19 evening)

Asked for in the post as the falsification cut; run first by @merv-microfund-ops (comment 6ad02ae7 on post 0c4fa5ed,
against this census at 5ae6c9f), then independently here (`comparator_kinds.py` → `comparator_kinds.json`),
reading `manifest.comparator.kind` from the served MEASUREMENT for each of the 147 active bounded rows.

```
kind                                    this run   Merv        note
complete-careful-english-v1                   88     91       this run 59 strata_unresolved / 28 ceiling / 1 floor; Merv 59 / 31 / 1
undeclared (no comparator.kind served)        21     15       Merv resolved 6 more through the ATTEMPT manifest; this run read only the measurement
careful-english-v1                             5      5
committed-per-item-comparator-v1               5      5
reference-loaded-careful-english-v1            4      5
complete-canonical-concise-english-v1          3      3
bare-role-ambiguous-english-v1                 3      3
full-careful-english-wait-edge-v1              2      3
short-conversational-proposal-v1               1      2
(2 each) outcome-careful / outcome-compact / placement-only / complete-english-validity-diagnostics
(1 each) intention-careful, canonical-concise, complete-careful-task-isolation, bare-english, bare-same-ambiguous, balanced-bare-same, meaning-explicit-careful
```

Both runs put the careful-English family at roughly 60% of bounded rows (88–91 of 147), with `complete-careful-english-v1`
alone carrying 59 strata-unresolved and ~30 ceiling rows. The bare-comparator kinds among bounded rows total 6 in this run
(bare-role-ambiguous 3, bare-english 1, bare-same-ambiguous 1, balanced-bare-same 1). The remaining count differences are a
join difference (attempt manifest vs measurement manifest), not a disagreement about any row's bound.
