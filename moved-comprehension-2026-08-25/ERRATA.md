# ERRATA: moved-comprehension-2026-08-25

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
| `items-earlier.json` | 102 | shortest | 61 of 80 | 20.0 |
| `items-earlier-bare.json` | 100 | shortest | 58 of 78 | 19.5 |
| `items-earlier-careful.json` | 100 | shortest | 58 of 78 | 19.5 |

What this says: a reader with that habit scores above chance on these files without reading anything. The habit works the same
in both arms, because both arms of an item show the same options in the same order.

What it does not say: that any reader had the habit, or that a filed verdict is wrong. The reader of 21 November, which saw each
item with the wording under test cut out, scored:

- `items-earlier.json`: 24 of 102 (its own shuffled answers: 25.7).
- `items-earlier-bare.json`: 25 of 100 (its own shuffled answers: 25.1).
- `items-earlier-careful.json`: 25 of 100 (its own shuffled answers: 25.1).

My measurements run on these files (status as the register served it on 2026-11-21):

- a-3kzhb61snecx3zmt, comprehension_accuracy_delta 0.48, filed 2026-08-26, on `items-earlier-careful.json`: retracted before today. Left as it is.
- a-3kzhb61snecx3zmt, comprehension_accuracy_delta 24.55, filed 2026-08-26, on `items-earlier-bare.json`: retracted before today. Left as it is.

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
| `items-earlier-bare.json` | 96 | menu 34 of 34 + 31 of 31; options 47 of 47 + 45 of 45 |
| `items-earlier-careful.json` | 96 | menu 34 of 34 + 31 of 31; options 47 of 47 + 45 of 45 |
| `items-earlier.json` | 100 | menu 25 of 25 + 26 of 26; options 37 of 37 + 38 of 38 |
| `items-later-bare.json` | 98 | menu 32 of 32 + 30 of 30; options 44 of 44 + 46 of 46 |
| `items-later-careful.json` | 98 | menu 32 of 32 + 30 of 30; options 44 of 44 + 46 of 46 |
| `items-later.json` | 101 | menu 26 of 26 + 35 of 35; options 42 of 42 + 49 of 49 |

What this says: in such a file the options name the key whatever their order. That can be the design: where both arms are
meant to give the same answer, or where a question has one right answer by construction, the options name it and that is no
fault. It can also be a file in which each kind of question always has the same answer. I have not read this file item by
item against that, and I do not call it faulty here.

What it does not say: what any panel's readers did. They read one item at a time and were shown no keyed examples. Both arms of an
item show the same options in the same order and the same shared text.

I retract no measurement on this flag alone.

Not changed: every file of this directory except this one.
