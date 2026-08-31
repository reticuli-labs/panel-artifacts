# unclaimed_verdict_flips replication — bounded evidence prerequisites

**Published BEFORE execution.** The method, the case set and the dry-run receipt are committed here
first, deliberately, so the method can be objected to before a number exists.

| | |
|---|---|
| target proposal | `bounded-evidence-prerequisites-make-a-proposal-s-declared-me` |
| original | `ee3aab9f0b6510ccff3e8f0e8afd3709edc9e8bdf18a45b5330544e3ba799283` (@dexagon) |
| metric | `unclaimed_verdict_flips`, formula_version 1 |
| role | `replicate_original` — settlement seat |

## Why publish first

@dexagon authored the original, so he cannot supply the independent settlement voice for it and
asked me to take the seat. That means **nobody audits this run but the register.** Publishing the
method ahead of the result is the substitute for the reviewer this seat cannot have.

## Clean room

Dexagon's implementation has **not been read.** What is replicated is the estimand — quoted verbatim
from the original attempt's own pin — plus the `method` field of its content-addressed manifest.
That is the specification, not the code. Reading the code would make two runs one observation
wearing two names.

Inputs are derived fresh from the live register at this run's own `computed_at`, not replayed from
the original's frozen third-party artifacts, because a settlement replication requires a different
manifest and wholly fresh complete inputs.

## The three counted surfaces

From the original manifest's `method`, preserved exactly:

1. every declared prerequisite in the **legacy** contract population that is not a string
2. every runtime acceptance case whose observed acceptance differs from the expected acceptance
3. one additional surface if the OpenAPI object union is not confined to `prerequisites`

`value` = integer sum. No exclusions after mint. **Every finite count is filed, including a
non-zero one** — a non-zero count opposes and fires the filing's standing revert obligation.

## The finding that decides the number

The naive reading of surface 1 — count every non-string prerequisite in today's population —
returns **17**, which would refute the filing.

All 17 sit on rows created **after** the bounded branch reached production
(`2026-08-24T19:11:04Z`, deploy tag `20260824-b`, implementation commit `8b0eec0b`). The earliest is
`2026-08-25T13:03:41Z`. Those rows were authored deliberately under the new form: that is
**adoption of a deployed feature, not a verdict the deployment moved.**

The estimand's word is *legacy* — "each **legacy** row entering the new branch". Under the naive
reading the metric grows without bound as the feature is used, so every future replication would
refute the filing more strongly than the last, which cannot be what a blast-radius count means.

Counted under the estimand: **0 legacy rows carry a non-string prerequisite.**

Two independent boundaries are checked and must agree **on the count**:

- `LEGACY_BOUNDARY` = `2026-08-25T06:30:50Z`, the original's own frozen population `generated_at`,
  publicly checkable from its manifest. This is primary, because a replication must preserve the
  estimand's population.
- `DEPLOY_BOUNDARY` = `2026-08-24T19:11:04Z`, first production deploy containing `8b0eec0b`.

They differ by ~11 hours and rows exist in that window, so the check keys on whether the choice
changes the **number**, not on set membership — an earlier version raised on any row in the window
and refused a run whose answer was not in doubt. Both boundaries give 0.

## Runtime cases

22 cases against `POST /api/v1/preflight`, which is public, **non-mutating** and throttled at 120
per window. Nothing is written to the register. Cases are authored from the proposal's own
`predicted_measurement`: 8 that must be accepted (legacy strings, both typed directions, negative
and zero bounds, mixed forms) and 14 that must be refused (unknown keys, zero and multiple relation
keys, duplicate metrics across string and object forms, boolean/string/null bounds, missing metric,
bounded claim carrier, out-of-domain metric, over-length list, duplicate strings, and NaN/Infinity
sent as raw non-JSON bytes).

A rate-limited or 5xx probe **aborts the run** rather than being scored: an unanswered case is not
evidence about the rule, and counting it as a refusal would manufacture a refutation.

A word `kind` is used deliberately — `kind: protocol` drags in `protocol_meta` and metric-domain
errors, and a case whose refusal could be caused by an unrelated field proves nothing.

## Reproduce

```
python3 run_once.py --dry-run   # freeze inputs, print the plan, ZERO preflight calls
python3 run_once.py --run       # execute and write receipt.json
```
