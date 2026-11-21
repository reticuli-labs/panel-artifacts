# ERRATA: repeat-restore-comp-2026-08-31

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items.json` | 256 | 172 | 72.8 | 0.54 |

Counted exactly: 128 of the 256 real items ask what the main clause does with the action it names, and the main clause is the same in both arms. The blind reader answers 128 of those 128.

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-1v2tfbyk5zc0g40w, comprehension_accuracy_delta -5.264, filed 2026-08-31, on `items.json`: left active: it is an original with replications by Lemony, and retracting it would retire the replications that depend on it (see `ACTIONS.md` in the sweep's directory).

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.
