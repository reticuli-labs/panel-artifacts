# they-one / they-many — comprehension item set (frozen before the run)

**198 items: 192 scientific + 6 calibration.** Frozen digest (harness formula,
`sha256(json.dumps(items, sort_keys=True, separators=(",",":"), ensure_ascii=False))`):

```
09f83faaa3cfdea78c52538d1c245c3367c7c648fe4af40390be0b6bee3fd3ad
```

## Why this construct

Of 61 proposals carrying a declared evidence contract, exactly **one** is `evidence_ready`, and
**50 are blocked on a missing `comprehension_accuracy_delta` original**. `they-one / they-many`
is one of four rows sitting at `stage=measured` with `token_delta` already satisfied and nothing
missing but this metric — so a single admissible original moves it to `evidence_ready`.

## The design is the proposal's, not mine

Taken from its declared `predicted_measurement`: at least 120 held-out operational items (192
here); each carrying one singular and one plural antecedent candidate, **both semantically live**;
a critical subject-pronoun clause; and a **consequence** question whose correct next action depends
on whether exactly one or more than one referent acted or owns the task. Balanced by construction:

| axis | balance |
|---|---|
| intended number | 96 one / 96 many |
| antecedent order | 96 singular-first / 96 plural-first |
| subject kind | 64 human / 64 agent / 64 entity |
| consequence family | 96 approval-quorum / 96 ownership-contact |

Verb morphology is identical across arms, because singular `they` takes ordinary plural
agreement — nothing about number may leak through agreement. The primary comparator is **bare
`they`**, as the proposal names it; the careful-English surface is carried on each item as
`careful` for the declared secondary comparison but is **not** run here.

Strata are manifest-bound (`settlement_strata`, equal weight), because the proposal's prediction
is that the marked arm improves **in both number strata** — a pooled scalar could hide one
stratum failing.

## One design fault the audit caught

The first build fixed the option order as `[act_one, act_many, cannot-tell]`, which puts **every**
`they-one` key at position A and **every** `they-many` key at position B. A reader with a
position bias would then manufacture a difference between exactly the two strata the proposal asks
to be compared, and it would read as a real stratum effect. Ornith-35B, qualified below, answers
'A' on 11 of 16 probe cells — so this was not hypothetical.

Answer positions are now placed deterministically and are **exactly** balanced, 32/32/32 within
each stratum; `author_they.py` asserts a zero spread and refuses to emit otherwise.

## Reader qualification

Run against a held-out probe before minting, at `max_tokens` 3072. The raised bound is itself a
finding: at the harness default of 1024 both Ornith-35B and Seed-OSS-36B were recorded as unusable,
because a reasoning reader spends the whole budget thinking and never reaches the option list.

- **ornith-35b — QUALIFIES**: detectable 6/6, other arm 1/6, gap **+0.833** against a 0.50 floor.
- seed-oss-36b — see `qualify.log`.
