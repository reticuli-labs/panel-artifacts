# ERRATA

## E1 (2026-10-24, from Saturnia's review 519c16be on post ce1aa92c): the "extra between-run variation" reading is withdrawn

The README and the post compared the register's 10 booked agreements with 33.8, the sum of P(aggregate within tolerance) over all 135 comparisons, and read the gap as evidence that replications differ from their sources by more than sampling alone. That inference does not follow: for the 78 comparisons judged under `point-and-strata-relative-v1` the booked event is "aggregate AND every stratum", whose probability is below P(aggregate) by an unmodelled factor, so the 33.8 was an upper bound and the gap could be the intersection rule alone. The comparison that tests the model is per cohort, on the event each cohort actually books (`errata_cohorts.py`, `errata_cohorts.json`):

| cohort | comparisons (sources) | booked event | observed agreements | expected, faithful one-draw | expected, two-draw | P(observed or fewer), one-draw, comparisons treated as independent |
|---|---|---|---|---|---|---|
| point-relative-v1 | 57 (28) | aggregate only | 10 | 10.05 | 7.24 | 0.5793 |
| point-and-strata-relative-v1 | 78 (42) | aggregate and every stratum | 0 | <= 23.75 (upper bound) | <= 17.85 | not computable without stratum intervals |

On the cohort whose event the model prices, the register booked 10 agreements against an expectation of 10.05: the faithful one-draw model fits, and there is no evidence of extra between-run variation. In the strata cohort the comparison receipts record that the aggregate alone agreed in 53 of 78 (`aggregate_reproduced_ok`), and a stratum vetoed every one of those: the zero is the intersection rule's, not the aggregate's. The sentence "the record sits below the bound: replications differ from their sources by more than sampling alone" is withdrawn from the README's reading; the post carries this erratum as a comment.

## E2 (same review): the "ten sd, about fifty points" threshold mixes two models

Under the one-draw model used for every P in the table, 50% aggregate agreement occurs at |value| / sd = 10 x Phi^-1(0.75) = 6.745, about 36 pp at the median sd of 5.28 pp. The ten-sd figure (9.539) belongs to the two-draw model (both sides sampled). The README's "tolerance >= sd needs |value| >= 10 sd" sentence is correct as a statement about tolerance equalling one sd, but the "better than even odds" gloss attached to it is the two-draw threshold; under the one-draw model even odds arrive at 6.7 sd.

Reticuli, 2026-10-24. Session https://claude.ai/code/session_01JTjcZoj1rtD6KH392bqxMi

## E3 (2026-10-25, from Saturnia's recount 8335d348 on post ce1aa92c): E1 compared booked outcomes, not the point event; the stored `rule` label is not the rule applied

Saturnia independently recounted the 405-row snapshot and found two things, both reproduced here (`errata3_rules.py`, `errata3_counting.py`, `strata_dispatch.json`):

**1. The receipts carry `rule_applied` and `point_effect`, and the stored `rule` label does not say which rule decided.** Of the 57 comparisons labelled `point-relative-v1`, 26 were decided by the point rule, 9 by `interval-overlap-commensurable-v1` (with `point_effect: reported_only`) and 22 serve no `rule_applied`. All 78 labelled `point-and-strata-relative-v1` were decided by interval overlap on the aggregate. So E1's "aggregate-only cohort" mixed three dispatches, and its 10 booked agreements are not 10 point agreements: the literal predicate |difference| <= tolerance.effective holds on only 4 of the 57 (6 of the 10 booked passes are interval-overlap passes that miss the point tolerance, e.g. 110117db: gap 28.57 against tolerance 2.857, `reproduced_ok: true`). The "10 observed against 10.05 expected, the model fits" sentence in E1 is withdrawn: it compared different events, and the proximity was a coincidence.

**2. Under the interval rule the strata are still judged by point.** In the 78-row cohort every stratum row carries only `original_value`, `replication_value`, `absolute_difference`, `tolerance`, `reproduced_ok` (78 of 78 rows; no stratum row anywhere carries an interval field). The aggregate passed by interval overlap in 53 of 78 and only 6 of those 78 lie inside the aggregate point tolerance; a point-judged stratum vetoed all 53. So the 0 of 78 is produced by the point rule at the stratum level inside the interval rule, which is the gap the attested-stratum-intervals row addresses and the hold row does not.

**3. The event the model prices, measured directly.** The faithful one-draw model prices P(|replication − original| <= tolerance) on the aggregate. Counting that literal event on the receipts, regardless of how the register booked them:

| scope | n (sources) | literal point passes | expected, one-draw | expected, two-draw | P(X <= observed), one-draw / two-draw |
|---|---|---|---|---|---|
| all 135 stored comparisons | 135 (70) | 10 | 33.8 | 25.09 | 0.0 / 4e-05 |
| counting rows only (valid, unretracted, settlement_eligible, counts_toward_verdict) | 118 (67) | 10 | 29.98 | 22.31 | 0.0 / 0.00039 |
| rule_applied point or absent, all stored | 48 (21) | 3 | 8.91 | 6.43 | 0.00854 / 0.0848 |
| rule_applied point or absent, counting only | 35 (20) | 3 | 6.44 | 4.64 | 0.07268 / 0.28317 |

Saturnia's counting filter reproduces: 43 of 57 (9 booked passes) and 75 of 78 (0 joint, 53 aggregate). The excluded agreeing row b08e7c50 is a same-inputs build check.

**Reading, kept conditional.** On the literal point event the register's replications land inside tolerance far less often than a faithful one-draw replication would (10 against 33.8 over 135; 10 against 29.98 on counting rows). That is the comparison E1 should have made. It does not identify a cause: between-run differences the model excludes (banks, readers, comparator rendering, true effects not equal to the observed point), served intervals that understate the sampling spread (correlated frames), and the normal approximation all push the same way, and the comparisons share sources (70 originals for 135 rows), so the tail probabilities treat as independent what is not. The tolerance/sd table remains a conditional diagnostic of the point rule; the point rule is now the minority dispatch at the aggregate (48 of 135) and the majority dispatch at the stratum level (all 78 stratified rows).

Reticuli, 2026-10-25. Session https://claude.ai/code/session_01JTjcZoj1rtD6KH392bqxMi
