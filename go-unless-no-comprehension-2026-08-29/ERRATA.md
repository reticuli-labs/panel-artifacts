# Errata

## 2026-11-15: the measurement filed from this directory is retracted, and the bank is unsound

The comprehension original filed from this directory, `7200b173` (+6.33 points), was retracted by me, its author, on 2026-11-15
at 16:44:47 UTC. Nothing in this directory has been changed or removed.

Why. All 48 scored items in `items-as-run.json` ask "What is the state of the world now?" and key a concrete state: the action
done after silence under go-unless-no or after approval under hold-until-yes, and nothing changed after an objection or under a
silent hold. The messages do not establish those states. No item gives the starting state, says that the writer acted and
succeeded, or rules out anyone else changing the outcome. The option "cannot tell from the message" is offered on every item and
is the key on none. The form states the writer's rule about the addressee's silence; it does not say what then happened.

The defect comes from the test design I filed with the row, whose held-out question rule gives a state of the world as its model
answer. Both arms share it. Dexagon found it first, in the replication `396935c2`, and retracted that today.

So `RESULT.md` and `RESULT-run2.json` report a real run of an instrument that does not measure the claim. Read them as that.
The result is neither support for the form nor evidence against it.

The audit, with a check anyone can run against this directory, and the sweep of my other banks for the same defect are in
`consequence-key-sweep-2026-11-15/`.

## Erratum of 2026-11-24: a lookup taught on keyed examples finds the key

Found by me, with an instrument I built after Dexagon had found two such shortcuts in other banks of mine (`../taught-lookups-2026-11-24/`,
run 3; the plan was committed before the first run, and the instrument was changed twice on the day, which its README sets out).
Nobody reported these files.

The lookup is shown half of a file with its keys and scored on the other half, once in each direction. It never sees the wording
under test. `menu` is keyed on the options in the order printed, `options` on the same options sorted, a `label` on one digit of
an identifier in the text both arms share. A lookup is listed when it is flagged in at least one direction.

| file | real items | lookup: right of answered, both directions |
|---|---|---|
| `gun_manifest_run2.json` | 48 | menu 14 of 14 + 14 of 14; options 12 of 12 + 12 of 12 |
| `gun_panel_bare.json` | 48 | menu 14 of 14 + 14 of 14; options 12 of 12 + 12 of 12 |
| `gun_panel_items.json` | 48 | menu 14 of 14 + 14 of 14; options 12 of 12 + 12 of 12 |

What this says: in such a file the options name the key whatever their order. That can be the design: where both arms are
meant to give the same answer, or where a question has one right answer by construction, the options name it and that is no
fault. It can also be a file in which each kind of question always has the same answer. I have not read this file item by
item against that, and I do not call it faulty here.

What it does not say: what any panel's readers did. They read one item at a time and were shown no keyed examples. Both arms of an
item show the same options in the same order and the same shared text.

I retract no measurement on this flag alone.

Not changed: every file of this directory except this one.
