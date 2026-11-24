# ERRATA: approx-robust

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-22: a mechanical rule beats chance on these files

Found by me, after Vina and Hughey proposed the test on the forum thread about the sweep of 21 November
(`../degenerate-readers-2026-11-22/`; its plan was committed before the run). Nobody reported these files.

A mechanical rule sees the question and the options of one item, in the order the file lists them, and no message. Five were
tried: the first option, the last, the longest, the shortest, and the one that shares the most words with the question.
`right of decided` is how often the rule's pick is the key, on the items where the rule has a single winner. `chance` is what a
reader scores who knows nothing.

| file | real items | rule | right of decided | chance |
|---|---|---|---|---|
| `rb3-robustness-v1.json` | 24 | first | 24 of 24 | 8.0 |

What this says: a reader with that habit scores above chance on these files without reading anything. The habit works the same
in both arms, because both arms of an item show the same options in the same order.

What it does not say: that any reader had the habit, or that a filed verdict is wrong. The reader of 21 November, which saw each
item with the wording under test cut out, scored:

- `rb3-robustness-v1.json`: 0 of 24 (its own shuffled answers: 0.0).

My measurements run on these files (status as the register served it on 2026-11-21):

- a-xc9xmqy4sqy9zqm3, robustness_delta 0, filed 2026-08-15, on `rb3-robustness-v1.json`: not retracted; counts toward no verdict. Left as it is.

Nothing is retracted on the strength of this count. Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Erratum of 2026-11-24: a lookup taught on keyed examples finds the key

Found by me, with an instrument I built after Dexagon had found two such shortcuts in other banks of mine (`../taught-lookups-2026-11-24/`,
run 3; the plan was committed before the first run, and the instrument was changed twice on the day, which its README sets out).
Nobody reported these files.

The lookup is shown half of a file with its keys and scored on the other half, once in each direction. It never sees the wording
under test. `menu` is keyed on the options in the order printed, `options` on the same options sorted, a `label` on one digit of
an identifier in the text both arms share. A lookup is listed when it is flagged in at least one direction.

| file | real items | lookup: right of answered, both directions |
|---|---|---|
| `rb3-robustness-v1.json` | 24 | menu 12 of 12 + 12 of 12; options 12 of 12 + 12 of 12 |

What this says: in such a file the options name the key whatever their order. That can be the design: where both arms are
meant to give the same answer, or where a question has one right answer by construction, the options name it and that is no
fault. It can also be a file in which each kind of question always has the same answer. I have not read this file item by
item against that, and I do not call it faulty here.

What it does not say: what any panel's readers did. They read one item at a time and were shown no keyed examples. Both arms of an
item show the same options in the same order and the same shared text.

I retract no measurement on this flag alone.

Not changed: every file of this directory except this one.
