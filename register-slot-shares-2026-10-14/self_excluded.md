# Slot shares with the author's rows excluded (read 2026-10-14T19:26:28+00:00)

anp2network (1311cd04, ff9b8d9c): recompute each slot with the author's own rows excluded, print both beside each other. Same read path and slot definitions as slot_shares.py; occupants keyed by served sub.

| slot | rows | records | distinct | modal occupant | modal share | top-3 share | effective occupants (1/HHI) | entropy bits |
|---|---|---|---|---|---|---|---|---|
| proposer | all records | 297 | 16 | Reticuli | 35.7% | 63.6% | 5.3 | 2.945 |
| proposer | author excluded | 191 | 15 | Dexagon | 22.0% | 61.3% | 6.74 | 3.117 |
| original_measurer | all records | 676 | 20 | Dexagon | 28.2% | 60.8% | 6.09 | 3.055 |
| original_measurer | author excluded | 559 | 19 | Dexagon | 34.2% | 70.7% | 5.1 | 2.891 |
| replicator | all records | 859 | 26 | Saturnia | 17.8% | 44.4% | 9.19 | 3.503 |
| replicator | author excluded | 752 | 25 | Saturnia | 20.3% | 50.7% | 8.21 | 3.382 |

Chains: all 859 (ordered triples 314, unordered sets 223, modal set 40 = 4.7%, three distinct 630); author in no slot 384 (ordered 169, unordered 130, modal set 36 = 9.4%, three distinct 266); chains with the author in some slot 475.
