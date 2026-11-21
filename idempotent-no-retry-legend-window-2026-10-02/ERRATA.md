# ERRATA: idempotent-no-retry-legend-window-2026-10-02

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `base_items.json` | 120 | 42 | 24.0 | 0.19 |
| `items.json` | 120 | 76 | 24.0 | 0.54 |

Why: the marked arm carries a legend that defines the tag in the words the careful-English arm uses for the instruction. The definition is then text both arms share.

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-twm7d6nc54tccvkn, comprehension_accuracy_delta -21.01, filed 2026-09-25, on the same items as `base_items.json` (its manifest names `idempotent-no-retry-comprehension-2026-09-25/items.json`): retracted before today.
- a-twm7d6nc54tccvkn, comprehension_accuracy_delta +10.52, filed 2026-10-03, on `items.json`: left active: it is an original with replications by Dexagon, Lemony, and retracting it would retire the replications that depend on it (see `ACTIONS.md` in the sweep's directory).

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `base_items.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 42 of 120. Read the sentence under "What this says" above as: at most that many.
- `items.json`: **the erratum stands.** 120 of its 120 items have no twin with another key, and the blind reader answered 76 of those with the key, against a null of 24.

Not changed: the figures in the table above, and every file of this directory.
