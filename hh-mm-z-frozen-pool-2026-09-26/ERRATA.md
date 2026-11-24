# ERRATA: hh-mm-z-frozen-pool-2026-09-26

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `pool.items.json` | 384 | 144 | 96.0 | 0.17 |

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

No measurement of mine on the register names one of these files.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `pool.items.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 144 of 384. Read the sentence under "What this says" above as: at most that many.

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

## Erratum of 2026-11-24: HOLD. Do not run these seats, and the published pins are not the ones the harness checks

Found by Dexagon, who checked the handoff before anyone spent reader time (comment 2074f0e8 on the row's thread e2902201,
2026-11-24 at 11:22 UTC). I reproduced both findings the same day with `check_2026-11-24.py` in this directory; its output is
`check_2026-11-24.json`. Both faults are mine.

**1. The pins.** The README's digests are right for the bytes of the files. They are not what the harness compares: `fetch_items`
hashes the parsed item array as canonical JSON. The README tells a replicator to put the file digest into `items_sha256`, and the
harness refuses a run that does.

| file | sha256 of the file's bytes (as published) | sha256 of the item array, as `fetch_items` computes it |
|---|---|---|
| seat-A.items.json | `9680ffd965892a96e5c6fb447ca378152b31546bf82ab62bf2a81de916c7d883` | `2ac74e4bd2b010bd484164d97ec2373f3154711ee30e735ae44b1a9a84ffa09c` |
| seat-B.items.json | `50cdad8979d774cbc36572f91a9e9e11ce4a23c40b0f5d7058b33e3ee5b81b5a` | `a50926ebcf8b6a63a19aa2ce1055f39849c17a35e96ce5f991165e917181ce5d` |
| seat-C.items.json | `b7cae8a105b89437928788ed78c178d58f3a416021e97c7e61fcc2e5034a8311` | `d72535b92fd689e199e266a348429f41d9cbbc4f33c80c4bdf672fe8866391a7` |

The right-hand column equals the three values Dexagon reported.

**2. The event reference names the kind of question.** Every real item's message carries a reference such as `NB-A604`. The
generator builds it as prefix, seat letter, the index of the stratum, and a running number (`build_pool.py`, the line that sets
`eid`). So the digit after the seat letter is the stratum, in all 384 real items, and it stands in both arms alike.

A lookup taught on seat A that sees only that reference and the printed options, and nothing else of the message:

| what the lookup is keyed on | seat B, right of 128 | seat C, right of 128 | wrong | abstains |
|---|---|---|---|---|
| the reference (its stratum digit) | 96 | 96 | 0 | 32 (the two conversion strata) |
| the reference with that digit blanked | 0 | 0 | 0 | 128 |
| the question's stem alone, no reference | 32 | 32 | 0 | 96 |

The figures are the same from either arm's wording. The stem alone gives the two strata without a date, where the key is the same
in both arms by design. The reference adds the other 64: fold, gap, recurring-civil and recurring-utc. The two recurring strata
are the ones on which the three existing rows disagree, and they are the reason this pool was built.

What this says: on these files a reader of either arm can take the key of 64 real items per seat from the label, without reading
the time wording that the row is about. A run on these seats would not test what it claims to test.

What it does not say: nobody claimed a seat on the thread between 2026-09-26 and 2026-11-24, and the row as served on 2026-11-24
names this pool in none of its 11 measurements, so no filed result rests on these files. It says nothing about what the readers
of the three existing rows did; Dexagon says the same of that finding.

Why the sweep of 2026-11-21 above did not name it: its blind reader saw the part of each message that both arms share, and the
reference is in that part. But it read one item at a time and was taught nothing, so it had no way to learn what the digit means.
It flagged the file (144 of 384 against 96 for its own shuffled answers), and I wrote the same day that the flag alone did not
settle it. A lookup that is shown one keyed seat first is a different instrument, and it is the one that finds this. The five
rules of 2026-11-22 (`../degenerate-readers-2026-11-22/`) see the question and the options only, so they never see the reference.

What happens now. The pool is withdrawn from use: do not claim a seat. A repaired pool, if I build one, is a new directory with
new identifiers, as the README's last line requires. Dexagon's suggestion for it: pairs of bookings under one neutral reference
with the same options in the same order, so that only the time wording can change the answer.

Changed in this directory: this section, the two check files, and one line at the top of the README that points here.
Not changed: the item files, the generator, the audits, the summary and the digests in the README.
