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

---

# Reader qualification: ALL FOUR CANDIDATES EXCLUDED (2026-08-30)

No panel was run on the real items. Two attempts, both retained, no reader qualified.

```
attempt 1 (max_tokens 1024)          english  ainglish   gap    live
  deepseek/deepseek-v4-flash          0.45     0.83     +0.38   23/24
  qwen/qwen3.8-flash                  1.00     1.00     +0.00   10/24
  z-ai/glm-5.3-flash                  0.50     1.00     +0.50   13/24
  google/gemini-3.7-flash             0.00     0.25     +0.25   24/24

attempt 2 (max_tokens 4096)          english  ainglish   gap    live
  deepseek/deepseek-v4-flash          0.50     0.92     +0.42   24/24
  qwen/qwen3.8-flash                  0.40     1.00     +0.60   15/24
  z-ai/glm-5.3-flash                  0.60     1.00     +0.40   17/24
  google/gemini-3.7-flash             0.00     0.42     +0.42   24/24
```

Exactly one configuration change was made, for a diagnosed cause, and both attempts are retained.
The runbook forbids retrying configurations until one passes, and none did.

## Cause 1 — the empties are truncations, not refusals

`finish_reason: length` on 9 of 10 empty cells, with up to **4,634 reasoning tokens** spent before
the budget ran out. Raising 1024 → 4096 improved liveness everywhere (deepseek 23→24, qwen 10→15,
glm 13→17) and still did not clear it. These readers think expensively and some need far more
headroom than a classifier ever would.

## Cause 2 — the item design fights the gate, and this is the useful finding

What the readers actually chose on the **ambiguous** english arm:

```
deepseek   6 lucky / 4 wrong / 2 not-determined
glm        6 lucky / 4 wrong
qwen       2 lucky / 3 wrong
gemini    12 not-determined
```

Three of four **coin-flip between the two action options**, scoring ~0.50 on an arm that carries no
information. With two actions plus a not-determined option, a forced choice floors at about 0.50,
not at 0 — so the achievable gap is roughly `1.00 − 0.50 = 0.50`, which **is** `min_gap`. A reader
behaving correctly lands exactly on the threshold and fails it.

And note gemini, the one reader that answers the ambiguous arm **honestly** — 12/12 not-determined,
scoring 0.00 — fails for the opposite reason: only 0.42 on the marked arm, so it does not read the
construct at all. The two failure modes are not on a spectrum; they are different readers.

**The design fix is more action options, not a lower bar.** With four distractor actions plus
not-determined, a coin-flipper floors near 0.25 and the gap ceiling rises to ~0.75, leaving room for
the gate to discriminate. This also explains @rosetta's `next-you` refusal from the other direction:
her four options carried **no** not-determined choice, so a careful reader's only honest move was
silence, and silence is a dead cell rather than a wrong answer.

Re-derive both attempts offline from `qualification-attempt1-maxtok1024.json` and
`qualification-attempt2-maxtok4096.json`. Total spend: **$0.087**.

---

# v2 (`d5f02568`): the design fix worked on the arm it targeted and broke the other one

Three qualification attempts now, all retained, **no reader has qualified and no real cell has been
bought**. Stopping here: the runbook forbids retrying until something passes, and I have already
made the one principled change per diagnosed cause that it allows.

```
                          v1: 2 actions + n/d      v2: 3 actions + n/d
reader                    english   ainglish       english   ainglish
deepseek-v4-flash          0.50      0.92           0.18      0.30
qwen3.8-flash              0.40      1.00           0.40      0.70
glm-5.3-flash              0.60      1.00           0.00      0.70
gemini-3.7-flash           0.00      0.42           0.25      0.50
```

**The prediction held on the ambiguous arm.** Adding a third action dropped the guessing floor
exactly as intended — deepseek 0.50 → 0.18, glm 0.60 → 0.00.

**And the marked arm fell with it, which I did not predict** — deepseek 0.92 → 0.30, glm 1.00 →
0.70, qwen 1.00 → 0.70. The distractor I added ("add it to the review agenda as a missed target")
is plausible under the *correct* reading too, so it absorbed probability from the right answer just
as readily as from a guess. I made the item harder for everyone rather than harder only for
guessers, and the gap barely moved.

## What this actually establishes

A distractor lowers the guessing floor **only if it is attractive when you cannot tell and
unattractive when you can**. For a genuine disambiguation construct that option already exists and
is called `cannot tell from the message`. Any additional action fair enough to be plausible on the
bare arm is, by construction, plausible on the marked arm too.

So the ambiguous arm's floor is not a design artefact that can be engineered away by adding options.
A reader forced to act on an ambiguous message picks *some* action, and any action set that is fair
to the marked arm leaves roughly even odds among the scope-compatible ones.

**Which moves the problem to the gate, not the items.** `min_gap: 0.5` is a constant applied to an
arm whose achievable floor depends on the option structure the construct forces. Either the gate
should be stated relative to that floor, or the bare arm should credit `cannot tell` as correct —
and the second changes the estimand from "can the reader act" to "can the reader recognise it
cannot act", which is a different and also worth measuring, but not this one.

`glm-5.3-flash` reached **+0.70** on v2 — the only gap above the bar in any attempt — and was
excluded on liveness (16/24, six truncations on the bare arm). That is the one thread worth pulling
next, and it is a transport problem rather than a design one.

Total spend across three attempts: **$0.165**. Real items bought: **zero**.
