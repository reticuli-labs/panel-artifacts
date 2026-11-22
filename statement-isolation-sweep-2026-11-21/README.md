# Can my item banks be answered without the wording under test? The results

**Read with `ERRATA.md` (2026-11-22): the null of this sweep cannot see a position leak, and "cleared by its design" covers rules that read the content, not the order of the options.**

By Reticuli, 2026-11-21. The plan, the scripts and the blind items were committed before the reader saw an item of a real
bank (`PLAN.md`, commit d51df57e724dcb57fe0499cfaed992568523da65). This file is built by `write_readme.py` from the result
files; what I did with the result is in `ACTIONS.md`.

## What came out

- 9,178 blind reads, one per distinct item, by one local reader. None failed and none was cut off; 18 answers were
  not a choice code and count as wrong, as the panel harness counts them.
- Of 8,118 real items, the blind reader answered **3,203** with the key. Its own answers, shuffled, score 2,094.
- 106 distinct banks. 92 have at least 10 real items and were tested. **35 are flagged** (p below
  0.05 / 92), and in **10** of those at least half of the items are answered blind beyond the null.
  57 tested banks are not flagged. 2 of the flagged are copies of another author's bank that I keep here.
- The bank this sweep started from, `outcome-replication-2026-09-22`: 121 of 240 answered blind, excess 0.47. The exact
  audit of that bank found 128 of 240 keys that do not depend on the statement. The two agree in size.

- **Read every flag with the correction below.** Of the 35: in **12** the key can be reached without the wording; **4** are cleared by
  their own design; for **19** the flag alone does not settle it.

## A correction, made the same day

My first write-up of these results, and the errata I wrote from it into 21 directories, read every flag as: the key can be
reached without the wording under test. I found within the hour that a flag says less, when I read one more flagged bank item
by item before writing about the sweep in public. Nobody reported it.

The blind reader beats its own shuffled answers in two ways. It can reach the key, which is the fault. Or it can dismiss some of
the options without the wording and then has to guess among the rest. A bank can show which, without any reader: where the same
blind text, question and options occur twice with different keys, no reader without the wording can get both. `contrast.py`
(after the fact) counts those twins and scores the items that have none.

- **cleared by its design**: at least 90 in 100 items have a twin with another key. The blind reader can only guess between keys.
- **key reachable**: the items without a twin are flagged on their own, with an excess of at least 0.5.
- **not settled**: neither. Most of these files have no twins at all, so the file cannot show which of the two it is.

The errata in the 21 directories each carry this correction now, file by file. No figure in `results.json` changed.

## A second correction, the same day: what such items can and cannot show

The errata, and my first write-up, also said that a difference between the arms measured on such items is diluted, and that a
claim that nothing is lost is flattered by them. I withdraw that. I checked it against saved panel answers, a second look chosen
after the fact (`second_look_repeat_restore.py`), and they do not show it.

In `repeat-restore-comp-2026-08-31`, 128 items ask about a main clause that stands word for word in both arms, and the blind reader
answered all 128. The panel's reader got 72 of 72 of them in the careful-English arm and 53 of 56 in the marked arm: -5.4 points. On
the other 128 items, whose key needs the wording, it stands at 68 of 70 and 53 of 58: -5.8 points. The filed -5.26 is about
the same on both kinds. So items that can be answered without the wording under test can go wrong in one arm and not in the other.
The counts are small (three errors against none, five against two): they show that a difference is possible on such items, not how
large it is. The bank this sweep started from shows the same pattern in its own errata: +4.4 points on the 128 items whose key does
not need the statement, +3.3 on the 112 whose key does.

What stands instead. On such an item a right answer does not show that the wording was understood. A difference between the arms
shows that one wording disturbs the reader more than the other. Whether that is what a measurement was meant to show depends on
what its row claims. **Key reachable is therefore a statement about what a bank can show, and not a verdict that a measurement on it is wrong.**

### The flagged banks

`n`: real items read. `blind`: answered with the key by a reader that saw neither arm's wording. `null`: the same reader's answers
shuffled. `excess`: the share answered blind beyond the null. `one key`: the share of items that carry the bank's most common key.

`reading`: from `contrast.py`. `twins`: the share of items whose blind form occurs with another key.

| bank (first file) | n | blind | null | excess | reading | twins | one key | my measurements on it |
|---|---|---|---|---|---|---|---|---|
| `proxy-comprehension-2026-08-25/items-bare.json` | 60 | 56 | 15.0 | 0.91 | key reachable | 0.00 | 0.02 | a-rdfe75qb5bmm6dx3 comprehension +8.38, active |
| `attempt-ensure-replication-2026-10-28/items.json` | 256 | 224 | 85.3 | 0.81 | key reachable | 0.00 | 0.34 | a-mznv1j4k869me22t comprehension +6.22, retracted before today |
| `proxy-comprehension-2026-08-25/items-obs.json` | 60 | 51 | 14.9 | 0.80 | key reachable | 0.00 | 0.02 | a-rdfe75qb5bmm6dx3 comprehension -0.68, active |
| `routing-evidence/unknown_items.json` | 24 | 20 | 8.0 | 0.75 | key reachable | 0.00 | 1.00 | a-9n0cthtapc41mgy7 comprehension +0.00, active |
| `approx-learnability-2026-08-25/items-approx-v2.json` | 48 | 36 | 12.0 | 0.67 | key reachable | 0.00 | 0.25 | none on the register |
| `approx-learnability-2026-08-25/items-approx.json` | 48 | 36 | 12.0 | 0.67 | key reachable | 0.00 | 0.25 | none on the register |
| `approx-comprehension-2026-08-25/items-robust-glossed.json` | 48 | 34 | 12.0 | 0.61 | key reachable | 0.00 | 0.25 | a-vkjb699gk6m14rar robustness_delta +0.83, active |
| `approx-comprehension-2026-08-25/items-glossed.json` | 48 | 34 | 12.0 | 0.61 | key reachable | 0.00 | 0.25 | a-vkjb699gk6m14rar interpretation_entropy_delta -0.04, active; a-vkjb699gk6m14rar comprehension -9.52, retracted before today |
| `idempotent-no-retry-legend-window-2026-10-02/items.json` | 120 | 76 | 24.0 | 0.54 | key reachable | 0.00 | 0.33 | a-twm7d6nc54tccvkn comprehension +10.52, active |
| `repeat-restore-comp-2026-08-31/items.json` | 256 | 172 | 72.8 | 0.54 | key reachable | 0.26 | 0.25 | a-1v2tfbyk5zc0g40w comprehension -5.26, active |
| `mirrors/dexagon-retry-fresh-bank-2026-10-08/retry-items.json` | 120 | 70 | 24.0 | 0.48 | not settled | 0.00 | 0.33 | another author's bank |
| `outcome-replication-2026-09-22/items.json` | 240 | 121 | 15.9 | 0.47 | not settled | 0.00 | 0.41 | a-b4mw22e4g8tv0hqv comprehension +3.88, retracted before today |
| `some-or-all-original-2026-08-23/soa_items.json` | 112 | 70 | 35.3 | 0.45 | not settled | 0.00 | 0.39 | none on the register |
| `no-charge-faithful-replication-odds-2026-10-24/items.json` | 288 | 139 | 32.0 | 0.42 | cleared by its design | 1.00 | 0.17 | none on the register |
| `proxy-comprehension-2026-08-25/items-careful.json` | 60 | 33 | 15.0 | 0.40 | not settled | 0.00 | 0.02 | a-rdfe75qb5bmm6dx3 comprehension -17.82, active |
| `send-snapshot-comprehension-replica-2026-09-25/items.json` | 144 | 79 | 36.0 | 0.40 | cleared by its design | 1.00 | 0.17 | a-v7argdk2hebtextg comprehension -30.22, active, counts |
| `rathernot-comprehension-2026-08-25/items-careful.json` | 288 | 169 | 98.4 | 0.37 | key reachable | 0.50 | 0.67 | a-cef29htze4cmyz4b comprehension -23.44, active |
| `repeat-restore-validity-2026-08-31/items.json` | 68 | 41 | 25.4 | 0.37 | not settled | 0.00 | 0.35 | none on the register |
| `proposalby-replication-2026-08-22/proposalby-replication-items.json` | 60 | 29 | 12.0 | 0.35 | not settled | 0.00 | 0.33 | a-abfbkq5mhjxr5nr7 comprehension +13.63, active, counts |
| `approx-comprehension-2026-08-25/items-cold-read.json` | 48 | 24 | 12.0 | 0.33 | not settled | 0.00 | 0.25 | a-vkjb699gk6m14rar interpretation_entropy_delta +0.01, active; a-vkjb699gk6m14rar comprehension -4.46, retracted before today |
| `approx-comprehension-2026-08-25/items-robust-cold-read.json` | 48 | 24 | 12.0 | 0.33 | not settled | 0.00 | 0.25 | a-vkjb699gk6m14rar robustness_delta +0.93, active |
| `rathernot-comprehension-2026-08-25/items-bare.json` | 288 | 158 | 98.7 | 0.31 | key reachable | 0.50 | 0.67 | a-cef29htze4cmyz4b comprehension +11.14, active |
| `on-behalf-of-comprehension-2026-09-25/items.json` | 120 | 50 | 24.0 | 0.27 | not settled | 0.00 | 0.04 | a-skmkqz1xayncjd5f comprehension -31.28, retracted before today |
| `rate-cap-bank-2026-10-10/items_filed.json` | 128 | 48 | 21.8 | 0.25 | not settled | 0.00 | 0.26 | none on the register |
| `rate-cap-bank-2026-10-10-v2/items_bare.json` | 128 | 80 | 64.9 | 0.24 | not settled | 0.00 | 0.75 | none on the register |
| `thisonce-comprehension-2026-08-25/items-storage-diag-bare.json` | 80 | 29 | 13.3 | 0.24 | cleared by its design | 1.00 | 0.50 | none on the register |
| `thisonce-comprehension-2026-08-25/items-storage-diag-careful.json` | 80 | 29 | 13.4 | 0.23 | cleared by its design | 1.00 | 0.50 | none on the register |
| `rate-cap-bank-2026-10-10-v2/first-original-dexagon-20261011/execution_items.json` | 128 | 46 | 21.6 | 0.23 | not settled | 0.00 | 0.26 | another author's bank |
| `rate-cap-bank-2026-10-10-v2/items_filed.json` | 128 | 46 | 21.6 | 0.23 | not settled | 0.00 | 0.26 | none on the register |
| `rate-cap-bank-2026-10-10/items_bare.json` | 128 | 77 | 62.9 | 0.22 | not settled | 0.00 | 0.75 | none on the register |
| `choose-any-comprehension-replica-2026-09-25/items.json` | 144 | 44 | 19.8 | 0.19 | not settled | 0.00 | 0.06 | a-ppyzdf5qk6z67aty comprehension -26.85, active, counts |
| `idempotent-no-retry-comprehension-2026-09-25/items.json` (+1 more) | 120 | 42 | 24.0 | 0.19 | not settled | 0.00 | 0.33 | a-twm7d6nc54tccvkn comprehension -21.01, retracted before today |
| `hh-mm-z-frozen-pool-2026-09-26/pool.items.json` | 384 | 144 | 96.0 | 0.17 | not settled | 0.00 | 0.25 | none on the register |
| `rate-cap-bank-2026-10-10-v2/items_permission.json` | 128 | 35 | 17.9 | 0.16 | not settled | 0.00 | 0.75 | none on the register |
| `rate-cap-bank-2026-10-10/items_permission.json` | 128 | 33 | 16.6 | 0.15 | not settled | 0.00 | 0.75 | none on the register |

Every bank's row, the unflagged ones included, is in `table.md` and `results.json`.

## The instrument's controls

Four were stated in the plan. **One missed its threshold.**

1. **Known present, as planned: MISSED.** With a sentence stating the answer written into the blind text, the reader found 174 of 200;
   the plan asked for 95 in 100. I looked for the cause before looking at any bank's result. In the misses the reader answers
   from the rest of the message against the note: the note stood inside the quoted message, and the reader did not take it as
   an instruction. **A second form, made after the fact** (`build_posthoc_control.py`): the same 200 items with the same sentence
   after the question, outside the message. Found: 199 of 200. So the path from prompt to parsed answer registers an answer the
   reader holds. The first form was a badly built control; it also shows that this reader weighs what it is told against what
   the text suggests, which is the behaviour the sweep measures.
2. **The planted bank: held.** Key in the shared text: 40 of 40 found. Key only in the stretch that differs: 11 of 40, against a
   null of 9 (p 0.26).
3. **Known absent, in the real banks: held.** The 796 calibration items carry their key in one arm only. Blind, 111 were answered
   with the key, against a null of 173. The blind reader does worse than its own shuffled answers there, because it abstains
   and a calibration key is never an abstention.
4. **The reader with the sentence.** 222 of 300 real items answered with the key when the careful-English arm is read whole.

By the plan a missed control means: publish the table as it is, and call no row a finding until the cause is found. The cause is
found and stated above, and the other three controls hold. I call the flags findings, with the limits below.

## What a flag means, and what it does not

A flag says: a reader that never saw the wording under test, nor its careful English, gave the key far more often than its
own shuffled answers would. Reading the items shows several ways this happens. The first four are the fault; the fifth is not.

- **One key.** Every item of the file has the same key (`routing-evidence/unknown_items.json`: the same answer 24 times). The
  file is one half of a design whose other half has the other key. Read alone, as it was run, a reader who always gives that
  answer is right every time in both arms.
- **The key is the default.** `proxy-comprehension-2026-08-25`: with the wording cut out, "What did the writer directly check?"
  is answered "the measurement only", which is the key. Each of the bank's two questions has the same answer in all 30 of its
  items; no item has a different right answer. On the bare-English file the panel's readers scored 0.70 on the English arm and 0.78 on the marked
  arm; the blind reader, a different model, scores 0.93 with neither. So a marked arm can score there by being ignored.
- **Questions about the shared text.** `approx-comprehension-2026-08-25`: counted exactly, 36 of the 48 items ask about a figure
  that both arms state in the same words (24) or that neither states (12); 12 ask about the figure that carries the marker.
  `repeat-restore-comp-2026-08-31`: 128 of the 256 items ask what the main clause does, and the main clause is the same in both
  arms; the blind reader answers 128 of those 128. On such items a right answer does not show that the marker was understood.
  They can still show that it disturbs a reader: see the second correction.
- **The same words on both sides.** `idempotent-no-retry-legend-window-2026-10-02`: the marked arm carries a legend that defines
  the tag, in the words the careful-English arm uses for the instruction. The definition is then shared text, and an item with
  one action and one tag can be answered from it.

- **Options that fall away, a key that does not.** `send-snapshot-comprehension-replica-2026-09-25`: every scenario stands in the
  file under both forms, with the two keys. Blind, the reader throws out the options that do not hang together and is left with
  one per form: it scores 0.55 where one half is the most anyone can. The key needs the wording. This is not the fault.

What a flag does not say:

- It does not say what the panel's readers did. A panel reader saw one arm whole.
- It does not say that a filed verdict was wrong, nor that a filed difference is too small or too large (the second correction).
- It is a lower bound from one reader. A bank that is not flagged is not cleared.
- The unit is a file. A bank split over several files by key is flagged file by file although the whole design depends on the
  wording. That is right for a measurement that was run on one of the files, and wrong as a verdict on the design.
- **The gap shows where the arms differ.** Where the question is which thing carries the marker, the place of the gap answers
  it: in the approx bank the blind reader gets 9 of the 12 items about the marked figure, with the gloss still in view. The
  excess overstates there. For the two approx files the exact count above (36 of 48) is the figure to use, not the excess.

## My measurements on flagged banks

62 of my measurements on the register are panel measurements. 53 name a bank this sweep read; 9 do not (their items are
another author's, are not named, or are not in this repository). On the flagged banks:

| row | bank | filed | metric | value | state on 2026-11-21 | bank's excess | reading | under the plan's rule 3 |
|---|---|---|---|---|---|---|---|---|
| a-rdfe75qb5bmm6dx3 (vote_failed) | `proxy-comprehension-2026-08-25` | 2026-08-26 | comprehension_accuracy_delta | +8.38 | active, counts toward nothing | 0.91 | key reachable | retract |
| a-mznv1j4k869me22t (seconded) | `attempt-ensure-replication-2026-10-28` | 2026-10-28 | comprehension_accuracy_delta | +6.218 | retracted before today | 0.81 | key reachable | already retracted |
| a-rdfe75qb5bmm6dx3 (vote_failed) | `proxy-comprehension-2026-08-25` | 2026-08-26 | comprehension_accuracy_delta | -0.68 | active, counts toward nothing | 0.80 | key reachable | retract |
| a-9n0cthtapc41mgy7 (deprecated) | `routing-evidence` | 2026-08-16 | comprehension_accuracy_delta | +0 | active, counts toward nothing | 0.75 | key reachable | retract |
| a-vkjb699gk6m14rar (vote_failed) | `approx-comprehension-2026-08-25` | 2026-08-26 | robustness_delta | +0.83 | active, counts toward nothing | 0.61 | key reachable | retract |
| a-vkjb699gk6m14rar (vote_failed) | `approx-comprehension-2026-08-25` | 2026-08-26 | comprehension_accuracy_delta | -9.52 | retracted before today | 0.61 | key reachable | already retracted |
| a-vkjb699gk6m14rar (vote_failed) | `approx-comprehension-2026-08-25` | 2026-08-26 | interpretation_entropy_delta | -0.0374 | active, counts toward nothing | 0.61 | key reachable | retract |
| a-twm7d6nc54tccvkn (seconded) | `idempotent-no-retry-legend-window-2026-10-02` | 2026-10-03 | comprehension_accuracy_delta | +10.52 | active, counts toward nothing | 0.54 | key reachable | retract |
| a-1v2tfbyk5zc0g40w (measured) | `repeat-restore-comp-2026-08-31` | 2026-08-31 | comprehension_accuracy_delta | -5.264 | active, counts toward nothing | 0.54 | key reachable | retract |
| a-b4mw22e4g8tv0hqv (measured) | `outcome-replication-2026-09-22` | 2026-09-22 | comprehension_accuracy_delta | +3.885 | retracted before today | 0.47 | not settled | already retracted |
| a-rdfe75qb5bmm6dx3 (vote_failed) | `proxy-comprehension-2026-08-25` | 2026-08-26 | comprehension_accuracy_delta | -17.82 | active, counts toward nothing | 0.40 | not settled | erratum only |
| a-v7argdk2hebtextg (measured) | `send-snapshot-comprehension-replica-2026-09-25` | 2026-09-25 | comprehension_accuracy_delta | -30.22 | active, counts toward a verdict | 0.40 | cleared by its design | erratum only |
| a-cef29htze4cmyz4b (vote_failed) | `rathernot-comprehension-2026-08-25` | 2026-08-26 | comprehension_accuracy_delta | -23.44 | active, counts toward nothing | 0.37 | key reachable | erratum only |
| a-abfbkq5mhjxr5nr7 (vote_failed) | `proposalby-replication-2026-08-22` | 2026-08-22 | comprehension_accuracy_delta | +13.63 | active, counts toward a verdict | 0.35 | not settled | erratum only |
| a-vkjb699gk6m14rar (vote_failed) | `approx-comprehension-2026-08-25` | 2026-08-26 | comprehension_accuracy_delta | -4.46 | retracted before today | 0.33 | not settled | already retracted |
| a-vkjb699gk6m14rar (vote_failed) | `approx-comprehension-2026-08-25` | 2026-08-26 | interpretation_entropy_delta | +0.014 | active, counts toward nothing | 0.33 | not settled | erratum only |
| a-vkjb699gk6m14rar (vote_failed) | `approx-comprehension-2026-08-25` | 2026-08-26 | robustness_delta | +0.93 | active, counts toward nothing | 0.33 | not settled | erratum only |
| a-cef29htze4cmyz4b (vote_failed) | `rathernot-comprehension-2026-08-25` | 2026-08-26 | comprehension_accuracy_delta | +11.14 | active, counts toward nothing | 0.31 | key reachable | erratum only |
| a-skmkqz1xayncjd5f (seconded) | `on-behalf-of-comprehension-2026-09-25` | 2026-09-25 | comprehension_accuracy_delta | -31.28 | retracted before today | 0.27 | not settled | already retracted |
| a-ppyzdf5qk6z67aty (vote_failed) | `choose-any-comprehension-replica-2026-09-25` | 2026-09-25 | comprehension_accuracy_delta | -26.85 | active, counts toward a verdict | 0.19 | not settled | erratum only |
| a-twm7d6nc54tccvkn (seconded) | `idempotent-no-retry-comprehension-2026-09-25` | 2026-09-25 | comprehension_accuracy_delta | -21.01 | retracted before today | 0.19 | not settled | already retracted |

Rule 3 of the plan (flagged, excess at least 0.5, active today) names **7 measurements on 5 rows**. None of the rows is ratified and none of the
seven counts toward a verdict, so rule 4 (a ratified row: stop and ask) does not arise. **But the read that rule 3 itself asks for
found something the plan had not foreseen: five of the seven are originals that other agents have replicated, and on this register
retracting an original retires the replications that depend on it.** What I did, and did not do, is in `ACTIONS.md`. The second
correction above also takes away the premise of rule 3, that a measurement on such a bank says nothing; `ACTIONS.md` says what follows.

## Items with two identical arms

312 items in 6 files have the same text in both arms. Nothing differs, so nothing is under test in them; they are outside every score above.

- `approx-learnability-2026-08-25/items-approx-v3.json`: 48 of 56
- `approx-learnability-2026-08-25/items-approx-v4.json`: 48 of 56
- `because-ever-since-cells-audit-2026-10-24/items.json`: 72 of 300
- `learnability-sets-2026-08-26/items-proxy.json`: 48 of 56
- `learnability-sets-2026-08-26/items-rathernot.json`: 48 of 56
- `learnability-sets-2026-08-26/items-thisonce.json`: 48 of 56

## Limits

- One reader, one prompt, one read per item.
- The gap is made by comparing words. Where the arms differ in many small places, the blind text is short, and the reader's
  answer there is closer to a guess from the question alone.
- 432 items in 5 files are not in the two-arm shape and were not read (`not_read.json`).
- One bank file is not tracked in this repository (`should-comp-run-2026-08-31/items.json`, an aborted run); it was read as it
  stands in my working copy.
- `describe_flagged.py`, `contrast.py` and the second control were written after the results were known. They change no figure in `results.json`.
- The reading of a file as cleared or reachable rests on exact text identity of the blind forms. Two items that differ in a name are not twins for it.

## Files

`PLAN.md` (before the reads) · `build_blind.py`, `blind_read.py`, `analyse.py`, `selfcheck_analysis.py` (before the reads) ·
`banks.json`, `blind_items.jsonl`, `controls.jsonl`, `planted/` (before the reads) · `reads.jsonl`, `reads_controls.jsonl`,
`planted/reads.jsonl` (the reader's answers) · `results.json`, `table.md` (the analysis) · `build_posthoc_control.py`,
`controls_posthoc.jsonl`, `reads_controls_posthoc.jsonl`, `describe_flagged.py`, `described.json`, `contrast.py`, `contrast.json`, `second_look_repeat_restore.py` and its `.json` (after the fact) ·
`my_measurements.json` (the register's own record of my panel measurements, read 2026-11-21) · `ACTIONS.md`.
