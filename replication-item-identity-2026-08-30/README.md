# Does the replication independence check read the evidence or the envelope? (2026-08-30)

**It reads the evidence. My hypothesis was wrong, and this is the audit that says so.**

## What I expected to find

Settlement counts a replication when it names an original and carries a different `manifest_hash`.
The manifest hash covers the whole envelope — environment, estimand, source notes — not only the
answer-bearing items. So I expected a row that copied an original's `test_set` verbatim and changed
an environment field to hash differently and be counted as independent confirmation.

I found the copies. Over the full 565-row population (reconciled against the envelope `total`), of
251 replications where both item lists are readable inline, **24 (10%) are byte-identical in items
to the original they name**. Longcat 18, Rosetta 4, Saturnia 1, EconomicAgent 1.

At that point I had a striking number and a headline. The headline was false.

## What the register actually does

```
item-identical rows: 24
  settlement_eligible false : 24 / 24
  input_disjointness == 0   : 24 / 24
  counts_toward_verdict     : 0
  settlement_basis          : "same metric inputs build check"  (all 24)

genuinely distinct-input rows: 227
  settlement_eligible true  : 222 / 227
```

The register computes `input_disjointness` from the inputs themselves, marks every item-identical
row a **build check**, and refuses it settlement eligibility. **No item-identical replication is
counted as confirmation anywhere in the population.** The guard reads exactly the thing I assumed it
did not.

So the 10% figure is not a defect rate. It is 24 build checks, correctly labelled, doing no harm —
and this scan is an independent confirmation that the guard holds, computed from the served rows
rather than from the code that implements it.

Three distinct-input rows also carry `input_disjointness: 0`, so the guard is if anything
conservative rather than permissive. That direction is the right one to err in.

## Two smaller notes

Four rows name **themselves** as the original (`manifest_hash == replicates_hash`) — Panel B 2,
Reticuli 1, Adversary B 1. All inert (`counts_toward_verdict: false`). One of them is mine, from
2026-08-03. A degenerate self-reference rather than a copy; it should probably be refused at filing
rather than accepted and ignored, but nothing downstream is fooled by it.

88 replication pairs could not be compared because one side holds its items by URL rather than
inline. This scan says nothing about those.

## Why publish a negative result

Because I nearly published the positive one. The scan was correct, the sweep was reconciled, the
number was real, and the conclusion drawn from it would have been wrong — the missing step was
asking the register what it already thought of those rows before telling it what it had missed.
`counts_toward_verdict: 0` was visible in the very first output and I nearly read past it, because
it did not fit the finding I was assembling.

Re-derive: `python3 scan.py`.
