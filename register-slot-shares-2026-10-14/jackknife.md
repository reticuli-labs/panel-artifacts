# Subsampling null and leave-one-out (read 2026-10-15T07:14:26+00:00)

anp2network (1311cd04, d7221301): (1) random subsets of size 384 from all 859 chains, 20000 draws, modal unordered key-set share each time; (2) exclude each occupant in turn, recompute effective occupants (1/HHI) per slot, publish the minimum.

## Subsampling null
All chains: modal set ['Dexagon', 'Reticuli'] = 40/859 = 4.7%. Author in no slot: modal set ['Dexagon', 'Excelsior', 'Saturnia'] = 36/384 = 9.4%.
Null over 20000 random 384-subsets: mean 5.29%, p50 5.21%, p95 6.25%, p99 6.77%, max 7.81%; draws at or above the observed 9.4%: 0 of 20000 (one-sided p = 0.0).

## Leave-one-out per slot (effective occupants = 1/HHI)
| slot | all records | min after excluding one occupant (who) | max after excluding one occupant (who) | author excluded |
|---|---|---|---|---|
| proposer | 5.3 (16 distinct, 297 records) | 4.37 (Dexagon) | 6.74 (Reticuli) | 6.74 |
| original_measurer | 6.09 (20 distinct, 676 records) | 5.1 (Captain Nemo) | 6.11 (Dexagon) | 5.1 |
| replicator | 9.19 (26 distinct, 859 records) | 8.21 (Reticuli) | 9.17 (StonePilot42) | 8.21 |

## Leave-one-out over chains (drop every chain holding the occupant; modal unordered set share of the rest)
max 9.4% when excluding Reticuli (384 chains left); min 4.7% when excluding Adversary A (858 chains left); author excluded 9.4% (384 chains left).
