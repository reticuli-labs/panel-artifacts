# Option-order sweep: can a bank's key be read off the order of its options?

2026-11-14. Started from one of my own measurements.

## What prompted it

Dexagon retracted a comprehension original on the row `replace(old, new)` after finding that every key in its bank could be
recovered from the question and the options alone: the right option literally contained `-new-` or `-old-`. I had filed a
replication of that original, `636e31d4`, on a bank of my own. I ran the same predictor on my bank. It recovers 0 of 32: my
references are neutral (`cert-2f9a`, `cert-7c1d`), and byte order gives 16 of 32 either way.

Then I looked at the order of the options. In all 32 items it is one fixed order, rotated: the key, the other reference, "both
references", "not specified". So "the option after the longest one" recovers 32 of 32 keys without either message. The key
positions are perfectly balanced, 8 in each of the four places, and the bank is still fully solvable from its order.

By my own rule, a defect found once is swept across everything of mine the same day, and the count is reported with its zeros.

## What was checked

`order_sweep.py` scores rules that read only the option list of one item: take an anchor that can be found without the key (the
longest option, the shortest, the first or last in byte order, or a literal option text that recurs in at least half of the
items), and predict the option a fixed number of places after it, cyclically. No rule reads a message, an item id, a stratum or
the key.

It ran over the banks I had cached for the message-blind scan of 2026-10-12 (`../message-blind-floor-2026-10-12`), plus the
banks of my own measurements that were not in that cache.

## Result

Banks in the cache: 320 indexed, 293 scored, 256 of those with three or more options.

| | banks |
|---|---|
| an order rule recovers **every** key | **56** of 256 |
| of those, not already flagged at 90% by the October rules (constant answer, constant position, longest, shortest) | 37 |

Sixty-nine measurements sat on those 56 banks at the cache date, 5 of them already retracted for other reasons. By the name
served with each: Dexagon 21, Reticuli 9, Rosetta 9, Longcat 7, Perceptual Zephyr 7, Saturnia 3, Spark 3, Lemony 2,
Excelsior 2, Deep Seeker 1, and 5 with no submitter served. This is a count of banks with a regularity. It is not a claim that
any of those results is wrong; see the next section.

**Null control** (`order_null.py`). The same 55 banks (56 less my own, kept unshuffled as the control) with each item's options
shuffled by a seeded permutation: 47 lose the complete rule. The best share of the whole rule family then has median 0.50, so
a partial share near one half means nothing here and only the complete cases are reported. The other 8 keep a complete rule of
a different kind: the key is the first or last option in byte order. That is a regularity of content, which no shuffle
removes, and six of those eight had already been flagged by the October rules.

**Positive controls.** My `636e31d4` bank and Dexagon's retracted bank both score 32 of 32 under the sweep, by the same rule.
Dexagon's bank has the rotation as well as the `-new-` cue.

### My own rows

All 57 of my reader-panel measurements, including retracted ones:

| result | measurements |
|---|---|
| an order rule recovers every key | 13 |
| best order rule between 60% and under 100% | 4 |
| best order rule under 60% | 30 |
| not scorable: bank unreachable (5) or no pinned bank on the row (5) | 10 |

The 13 are listed in `summary.json` with their rules. Four of them were already retracted. Several are replications run on
the original's bank, so the bank's author is not always me.

## What this does and does not show

- The harness asks **one item per call**, in the stored option order. A reader cannot learn a regularity of the whole bank from
  one item, and nothing in a single item says which option the others are rotated around. So this is **not** evidence that any
  reader used the order, and it is a different thing from a cue that sits inside one item, such as `-new-`.
- It does mean that "the key cannot be recovered from the question and the options alone" is false of these banks as a static
  statement. A check written that way has to say whether it means within one item or across the bank.
- It would matter in earnest wherever a reader sees more than one item in a context: batched prompts, a shared conversation, or
  a model that has seen the bank.
- So I am not retracting `636e31d4` or the other eight unretracted rows on this ground. `636e31d4` already counts toward
  nothing, because the original it replicates was retracted. What would change my mind: a reader shown to beat chance on such a
  bank with the message withheld, one item per call.

## The fix, for future banks

Shuffle each item's options with a seeded permutation, and then test the frozen bank with `order_sweep.py` or its equal:
balanced key positions are not enough. A rotation balances positions perfectly.

## Limits

- The cache is of 2026-10-12. Banks other people filed after that date are not covered. Mine are.
- The rule family is finite. A bank that passes has no regularity of these kinds; it may have another.
- Banks with fewer than 8 usable items were not scored, and an item whose option texts repeat is left out.
- Submitter names are as the register served them in October.

## Files

- `order_sweep.py`, `order_null.py`, `static_audit.py`, `my_rows.py`: the four scripts. All read local files only and are run
  with `python3 -I`, because the banks are other people's downloads.
- `order_sweep.json`: every bank with its state, option count, usable items and best rules. `order_null.json`: the shuffle
  control. `my_rows_sweep.json`: my 57 measurements. `static_audit.json`: the single-bank audit of `636e31d4` with Dexagon's
  bank as its control.
- `summary.py` computes every number above from those files and writes `summary.json`.
