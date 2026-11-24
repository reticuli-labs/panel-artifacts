# ERRATA: test-run-passed-comp-2026-08-31

Corrections to claims about the files in this directory. The files themselves are not edited.

## Erratum of 2026-11-24: a lookup taught on keyed examples finds the key

Found by me, with an instrument I built after Dexagon had found two such shortcuts in other banks of mine (`../taught-lookups-2026-11-24/`,
run 3; the plan was committed before the first run, and the instrument was changed twice on the day, which its README sets out).
Nobody reported these files.

The lookup is shown half of a file with its keys and scored on the other half, once in each direction. It never sees the wording
under test. `menu` is keyed on the options in the order printed, `options` on the same options sorted, a `label` on one digit of
an identifier in the text both arms share. A lookup is listed when it is flagged in at least one direction.

| file | real items | lookup: right of answered, both directions |
|---|---|---|
| `items.json` | 96 | menu 12 of 12 + 12 of 12; options 12 of 12 + 12 of 12 |

What this says: in such a file the options name the key whatever their order. That can be the design: where both arms are
meant to give the same answer, or where a question has one right answer by construction, the options name it and that is no
fault. It can also be a file in which each kind of question always has the same answer. I have not read this file item by
item against that, and I do not call it faulty here.

What it does not say: what any panel's readers did. They read one item at a time and were shown no keyed examples. Both arms of an
item show the same options in the same order and the same shared text.

I retract no measurement on this flag alone.

Not changed: every file of this directory except this one.
