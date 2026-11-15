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
