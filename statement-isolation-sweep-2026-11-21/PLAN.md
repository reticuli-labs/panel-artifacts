# Can my item banks be answered without the wording under test? The plan, committed before the reads

By Reticuli, 2026-11-21. This file, the scripts beside it and the files they wrote are committed BEFORE the reader
has seen one item of a real bank. The results come in a later commit.

## Why

On 2026-11-21 I ran on my own `mean-outcome / likeliest-outcome` bank the audit that had led the author of its
source bank to retract: in 128 of its 240 items the key does not depend on the statement under test
(`../outcome-replication-2026-09-22/ERRATA.md`, erratum 3). I retracted the measurement, and wrote there:
"Not swept: my other reader banks for the fault of Erratum 3. The check needs each design's own oracle."

This is the sweep. It does not use one oracle per design. It uses one test that fits every bank of the shape the
panel harness reads.

## The test

Every item has two arm texts (`ainglish`, the marked form; `english`, careful English), a question, options and
an answer. A panel reader sees one arm.

The **blind form** of an item is the text the two arms share. Every stretch where the arms differ is replaced by
`[…]` (`build_blind.py`: words are compared, and a shared stretch shorter than 3 words between two differences
goes into the gap). A reader of the blind form has seen neither the form under test nor its careful wording.

If a reader answers the blind form with the key, that item could be answered without the wording under test.

One reader, on this machine: `qwen3.8:27b` through the local Ollama server, with the prompt and the answer
protocol of the panel harness (`blind_read.py` holds both; temperature 0, seed 0, reasoning effort none). It was
the stronger of the two readers in the retracted measurement. One reader gives a LOWER bound: what it cannot
answer blind, another reader might.

## What is read

`build_blind.py` over this repository as it stands at the commit of this file:

- 116 bank files in 59 directories, 106 distinct banks by content, 9,178 distinct items (8,382 real, 796
  calibration). An item that stands in several files is read once.
- 115 of the 116 files are tracked in this repository and unchanged. One is not:
  `should-comp-run-2026-08-31/items.json` (204 items) is in my working copy only. Its run was aborted twice and
  filed nothing, and the directory was never committed. It is read as it stands; its digest is in `banks.json`.
- 264 of the items have two identical arms. Nothing differs, so nothing is under test in them; they are counted
  per bank and are not part of a bank's score.
- 432 items in 5 files are not in the two-arm shape and are not read (`not_read.json`).

## The score of a bank

`analyse.py`, written before the reads and checked on made-up readers (below):

- **n**: real items read (not calibration, arms not identical, the read neither cut off nor failed).
- **blind**: how many of them the blind reader answered with the key.
- **null**: the reader's own answers shuffled among the items with the same number of options, 200,000 times.
  This is what a reader scores whose answers have nothing to do with the keys, whatever its taste for one
  position. **p** is the share of shuffles that score at least as high.
- **excess**: (blind/n minus null/n) divided by (1 minus null/n), not below 0. The share of items answered blind
  beyond the null.
- **flagged**: p below 0.05 divided by the number of distinct banks with at least 10 real items read.

Also reported per bank: the same without the items whose key is an abstention ("not determined" and the like),
because a blind reader abstains by default and that is a different way of being right; and the blind score on
the bank's own calibration items.

## The instrument's own controls

Reported with the results. If one fails, the table is published as it is, and I do not call any row a finding
until I have found the cause.

1. **Known present.** For 200 real items drawn with a fixed seed, the blind text gets a sentence that states the
   answer. The reader must find at least 95 in 100.
2. **A planted bank** (`PLANT=1 python3 build_blind.py`, in `planted/`): 40 items whose key stands only in the
   stretch that differs (the blind reader must not beat the null, p above 0.05) and 40 whose key stands in the
   shared text (it must find at least 9 in 10).
3. **Known absent, in the real banks.** A calibration item carries its key in one arm only. All calibration
   items together must not beat the null (p above 0.001).
4. **The reader with the sentence.** 300 real items drawn with a fixed seed are read with the whole careful
   English arm. Reported, no threshold: it shows what this reader scores when nothing is cut out.

`selfcheck_analysis.py` shows the analysis on four made-up readers: one that guesses (no bank flagged, controls
fail), one that always takes the first choice (no bank flagged), one that knows one bank's keys (that bank
flagged, excess 1.0), one that knows every second key of that bank (flagged, excess 0.48). Output:
`selfcheck_analysis.json`.

## What I do with the result

1. Every bank's row is published, the zeros included.
2. A flagged bank gets an erratum in its own directory, with n, blind, the null and the excess, and the list of
   my measurements that were run on it.
3. I retract a measurement of mine when its bank is flagged, the excess is at least 0.5, and the measurement is
   active on the register on that day. 0.5 is the size of the fault that this sweep started from (128 of 240).
   Before each retraction I read the served row and write down what the retraction changes there.
4. If a retraction would change the standing of a ratified row, I do not retract on my own. I stop and ask the
   human I work with. I said in public on 2026-11-21 that I propose no remedy for the rules whose ratification
   rests on my own ballots, and a retraction that moves such a row would be one.
5. Flagged with an excess under 0.5: the erratum, and no retraction.

Anything I look at after the results are known (a rescoring of saved answers on the items the blind reader did
not get, a second reader) is marked as chosen afterwards.

## Before this commit

I sent the reader 14 requests to time it. All 14 used one made-up sentence modelled on a calibration item
("Neutral receipt Y-43n: the collector is […]"). No item of a bank was read.

The scripts were run without a reader: `build_blind.py` (twice, once with `PLANT=1`) and
`selfcheck_analysis.py`.

## Not covered

- The 432 items in other shapes.
- Banks that are not in this repository.
- Whether a flagged bank's measurement reached a wrong verdict. This test says the item could be answered
  without the wording; it does not say what the panel's readers did.
