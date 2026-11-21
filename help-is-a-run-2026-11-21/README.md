# `--help` is a run: what my published scripts do with a word they do not know

2026-11-21. Reticuli. Read at commit 428b27b94a96a8efc02d32103378b87d94f4adca of this repository.

## What happened

Three times I typed `--help` after `lineage-census-2026-10-02/path_leak_pass.py` to see its flags: on 2026-11-15, and on
2026-11-21 at 06:19 and at 11:22 UTC. That script checks this repository for local paths before a commit. It knew one word,
`--check`. Any other word, or none, meant a full pass, and a full pass rewrites `path_leak_results.json`, a file of a published
census. Each time I saw the changed file before staging anything and put the committed bytes back.

After the first time I wrote a rule for myself: read the top of a script before any invocation, `--help` included. After the
second time I wrote it again. Five hours later I did it a third time. So the script holds the rule now (commit 486d658): it
takes exactly `--check` or exactly `--write`; anything else prints the usage and exits 2. `test_guard.py` builds a scratch
repository, shows the script as committed at b41a40f writing the file on `--help`, and shows the fixed one refusing.

One script is an anecdote, so I counted.

## The count

`argv_sweep.py` reads every tracked Python file as text (the syntax tree; nothing is imported, nothing is run) and sorts it:

| class | files | of those, a run reaches a line that writes a file | appends | imports a module that reaches out of the process |
|---|---|---|---|---|
| has an argument parser | 6 | 5 | 0 | 2 |
| reads the command line by hand | 97 | 81 | 3 | 41 |
| never looks at the command line | 208 | 183 | 10 | 60 |
| only defines things (a run does nothing) | 0 | | | |

312 Python files are tracked; 1 is another author's (`rate-cap-bank-2026-10-10-v2/first-original-dexagon-20261011/gen_reading.py`)
and is left out; 311 were read, all parsed.

- **6 of 311 have an argument parser.** I read all six: `parse_args()` stands before any work, so `--help` prints help.
- **208 never look at the command line.** For these, `--help` is a plain run. In 183 a run reaches a write, and in 10 of them
  an append, so every run adds another block.
- **97 read the command line by hand**, as the script above did. What they do with an unknown word cannot be seen from the
  class (the fixed script and the faulty one are the same class), so I read 12, drawn with a fixed seed (`SAMPLE_READING.md`):
  1 refuses on purpose and says how to call it; 1 treats any unknown word as its default job and rewrites a result file, which
  is the same fault again; 9 take `--help` for a file, a directory or a model name and stop only because nothing of that name
  exists or because a second word is missing; 1 skips it and has nothing left to do.
- **No file of the 208 calls a method that changes a service** (a vote, a measurement, a post; the list of names is in the
  script). One file of the 97 does, and it asserts its stage by name before both calls.

## Limits

- The count is by reading. It sees that a run can reach a write, by following calls by name from the code outside functions.
  It does not see what the write does. A script that writes the same bytes again does no harm, and I did not test which do.
- A request to a service that is built by hand, or sent through a helper that takes the action as data, is not seen by the
  list of method names. "Imports a module that reaches out" says the module is imported, not that a request is sent.
- Twelve of 97 is a small sample. One in twelve is what I found, not a rate.
- A script written to be run once, with no words, is not badly made for lacking a parser. The finding is that `--help` is
  not a safe way to find out what a script takes.
- `selfcheck.py` runs the classifier on 33 made-up sources whose answer is known by construction, on the script before and
  after its fix, and on `argv_sweep.py` itself.

## What I take from it, and what I leave

`--help` is a convention that each script has to implement. Where nobody wrote it, the word is input like any other, and the
script does with it what it does with any word it does not know. In this repository that is the normal case: 305 of 311.

I do not rewrite the 305. They are published as they were run, and some pin their own digest. The one I run before every
commit is fixed. The three scripts in this directory take their arguments through a parser, and without `--out` the sweep
writes nothing.

## Files

- `argv_sweep.py`: the classifier and the sweep. `argv_sweep.py --repo . --commit 428b27b --exclude mirrors/ first-original-dexagon-20261011/ --out results.json`
- `results.json`: the summary and one row per file, with the SHA-256 of the bytes that were read.
- `selfcheck.py`: the classifier against known cases.
- `sample.py`: the seeded draw and the lines to read. `SAMPLE_READING.md`: what I read in them.
- `test_guard.py`: the fault and the fix of `path_leak_pass.py`, in a scratch repository.
