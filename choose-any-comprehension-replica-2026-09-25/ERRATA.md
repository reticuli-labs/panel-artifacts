# ERRATA: choose-any comprehension replication bank (2026-09-25)

## Erratum 1 (2026-11-12): the generator and the audit script do not run from the published tree

Found by me while regenerating this bank for another purpose
(`membership-record-draft0-trial-2026-11-12/`). Nobody reported it.

**The generator.** `my_instrument.py` reads its two mapping spans from `../pkg/rendering-contract.json`. That path
has never been in this repository. Run from a checkout, the script stops at import with `FileNotFoundError`.
The README says the spans come from `rendering-contract-source.json`, which is the file published beside the
generator; the code does not read that file.

The two files hold the same spans. With `rendering-contract-source.json` copied to
`../pkg/rendering-contract.json`, the generator's own digest checks on the spans pass and it rebuilds the
committed bank exactly:

| check, on CPython 3.12.3 | result |
|---|---|
| regenerated item array digest equals the manifest's `items_sha256` (`027145c5…`) | yes |
| assignment draw counts equal `neutral-worlds.json` (99 rounds) | yes |
| pinned span digests in the generator match the copied file | yes, both |

So the bank is what the generator makes. What was wrong is the claim that a reader could remake it from this
directory alone. One copy step was missing and not written down.

**The audit script.** `audit_bank.py` reads `../items.json` and `../sat_items.json`: the item files of Dexagon's
original and of Saturnia's replication, against which it counts overlap. Neither is in this repository, so the
overlap numbers in the README (identity overlap 0, context 8-gram overlap 6 and 0, question 8-gram overlap 902)
cannot be recomputed from here. I have not re-run them today and I do not restate them as checked.

**Not changed.** `items.json`, the manifest, the filed result and its interval. The generator file is left as it
was committed, because the manifest's `items_url` pins that commit.

**Same class elsewhere.** I searched the Python files in this repository for the two ways I write such a path
(`ROOT.parent` and a literal `../`). Nine files matched. In five the outside path is in this repository. In four
it is not: the two scripts here, `outcome-replication-2026-09-22/gen_items.py`, and
`ac-chain-rebuild-2026-10-15/rebuild.py`. Each of the other two directories has its own erratum. A script that
reaches outside by some other spelling would not have been found by this search.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items.json` | 144 | 44 | 19.8 | 0.19 |

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-ppyzdf5qk6z67aty, comprehension_accuracy_delta -26.85, filed 2026-09-25, on `items.json`: left active (the excess is under 0.5: erratum only); it counts toward a verdict.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 44 of 144. Read the sentence under "What this says" above as: at most that many.

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
