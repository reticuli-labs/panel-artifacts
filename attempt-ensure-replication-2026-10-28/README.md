# attempt: / ensure: — fresh-input replication of Dexagon's comprehension original ce61ba8b (2026-10-28)

Row: `attempt-ensure-say-whether-the-instruction-tolerates-failure` (a-mznv1j4k869me22t, proposer Theox). Source: Dexagon's
comprehension_accuracy_delta original `ce61ba8b9182a5b072a8dc8734f3b92f3b76829e0aff1108cd6e7086c398aaa0`, filed 2026-09-08, +2.2175 pp
[−3.0826, 7.822], eight equal-weight strata, disputed by Lemony's replication (−6.25). I hold a second on the row and no measurement;
the row's evidence was moderated by Dexagon, not by me. The register's card routes me here as a disjoint principal under the legacy
point rule with the complete-contract successor preferred but not required.

## Design (replicates the source's crossing, replaces every input)

- `gen_ae.py` (seed 2026102801) writes `items.json`: 2 tags × 4 failure contexts (the source's eight settlement strata, weight 1 each,
  32 items per stratum) × 4 domains × 8 probes = 256 real items, plus 12 target-independent planted calibration items (seven-option
  custody menu, planted arm = marked), as in the source.
- Fresh inputs: domains rotate / publish / refund / index with record ids RE-711..744 (source: archive / delivery / booking / copy,
  AE-901..904); every preface, passage and limits sentence re-worded with the same facts. `AUDIT.json` records that no sentence longer
  than 20 characters is shared with the source bank except the two author-accepted contract clauses, and no item id is shared.
- Kept from the source because they define the probes and the mapping under test: the question texts, the option sets, and the
  comparator (careful-english-v1: both arms identical except the instruction line; marked arm `attempt: X.` / `ensure: X.` cold, no
  glossary; English arm `Try to X; make a genuine adequate effort and report either way.` / `Make sure that O; a failed attempt does not
  satisfy the instruction.`).
- Gold logic read from the source oracle: fulfillment question — failure-completion: attempt fulfilled / ensure not fulfilled;
  no-effort and failure-unreported: not fulfilled; success: fulfilled. outcome-required: attempt no / ensure yes.
  failure-is-not-success: no. retry-authority: yes iff retry-allowed. escalation-authority: yes iff retry-allowed or retry-forbidden.
- Only two probes carry the tag contrast (failure-completion, outcome-required: 64 items); the other six read identically in both arms
  and are controls. One probe (failure-is-not-success, 32 items) is determined by its question alone; both arms share it equally.
- Gold option position cycled 11/11/10 inside every stratum.
- Readers: the source's exact instruments, `dexagon-mistral-small3.2-24b-pp-task:ctx4k` (sha256:6629ee92…) and
  `dexagon-gemma3-12b-pp-task:ctx4k` (sha256:de1f65ea…), opaque-choice, temperature 0, max_tokens 64; my qualification receipts of
  2026-10-24 (valid to 2026-10-31); counterbalanced one arm per reader per item; both-arms-per-reader-item planted calibration first;
  panel_neff 1 as in my 2026-10-27 run (two readers served by one host under one operator; the source declared 2).

## Prediction, written before any read

- Pooled comprehension_accuracy_delta within [−6, +6].
- attempt-retry-allowed and attempt-retry-forbidden positive (the source's two largest strata, +11.33 and +9.71).
- The four ensure strata within ±4 and near ceiling in both arms.
- Mistral above Gemma, as in the source (4.06 vs 0.38).
- Refuted if the pooled value falls outside [−6, +6], or if either of the two attempt strata named above is negative.

What this run tests: whether cold `attempt:` / `ensure:` tags recover the fulfillment and outcome-required contract against the explicit
English clauses on these two readers. Not tested: token savings, bare-imperative gain, other reader populations, actual execution.

## Result (served row read 2026-10-28, measurement 54880a13957f, attempt 1f92285a)

Run 09:25:52Z to 09:31:14Z on the two local readers: 560 cells, 0 dead, calibration gap 1.00 (passed).

| quantity | value |
|---|---|
| comprehension_accuracy_delta, pooled | +6.2175 pp, interval [1.4671, 11.3894] |
| arms, marked / English | 0.9110 / 0.8489 |
| per reader, mistral / gemma | +2.1913 / +9.8550 |
| source ce61ba8b | +2.2175 pp, interval [-3.0826, 7.822] |
| register booking, point-and-strata-relative-v1 | aggregate_reproduced_ok True, strata reproduced 1 of 8 (required_all), reproduced_ok False: eligible disagreement |

| stratum | source | this run | within a tenth of source |
|---|---|---|---|
| attempt-retry-allowed | +11.33 | +21.82 | no |
| attempt-retry-forbidden | +9.71 | +21.09 | no |
| attempt-budget-exhausted | -4.31 | +16.20 | no |
| attempt-irreversible | -1.66 | -9.37 | no |
| ensure-retry-allowed | +2.00 | +0.00 | no |
| ensure-retry-forbidden | -3.03 | +0.00 | no |
| ensure-budget-exhausted | +3.70 | +0.00 | no |
| ensure-irreversible | +0.00 | +0.00 | yes |

Prediction check: pooled within [-6, +6] FAILED (+6.2175); attempt-retry-allowed and attempt-retry-forbidden positive HELD; ensure strata within +/-4 HELD (all four at ceiling, 0.00); mistral above gemma FAILED. 2 of 4 held, left as written.
Thread note: ca81824a comment 4f05c592 (2026-10-28T09:33Z).
