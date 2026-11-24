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

# Second amendment, 2026-11-24: run 2's chance figure was too small, and its own control showed it

Written after run 2 and before run 3 was written to this directory. Run 2 is kept as it came out: `results_run2.json`,
`run2.log`, and the script that made it, `taught_run2.py`.

## What happened

Run 2 found both known cases: 144 of 144 on the send-snapshot replica by `menu`, 80 of 80 on each seat of the frozen pool by
`label0`. It flagged 41 banks.

Its control did not hold. With every key drawn at random, three banks were still flagged. At the level I set, fewer than one in
ten such runs should flag anything.

The cause is in how I scored. Each item was answered by a lookup taught on the other parts, and all answers were added up. Take
a menu that occurs in two items in different parts. The first is right exactly when its key equals the second's, and the second
is right exactly when its key equals the first's: both right or both wrong, never one of each. The chance figure treats every
answer as its own draw, so it is too small, and a bank is flagged too easily. Run 1 scored the same way, with two parts; its
control flagged nothing, which was luck and not a check that passed.

A second fault, found while looking for the first: some banks list an item twice, identical in everything a lookup sees. Taught
on one copy and scored on the other, the lookup is right by copying. Eleven bank files have such repeats.

## What changes for run 3

1. One direction at a time. A bank's distinct items are shuffled once with the fixed seed and dealt into two halves. A lookup is
   taught on one half and scored on the other, and that is one test. The other direction is a second test. Given the taught
   half, each scored answer is its own draw, so the chance figure holds. The number of tests doubles and the level per test
   halves with it.
2. An item listed twice in a bank is used once.

Nothing else changes.

## What this costs the result

This is the third form of the instrument in one day, and I said after the first amendment that a third change on the same day is
tuning. I make it anyway, for one reason: run 2's flags rest on a chance figure that its own control refutes, and publishing them
as flags would be wrong. The change follows from the control and from nothing I saw in a bank's result. I ran the changed script
once, to a scratch file, before writing this section, so I had seen run 3's list when I wrote it. I change nothing after this,
whatever run 3 shows.

What a reader can take from run 2 without its chance figure: the banks where a lookup answered many items and was right on every
one. Keys drawn at random do not produce that.
