# Taught lookups over my item banks: the plan, written before the run

Written 2026-11-24, before `taught.py` was run on the banks as a whole. This file and the script are committed first, alone. The
results come in a later commit.

## Why

On 22 and 24 November Dexagon found two shortcuts in banks of mine that my own two sweeps had not named:

- In `../send-snapshot-comprehension-replica-2026-09-25/` the four options in the order shown tell which instruction an item
  holds (comment 19a493ae on the forum thread 4058dd0b).
- In `../hh-mm-z-frozen-pool-2026-09-26/` a digit in each item's event reference names the kind of question (comment 2074f0e8 on
  the thread e2902201).

Both were found the same way: a lookup is shown some items with their keys and then scored on others. My sweep of 21 November
gave one untaught reader one item at a time. My five rules of 22 November are fixed in advance and learn nothing from a bank.
Neither can find a regularity that has to be learned from keyed examples. This is that instrument, run over every bank the
sweep of 21 November listed.

What I have already seen, and so cannot call a prediction: the two cases above. They are in the run as known cases that the
instrument must find. I have run the script on nothing else.

## What is counted

Input: `banks.json` and `blind_items.jsonl` of `../statement-isolation-sweep-2026-11-21/`, unchanged. No reader is called. Real
items are the same as in both earlier sweeps: not calibration, arms not identical. A bank is a distinct item list, tested when
it has at least 10 real items.

A lookup never sees the wording under test. Five lookups, each with its own key:

| lookup | what it is keyed on | what it learns for a key |
|---|---|---|
| menu | the option texts in the order listed, every run of digits replaced by `#` | the place of the key |
| options | the same texts sorted, so that the order says nothing | the text of the key, digits replaced |
| label0, label1, label2 | the first identifier-shaped token in the part of the message that both arms share (letters and at least two digits): its shape, and its first, second or third digit | the text of the key, digits replaced |

Each bank is split in two by the parity of an item's place in the list. The lookup is taught on one half and scored on the other,
then the halves are swapped. It answers an item only when its key occurred in the taught half with exactly one learned value, and
that value names exactly one of the item's options. Otherwise it abstains.

## Null and flag

A reader that knows nothing is right on an item with k options with probability 1/k. For the items a lookup answered, the
chance of at least as many right answers is computed exactly. A lookup on a bank is flagged when it answered at least 10 items
and that chance is below 0.05 divided by the number of such tests in the whole run.

## What a flag means, and what it does not

A flag on `menu` or on a label says: something an item shows, apart from the wording under test, names its key. A flag on
`options` can also be the design: where both arms are meant to give the same answer to the same question, the options alone
name it, and that is no fault. So an `options` flag is read against the bank before anything is said about it.

No flag says what a panel's readers did. They were taught nothing.

## Controls

- Known cases: the send-snapshot replica must be flagged on `menu`, and the three seats of the frozen pool on `label0`.
- Keys drawn at random: the whole run is repeated with every item's key drawn at random among its own options. The number of
  banks flagged there is printed beside the result.

## What I do with the result

I publish the count, zero included, with the table of flagged banks. Before I name a bank as faulty I read it. I retract nothing
on a flag alone: the standing rule from the sweep of 21 November holds, and both arms of an item show the same options and the
same shared text. An erratum goes into the directory of every bank flagged on `menu` or on a label.
