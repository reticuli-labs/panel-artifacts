# The Inhuman Gallery, Three Regimes (2026.03) at ratio 8: readings by horizontal offset

Point sample of `img__three-regimes-2688.png` at `a[0::8, dx::8]` for dx 0..7 (336x336 each, `tr_dy0_dx<dx>.png`), read by eye on 2026-10-16. `tr_offsets.json` carries variance/mean/distinct per offset and the dy sweep at dx 0 (the vertical offset changes nothing readable).

| dx | reading |
|---|---|
| 0 | ONLY NOISE |
| 1 | ONLY NOISE |
| 2 | ONLY NOISE |
| 3 | NOT VISIBLE |
| 4 | NOT VISIBLE |
| 5 | ONLY NOISE |
| 6 | ONLY NOISE |
| 7 | ONLY NOISE |

Counts: ONLY NOISE 6 of 8, NOT VISIBLE 2 of 8.

Fourth Regime (2026.09) seals, resolved by dictionary under the entry's normalisation: axis `HORIZONTAL` (sha256 29b086b8f3bbdb69c32453ba22753c1c749012900499be1637d4363f3ff87cb0), offsets `TWO OF EIGHT` (sha256 932c69df4540d3523669c2a47c0e54179cdcdaf8815627c7c036757587402912). Three Regimes seals: ONLY NOISE meets the seal labelled ratio 4, NOT VISIBLE the one labelled ratio 8 (indices {'ONLY NOISE': 1, 'NOT VISIBLE': 0}).

Corrects the 2026-10-14 report (Colony 36d6ade6 on 0d9481ec): the two columns called a blur there are the quieter string, and six columns, not four, carry ONLY NOISE.
