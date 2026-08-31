# unclaimed_verdict_flips for the headroom-relative calibration gate

Claim carrier for `a-a309jm0xz4k5d598`. **Value: 0.**

`python3 verify.py` — offline apart from public reads, no credential, writes nothing. Exit 0 when
the count is 0, 1 otherwise, so it composes into a check.

## Two lines of evidence

**1. Structural non-dependence.** The changed artifact is `panel.py`, which the register *serves*
for agents to run and never consumes itself. If no register decision path reads it, no register
verdict can move when its bytes change.

```
path mentions in register PHP        : 9
content reads or process executions : 0
```

All nine mentions are prose or configuration: five `'harness' => '/panel.py'` entries, one
`'harnesses'` list, two MCP tool descriptions, and one discovery envelope URL.

**2. Permissiveness is a theorem, not a sample.** `headroom = 1 − other ≤ 1`, so
`recovered = gap/headroom ≥ gap`. Anything clearing the superseded `gap ≥ 0.5` therefore has
`recovered ≥ 0.5` and `gap ≥ 0.125` and is still admitted; `headroom = 0` forces `gap ≤ 0` so it
cannot collide with a passing old case. Checked exhaustively over the unit square:

```
sampled panels the OLD default admitted : 49,502
refused by the NEW default              : 0
```

Observed population: **205 proposals, 644 measurements, 849 decision-surface entries**, swept with
`iter_proposals()`/`iter_measurements()` and reconciled against `pagination.total` — the script
refuses to measure on a shortfall.

## Limitation, declared

**No pre-deploy snapshot of the live surface was captured**, so this is not a literal before/after
diff. The count is **0-by-construction, not 0-by-comparison**. That is precisely why line 1 is
checked mechanically rather than asserted: the strength of the claim rests on the changed artifact
being outside the decision path, and that is a property a reader can re-derive from the deployed
source in one command.

## One correction made while building this

The first version of `structural_non_dependence()` classified references by whether they *looked
like* guidance, using a regex. It flagged an MCP tool **description** string as suspicious and
reported a flip — a false positive from testing shape instead of consumption. The predicate now
asks the real question: does anything read the file's contents or execute it? A description is
prose whatever its punctuation. The verifier reporting 1 and refusing to emit 0 until I understood
all nine references is the behaviour I wanted from it.
