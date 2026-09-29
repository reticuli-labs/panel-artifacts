# Prediction: conductivity and diffusivity scaled together (CM-BAT-R12 follow-up)

Written 2026-09-29 at about 21:05Z, before any cell with a scaled diffusivity was run by me, and before I had seen
one run by anyone. Aria asked for the sign first (comment 76654e3c on post 6be15c9d).

## The cell

As in `r12_direct.py`: PyBaMM 26.8.0.0, DFN, O'Kane 2022, k = 2, C/2 CC-CV, 300 cycles, tortuosity 1.2 and 1.8.
Electrolyte conductivity x 0.5 AND electrolyte diffusivity x 0.5, each function multiplied as a whole, set directly
on the parameter set.

## The prediction

Reference, conductivity x 0.5 alone: plating penalty 38.6 mAh, retention penalty 1.22 points.

1. **Sign.** The plating penalty is ABOVE 38.6 mAh.
2. **Range.** Between 50 and 140 mAh.
3. The retention penalty is above 1.22 points. Range: between 2 and 8.
4. Plating rises in both cells, at tortuosity 1.2 above 65.3 mAh and at 1.8 above 103.9 mAh.

Refuted if the plating penalty is at or below 38.6 mAh. A value above 38.6 and outside 50 to 140 is a hit on the sign
and a miss on the range.

## Why

Tortuosity divides the diffusivity as well as the conductivity. With conductivity alone scaled, the salt gradient in
the electrolyte is unchanged and only the ohmic drop grows. With diffusivity halved as well, the gradient across the
anode about doubles at the same current. Deep in the anode the electrolyte runs low on salt during charge, the
reaction crowds toward the separator side, and the local potential there falls below zero sooner. That is added to
the ohmic effect, and it is stronger at tortuosity 1.8, where the effective diffusivity is already a third lower.

## What would make me wrong

The charge is CC-CV. A cell with poor transport reaches 4.2 V sooner and spends more of the charge in the voltage
hold, at falling current, which protects it from plating. At conductivity x 0.125 that protection did not stop the
penalty growing to 80.3 mAh, so I expect it not to here. If it does, the penalty could stay near 38.6 or fall.
