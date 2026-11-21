# The sample, read by hand

`sample.py --repo . --results help-is-a-run-2026-11-21/results.json` draws 12 files of each class with the seed 20261121 and prints
the lines that decide the question. I read those lines, and where they did not settle it, the code around them (`git show`).
Nothing was run. The judgments below are mine, made on 2026-11-21 at commit 428b27b.

## Class "by hand": 12 of 97 drawn. What does the code do when `--help` is the only word on the command line?

| file | what the code does with it | outcome |
|---|---|---|
| `ac-clerk-draft-2026-11-21/clerk.py` | asserts two arguments, the first being `live` or `saved`; the assertion's message is the usage line | **refuses on purpose** and says how to call it |
| `adoption-judge-2026-08-25/judge.py` | takes the word as the name of a model; opens `candidates.json` in the current directory; with that file there, it asks the local model server for a model of that name | stops on an error nobody planned (no such file, or no such model) |
| `arcaeon-exchange/stranger_verify.py` | takes the word as a directory and lists it | stops: no such directory |
| `colony-notification-holes-2026-10-18/atnames.py` | takes the word as a directory, then reads a second argument | stops: the second argument is missing |
| `colony-notification-holes-2026-10-18/mention_precedence.py` | takes the word as a directory and opens a file in it | stops: no such file |
| `colony-thread-helper/fetch.py` | skips every word that starts with two hyphens; no identifier is left | nothing to do, and nothing is fetched |
| `gate-sweeps/2026-08-16-settlement-receipt-rev1/receipt_scan_v2.py` | the first word is the mode; only `snapshot` is tested for; any other word falls through to the compute pass, which writes `settlement_receipt_v2.json` | **runs its default job and rewrites a result file** |
| `insect-decline-methods-2026-11-14/fetch/kwic.py` | opens the word as a file | stops: no such file |
| `insect-decline-methods-2026-11-14/fetch/sources.py` | takes the word as a directory, then reads a second argument | stops: the second argument is missing |
| `insect-decline-methods-2026-11-14/verify_quotes.py` | skips words that start with two hyphens, then reads a first argument | stops: the first argument is missing |
| `novel-markers-audit-2026-10-12/refs_check/count_refs.py` | reads four arguments | stops: the second argument is missing |
| `outcome-replication-2026-09-22/overlap_check.py` | opens the word as a file | stops: no such file |

Counted: 1 refuses on purpose, 1 runs its default job and rewrites a file, 9 stop on an error that nobody planned, 1 has nothing
to do. The nine are safe by accident: a file or a directory with that name, or one more word on the line, and they would go on.

`receipt_scan_v2.py` has the fault this directory started from: a word the script does not know means the default.

## Class "never": 12 of 208 drawn

A file of this class does not read the command line, so there is nothing to judge: `--help` is a run. I read the 12 only to see
that each does work when run. All 12 do. 11 of them reach a write; the twelfth (`headroom-gate-flips-2026-08-31/verify.py`)
reads the register and prints. One of the 11 (`novel-markers-audit-2026-10-12/erratum2_order_labels.py`) appends a block to an
`ERRATA.md` each time it runs. On 2026-10-14 I ran a script of that kind to see its numbers and got the block twice.

## Class "parser": all 6

`attested-strata-uvf-2026-09-18/candidate.py`, `census.py`, `oracle.py`, `reference.py`, `gate-admission-quality-2026-08-30/simulate.py`,
`waiting-window-2026-10-04/bracket_read.py`. In each, `parse_args()` stands before any work: four parse at the start of `main()`,
two parse at the top of the file after the imports. `census.py` imports two sibling modules first; both keep their work under
`if __name__ == "__main__"`. So for all six `--help` prints help and stops.

## The one file that changes a service

`no-undo-token-original-2026-09-30/noundo_token.py` is the only file in which a run reaches a call that changes something at a
service (`mint_attempt`, `measure`). It reads the first word as the stage, and `assert STAGE == "mint"` stands before both
calls. With `--help` it stops before them.
