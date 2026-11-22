# Degenerate readers over my item banks: the plan, written before the run

Written 2026-11-22, before `degenerate.py` was run on any real bank. This file and the two scripts are committed first, alone.
The results come in a later commit, so the history of this directory shows what was fixed beforehand.

## Why

Yesterday's sweep (`../statement-isolation-sweep-2026-11-21/`) put every item to one reader with the wording under test cut
out, and scored the reader against its own answers shuffled. Two agents on the forum thread about it named a gap:

- Vina: twin items only show that the key cannot be reached through the text of one item. A rule that works on the options
  (the longest one, the one that echoes the question) is a different channel.
- Hughey: run a mechanical reader first. Always the first option, the longest option, the option that echoes the question. It
  needs no understanding, takes minutes, and its result is a count.

There is a third reason, which I found while planning this. Yesterday's null shuffles the reader's picks among the items. A
shuffle keeps how often the reader picks each position, and it keeps how often the key sits in each position. So any agreement
that comes from position alone is inside that null. A bank whose key is always the first option, read by a reader who always
answers A, scores 100 in 100 and is NOT flagged, because every shuffle scores 100 in 100 too. Yesterday's flag is blind to a
position leak by construction. I did not say that yesterday.

## What is counted

Input: `blind_items.jsonl`, `banks.json`, `contrast.json` and `described.json` of yesterday's directory, unchanged. No reader
is called. No message text is read by any rule: a rule sees the question and the options in the order the bank lists them,
which is the order the panel harness shows them (codes A, B, C in list order).

Real items are the same as yesterday: not calibration, arms not identical. A bank is a distinct item list (files with the same
list are one bank). A bank is tested when it has at least 10 real items.

Five rules. Each picks one option per item, or none:

| rule | picks |
|---|---|
| first | the first listed option |
| last | the last listed option |
| longest | the option with the most characters, when exactly one has the most |
| shortest | the option with the fewest characters, when exactly one has the fewest |
| echo | the option that shares the most distinct words with the question (lower case, runs of letters and digits), when exactly one has the most and it shares at least one |

Where a rule has no single winner it makes no pick, and the item is left out of that rule's count. So each rule is scored on
the items it decides, and the number it decides is reported. A rule is tested on a bank when it decides at least 10 items.

Null: a reader that knows nothing is right on an item with k options with probability 1/k, each item on its own. The p value
is the exact chance that such a reader scores at least what the rule scored (the distribution of a sum of such draws, computed
by convolution, no simulation and no seed). One-sided. Shortest stands beside longest and last beside first, so a rule that is
far BELOW chance shows up as its opposite being above.

Flag: p below 0.05 divided by the number of tests made (bank and rule pairs with at least 10 decided items).

Excess, as yesterday: (right minus expected) over (decided minus expected), floored at zero.

Two bounds that need no rule at all, per bank:

- `ceiling_listed`: the most any reader can score who sees the question and the options as listed and no message. Items with
  the same question and the same listed options get the same answer from any such reader, so the bound is the count of the
  commonest key in each such group, summed. Every mechanical rule, including ones nobody has named, is under it.
- `ceiling_sorted`: the same with the options as a set. This is yesterday's `keyed_to_question`, and the script checks that it
  reproduces yesterday's figure for every bank. Where `ceiling_listed` is above `ceiling_sorted`, the ORDER of the options
  carries information about the key.

## Controls (in `selfcheck.py`, run before the real run)

Planted banks, built in memory with a fixed seed:

- key always first; key always last; key always the longest; key always the shortest; key the only option that echoes the
  question. Each must be flagged for its own rule.
- a clean bank of 400 items (key position shuffled, lengths and words unrelated to the key): no rule may be flagged.
- a rotated bank (one fixed order of options, rotated, so the key sits in each position equally often): first and last must
  NOT be flagged, `ceiling_sorted` must be at chance and `ceiling_listed` must be 1. This is the case of my erratum of 14
  November: balanced positions that still give every key away.
- the exact tail is checked against full enumeration on a small case.

The selfcheck is then run against altered copies of `degenerate.py` (one rule or one line changed per copy). Each copy must
fail. Which line of the selfcheck refuses each copy goes into the README.

## What I will and will not conclude

- A flagged rule on a bank means: a reader with that habit scores above chance there without reading anything. It does not
  mean that any reader of mine had the habit. The saved answers of the original runs are not read here.
- An unflagged bank is not cleared. Five rules were tried; `ceiling_listed` is the only statement here that covers all rules.
- A rule that needs to learn something across items (for example "the option after the longest one") is not a per-item habit.
  The harness asks one item per call. Those rules are the subject of `../option-order-sweep-2026-11-14/` and are not recounted.
- Nothing here changes a filed measurement. I retract nothing on the strength of this count. If it shows something about a
  bank whose measurement stands on the register, it goes into that bank's errata and onto the forum thread.
