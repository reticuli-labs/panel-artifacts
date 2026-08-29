# Amendment: the calibration set was not a positive control

**Run 1 refused at the calibration gate, `cause: competence`. Zero real cells bought.** Pooled
gap **0.292** against a 0.50 floor. Envelope: `REFUSAL-run1.json`.

| reader | detectable | other | gap |
|---|---|---|---|
| command-r-35b | 0.333 | 0.333 | **0.000** |
| gemma4-31b | 0.833 | 0.500 | 0.333 |
| qwen3.6-27b | 0.833 | 0.333 | 0.500 |
| ornith-35b | 0.833 | 0.500 | 0.333 |
| **pooled** | 0.708 | **0.417** | **0.292** |

The pooled `other` arm at 0.417 sits well above the 0.333 chance floor, which says the bare arm was
partly answerable. Dropping the blind reader alone does not fix that — it only lifts the gap to
0.389, still short.

## Why, measured rather than assumed

`default_probe.py` re-ran the six calibration items across both arms on two readers,
split by stratum:

| stratum | marked | bare | gap |
|---|---|---|---|
| **they-one** | 6/6 | **0/6** | **+1.000** |
| **they-many** | 4/6 | **5/6** | **−0.167** |

**Bare `they` carries a plural default.** On `they-many` items the default already yields the
correct consequence, so the marker adds nothing and mildly misleads; on `they-one` items the
default is wrong every time, so the marker is worth a full point of recovery.

Half the calibration set therefore contained **no effect to detect**. A positive control exists to
prove the instrument can see a KNOWN difference; items where the difference is absent are not
controls, they are null items, and pooling them asks the panel to detect something that is not
there.

## What changes, and what deliberately does not

**Changed — the calibration set only.** Six fresh `they-one` control items replace the mixed six.
`they-one` is where a known, measured difference exists (+1.000 on the probe), which is the
definition of a positive control.

**Changed — one reader excluded, under a rule fixed in advance of seeing any real cell:** a reader
whose individual calibration gap is **0.000** is indistinguishable from blind on this construct and
is not an instrument for it. That excludes `command-r-35b`. The rule is stated here before the run
rather than chosen after seeing which roster passes.

**NOT changed — the 192 real items.** Same set, same digest, still 96 `they-one` / 96 `they-many`,
still manifest-bound strata at equal weight. This is the point: **the amendment cannot manufacture
the result.** If `they-many` genuinely fails to improve over bare `they`, the stratified output
will say so at n=96 per stratum, and the proposal names that as a refutation condition —
*"Refuted if either number stratum fails to improve over bare they."* On the 12-cell probe it
already points that way.

Fixing the admission test is not the same as fixing the answer. The gate decides whether the
experiment is allowed to run; the real items decide what it says.

## Standing prediction, recorded before the run

`they-one` improves substantially over bare `they`; `they-many` improves little or not at all.
If that holds at n=96 per stratum, the honest reading is that the construct's value lives almost
entirely in `they-one`, and the pair as specified is refuted by its own declared criterion. I will
report that outcome if it lands, including that it is adverse to a row I chose to invest a day in.
