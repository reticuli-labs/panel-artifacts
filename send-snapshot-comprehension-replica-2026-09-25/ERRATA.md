# ERRATA: send-snapshot-comprehension-replica-2026-09-25

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items.json` | 144 | 79 | 36.0 | 0.40 |

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-v7argdk2hebtextg, comprehension_accuracy_delta -30.22, filed 2026-09-25, on `items.json`: left active (the excess is under 0.5: erratum only); it counts toward a verdict.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items.json`: **cleared by its own design.** Every item has a twin in the file: the same text, question and options under the other form, with the other key. No reader without the wording can score above 0.50; the blind reader scored 0.55. What it beat was its own shuffled answers, because some options can be dismissed without the wording. The key cannot be reached without the wording here, and nothing in this file is diluted. The sentence under "What this says" above does not hold for it.

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

## Third correction (2026-11-22): what "cleared by its own design" covers

Found by me, when Vina asked on the forum thread what the twin test leaves open (`../degenerate-readers-2026-11-22/`). Nobody reported these files.

The correction of 21 November above calls these files cleared by their own design and says: "No reader without the wording can
score above 0.50". That is more than the design gives.

The two twins hold the same text, question and options. They do not list the options in the same order:

- `items.json`: 72 twin groups, 0 of them listed in one order. The blind reader scored 79 of 144; the most a reader of the content can reach is 72.

So the reader was not asked the same thing twice. What the design gives: no rule that reads the content can score above one
half, and a reader for whom the order of the options says nothing about the key scores one half at most on average, not in
every run. What it does not give is a bound on a rule that reads the order.

Counted today on the order:

- `items.json`: the first option is the key in 36 of 144 items and the last in 36 (chance 36.0). Key by place: 1 of 4: 36, 2 of 4: 36, 3 of 4: 36, 4 of 4: 36. No rule of the five is flagged.

I found nothing that says the order gives the key away in these files. I have not shown that it cannot.

Not changed: every figure above, and every file of this directory.
