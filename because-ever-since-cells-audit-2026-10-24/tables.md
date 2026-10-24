# Tables (written by audit.py)

## Cells by stratum, arm and reader (Ry/Rn = reason asserted yes/no, Iy/In = interval asserted yes/no; gold: reason RyIn, interval RnIy, both RyIy, neither RnIn)

| stratum | arm | reader | cells | correct | accuracy | RyIn | RnIy | RyIy | RnIn |
|---|---|---|---|---|---|---|---|---|---|
| reason | ainglish | all | 73 | 1 | 0.014 | 1 | 36 | 18 | 18 |
| reason | ainglish | gemma3 | 34 | 0 | 0.000 | 0 | 3 | 13 | 18 |
| reason | ainglish | mistral | 39 | 1 | 0.026 | 1 | 33 | 5 | 0 |
| reason | english | all | 71 | 30 | 0.423 | 30 | 9 | 15 | 17 |
| reason | english | gemma3 | 38 | 6 | 0.158 | 6 | 0 | 15 | 17 |
| reason | english | mistral | 33 | 24 | 0.727 | 24 | 9 | 0 | 0 |
| interval | ainglish | all | 78 | 49 | 0.628 | 0 | 49 | 5 | 24 |
| interval | ainglish | gemma3 | 39 | 10 | 0.256 | 0 | 10 | 5 | 24 |
| interval | ainglish | mistral | 39 | 39 | 1.000 | 0 | 39 | 0 | 0 |
| interval | english | all | 66 | 37 | 0.561 | 0 | 37 | 14 | 15 |
| interval | english | gemma3 | 33 | 4 | 0.121 | 0 | 4 | 14 | 15 |
| interval | english | mistral | 33 | 33 | 1.000 | 0 | 33 | 0 | 0 |
| both | ainglish | all | 70 | 37 | 0.529 | 0 | 28 | 37 | 5 |
| both | ainglish | gemma3 | 38 | 18 | 0.474 | 0 | 15 | 18 | 5 |
| both | ainglish | mistral | 32 | 19 | 0.594 | 0 | 13 | 19 | 0 |
| both | english | all | 74 | 39 | 0.527 | 0 | 27 | 39 | 8 |
| both | english | gemma3 | 34 | 18 | 0.529 | 0 | 8 | 18 | 8 |
| both | english | mistral | 40 | 21 | 0.525 | 0 | 19 | 21 | 0 |
| neither | ainglish | all | 74 | 30 | 0.405 | 0 | 41 | 3 | 30 |
| neither | ainglish | gemma3 | 40 | 16 | 0.400 | 0 | 21 | 3 | 16 |
| neither | ainglish | mistral | 34 | 14 | 0.412 | 0 | 20 | 0 | 14 |
| neither | english | all | 70 | 34 | 0.486 | 0 | 35 | 1 | 34 |
| neither | english | gemma3 | 32 | 19 | 0.594 | 0 | 12 | 1 | 19 |
| neither | english | mistral | 38 | 15 | 0.395 | 0 | 23 | 0 | 15 |

## Question-phrase echo (count of the stratum's 72 sentences containing the phrase)

| stratum/arm | explains why | from that event | because | ever since | present perfect |
|---|---|---|---|---|---|
| reason/english | 72 | 0 | 0 | 0 | 72 |
| reason/ainglish | 0 | 0 | 72 | 0 | 72 |
| interval/english | 0 | 72 | 0 | 0 | 72 |
| interval/ainglish | 0 | 0 | 0 | 72 | 72 |
| both/english | 72 | 72 | 0 | 0 | 72 |
| both/ainglish | 0 | 0 | 72 | 72 | 72 |
| neither/english | 0 | 0 | 0 | 0 | 72 |
| neither/ainglish | 0 | 0 | 0 | 0 | 72 |

## Stratum tolerance against one item step

| stratum | served value pp | tolerance pp | cells en / ai | one item step pp | tolerance below step |
|---|---|---|---|---|---|
| reason | -40.88 | 4.088 | 71 / 73 | 1.4085 | no |
| interval | 6.76 | 0.676 | 66 / 78 | 1.5152 | yes |
| both | 0.16 | 0.02 | 74 / 70 | 1.4286 | yes |
| neither | -8.03 | 0.803 | 70 / 74 | 1.4286 | yes |
