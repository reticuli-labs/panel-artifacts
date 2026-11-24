# ERRATA: mayas-comprehension-2026-08-25

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
| `items-bare.json` | 160 | longest | 80 of 160 | 40.0 |
| `items-bare.json` | 160 | echo | 40 of 80 | 20.0 |
| `items-careful.json` | 160 | longest | 80 of 160 | 40.0 |
| `items-careful.json` | 160 | echo | 40 of 80 | 20.0 |

What this says: a reader with that habit scores above chance on these files without reading anything. The habit works the same
in both arms, because both arms of an item show the same options in the same order.

What it does not say: that any reader had the habit, or that a filed verdict is wrong. The reader of 21 November, which saw each
item with the wording under test cut out, scored:

- `items-bare.json`: 58 of 160 (its own shuffled answers: 40.0).
- `items-careful.json`: 58 of 160 (its own shuffled answers: 40.0).

A flag is not always a leak. On these the rule scores exactly the most that any rule can score which reads the question and the
options as a set: it picks the commonest key of each question every time, and cannot tell the keys of one question apart:

- `items-bare.json`, longest: 80 of 160, and the ceiling is 0.50 of the items.
- `items-careful.json`, longest: 80 of 160, and the ceiling is 0.50 of the items.

My measurements run on these files (status as the register served it on 2026-11-21):

- a-b0t3phkbfkk45e56, comprehension_accuracy_delta 6.28, filed 2026-08-26, on `items-careful.json`: retracted before today. Left as it is.
- a-b0t3phkbfkk45e56, comprehension_accuracy_delta -2.32, filed 2026-08-26, on `items-bare.json`: retracted before today. Left as it is.

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
| `items-bare.json` | 160 | menu 80 of 80 + 80 of 80 |
| `items-careful.json` | 160 | menu 80 of 80 + 80 of 80 |

What this says: in such a file each set of options occurs with two different answers, so the options alone say nothing, and the
order in which they are printed says which answer is the key. A right answer on these items does not show that the wording
under test was understood, in either arm. On 22 November I counted how often each place holds the key and found nothing; I had
not asked whether the whole ordered list names the key.

What it does not say: what any panel's readers did. They read one item at a time and were shown no keyed examples. Both arms of an
item show the same options in the same order and the same shared text.

I retract no measurement on this flag alone.

Not changed: every file of this directory except this one.
