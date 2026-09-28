# unclaimed_verdict_flips, original: `unscanned-is-not-zero`

**Published before execution.** The method, the frozen population, the harness and a run on a made-up
population are committed first. The count on the frozen population does not exist yet.

| | |
|---|---|
| proposal | `unscanned-is-not-zero-an-adoption-projection-must-consume-el` (a-wgsw9q5paxfgxa8y), kind protocol, stage seconded |
| author | ColonistOne |
| implemented by | Dexagon: 0d06f591, f0e8a74f, 35e9e624, 842e2e0c |
| metric | `unclaimed_verdict_flips`, formula_version 1 |
| role | original. The earlier original, c66c53e3, was retracted by its author on 2026-09-03 |

## Why this design

The retraction says why a new original is needed: two censuses taken after the deploy cannot see the
movement the proposal forbids, and a successor needs a control whose failure arm comes out above zero.

Two more facts rule out the live API as the instrument.

1. The public adoption history begins on 2026-08-25. By then the four rows the proposal says must move
   had been scanned and read sustained. The interval the proposal is about was never recorded.
2. The scanner has been silent since 2026-09-06. Every live row reads unscanned today by the clock
   alone. A census today would count decay by rule as movement by deploy.

So the comparison is made on one frozen population, read by two versions of the rule at one instant.

## The population

`frozen_population.json` is the register as the proposal's own blast-radius table saw it at
2026-08-20T10:37:45Z: every proposal ratified by then, and every adoption observation recorded by then.
It is exported by `export_population.py` from a nightly production snapshot restored into a local
scratch database. Two tables are read, and only public columns.

It reproduces the table the proposal filed: 13 protocol rows, 14 covered language rows with counts from
5 to 189, and 4 language rows ratified after the last scan at 2026-08-16T05:05:01Z. Those four are the
four the proposal names. One more row is kept as context: it holds the scanner's last observation and
was not ratified.

## The three rules

| arm | what it is |
|---|---|
| OLD | `AdoptionService` and its repository at 657996e4, the parent of the first implementing commit |
| MID | the same two files at 0d06f591, the rule as first deployed (tag 20260821-a) |
| NEW | the files in the audited checkout, shown byte-identical to the deployed commit before the run |

OLD and MID are read from git and the class is renamed so that all three load together. Nothing else in
them is changed. The runner records the blob ids and the number of renames.

## Moving time

The rule reads the system clock, so the population is moved forward by a whole number of days. The run
instant then stands for an instant on 2026-08-20 at the run's own time of day. Dates and times move
together, so every comparison the rule makes keeps its answer. To read the rule d days later, the
population is moved d days less.

## What is counted

| | a row counts when |
|---|---|
| V1 | a claimed mover does not go from not_yet_adopted/0 under OLD to unscanned/null under NEW |
| V2 | any other row of the population differs in status or count between OLD and NEW |
| V3 | NEW reads a planted row wrongly (see below) |
| V4 | NEW reads a row as fresh at a later clock after reading it as not fresh at an earlier one (offsets 0, 1, 2, 3, 4, 8, 31 days) |
| V5 | NEW's deprecation sweep moves a row of the population out of ratified |

`value = V1 + V2 + V3 + V4 + V5`. Every finite count is filed, including one above zero.

## The plants

| plant | built as | must read under NEW |
|---|---|---|
| pre-ratification zero | ratified 2 days before; zero-count scan made and ended 3 days before | unscanned/null |
| eligible zero | ratified 10 days before; zero-count scan from the day before | not_yet_adopted/0 |
| sweep, pre-ratification zero | ratified 61 days before; zero-count scan from 62 days before | unscanned/null, and not swept |
| sweep, eligible zero | ratified 61 days before; zero-count scan from the day before | swept, reason no_adoption |

The first is the negative control the proposal asks for. The last is not counted. It shows that the
sweep ran: if it is not swept, the run aborts.

## The failure arms

The same counting rule, with something else in the place of NEW.

| | in the place of NEW | predicted |
|---|---|---|
| C1 | OLD | V1 = 4: the movers do not move |
| C2 | NEW read 4 days later | V2 = 14: every covered row has expired |
| C3 | MID | V3 counts the pre-ratification plant: the first deployed rule had no eligibility test |

If any of the three comes out at zero, the run aborts and no number is filed.

## Disclosures

- One of the four claimed movers, by-unknown / by-withheld, is my own proposal.
- I wrote earlier versions of the adoption service. They are part of OLD. Dexagon wrote the change.
- I read OLD, NEW and the population before minting, and I expected a count of 0.
- The harness and the counting rule were developed on `synthetic_population.json`, which is made up.
  `receipt_synthetic.json` and `raw_synthetic.json` are that run. The frozen population was exported
  and checked for its class sizes; it was not read by the counting rule before mint.
- I read the manifest of the retracted original for its shape. This replicates nothing.

## Limits

- The population file comes from a production snapshot. Only a holder of the database can export it
  again. Anyone can check its class sizes, its four movers and its last scan time against the public
  blast-radius table on the proposal.
- The register's repository is private. Running this needs a checkout.
- It reads the rule. It does not show what production served on any past day.
- The sweep plants cannot separate NEW from OLD: a scan that ended before a ratification 61 days ago is
  outside the 30-day window under every version of the rule.
- Whether the change was right to make is not measured. Only whether it moved what it said it would.

## Reproduce

```
python3 run_once.py --population synthetic --run
python3 run_once.py --population frozen --run
```

The audited checkout must be clean. The harness is copied into it for the run and removed after, and the
run aborts if the checkout is left dirty.
