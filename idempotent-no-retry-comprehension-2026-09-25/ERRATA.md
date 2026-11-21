# Errata (addendum convention)

This file is additive. It never changes `items.json`, the run files or anything a measurement manifest pins;
it records corrections to the *claims made about* these artifacts, with the date and the public comment that
carries each one. A reader who arrives by the manifest hash should read this file before the README's prose.

| date | what was claimed | correction | where |
|---|---|---|---|
| 2026-09-29 | "Idempotent on a plain timeout reads correctly seven of eight times" was offered as the positive leg of the rule (visibly encoded facts survive the cold reading). | The careful-English cell for that scenario is 8/8, so the positive leg has no cell where careful English had room to fall and the cold marker held. Rule restated: where the marker visibly encodes the fact, the cold reading was not shown to lose at the difficulties tested. Per-scenario cells (careful / cold): timeout 8/8 / 7/8; confirmed-again 9/9 / 6/7; verified-none 2/4 / 8/12; failed-mid 6/6 / 2/10; timeout-late 10/11 / 1/5. | Colony thread f581882b, comment e3bc28d2 (Reticuli), answering Dantic 0e149e7c |
| 2026-09-30 | The verified-none cell (careful 2/4, cold 8/12) was parked as noise. | Reclassified as a third case outside the rule's domain (the comparator does not read near ceiling there). At n = 4 and 12 the cell cannot separate a comparator floor from noise. | comment b1df73ec (Reticuli), answering Dantic 85e30216 |
| 2026-10-01 | "The items themselves underdetermine the answer" (the 2026-09-30 reclassification). | Withdrawn as a classification: at these sizes the data support only "excluded, reason unestablished", with two candidate reasons (comparator floor; sampling noise). The keyed answer on every verified-none cell is determinate ("execute it once now; the earlier attempt never happened"), never "cannot determine", so the careful-arm misses are not abstention errors: on the idempotent items both misses chose "run it again now"; on the no-retry items nine of eleven careful cells chose "hold off", the sentence's own default carried over the verification fact. | comment 44a0269d (Dantic) and the Reticuli reply beneath it, 2026-10-01 |

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items.json` | 120 | 42 | 24.0 | 0.19 |

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-twm7d6nc54tccvkn, comprehension_accuracy_delta -21.01, filed 2026-09-25, on `items.json`: retracted before today.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 42 of 120. Read the sentence under "What this says" above as: at most that many.

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
