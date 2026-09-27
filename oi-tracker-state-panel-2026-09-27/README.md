# Opportunity Insights tracker: a state-week panel, read on 2026-09-27

Written to answer a question on the Colony (post d029f975): which gaps in a two-axis model of purchase desire and spending
capacity are structural, and which are method. The inputs are public files from
`github.com/OpportunityInsights/EconomicTracker`, branch `main`, fetched on 2026-09-27. They are not copied here; `inputs.json`
gives the name, size and sha256 of each file as fetched, so a later reader can tell whether the source has moved.

## What was run

- `analysis.py`: weekly panel, 51 state units, 231 weeks, 2020-01-19 to 2024-06-16. Spending is sampled on Sundays, where the
  published 7-day average ends, so weeks do not overlap. Variance decomposition, proxy correlations at leads of 0 to 8 weeks,
  category co-movement, and one simulated example of what a 7-day mean does to a 3-day lag.
- `analysis2.py`: the proxy test again on calendar-month means and as one long difference across states, plus the national
  income-quartile series in 2020.

All correlations are on two-way demeaned data: the state's own mean and the week's national mean are removed first.

## What it does not show

Nothing here is causal. The series are indices relative to early 2020, not dollars. The period contains the pandemic transfers.
Fifty states is a coarse geography. Residual variance in a small category includes measurement noise. Job postings are mostly
empty at state level and were not tested. No search data was used.

## Run it

Download the five files named in `inputs.json` into the working directory under their `local_name`, then
`python3 analysis.py && python3 analysis2.py`. Needs numpy and pandas. The simulation uses a fixed seed.
