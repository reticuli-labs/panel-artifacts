# ERRATA: mean-outcome / likeliest-outcome replication bank (2026-09-22)

## Erratum 1 (2026-11-12): the generator does not run from the published tree

Found by me in a sweep that started from the same defect in `choose-any-comprehension-replica-2026-09-25/`.
Nobody reported it.

The README says that `python3 gen_items.py` regenerates `items.json` byte for byte and asserts zero overlap with
the source items file. The script reads that source file from `../src0_items.json`, which has never been in this
repository. Run from a checkout, it builds the 252 items, then stops with `FileNotFoundError` before it writes
anything.

What I could check today, in a scratch copy on CPython 3.12.3: with an empty list standing in for the missing
file, the script writes an `items.json` whose bytes equal the committed file (SHA-256 `ef63c73d…`). So the
committed bank is what the generator makes.

What I could not check: the overlap assertion. With an empty stand-in it passes without testing anything. The
source items file is not here, so "zero overlap with the source" is not recomputable from this directory, and I
do not restate it as checked.

**Not changed.** `items.json`, the runspecs, the filed result. The generator is left as committed.
