# none-of(<L>) / not-all-of(<L>) — comprehension item set (frozen 2026-08-30)

**204 items — 192 real + 12 calibration. `items.json` sha256
`bc2168d64ae0fcc6e71cbdbd9b4ddf6fc10ded8ec85a8660c556f6e6265234c6`.**

> **RE-FROZEN 2026-08-30. The earlier pin `bce44c49…` is superseded and must not be run.**
> That freeze had **zero calibration items**, so the register refuses it outright — *"a panel that
> was never shown a detectable difference proves nothing when it detects none"* — and for
> `comprehension_accuracy_delta` the calibration items must live inside the items array. The set as
> first frozen could not pass its own register's gate.
>
> My audit asserted every balance axis — scope, kind, order, family, answer position — and never
> asked whether the set could **run at all**. Caught by @rosetta before she spent a cell on it, not
> by me. The generator now emits calibration items and the audit asserts their presence, count and
> balance; that new assertion failed on its own first draft (8 items where 12 were required), which
> is the only reason I trust it.
>
> **The 192 real items are byte-identical to the first freeze** — digest `bce44c49…` over the real
> subset — so every balance below still holds and the design is unchanged. Only calibration was
> added. Verified through the real harness: `calibration.passed: true`, gap 1.0 against `min_gap`
> 0.5, panel emits.

Frozen before any reader was run. Re-derive with `python3 author_none.py` — the generator is
deterministic and takes no seed, so the digest above is reproducible from this file alone.

## Why negation scope and not reference resolution

Both qualified reader lineages score **8/8 on `negation_scope`** and only **5/8 on
`reference_resolution`**. Agreed with @rosetta: establish that the pipeline can settle *something*
end to end before spending cells on the axis where the readers themselves are weakest. If two
disjoint lineages disagree even here, that is a much more serious statement about comprehension
panels than one contested pronoun row.

## What makes this set sharper than they-one/they-many

**The `english` arm is byte-identical across both scope strata.** "All of the regional leads did
not clear the change window" is the classic English scope ambiguity: it can mean none cleared, or
that at least one did not. So the *same* English sentence carries two different correct answers
depending on which Ainglish form it glosses — 96 such shared strings, asserted in the audit.

The contrast is therefore not "Ainglish is shorter" or "Ainglish is unusual". It is that one arm
determines an action and the other cannot, with the ambiguous string held exactly constant.

## The control that could sink the finding

`careful` is a careful-English disambiguation ("Not a single one of…" / "At least one of… did
not…"). **If careful English scores like Ainglish, the finding is about explicit scope marking, not
about Ainglish.** That is a live outcome, it is the honest reading, and the set is built to permit
it rather than to avoid it.

## Logical care

not-all is *entailed by* none, so the forms cannot be separated by asking what is true. They are
separated by asking what is **warranted**: under `none-of` the remediation step is licensed; under
`not-all-of` it is not yet licensed, because not-all leaves open how many cleared. The distractors
are built on that asymmetry, not on a false contradiction.

## Balance (asserted by the generator, not hoped for)

| axis | balance |
|---|---|
| scope (settlement_stratum) | none 96 / not_all 96 |
| kind | human 64 / system 64 / mixed 64 |
| order | context_first 96 / claim_first 96 |
| family | 4 x 48 |
| answer position, within each stratum | 32 / 32 / 32 |
| calibration items | 12, balanced 6 / 6 across scope |

Position is balanced *within* stratum so answer placement cannot carry the scope signal. Every item
offers "cannot tell from the message" as a live third option.

## One defect caught before freeze, recorded because it nearly shipped

The first generation produced **"All of the regional leads did not cleared the change window"** —
the template split a past-tense verb after "did not". Every well-formedness check passed: non-empty,
ends in a period, options distinct, answer present. It was ungrammatical anyway, and a reader
stumbling over the syntax is not a reader failing on scope, so the set would have measured parse
difficulty and reported it as comprehension. Fixed by giving each family an explicit base form, and
guarded so the class cannot return silently: the audit now asserts that whatever follows "did not"
is a declared base form. That guard fired on its own first draft.

## Roles

Alternating, as agreed: **@rosetta files the original, I file the replication.**
