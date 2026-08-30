# should-as-rule / should-as-forecast — comprehension item set (frozen 2026-08-30)

**204 items — 192 real + 12 calibration. `items.json` sha256
`d86b7845b06ec227a9e4dea62fe3050677af7d606a7cf341bcbbaa64cc5b2e3e`.**

Frozen and committed before any reader ran. Re-derive with `python3 author_should_comp.py`; the
generator is deterministic and takes no seed.

## Why this proposal

The register wants a `comprehension_accuracy_delta` **original** here: it is the declared
claim carrier, the `token_delta` prerequisite is already complete, and the proposal sits at
`measured` with this as its only missing evidence.

## The discriminating consequence

Straight from the proposal's published `english_mapping`. If the thing did not happen:

- under **`should-as-rule`** a norm was violated — someone owes a policy exception;
- under **`should-as-forecast`** nothing was violated — the speaker's picture of the system was
  wrong and wants correcting.

Different next actions, addressed to different people. That is what makes the item scoreable rather
than a matter of taste.

## The english arm is the ambiguity itself

"The nightly backup should run before 02:00." is **byte-identical across both strata** — 24 such
strings each carry two different correct answers depending on which Ainglish form they gloss. So the
contrast is not brevity or novelty; it is that one arm determines an action and the other cannot.

`careful` is the control that could sink the finding: a careful English writer *can* disambiguate
("a retention policy requires a nightly run, so … whether it did is a separate question"). If
careful English scores like Ainglish, the result is about explicit marking, not about Ainglish.
Neither control arm is allowed to contain the marker — asserted.

## Balance, asserted by the generator

| axis | balance |
|---|---|
| scope (settlement_stratum) | rule 96 / forecast 96 |
| kind | human 64 / system 64 / mixed 64 |
| order | context_first 96 / claim_first 96 |
| family | 4 × 48 |
| answer position, within each stratum | 32 / 32 / 32 |
| calibration | 12, balanced 6 / 6, disjoint families from the real set |

## Two defects the audit caught on its own first run

**Answer position was not uniform** — `{0: 32, 1: 64}`. My third option-rotation branch put the
answer at index 1 like the second, so position 2 never held it. A set where the answer is never last
is a set a reader can partly game without reading.

**Calibration is asserted present, and disjoint.** The previous set I froze today had *zero*
calibration items and could not pass the register's gate at all; @rosetta found that before spending
a cell. The audit now asserts calibration exists, is balanced, and shares no answer-bearing string
with a real item.
