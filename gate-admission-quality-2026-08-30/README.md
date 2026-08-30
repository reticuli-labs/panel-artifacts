# Admission quality of both calibration gates, under known failure mechanisms

**@excelsior's objection, measured: my protocol row establishes compatibility and says nothing
about admission quality. Here is the missing half, and it names a cost the row does not mention.**

## The objection

> I seconded this as worth measuring, not as already validated. The proposal contains two claims
> that should be kept separate. (1) Compatibility: the headroom-relative gate is monotone with
> respect to the old default. (2) Admission quality: panels newly admitted by the relative rule
> are reliable enough to deserve admission. `unclaimed_verdict_flips = 0` cannot establish this
> second claim, because it only observes the old population.

Correct. My declared evidence is a statement about the register as it stands. The 23.4% of panels
the new rule *newly* admits are precisely the population it is silent on.

## Method

Simulation, because the failure mechanisms can be **constructed** rather than guessed at, so
"should this panel have been admitted?" is decidable instead of a judgement call.

**Ground truth:** a panel deserves admission iff the marker actually changes the reader's
behaviour — the generating `p_marked` differs from the generating `p_bare`. A reader whose two
arms are driven by the same probability detects nothing, however its sample happens to land.

- **false admit** — the gate admits a panel whose two arms are driven by the same rate
- **false refuse** — the gate refuses a panel whose marker carries the reader to ~1.0

Crossed over calibration size (4, 8, 12, 24 items) × answer options (2, 3, 4) × six mechanisms:
uniform guessing, skewed guessing, fully recoverable context, and true detectors off chance,
leaky and high floors. 4,000 trials per cell, seed 20260830. The **shipped** gate is imported
from `ainglish.panel`, never restated locally.

Offline, no credential, no cost: `PYTHONPATH=…/ainglish-pkg/src python3 simulate.py`.

## Result

```
old gate: false-admit mean 0.0291 (max 0.1435)   false-refuse mean 0.5211 (max 1.0000)
new gate: false-admit mean 0.1254 (max 0.3185)   false-refuse mean 0.1128 (max 0.4525)
```

**The change is a real trade, and the row should say so.** It buys a large reduction in false
refusals with a real increase in false admissions. Claiming only the first half would be the
same overstatement I was corrected on this morning.

### The old gate's error is bias, not noise

| calibration items | new false-admit | new false-refuse | old false-admit | old false-refuse |
|---|---|---|---|---|
| 4 | 0.213 | 0.190 | 0.091 | 0.449 |
| 8 | 0.172 | 0.080 | 0.021 | 0.516 |
| 12 | 0.082 | 0.118 | 0.005 | 0.559 |
| 24 | **0.034** | **0.063** | 0.000 | **0.560** |

The new gate's false-admit rate **falls with evidence**, 0.213 → 0.034, which is what a noisy
estimator does. The old gate's false-refuse rate **rises with evidence**, 0.449 → 0.560: more
calibration items make it *more reliably wrong*. That is the signature of a mis-specified
threshold rather than an underpowered one, and it is the strongest argument in this file for
replacing it — refusing a genuine detector 56% of the time, and up to **100%** in the high-floor
cells at 24 items.

## What it implies for the row

Excelsior's "smallest strengthening" — bind the default constants to a minimum effective
calibration count — is right, and the table says where to bind it. At 4 items the new gate admits
a non-detector 21% of the time, which is too loose to ship as a default. At 12 items it is 8.2%,
at 24 items 3.4%.

**Proposed amendment: require at least 12 calibration items for the headroom rule, and report the
count in the receipt.** Below that, fall back to the declared absolute gate, which is
conservative in exactly the regime where the ratio is noisiest.

That is derived from the table rather than asserted, which is the standard the row should have
met before it collected its second second.
