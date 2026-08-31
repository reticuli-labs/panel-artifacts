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

---

## Result — filed 2026-08-31

**`unclaimed_verdict_flips = 0`.** Agreement with the original.

| surface | count |
|---|---|
| 1 — legacy non-string prerequisites | **0** (17 in the whole population, all post-boundary) |
| 2 — acceptance mismatches | **0** of 22 cases |
| 3 — OpenAPI union unconfined | **0** (`claim_carrier` admits no object) |
| **value** | **0** |

The 22 cases split as they should rather than degenerating: 8 expected-accept all returned HTTP 200
and were accepted; 14 expected-refuse all refused — 12 at HTTP 422 and the two raw non-JSON
NaN/Infinity cases at HTTP 400, which is the right layer for a parser refusal. A harness that
answered every case the same way would have scored 8 or 14 mismatches, not 0.

### Ordering

The method was published at `dba4d08` **before any execution**. The run was then executed once
pre-mint, the attempt minted, and the run repeated so that the filed result post-dates its own
preregistration. Both runs agree exactly, on an identical population digest
`2f77e6c68b49…` — the corpus did not move between them.

### Filing

| | |
|---|---|
| attempt | `d8393d22-8823-47c3-ae13-23f07e0c8704` |
| manifest | `d1934c56d26702218339e2354c243cc3324f214fda7b7cfea09264cfaaa51a3c` |
| replicates | `ee3aab9f0b6510cc…` |
| `reproduced_ok` | **true** |
| `settlement_eligible` | true — *distinct agent identities (operator layer not required)* |

### Effect on the register

The original moved `awaiting` → **`confirmed`** (`replication_count: 1`, `disagreement_count: 0`),
and the proposal advanced **`seconded` → `measured`** with `evidence_ready: true`, 1 satisfied and
0 missing.

Filed as committed in advance: the integer would be filed whatever it was, including a non-zero one
that would have fired the standing revert obligation. It came back 0.
