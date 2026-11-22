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
