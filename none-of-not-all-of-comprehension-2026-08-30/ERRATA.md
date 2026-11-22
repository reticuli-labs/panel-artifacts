# ERRATA: none-of-not-all-of-comprehension-2026-08-30

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
| `items.json` | 192 | longest | 96 of 192 | 64.0 |
| `items.json` | 192 | echo | 96 of 192 | 64.0 |

What this says: a reader with that habit scores above chance on these files without reading anything. The habit works the same
in both arms, because both arms of an item show the same options in the same order.

What it does not say: that any reader had the habit, or that a filed verdict is wrong. The reader of 21 November, which saw each
item with the wording under test cut out, scored:

- `items.json`: 37 of 192 (its own shuffled answers: 64.0).

A flag is not always a leak. On these the rule scores exactly the most that any rule can score which reads the question and the
options as a set: it picks the commonest key of each question every time, and cannot tell the keys of one question apart:

- `items.json`, longest: 96 of 192, and the ceiling is 0.50 of the items.
- `items.json`, echo: 96 of 192, and the ceiling is 0.50 of the items.

No measurement of mine is joined to these files.

Nothing is retracted on the strength of this count. Not changed: the item files, the runspecs, the saved answers, the filed measurement files.
