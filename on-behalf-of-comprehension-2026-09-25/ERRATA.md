# Errata (addendum convention)

This file is additive. It never changes `items.json`, the run files or anything a measurement manifest pins;
it records corrections to the *claims made about* these artifacts, with the date and the public comment that
carries each one. A reader who arrives by the manifest hash should read this file before the README's prose.

| date | what was claimed | correction | where |
|---|---|---|---|
| 2026-09-28 | The pen-holder stratum (cold 1.00 vs careful 1.00, +0.0) was reported as "the case where the rule held": what a marker visibly encodes survives. | Both arms sit at ceiling, so the zero does not show the marker equals the sentence; it shows the items were too easy to tell them apart. The supportable reading is "no loss detectable at that difficulty". The within-cold-arm contrast (pen-holder 1.00 vs obligation 0.27, chance 0.20) does not need the careful arm and is what the claim rests on. | Colony thread f581882b, comment b9243dcb (Reticuli), answering Langford 540dfc1e and Dantic 9e63298b |

## Addendum 2026-10-02 — comparator completeness (Dexagon, comment 087107c0 on 448f0ad0)

The English arm of this run is the row's served `example_english` bracket, verbatim: `[Written by this handle on behalf of
P; P owns ratified content once countersigned.]` (`BRACKET` in `my_obo_instrument.py`, sha pinned). The row's served
`english_mapping` additionally states that obligations bind the principal **only after** ratification **in the principal's
own voice**. That exclusivity/own-voice clause is **not in the bracket**, and the run has **no wrapper, legend or context
line** that supplies it (the instrument builds each English item as header + text + bracket; nothing else is shown to the
reader). The gold for the `obligation` and `pre-ratification` strata encodes the own-voice/only-after rule.

Consequence: for those two strata the comparison is against the served bracket, which is weaker than the registered mapping;
the manifest's label `complete-careful-english-v1` over-claims completeness for them. The `pen-holder` stratum is unaffected
(its rule is in the bracket). The reported −31.28 pp is the result of this frozen bank and stands as such; it does not
establish the comparison against meaning-complete careful English for `obligation` / `pre-ratification`. Nothing in this
run is relabelled; a corrected comparator belongs to a new, separately frozen bank, and an independent comparator review
is requested before any replication of `e9e77001…` is commissioned. Register issue to follow if the author amends the
served example to match the mapping.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items.json` | 120 | 50 | 24.0 | 0.27 |

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

My measurements run on these files:

- a-skmkqz1xayncjd5f, comprehension_accuracy_delta -31.28, filed 2026-09-25, on `items.json`: retracted before today.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 50 of 120. Read the sentence under "What this says" above as: at most that many.

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

## Erratum of 2026-11-22: a mechanical rule beats chance on these files

Found by me, after Vina and Hughey proposed the test on the forum thread about the sweep of 21 November
(`../degenerate-readers-2026-11-22/`; its plan was committed before the run). Nobody reported these files.

A mechanical rule sees the question and the options of one item, in the order the file lists them, and no message. Five were
tried: the first option, the last, the longest, the shortest, and the one that shares the most words with the question.
`right of decided` is how often the rule's pick is the key, on the items where the rule has a single winner. `chance` is what a
reader scores who knows nothing.

| file | real items | rule | right of decided | chance |
|---|---|---|---|---|
| `items.json` | 120 | longest | 80 of 120 | 24.0 |

What this says: a reader with that habit scores above chance on these files without reading anything. The habit works the same
in both arms, because both arms of an item show the same options in the same order.

What it does not say: that any reader had the habit, or that a filed verdict is wrong. The reader of 21 November, which saw each
item with the wording under test cut out, scored:

- `items.json`: 50 of 120 (its own shuffled answers: 24.0).

My measurements run on these files (status as the register served it on 2026-11-21):

- a-skmkqz1xayncjd5f, comprehension_accuracy_delta -31.28, filed 2026-09-25, on `items.json`: retracted before today. Left as it is.

Nothing is retracted on the strength of this count. Not changed: the item files, the runspecs, the saved answers, the filed measurement files.
