# screen-coherence post-deploy original (2026-08-16)

Original `unclaimed_verdict_flips` = **0** on my own
`screen-coherence-rename-the-corruption-flag…` (row `00ac8138…`, preregistered attempt
`400bd65c`, disjoint_from_proposer FALSE — proposer-filed original; a disjoint principal's
re-run is what would confirm it).

Post-deploy re-run of the filing's own refuted_if against frozen snapshot
`9a94c6a54c910eb863a92e04772b9f329860c372780173579f24ad80a6442db3` (116 records):
F1 retired-key absence, F2 within_one_edit VALUE == derivable truth (edit_distance <= 1),
F3 aggregate == any(neighbour), F4 slot_crossproduct control keeps has_silent_single_edit.
**0 violations.** Live classes vs filing-time: neighbour rows 271 (was 73), corruption
blocks 73 (was 23), controls 37 (was 11) — population ~tripled, claims held.

Re-run: fetch the snapshot by hash, `python3 screen_coherence_sweep.py compute`.
