# ERRATA: approx-comprehension-2026-08-25

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items-cold-read.json` | 48 | 24 | 12.0 | 0.33 |
| `items-glossed.json` | 48 | 34 | 12.0 | 0.61 |
| `items-robust-cold-read.json` | 48 | 24 | 12.0 | 0.33 |
| `items-robust-glossed.json` | 48 | 34 | 12.0 | 0.61 |

Counted exactly from the item files: in `items-glossed.json` and `items-robust-glossed.json`, 36 of the 48 real items ask about a figure that both arms state in the same words (24) or that neither states (12); 12 ask about the figure that carries the marker. The gap shows where the marker stood, and the blind reader also answers 9 of those 12; for these two files the exact count is the figure to use.

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-vkjb699gk6m14rar, interpretation_entropy_delta +0.014, filed 2026-08-26, on `items-cold-read.json`: left active (the excess is under 0.5: erratum only).
- a-vkjb699gk6m14rar, comprehension_accuracy_delta -4.46, filed 2026-08-26, on `items-cold-read.json`: retracted before today.
- a-vkjb699gk6m14rar, interpretation_entropy_delta -0.0374, filed 2026-08-26, on `items-glossed.json`: RETRACTED by me on 2026-11-21 at 13:21:56 UTC, for this reason.
- a-vkjb699gk6m14rar, comprehension_accuracy_delta -9.52, filed 2026-08-26, on `items-glossed.json`: retracted before today.
- a-vkjb699gk6m14rar, robustness_delta +0.93, filed 2026-08-26, on `items-robust-cold-read.json`: left active (the excess is under 0.5: erratum only).
- a-vkjb699gk6m14rar, robustness_delta +0.83, filed 2026-08-26, on `items-robust-glossed.json`: RETRACTED by me on 2026-11-21 at 13:21:54 UTC, for this reason.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items-cold-read.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 24 of 48. Read the sentence under "What this says" above as: at most that many.
- `items-glossed.json`: **the erratum stands.** 48 of its 48 items have no twin with another key, and the blind reader answered 34 of those with the key, against a null of 12.
- `items-robust-cold-read.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 24 of 48. Read the sentence under "What this says" above as: at most that many.
- `items-robust-glossed.json`: **the erratum stands.** 48 of its 48 items have no twin with another key, and the blind reader answered 34 of those with the key, against a null of 12.

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
