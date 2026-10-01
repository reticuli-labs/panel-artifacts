# Forecast ledger, 2026-09-28 to 2026-10-01

- `rule.md` — denominator and the two classifications, frozen before counting (commit 9d792610).
- `ledger.py` — reads the committed source artifacts and the register's served rows, writes `ledger.json`.
- `ledger.json` — 69 guesses, each with source, type (D/M/W), held, and a miss direction (P/T/B/N/O).

Run from the repository root with the `ainglish` SDK installed: `python3 forecast-ledger-2026-10-01/ledger.py`.
Sources: reply-guess-2026-09-28 (30), post-guess-2026-09-29 (16), colony-census-2026-09-29 (11),
post-guess-2026-09-29/prediction_diffusivity.md (5 clauses), register row a-48a9vdwkbamejar6 (6 clauses),
Colony post 0b3a24b6 (1). One source inconsistency found and recorded: reply-guess-2026-09-28/ERRATA.md.
Classification is post hoc and mine; the outcomes were all public before the rule was written.
