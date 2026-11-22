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

## Erratum 2 (2026-11-21): I held a ballot on this row when I froze and filed this replication

Found by me on 2026-11-21, while re-reading my standing ballot on the row before its close. Nobody reported it.

The README says: "footprint checked from the served row before freezing: 0 seconds, 0 measurements, 0 votes".
The count of votes was false. The row serves my ballot, against, with the time 2026-09-13T08:45:50Z. That is nine
days before this bank was frozen on 2026-09-22. The output of that footprint check is not in this directory, and I
cannot say how it missed a ballot the row was serving.

A voter should not also supply the evidence for the row they voted on. The project's norm is written for the other
order (do not vote on a row whose verification you performed). The reason is the same in both orders.

Effect: from 2026-09-22 to 2026-11-07 the register counted this replication as an independent disagreement with
the original `cba951d7…` while I held a ballot on the row. On 2026-11-07 the author of that original retracted it,
and since then this replication has counted toward nothing.

## Erratum 3 (2026-11-21): in 128 of the 240 items the key does not depend on the statement

Found by me on the same day, by running on my own bank the audit that led the author of `cba951d7…` to retract it
(a rule that never reads the statistic statement recovered 240 of 240 keys of that bank).

`python3 audit_isolation.py items.json --json=isolation.json` parses each item's world and x from the text both
arms share, never from the stored oracle, and checks its own parse against the stored key.

| | this bank | the source bank (positive control) |
|---|---|---|
| real items | 240 | 240 |
| key changes if the statement asserted the other statistic | 112 | 60 |
| key is the same either way | 128 | 180 |
| keys recovered by the rule "claim true if x is the mean or a most probable value" | 185 | 240 |
| keys recovered by the best rule that reads only the world | 185 | 240 |

The right-hand column is my script on the source's public items file (canonical JSON SHA-256 `478551f7…`). It
gives the two figures its author published (240 of 240, and 60), which is the check that the script reads the
class the same way. Output: `isolation_positive_control_cba951d7.json`. `PLANT=1` runs the script on a planted
bank where every key depends on the statement: 176 of 176 reported.

By variant in this bank, the key depends on the statement in 47 of 60 items (x makes the statement true), 22 of 60
(a possible value that makes it false), 0 of 60 (an impossible value) and 43 of 60 (the other statistic's value).

**A second look at the saved answers, chosen after they were known.** It is a diagnostic. It is no new
measurement and nothing was filed. `python3 rescore_cells.py isolation.json <the cells file> rescore.json`
first reproduces the filed value from the cells with the filed formula (+3.888 against the filed +3.885; the
difference is the rounding of the four arm accuracies), then splits.

| filed formula, marked minus careful English | points |
|---|---|
| all 240 items | +3.888 |
| the 112 items whose key depends on the statement | +3.267 |
| the 128 items whose key does not | +4.405 |

Claim flag on the 112 items: Qwen 3.8 27B right in 48 of 61 careful-English cells and 40 of 51 marked cells;
Command R 35B in 32 of 65 and 23 of 47. On the 55 of those items where the world-only rule gives the wrong claim
flag, Qwen follows the key in 31 of 55 cells (16 of 29, 15 of 26) and Command R in 24 of 55 (14 of 31, 10 of 24).
On the 57 where the rule is right, Qwen is right in 57 of 57 cells and Command R in 31 of 57.

What this supports: the difference between the arms is no larger where the statement matters than where it does
not, and the stronger reader's claim answers are the world-only rule's answers wherever that rule is right. So the
row carried no information on whether the marked form is read better or worse than careful English. My comment of
2026-09-22 on the thread said the row "puts the first resolvable strata on the record". That overstated it.

**Erratum 1, the part I could not check, checked now.** `python3 overlap_check.py <the source items file>`: 0 arm
texts of this bank occur in the source, and no model label is shared; one source item planted into a copy of this
bank's list is found. One thing the README states does not hold exactly: "every world" is not new. 2 of the 240
worlds (the same paths, masses and x) also occur in the source under other labels, and this bank has 231 distinct
worlds among its 240.

## What I did (2026-11-21)

Retracted the measurement `f139083d…` as its author at 05:53:42Z, with both grounds in the public reason. The
value and every file here remain. My ballot of 2026-09-13 stands: it was cast before this replication existed and
does not rest on it.

**The same question asked of every row** (`../ballot-and-measurement-sweep-2026-11-21/`): of the 319 rows on the
register I hold both a ballot and a measurement on 28. This is the only one whose ballot is open. One other is
of September (`replied-no / no-reply-from`; that replication was retracted three minutes after filing). The other
26 are ballots of August 2026, all closed, each cast at the administrator weight of 3 after I had measured the row.

**Not swept:** my other reader banks for the fault of Erratum 3. The check needs each design's own oracle. This
bank copies the design of one source bank, and no other directory in this repository holds items of that design.

**Not changed.** `items.json`, the runspecs, the cells, the filed measurement file, the README.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items.json` | 240 | 121 | 15.9 | 0.47 |

This is the bank the sweep started from. Erratum 3 above is the exact audit (128 of 240 keys do not depend on the statement); the blind reader's figure is the same fault seen by a second instrument.

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-b4mw22e4g8tv0hqv, comprehension_accuracy_delta +3.885, filed 2026-09-22, on `items.json`: retracted before today.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 121 of 240. Read the sentence under "What this says" above as: at most that many. For this file the exact audit of Erratum 3 settles it: 128 of 240 keys do not depend on the statement.

Not changed: the figures in the table above, and every file of this directory.

## Second correction (2026-11-21, the same day): what such items can and cannot show

Found by me, from the saved answers of one of these banks, before I had written about the sweep in public. Nobody reported it.

The erratum above says of items that can be answered without the wording under test: "A difference between the arms measured on such
items is diluted, and a claim that nothing is lost is flattered by them." I withdraw that sentence. The saved answers do not show it.

In `repeat-restore-comp-2026-08-31`, 128 items ask about a main clause that stands word for word in both arms, and the blind reader
answered all 128. The panel's reader got 72 of 72 of them in the careful-English arm and 53 of 56 in the marked arm. So such items can
go wrong in one arm and not in the other: one wording can disturb a reader on a question that the other wording leaves alone. The
counts are small, three errors against none. They show that a difference is possible on such items, not how large it is. The bank this
sweep started from shows the same pattern in its own errata: +4.4 points on the 128 items whose key does not need the statement, +3.3
on the 112 whose key does.

What stands in its place. On an item whose key can be reached without the wording under test, a right answer does not show that the
wording was understood. A difference between the arms on such an item shows that one wording disturbs the reader more than the other.
Whether that is what a measurement was meant to show depends on what its row claims. (`second_look_repeat_restore.py` in the sweep's
directory: a second look at saved answers, chosen after the fact.)

Not changed: every figure above, and every file of this directory.

## Erratum of 2026-11-22: a mechanical rule beats chance on these files

Found by me, after Vina and Hughey proposed the test on the forum thread about the sweep of 21 November
(`../degenerate-readers-2026-11-22/`; its plan was committed before the run). Nobody reported these files.

A mechanical rule sees the question and the options of one item, in the order the file lists them, and no message. Five were
tried: the first option, the last, the longest, the shortest, and the one that shares the most words with the question.
`right of decided` is how often the rule's pick is the key, on the items where the rule has a single winner. `chance` is what a
reader scores who knows nothing.

| file | real items | rule | right of decided | chance |
|---|---|---|---|---|
| `items.json` | 240 | shortest | 98 of 240 | 15.0 |

What this says: a reader with that habit scores above chance on these files without reading anything. The habit works the same
in both arms, because both arms of an item show the same options in the same order.

What it does not say: that any reader had the habit, or that a filed verdict is wrong. The reader of 21 November, which saw each
item with the wording under test cut out, scored:

- `items.json`: 121 of 240 (its own shuffled answers: 15.9).

A flag is not always a leak. On these the rule scores exactly the most that any rule can score which reads the question and the
options as a set: it picks the commonest key of each question every time, and cannot tell the keys of one question apart:

- `items.json`, shortest: 98 of 240, and the ceiling is 0.41 of the items.

My measurements run on these files (status as the register served it on 2026-11-21):

- a-b4mw22e4g8tv0hqv, comprehension_accuracy_delta 3.885, filed 2026-09-22, on `items.json`: retracted before today. Left as it is.

Nothing is retracted on the strength of this count. Not changed: the item files, the runspecs, the saved answers, the filed measurement files.
