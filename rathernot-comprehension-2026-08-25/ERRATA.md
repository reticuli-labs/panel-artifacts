# ERRATA: rathernot-comprehension-2026-08-25

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items-bare.json` | 288 | 158 | 98.7 | 0.31 |
| `items-careful.json` | 288 | 169 | 98.4 | 0.37 |

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-cef29htze4cmyz4b, comprehension_accuracy_delta +11.14, filed 2026-08-26, on `items-bare.json`: left active (the excess is under 0.5: erratum only).
- a-cef29htze4cmyz4b, comprehension_accuracy_delta -23.44, filed 2026-08-26, on `items-careful.json`: left active (the excess is under 0.5: erratum only).

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.
