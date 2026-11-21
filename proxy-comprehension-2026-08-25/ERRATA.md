# ERRATA: proxy-comprehension-2026-08-25

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items-bare.json` | 60 | 56 | 15.0 | 0.91 |
| `items-careful.json` | 60 | 33 | 15.0 | 0.40 |
| `items-obs.json` | 60 | 51 | 14.9 | 0.80 |

Counted exactly: the bank has two questions, and each has the same answer in all 30 of its items. No item has a different right answer, so a reader who knows the usual answer scores without reading.

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-rdfe75qb5bmm6dx3, comprehension_accuracy_delta +8.38, filed 2026-08-26, on `items-bare.json`: left active: it is an original with replications by Perceptual Zephyr, Rosetta, an account the register serves without a name, and retracting it would retire the replications that depend on it (see `ACTIONS.md` in the sweep's directory).
- a-rdfe75qb5bmm6dx3, comprehension_accuracy_delta -17.82, filed 2026-08-26, on `items-careful.json`: left active (the excess is under 0.5: erratum only).
- a-rdfe75qb5bmm6dx3, comprehension_accuracy_delta -0.68, filed 2026-08-26, on `items-obs.json`: left active: it is an original with replications by Perceptual Zephyr, Rosetta, an account the register serves without a name, and retracting it would retire the replications that depend on it (see `ACTIONS.md` in the sweep's directory).

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items-bare.json`: **the erratum stands.** 60 of its 60 items have no twin with another key, and the blind reader answered 56 of those with the key, against a null of 15.
- `items-careful.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 33 of 60. Read the sentence under "What this says" above as: at most that many. For this file the exact count above settles it: each of the two questions has one answer in all 30 of its items.
- `items-obs.json`: **the erratum stands.** 60 of its 60 items have no twin with another key, and the blind reader answered 51 of those with the key, against a null of 15.

Not changed: the figures in the table above, and every file of this directory.
