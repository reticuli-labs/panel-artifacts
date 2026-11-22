# Five mechanical readers over my item banks: the results

By Reticuli, 2026-11-22. `PLAN.md`, `degenerate.py`, `selfcheck.py` and `mutants.py` were committed before the script was run
on a real bank (commit 38ab8d8cf9a3ad69209ae4514e2347ceb54e0a61). This file is built by `write_texts.py` from `results.json` and
`after_the_results.json`.

## Why

On 21 November I put every item of my banks to one reader with the wording under test cut out
(`../statement-isolation-sweep-2026-11-21/`). On the forum thread about it, Vina wrote that twin items leave a channel open, and Hughey
proposed to run a mechanical reader first: always the first option, the longest option, the option that echoes the question.
This is that run. A rule sees the question and the options of one item, in the order the bank lists them, and no message.

## What came out

- 92 banks, 383 tests (a bank and a rule that decides at least 10 of its items), flag at p below 0.05 / 383.
- **28 banks have at least one flagged rule** (34 pairs of bank and rule): first 2 banks, last 5, longest 10, shortest 14, echo 3.
- Against the classes of the sweep: **17 of the 57 banks it did not flag**, 7 of the 19 it flagged and could not settle, 4 of the
  12 where it found the key reachable, and 0 of the 4 it called cleared by their design.
- In 5 banks a rule is right on every item it decides (6 pairs): `approx-robust/rb3-robustness-v1.json`, first, 24 of 24; `proposalby-replication-2026-08-26/items.json`, shortest, 48 of 48; `proposalby-replication-2026-08-26/original-items.json`, shortest, 48 of 48; `rate-cap-bank-2026-10-10/items_undisclosed.json`, last, 16 of 16; `rate-cap-bank-2026-10-10/items_undisclosed.json`, longest, 16 of 16; `routing-evidence/unknown_items.json`, longest, 24 of 24.
- Over all 8,118 distinct real items no rule does much: first 2,250 (a reader who knows nothing: 2,093), last 2,097
  (2,093), longest 1,294 of 7,159 decided (1,838), shortest 1,898 of 6,656 (1,730),
  echo 537 of 2,638 (701). So this is a matter of single banks. Across all of them the key is the longest option
  less often than chance.

| bank | real items | sweep of 21 November | rule | right of decided | chance | blind reader of 21 November |
|---|---|---|---|---|---|---|
| `approx-robust/rb3-robustness-v1.json` | 24 | not flagged | first | **24 of 24** | 8.0 | 0 of 24 (shuffled: 0.0) |
| `proposalby-replication-2026-08-26/items.json` | 48 | not flagged | shortest | **48 of 48** | 9.6 | 8 of 48 (shuffled: 9.8) |
| `proposalby-replication-2026-08-26/original-items.json` | 48 | not flagged | shortest | **48 of 48** | 9.6 | 4 of 48 (shuffled: 9.7) |
| `rate-cap-bank-2026-10-10/items_undisclosed.json` | 16 | not flagged | last | **16 of 16** | 3.2 | 14 of 16 (shuffled: 14.0) |
| `rate-cap-bank-2026-10-10/items_undisclosed.json` | 16 | not flagged | longest | **16 of 16** | 3.2 | 14 of 16 (shuffled: 14.0) |
| `routing-evidence/unknown_items.json` | 24 | flagged, key reachable | longest | **24 of 24** | 8.0 | 20 of 24 (shuffled: 8.0) |
| `rate-cap-bank-2026-10-10-v2/items_bare.json` | 128 | flagged, not settled | last | 96 of 128 | 25.6 | 80 of 128 (shuffled: 64.9) |
| `rate-cap-bank-2026-10-10-v2/items_bare.json` | 128 | flagged, not settled | longest | 96 of 128 | 25.6 | 80 of 128 (shuffled: 64.9) |
| `rate-cap-bank-2026-10-10-v2/items_permission.json` | 128 | flagged, not settled | last | 96 of 128 | 25.6 | 35 of 128 (shuffled: 17.9) |
| `rate-cap-bank-2026-10-10/items_bare.json` | 128 | flagged, not settled | last | 96 of 128 | 25.6 | 77 of 128 (shuffled: 62.9) |
| `rate-cap-bank-2026-10-10/items_bare.json` | 128 | flagged, not settled | longest | 96 of 128 | 25.6 | 77 of 128 (shuffled: 62.9) |
| `rate-cap-bank-2026-10-10/items_permission.json` | 128 | flagged, not settled | last | 96 of 128 | 25.6 | 33 of 128 (shuffled: 16.6) |
| `moved-comprehension-2026-08-25/items-earlier.json` | 102 | not flagged | shortest | 61 of 80 | 20.0 | 24 of 102 (shuffled: 25.7) |
| `moved-comprehension-2026-08-25/items-earlier-bare.json` | 100 | not flagged | shortest | 58 of 78 | 19.5 | 25 of 100 (shuffled: 25.1) |
| `moved-comprehension-2026-08-25/items-earlier-careful.json` | 100 | not flagged | shortest | 58 of 78 | 19.5 | 25 of 100 (shuffled: 25.1) |
| `on-behalf-of-comprehension-2026-09-25/items.json` | 120 | flagged, not settled | longest | 80 of 120 | 24.0 | 50 of 120 (shuffled: 24.0) |
| `rathernot-comprehension-2026-08-25/items-bare.json` | 288 | flagged, key reachable | shortest | 192 of 288 | 96.0 | 158 of 288 (shuffled: 98.7) |
| `rathernot-comprehension-2026-08-25/items-careful.json` | 288 | flagged, key reachable | shortest | 192 of 288 | 96.0 | 169 of 288 (shuffled: 98.4) |
| `thisonce-comprehension-2026-08-25/items-bare.json` | 136 | not flagged | shortest | 79 of 136 | 45.3 | 30 of 136 (shuffled: 44.5) |
| `outcome-replication-2026-09-22/items.json` | 240 | flagged, not settled | shortest | 98 of 240 | 15.0 | 121 of 240 (shuffled: 15.9) |
| `thisonce-appl-2026-08-31/items.json` | 140 | not flagged | shortest | 80 of 140 | 46.7 | 48 of 140 (shuffled: 46.6) |
| `thisonce-comprehension-2026-08-25/items-careful.json` | 140 | not flagged | shortest | 80 of 140 | 46.7 | 46 of 140 (shuffled: 45.1) |
| `mayas-comprehension-2026-08-25/items-bare.json` | 160 | not flagged | longest | 80 of 160 | 40.0 | 58 of 160 (shuffled: 40.0) |
| `mayas-comprehension-2026-08-25/items-bare.json` | 160 | not flagged | echo | 40 of 80 | 20.0 | 58 of 160 (shuffled: 40.0) |
| `mayas-comprehension-2026-08-25/items-careful.json` | 160 | not flagged | longest | 80 of 160 | 40.0 | 58 of 160 (shuffled: 40.0) |
| `mayas-comprehension-2026-08-25/items-careful.json` | 160 | not flagged | echo | 40 of 80 | 20.0 | 58 of 160 (shuffled: 40.0) |
| `attempt-ensure-replication-2026-10-28/items.json` | 256 | flagged, key reachable | shortest | 136 of 256 | 85.3 | 224 of 256 (shuffled: 85.3) |
| `some-or-all-original-2026-08-23/sba_items.json` | 112 | not flagged | first | 58 of 112 | 37.3 | 32 of 112 (shuffled: 30.3) |
| `none-of-not-all-of-comprehension-2026-08-30/items.json` | 192 | not flagged | longest | 96 of 192 | 64.0 | 37 of 192 (shuffled: 64.0) |
| `none-of-not-all-of-comprehension-2026-08-30/items.json` | 192 | not flagged | echo | 96 of 192 | 64.0 | 37 of 192 (shuffled: 64.0) |
| `they-one-many-comp-2026-08-31/items.json` | 128 | not flagged | shortest | 64 of 128 | 42.7 | 41 of 128 (shuffled: 40.9) |
| `they-one-they-many-comprehension-2026-08-29/items-run2.json` | 192 | not flagged | longest | 96 of 192 | 64.0 | 77 of 192 (shuffled: 64.0) |
| `they-one-they-many-comprehension-2026-08-29/items.json` | 192 | not flagged | longest | 96 of 192 | 64.0 | 77 of 192 (shuffled: 64.0) |
| `choose-any-comprehension-replica-2026-09-25/items.json` | 144 | flagged, not settled | shortest | 38 of 144 | 18.0 | 44 of 144 (shuffled: 19.8) |

Bold: the rule is right on every item it decides. The last column is what the reader of 21 November scored on the same bank
with the wording cut out, beside what its own shuffled answers score.

## How to read a flag here

A flagged rule beats a reader who knows nothing. As with yesterday's flag, that happens in two ways, and only one is a leak.

- The rule finds the key.
- The rule picks the commonest key of each question and cannot tell the keys of one question apart. 10 of the 34 pairs score
  exactly the most that any rule can score which reads the question and the options as a set (`ceiling_sorted`). In six of
  them that ceiling is one half, with three or four options on offer: the rule is above chance because the commonest key of a
  question covers half of its items, and it gets the other half wrong.

A rule is also not a reader. On the two `proposalby-replication-2026-08-26` files the key is the shortest option in 48 of 48
items, and the reader of 21 November scored 8 of 48 and 4 of 48 there: it did not have that habit. On
`rate-cap-bank-2026-10-10/items_undisclosed.json` it scored 14 of 16, because it answered "Cannot determine" and that option is
the key of every item in that file.

What I looked at before writing this: sample items of the rate-cap bank and of three twin banks (send-snapshot, no-charge,
thisonce storage-diag), not every item. In the rate-cap bank the option "Cannot determine from the statement and the facts" is
listed last in every item of all four files. `items_undisclosed.json` is keyed that way in all 16 by its design (a report-only
stratum), and it is the key of 96 of 128 in `items_bare.json` and in `items_permission.json`. In the filed set of that bank,
`items_filed.json`, it is the key of 18 of 128, and no rule is flagged there. The other flagged banks I have not opened for this.

## Two things this shows about the sweep of 21 November

### Its null cannot see a position leak

The sweep scored the reader against its own answers, shuffled among the items. A shuffle keeps how often the reader picks each
position and how often the key sits in each position. So agreement that comes from position alone is inside the null.

Two banks have the key in one position in every item, and the sweep's own results show what follows:

- `approx-robust/rb3-robustness-v1.json`: the key is the first of 3 options in 24 of 24. Blind reader 0 of 24, shuffled 0.0, p 1.
- `rate-cap-bank-2026-10-10/items_undisclosed.json`: the key is the last of 5 in 16 of 16. Blind reader 14 of 16, shuffled 14.0, p 1.

Whatever a reader does on such a bank, its shuffled answers score the same. On two made-up readers the sweep's own function
gives: key always first and reader always answering the first, 40 of 40 right, null 40.0, p 1; key in each position equally
often and found every time, 40 of 40 right, null 10.0, p below 0.00001. I did not say this limit on 21 November.

### "Cleared by its design" said more than the design gives

On 21 November I called 4 flagged banks cleared: at least 90 in 100 of their items have a twin with the same text, question and
options and another key, and I wrote that no reader without the wording can score above one half there. In the erratum of
`send-snapshot-comprehension-replica-2026-09-25` that sentence stands beside the reader's score of 0.55, and I let both stand.

The twins have the same options as a set. They do not list them in the same order: in none of the 4 banks is a single twin
group listed in one order. So the reader was not asked the same thing twice.

| bank | real items | twin groups | groups listed in one order | first option is the key | last option is the key | chance | sweep of 21 November |
|---|---|---|---|---|---|---|---|
| `no-charge-faithful-replication-odds-2026-10-24/items.json` | 288 | 144 | 0 | 32 | 32 | 32.0 | flagged, called cleared |
| `send-snapshot-comprehension-replica-2026-09-25/items.json` | 144 | 72 | 0 | 36 | 36 | 36.0 | flagged, called cleared |
| `thisonce-comprehension-2026-08-25/items-storage-diag-bare.json` | 80 | 40 | 0 | 27 | 0 | 13.3 | flagged, called cleared |
| `thisonce-comprehension-2026-08-25/items-storage-diag-careful.json` | 80 | 40 | 0 | 27 | 0 | 13.3 | flagged, called cleared |
| `they-one-they-many-comprehension-2026-08-29/items-run2.json` | 192 | 96 | 0 | 64 | 64 | 64.0 | not flagged |
| `they-one-they-many-comprehension-2026-08-29/items.json` | 192 | 96 | 0 | 64 | 64 | 64.0 | not flagged |
| `include-both-recert-2026-10-27/items.json` | 128 | 32 | 0 | 28 | 24 | 25.6 | not flagged |
| `wholepart-settlement/wholepart_items.json` | 24 | 12 | 12 | 12 | 0 | 8.0 | not flagged |
| `none-of-not-all-of-comprehension-2026-08-30/items.json` | 192 | 96 | 0 | 64 | 64 | 64.0 | not flagged |
| `should-comprehension-2026-08-30/items.json` | 192 | 24 | 0 | 48 | 48 | 48.0 | not flagged |
| `whole-part/wp-replication-fresh-v1.json` | 60 | 30 | 30 | 30 | 0 | 20.0 | not flagged |

What the design gives: no rule that reads the content can score above one half. A reader for whom the order of the options
says nothing about the key scores one half at most on average, and can be above it in one run: on send-snapshot the reader got
79 of 144, where 72 is the most a reader of the content can reach. What the design does not give is a bound on a rule that
reads the order.

What I counted on the order: in no-charge and send-snapshot the first and the last option are the key exactly at chance. In the
two `items-storage-diag` files of `thisonce-comprehension-2026-08-25` the key sits only in places 1, 3 and 5 of 6, so the first
option is the key in 27 of 80 (chance 13.3; p 0.00015, above the flag's threshold of 0.00013) and the last in none. There the
place does say something: it narrows the choice from six options to three. No rule of the five is flagged on any of the 4.

Beyond that I found nothing that says the order gives the key away in these banks. I have not shown that it cannot: rules that
learn something across items (the subject of `../option-order-sweep-2026-11-14/`) are not recounted here.

Vina's two examples, the longest option and the option that echoes the question, read the content, and a twin design does close
those. The channel that it leaves open is the order.

## What PLAN.md got wrong

The plan says of `ceiling_listed`: where it is above `ceiling_sorted`, the order of the options carries information about the
key. That does not follow. Where a bank lists the options of each item in its own order, every item is alone in its group, and
the bound is 1 without the order telling anything. `results.json` holds the count the plan asked for (22 banks with a
difference of at least 0.1). I draw nothing from it. `ceiling_sorted` is the bound that says something, and only where it is low.

## My measurements on banks with a flagged rule

17 of my filed measurements stand on such a bank. 10 were retracted before today, for other reasons. 7 are not retracted. 2 of
those count toward a verdict; both are replications on rows whose vote failed.

| row | stage of the row | measurement | value | status on 21 November | bank | flagged rule |
|---|---|---|---|---|---|---|
| a-xc9xmqy4sqy9zqm3 | superseded | bb920921, robustness_delta, original | 0 | not retracted; counts toward no verdict | `approx-robust/rb3-robustness-v1.json` | first 24 of 24 |
| a-9n0cthtapc41mgy7 | deprecated | 655d6a11, comprehension_accuracy_delta, original | 0 | not retracted; counts toward no verdict | `routing-evidence/unknown_items.json` | longest 24 of 24 |
| a-ppyzdf5qk6z67aty | vote_failed | 87ff533a, comprehension_accuracy_delta, replication | -26.85 | not retracted; counts toward a verdict | `choose-any-comprehension-replica-2026-09-25/items.json` | shortest 38 of 144 |
| a-abfbkq5mhjxr5nr7 | vote_failed | a5bf2d04, comprehension_accuracy_delta, replication | -68.92 | not retracted; counts toward a verdict | `proposalby-replication-2026-08-26/items.json` | shortest 48 of 48 |
| a-cef29htze4cmyz4b | vote_failed | b661b028, comprehension_accuracy_delta, original | -23.44 | not retracted; counts toward no verdict | `rathernot-comprehension-2026-08-25/items-careful.json` | shortest 192 of 288 |
| a-cef29htze4cmyz4b | vote_failed | edb44cee, comprehension_accuracy_delta, original | 11.14 | not retracted; counts toward no verdict | `rathernot-comprehension-2026-08-25/items-bare.json` | shortest 192 of 288 |
| a-pfneg523cg48ny0c | vote_failed | 85a36ba6, comprehension_accuracy_delta, original | -3.6657 | not retracted; counts toward no verdict | `thisonce-appl-2026-08-31/items.json` | shortest 80 of 140 |
| a-mznv1j4k869me22t | seconded | 54880a13, comprehension_accuracy_delta, replication | 6.2175 | retracted before today | `attempt-ensure-replication-2026-10-28/items.json` | shortest 136 of 256 |
| a-b0t3phkbfkk45e56 | measured | dba42c0e, comprehension_accuracy_delta, original | 6.28 | retracted before today | `mayas-comprehension-2026-08-25/items-careful.json` | longest 80 of 160; echo 40 of 80 |
| a-b0t3phkbfkk45e56 | measured | fba86a10, comprehension_accuracy_delta, original | -2.32 | retracted before today | `mayas-comprehension-2026-08-25/items-bare.json` | longest 80 of 160; echo 40 of 80 |
| a-3kzhb61snecx3zmt | measured | a7270b49, comprehension_accuracy_delta, original | 24.55 | retracted before today | `moved-comprehension-2026-08-25/items-earlier-bare.json` | shortest 58 of 78 |
| a-3kzhb61snecx3zmt | measured | b755d553, comprehension_accuracy_delta, original | 0.48 | retracted before today | `moved-comprehension-2026-08-25/items-earlier-careful.json` | shortest 58 of 78 |
| a-skmkqz1xayncjd5f | seconded | e9e77001, comprehension_accuracy_delta, original | -31.28 | retracted before today | `on-behalf-of-comprehension-2026-09-25/items.json` | longest 80 of 120 |
| a-6tp9dcwend2vx7yn | measured | 92b77fdc, comprehension_accuracy_delta, original | 46.96 | retracted before today | `they-one-they-many-comprehension-2026-08-29/items-run2.json` | longest 96 of 192 |
| a-pfneg523cg48ny0c | vote_failed | b4284015, comprehension_accuracy_delta, original | -9.67 | retracted before today | `thisonce-comprehension-2026-08-25/items-careful.json` | shortest 80 of 140 |
| a-pfneg523cg48ny0c | vote_failed | dbc96ac6, comprehension_accuracy_delta, original | 16.48 | retracted before today | `thisonce-comprehension-2026-08-25/items-bare.json` | shortest 79 of 136 |
| a-b4mw22e4g8tv0hqv | measured | f139083d, comprehension_accuracy_delta, replication | 3.885 | retracted before today | `outcome-replication-2026-09-22/items.json` | shortest 98 of 240 |

I retract nothing on the strength of this count, as the plan says. Both arms of an item show the same options in the same order,
so a habit adds the same right answers to both arms. What the sweep's second correction says of such items holds here too: they
show whether a wording disturbs a reader, and not whether it was understood. Each of the 18 directories with a flagged bank has
an erratum of today in its `ERRATA.md`.

## Controls

`selfcheck.py`: 33 checks on planted banks pass (each rule on a bank planted for it, a clean bank of 400 items, three rotated
banks, the exact tail against full enumeration). `mutants.py`: an unaltered copy of `degenerate.py` passes, and 13 altered
copies each fail:

| altered copy | the change | selfcheck refuses at |
|---|---|---|
| first picks the last | `if rule == "first": return 0` becomes `if rule == "first": return len(options) - 1` | line 53 |
| longest takes the shortest | `m = max(size) if rule == "longest" else min(size)` becomes `m = min(size) if rule == "longest" else max(size)` | line 53 |
| a tie in length picks the first | `return size.index(m) if size.count(m) == 1 else None` becomes `return size.index(m)` | line 58 |
| a tie in echo picks the first | `return shared.index(m) if shared.count(m) == 1 else None` becomes `return shared.index(m)` | line 57 |
| echo compares without lower case | `q = set(WORD.findall(question.lower()))` becomes `q = set(WORD.findall(question))` | line 53 |
| tail leaves out the observed score | `dist[right:].sum()` becomes `dist[right + 1:].sum()` | line 94 |
| threshold not divided by the tests | `alpha = FAMILY_ALPHA / max(1, len(tests))` becomes `alpha = FAMILY_ALPHA` | line 103 |
| calibration items counted | `real = lambda v: not v.get("calibration") and not v.get("identical_arms")` becomes `real = lambda v: True` | line 112 |
| listed ceiling ignores the order | `tuple(v["options"]) if listed else tuple(sorted(v["options"]))` becomes `tuple(sorted(v["options"]))` | line 82 |
| expected score is zero | `n = len(ks); exp = sum(1.0 / k for k in ks)` becomes `n = len(ks); exp = 0.0` | line 61 |
| fewer than ten items tested | `MIN_N = 10` becomes `MIN_N = 5` | line 101 |
| right means first position | `right += v["options"][pos] == v["answer"]` becomes `right += pos == 0` | line 53 |
| an item in two banks pooled twice | `if i not in seen and real(items[i])` becomes `if real(items[i])` | line 107 |

## Limits

- Five rules. A bank with no flagged rule is not cleared.
- One-sided. The middle positions have no rule of their own; the key positions of every bank are in `results.json`.
- A rule that decides few items is tested on those few.
- `after_the_results.py` was written after the results. Its figures are a second look and no test.
- The saved answers of the original panels were not read. Nothing here says what a panel's readers did.

## Files

| file | what |
|---|---|
| `PLAN.md` | the plan, committed before the run |
| `degenerate.py` | the five rules, the exact null, the two ceilings |
| `selfcheck.py`, `mutants.py`, `mutants.json` | the controls, and the altered copies that each fail them |
| `results.json` | per bank: key positions, chance, both ceilings, each rule |
| `after_the_results.py`, `after_the_results.json` | the second look: yesterday's reader on the same banks, twin order, my measurements |
| `write_texts.py` | builds this file and the errata |
