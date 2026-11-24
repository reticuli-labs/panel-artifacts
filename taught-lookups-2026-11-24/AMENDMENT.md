# Amendment to the plan, 2026-11-24: the instrument as planned missed both known cases

Written after run 1 and before run 2. Run 1 is kept as it came out: `results_run1.json` and `run1.log`.

## What happened

The plan names two known cases the instrument must find. Run 1 found neither. On both it answered no item at all.

- **The send-snapshot replica.** The plan splits a bank by the parity of an item's place in the list. That bank lists its two
  instructions in turn, so every `send-snapshot` item fell into one half and every `grant-live-view` item into the other. No
  ordered menu of one half occurs in the other, and the lookup abstained on all 144. A split by parity is tied to the order in
  which a generator writes its items, and that order is part of the design.
- **The frozen pool.** Its files list the options as bare codes, A to D, and print the option texts inside the question. The
  lookup learned "the key is A" for a label, which is balanced by design and says nothing. Ten bank files in the sweep list bare
  codes: this pool, `multiply-the-quantity-frozen-pool-2026-09-27`, `because-ever-since-cells-audit-2026-10-24` and
  `prob-odds-replication-2026-09-13`.

So the faults were in my instrument, and I had not run it on the two cases it was built for before I wrote the plan. I had run
other scripts on them.

## What changes for run 2

1. The split. Each bank's items are shuffled once with a fixed seed and dealt into four parts. An item is scored by a lookup
   taught on the three other parts.
2. The option texts. Where an item lists bare codes and its question prints `A = ...`, the texts are taken from the question.

Nothing else changes: the five lookups, the null, the flag, the controls.

## What this costs the result

Run 2 is not the run the plan fixed in advance. I changed the instrument after seeing that it failed, and I saw run 1's list of
flagged banks before I changed it. The two changes are aimed at the two known cases and at nothing else, but a reader should
weigh run 2 as a second look. Run 1 flagged 20 banks with the instrument that could not see the known cases, and with keys drawn
at random it flagged none. Both runs are published.

If run 2 misses a known case again, I say so and stop: a third change to the instrument on the same day is tuning.
