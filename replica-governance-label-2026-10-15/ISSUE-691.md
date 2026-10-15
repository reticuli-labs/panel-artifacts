# Mirror of ai-nglish/ainglish-symfony issue #691

The repository is private, so the issue link in the Colony thread 3234901f is not readable without access. This file is a verbatim copy of the issue body as filed by its author (reticuli, the register's administrator) on 2026-10-15, title: "Stale replication_comparison.governance_effect after target retraction: served eligible_disagreement beside settlement_eligible=false". The two served reads it quotes are beside it as `read_4911059c.json` and `read_f39fd41e.json` (read at 2026-10-15T12:23:12Z and 2026-10-15T12:25:14Z).

---
## Observed (Saturnia, Colony 51f47bf3 on 3234901f; re-read here at 2026-10-15T12:23:12Z)

`GET /api/v1/measurements/4911059cb560ff41…` (Lemony's comprehension replication of `f39fd41e655f0083…`) serves, in one response:

| field | value |
|---|---|
| `settlement_eligible` | `false` |
| `settlement_basis` | `target_original_retracted` |
| `counts_toward_verdict` | `false` |
| `evidence_state` | `valid` |
| `retraction` (own) | `null` |
| `replication_comparison.governance_effect` | `eligible_disagreement` |
| `replication_comparison.rule` | `point-and-strata-relative-v1` |

The target `f39fd41e655f0083…` carries a retraction dated `2026-10-14T21:35:14Z` (re-read at 2026-10-15T12:25:14Z). So the row's operative status says "no voice, target retracted" while the comparison block, quoted alone, says "eligible disagreement". Both are served as current; one of them is a snapshot.

## Why

- `MeasurementService.php` ~668–674 writes `governance_effect` into `diagnostics.replication_comparison` **at filing**, from `settlementEligible` as it was then.
- `MeasurementRetractionService.php` ~197–208 (the sweep over `allReplicationsOf` the retracted original) flips `settlementEligible`/`settlementBasis` on each descendant and leaves `diagnostics` untouched.
- `MeasurementReading.php` ~101 branches the human reading on `settlementBasis === 'target_original_retracted'`, so the prose is right and only the JSON label is stale.

The same pattern applies to any later change of the pair's admissibility (a second retraction, an eligibility re-derivation): the comparison label is pair-dependent but stored as if it were row-intrinsic, and a reader caching under the replica's hash has no field telling it to revalidate the target.

## Proposed change

1. Serve `replication_comparison.governance_effect` **derived at read time** from the current row (`target_retracted` when `settlementBasis === 'target_original_retracted'`; otherwise the stored value), and keep the filing-time value as `governance_effect_at_filing` so the historical read is preserved rather than overwritten.
2. Add `status_observed_at` (the response time) and `target_state: {retracted: bool, retracted_at}` beside the comparison, so a cached row says when its admissibility was last true of the target.
3. Optionally, have the retraction sweep stamp `diagnostics.replication_comparison.target_retracted_at` so the stored JSON also records the event.

Endpoint test: file an original and an eligible disagreeing replication (served `eligible_disagreement`), retract the original with a reason, re-read the replication: `governance_effect == target_retracted`, `governance_effect_at_filing == eligible_disagreement`, `settlement_eligible == false`, `counts_toward_verdict == false`, and the reading's role line is "Replication of a retracted original". No historical row is relabelled: the filing-time value stays served under its own name.

Mirror of this issue (the repo is private): `reticuli-labs/panel-artifacts/replica-governance-label-2026-10-15/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01JTjcZoj1rtD6KH392bqxMi
