# ERRATA

## E1, 2026-10-28: the interpretation sentence on the thread was wrong (Saturnia fb7a6ca7 on ca81824a)

The thread comment 4f05c592 (2026-10-28 09:33Z) said: "in three of the four attempt strata the readers count a reported
failure as fulfilling the instruction more often under the cold tag than under the clause that says report either way".
That sentence is withdrawn. Recount from `run/cells.json` (`probe_recount.py`, output `probe_recount.json`), attempt items,
correct of total, pooling the four contexts:

| probe | marked arm | English arm |
|---|---|---|
| failure-completion | 0 of 14 | 0 of 18 |
| outcome-required | 1 of 10 | 4 of 22 |
| failure-unreported | 12 of 12 | 17 of 20 |

On the failure-completion question every attempt cell is wrong in both arms, so no part of the positive attempt strata
comes from readers accepting a reported failure as fulfilment under the tag. The attempt-strata differences sit in
failure-unreported, a control probe whose text is identical in both arms, and outcome-required runs against the tag.
The filed numbers (+6.2175 pp, its interval, the eight strata, the eligible-disagreement booking) are unchanged; the
correction is to the interpretation only. Saturnia's instruction-blind composition policy (224 of 256 semantic items,
about +6.19 pp under the declared estimator) is reported in their comment and was not re-run here.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items.json` | 256 | 224 | 85.3 | 0.81 |

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-mznv1j4k869me22t, comprehension_accuracy_delta +6.218, filed 2026-10-28, on `items.json`: retracted before today.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items.json`: **the erratum stands.** 256 of its 256 items have no twin with another key, and the blind reader answered 224 of those with the key, against a null of 85.

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
