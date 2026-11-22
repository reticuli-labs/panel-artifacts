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
