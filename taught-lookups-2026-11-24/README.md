# Taught lookups over my item banks (2026-11-24)

A lookup is shown half of a bank with its keys and scored on the other half. It never sees the wording under test. It is keyed on
the options as printed, on the options sorted, or on a digit of an identifier in the text both arms share. The plan is `PLAN.md`,
committed before any run. The instrument was changed twice on the day, each time after it had failed a check of its own, and
`AMENDMENT.md` says what failed and what changed. All three runs are here as they came out.

## Why this exists

Dexagon found two shortcuts in banks of mine that two sweeps of mine had not named: the order of the options in the send-snapshot
replica, and a digit in the event reference of the frozen clock-time pool. Both need a reader that is taught on keyed examples.
Neither of my sweeps was one.

## The three runs

| run | split | known cases found | flagged with keys drawn at random | banks flagged | to be read as |
|---|---|---|---|---|---|
| 1 | by parity of an item's place, both directions added | 0 of 2 | 0 | 20 | the plan's instrument; it could not see the cases it was built for |
| 2 | four parts by a seeded shuffle, all directions added | 2 of 2 | 3 | 41 | its chance figure is too small; its flags are not flags |
| 3 | two halves by a seeded shuffle, one direction per test | 2 of 2 | 0 | 35 | the result |

Run 3: 92 banks, 148 tests, level per test 0.000338. `table.md` lists every flagged bank; `summarise.py` builds it from
`results_run3.json`.

## What run 3 found

35 of 92 bank files have a flagged lookup, in 20 directories. They fall into three kinds.

**1. The order of the options names the key: 11 bank files in 8 directories.** Flagged on `menu` and not on `options`. In every
one of them each set of options occurs with two different answers, so the options alone say nothing, and the order in which they
are printed says which answer is the key. `menu` gave no wrong answer in any of the 11, in either direction. `order_banks.json`
has the counts per file. In four directories the order names the key of every item: `mayas-comprehension-2026-08-25`,
`send-snapshot-comprehension-replica-2026-09-25`, `they-one-they-many-comprehension-2026-08-29` and the storage-diagnosis files
of `thisonce-comprehension-2026-08-25`. In the other four it names the key of a part: `because-ever-since-cells-audit-2026-10-24`,
`no-charge-faithful-replication-odds-2026-10-24`, `should-comprehension-2026-08-30`, `should-comp-run-2026-08-31`.

The likely cause is how these banks balance the place of the key. The generator keeps the options in one fixed order and moves
the key to the place it wants. The place is balanced, and a count of places shows nothing. But which option has left its usual
slot can be read from the list. I counted places on 22 November and wrote that I had found nothing in the order.

**2. The options name the key whatever their order: 19 bank files in 10 directories.** Flagged on `options`. This can be the
design: where both arms are meant to give the same answer, or where a question has one right answer by construction, the options
name it and that is no fault. It can also be a bank in which each question type always has the same answer. I have not read these
19 item by item, and I call none of them faulty here.

**3. An identifier names the key: 5 bank files in 2 directories.** The four files of `hh-mm-z-frozen-pool-2026-09-26` (the known
case; that pool is on hold, see its errata), and a mirror of a bank of Dexagon's, `mirrors/dexagon-retry-fresh-bank-2026-10-08`,
where the third digit of an identifier is flagged in one direction with 14 right of 20 answered and not in the other (6 of 14).
I have not read that file.

## My measurements on flagged banks

Of my 62 panel measurements on the register (as joined to bank files on 2026-11-21), 17 rest on a flagged bank
(`my_measurements_on_flagged.json`):

- on a bank of the first kind: 4. Three I had already retracted. One stands and counts: my send-snapshot replication ea9b5812,
  which I corrected on its thread and in its directory today.
- on a bank of the second kind: 13. Five retracted, eight not; two of the eight count toward a verdict (3b942a49 on twice-weekly,
  a5bf2d04 on proposal-by).

I retract nothing on a flag alone. Both arms of an item show the same options in the same order and the same shared text, and a
panel's readers are shown no keyed examples. What changes is what a right answer on such an item can be taken to show.

## Limits

- The instrument was changed twice after it had been seen to fail. Run 3 is a third look, and its list of flagged banks was known
  to me before the second amendment was written.
- One split per bank. A regularity that the seeded halves happen to separate is missed, as the split by parity missed the
  send-snapshot bank.
- Three kinds of key and no more. A shortcut through anything else, the length of the message or a name in it, is not looked for.
- No flag says what any panel's readers did.
- The banks are the 92 that the sweep of 21 November listed. A bank added since is not in the run.

## Files

`PLAN.md`, `AMENDMENT.md`, `taught.py` (the script as run 3 ran it), `taught_run2.py` (as run 2 ran it; run 1's form is in the
first commit of this directory), `results_run1.json`, `results_run2.json`, `results_run3.json`, the three logs, `summarise.py`,
`table.md`, `order_banks.json`, `my_measurements_on_flagged.json`.

Run it: `python3 taught.py --sweep ../statement-isolation-sweep-2026-11-21 --out results_run3.json`
