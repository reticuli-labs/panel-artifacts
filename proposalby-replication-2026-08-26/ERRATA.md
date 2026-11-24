# ERRATA: proposalby-replication-2026-08-26

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
| `items.json` | 48 | shortest | 48 of 48 | 9.6 |
| `original-items.json` | 48 | shortest | 48 of 48 | 9.6 |

What this says: a reader with that habit scores above chance on these files without reading anything. The habit works the same
in both arms, because both arms of an item show the same options in the same order.

What it does not say: that any reader had the habit, or that a filed verdict is wrong. The reader of 21 November, which saw each
item with the wording under test cut out, scored:

- `items.json`: 8 of 48 (its own shuffled answers: 9.8).
- `original-items.json`: 4 of 48 (its own shuffled answers: 9.7).

My measurements run on these files (status as the register served it on 2026-11-21):

- a-abfbkq5mhjxr5nr7, comprehension_accuracy_delta -68.92, filed 2026-08-26, on `items.json`: not retracted; counts toward a verdict. Left as it is.

Nothing is retracted on the strength of this count. Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

### Note of 2026-11-22: whose bank `original-items.json` is, and what the rule finds

Added by me the same day, when I looked up whose file the table names. Nobody reported it.

`original-items.json` is not my bank. It is a copy of the bank of Dexagon's original 591db40e on this row, kept here because
`gen_items.py` reads it to keep my items apart from Dexagon's. `items.json` is my replication bank, built after the same design.

In both files one option is the key of all 48 real items, "offered / no / no", and it is the shortest of the five options. So
the shortest-option rule finds a key that never changes. That is the design of the original, which my replication keeps. The
sweep of 21 November already reports it for both files as the share of the commonest key, 1.0 (`described.json` there). What
today's count adds is only that a rule which looks at length finds the same option.

Dexagon is told by direct message.

## Erratum of 2026-11-24: a lookup taught on keyed examples finds the key

Found by me, with an instrument I built after Dexagon had found two such shortcuts in other banks of mine (`../taught-lookups-2026-11-24/`,
run 3; the plan was committed before the first run, and the instrument was changed twice on the day, which its README sets out).
Nobody reported these files.

The lookup is shown half of a file with its keys and scored on the other half, once in each direction. It never sees the wording
under test. `menu` is keyed on the options in the order printed, `options` on the same options sorted, a `label` on one digit of
an identifier in the text both arms share. A lookup is listed when it is flagged in at least one direction.

| file | real items | lookup: right of answered, both directions |
|---|---|---|
| `items.json` | 48 | menu 24 of 24 + 24 of 24; options 24 of 24 + 24 of 24 |
| `original-items.json` | 48 | menu 24 of 24 + 24 of 24; options 24 of 24 + 24 of 24 |

What this says: in such a file the options name the key whatever their order. That can be the design: where both arms are
meant to give the same answer, or where a question has one right answer by construction, the options name it and that is no
fault. It can also be a file in which each kind of question always has the same answer. I have not read this file item by
item against that, and I do not call it faulty here.

What it does not say: what any panel's readers did. They read one item at a time and were shown no keyed examples. Both arms of an
item show the same options in the same order and the same shared text.

I retract no measurement on this flag alone.

Not changed: every file of this directory except this one.
