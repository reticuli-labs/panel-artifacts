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
arm and the delta is taken over live cells only.

## Re-derive without spending anything

```bash
python3 run.py --rederive      # offline: zero network, no credential, writes nothing
```

Reads the retained `cells.json` (sha256 `4a178f71a59cd20588b6842ef4e1669d92ce2f6b6d4c7ab315956a4ba6472a28`,
40 cells, each with outcome, answer, reasoning-token count and cost) and recomputes every figure
above. Verified with `NOUS_API_KEY` unset.

`run.py --run` is the paid path and writes a **new timestamped** cells file rather than the pinned
one. The script now refuses to do anything without an explicit flag, because the first version
re-ran on every invocation and overwrote `cells.json` — so "reproducing" the published result
destroyed the evidence it was reproducing, and cost money to do it. @dexagon caught that in review
of ainglish#119.

Immutable link to the exact bytes these figures come from:
`https://github.com/reticuli-labs/panel-artifacts/blob/9694ab0/nous-reasoning-effort-2026-08-30/cells.json`

## Correction to the first pass

An earlier pass of this experiment published **+60.0pp**. That figure was wrong. It divided **both**
arms by the *planned* n of 10 while a transport fault had killed one ainglish cell, so the surviving
9 correct-or-wrong answers were scored against a denominator of 10. Recomputed over live cells the
first pass was **+67.8pp** (english 1/10, ainglish 7/9).

A censored denominator is precisely the failure the panel harness's yield guard exists to prevent,
and I reproduced it by hand in a script that did not use the harness. It also failed quietly in the
*conservative* direction — the published number was too small, so nothing looked wrong. Caught by
@dexagon in review of ainglish#119, not by me.

Both passes agree on the sign and disagree on the magnitude (+67.8pp and +77.8pp), which is what a
10-item pilot should be expected to do. The `"none"` condition returned +30.0pp in both, being
deterministic at `temperature: 0`.

**What this does and does not support.** Two runs of 10 items on **one model** is a pilot. It
supports "suppressing reasoning on `deepseek-v4-flash` made this instrument worse on this item set",
and it is the basis on which I would set a default. It does **not** establish a general property of
reasoning suppression, does not generalise to other models, and the point estimates carry no
interval worth quoting. Earlier wording here said the direction was "established"; that overstated
what 20 live cells per condition can carry.
