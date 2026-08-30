# reasoning_effort on a remote Nous Portal reader (2026-08-30)

**Leave reasoning enabled.** Suppressing it with `reasoning_effort: "none"` roughly halves-to-thirds
the measured effect on identical frozen items.

Model `deepseek/deepseek-v4-flash`, `temperature: 0`, `max_tokens: 1024`, 10 items drawn with seed
11 from the frozen `none-of / not-all-of` set (`bce44c49…`), both arms, 40 planned cells.

```
                              english          ainglish        delta over LIVE cells
reasoning_effort ABSENT     2/9  (22.2%)     10/10 (100.0%)         +77.8pp
reasoning_effort "none"     0/10 ( 0.0%)      3/10 ( 30.0%)         +30.0pp
```

One english cell was lost to an `HTTPError` in the reasoning-on condition; `live_n` is recorded per
arm and the delta is taken over live cells only. Every cell is in `cells.json` with its outcome,
answer, reasoning-token count and cost. Re-derive with `python3 run.py`.

## Correction to the first pass

An earlier pass of this experiment published **+60.0pp**. That figure was wrong. It divided **both**
arms by the *planned* n of 10 while a transport fault had killed one ainglish cell, so the surviving
9 correct-or-wrong answers were scored against a denominator of 10. Recomputed over live cells the
first pass was **+67.8pp** (english 1/10, ainglish 7/9).

A censored denominator is precisely the failure the panel harness's yield guard exists to prevent,
and I reproduced it by hand in a script that did not use the harness. It also failed quietly in the
*conservative* direction — the published number was too small, so nothing looked wrong. Caught by
@dexagon in review of ainglish#119, not by me.

Both passes agree on the conclusion and disagree on the magnitude (+67.8pp and +77.8pp), which is
what a 10-item pilot should be expected to do. The `"none"` condition returned +30.0pp in both,
being deterministic at `temperature: 0`. Treat the direction as established and the point estimate
as a pilot, not a measurement.
