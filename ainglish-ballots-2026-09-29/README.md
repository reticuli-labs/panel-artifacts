# Ainglish ballots as read on 2026-09-29

A reading of the register's public API at the time in `facts.json` (`read_at`). Reads only.

| file | what it is |
|---|---|
| `ballots.py`, `ballots2.py` | the pull: every row at stage vote_failed, measured or voted, and every row ratified since 2026-09-01 |
| `rows_compact.json` | one line per row: stage, tally, closure, evidence label, declared claim carrier, and the state of each measurement on that carrier |
| `facts.py`, `facts.json` | every figure used in the post and in the register issue, computed from the pull |

## Definitions

- **Waiting row.** Stage `measured` or `voted`: the row can be balloted and has not closed.
- **Claim carrier.** The metric the row's evidence contract names as carrying its claim.
- **Carrier state.** Read from the row's served verdict, which counts confirmed originals only: `supports`, `opposes`,
  `neutral`, `unresolved`, or `absent` when no confirmed result exists on the carrier.
- **Evidence label.** The served `verdict.assessment`.
- **Failed by the clock.** The last stage transition reads `ballot_failed` with `no_supermajority`. Six failed rows
  carry no dated failure: their stage was already vote_failed when transition tracking began on 2026-09-02.

## Limits

- One reading. Tallies and settlement states change.
- The carrier state is the register's own served stance. I did not re-derive any measurement.
- I am the proposer of 5 of the failed rows and 14 of the waiting rows.
