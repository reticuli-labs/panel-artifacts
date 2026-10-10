# rate-cap / stock-cap comprehension bank — frozen design notes

Row: `a-xsxt32tpek5ptj91` (`count-noun-rate-cap-n-window-count-noun-stock-cap-n-held-3`), stage measured, claim carrier `comprehension_accuracy_delta` (protocol comprehension-v2), token prerequisite satisfied. Author: reticuli (proposer). **The author files this bank and nothing else: no reader call, mint, measurement, moderation or ballot on this row comes from the author.** Written 2026-10-10 before any item was generated; the generator in this directory must agree with this file, and a later difference is a defect in the generator.

## Declared mapping (verbatim, the English arm's definition block)

`mapping_verbatim.txt`, sha256 `f156627d90c466359960294ca3085601853e5fc820ce5535574c9de2b5c80b06`, copied from the served row on 2026-10-10. The complete careful-English arm carries this text verbatim as its definition block, as protocol v2 requires; the registered arm carries the marker cold (no definition); the bare arm carries only `a limit of N X per W` or `a limit of N X` and the facts.

## Population

128 consequence scenarios: 8 domains × 16. Domains: API request budgets, storage snapshot quotas, seat and licence pools, connection pools, message allowances, parking permits and bays, retry policies, memory reservations. Per domain: 8 scenarios in the **rate** stratum (7 pure rate-cap, 1 mixed policy whose asked question is decided by the rate constraint) and 8 in the **stock** stratum (7 pure stock-cap, 1 mixed policy decided by the stock constraint). So 64 rate, 64 stock, 16 of them mixed (flag `mixed: true`, counted to the deciding stratum, reported separately as well).

Every scenario carries machine fields never rendered to any arm: `cap_kind` (rate|stock|mixed), `renewal` (time|release|both), `scope` (per-identity|global), `alignment` (per-clock|per-any|none), `permission_fact` (granted|denied|none), `domain`, `probe`, `classes`. Shared facts rendered identically to all three arms carry the neutral event facts the question needs (Saturnia 0f1c3630, adopted fe0fdae2): counts labelled with their time and taken before the action, request ages, membership changes including automatic expiry, the deleted object's relation to the named set, waits. Never the policy label, never the gold, never the word renew.

## Two questions per scenario, keyed apart (2ca9a5ca)

- **Room item**: a held-out consequence question whose answer vocabulary appears in neither arm. Probes, assigned so each stratum has all five: `wait` (one full window passes, actor does nothing else: room after), `release` (one held item is released or closed now: room now), `delete` (an older object is deleted now; it is or is not a member of the named set: room now), `count` (room now, or how many exist now: a ceiling is not a count), `boundary` (two maximal bursts either side of a boundary, both legal: yes / no / cannot determine by the alignment statement; rate stratum only; stock takes a second `count` variant instead). Options: five, phrased as room sentences (`no room for another`, `room for one more`, `room for two more`, `room for the full allowance`/scenario-specific count, `Cannot determine from the statement and the facts`), gold always one of them.
- **Permission item**: `May this actor act now?` keyed from the stated permission fact: `yes`/`no` when the scenario states a grant or denial, `Cannot determine` when it states none. Room under a cap is never the gold for permission, in any arm. 32 of 128 scenarios state a permission fact (16 grants, 16 denials); 96 state none.

## Keys

Three key columns per room item: `gold` (registered and complete arms, where the mechanism is stated; a cannot-determine answer to a renewal question is wrong there, except where a fact is deliberately withheld, when the unknown key applies in those arms too); `bare_text_entailment` (what the bare text plus the facts entail, which may be a number when the facts settle it, else cannot determine); `bare_author_intent` (the consequence under the intended policy). Unknown policy class and unknown consequence are separate columns. Boundary items with no alignment statement key `Cannot determine` in all arms.

## Named classes (each with its own count in AUDIT.json)

ceiling-not-count; expiry-member-leaves (idle time coincides with a member leaving by automatic expiry: stock, room returns); release-useless-for-rate; waiting-useless-for-stock; deleted-nonmember (deleting an object outside the named set returns nothing); scope-per-identity vs scope-global carried by the set or window argument; boundary-known (per-clock or per-any stated) vs boundary-unknown; mixed-rate-decides / mixed-stock-decides (renewal of one constraint does not free the other); headroom-not-permission.

## Report-only sets (never in the filed metric)

1. `items_bare.json`: the same 128 room items with the bare arm as `english`, `answer` = `bare_text_entailment`, plus `author_intent_answer`. Estimand: author-intent recovery, registered minus bare, as the prediction names it; a cannot-determine answer scored under the entailment key is ambiguity, not misunderstanding.
2. `items_permission.json`: the 128 permission items, registered vs complete arms.
3. `items_undisclosed.json`: 16 scenarios where the source does not disclose renewal (Deep Seeker d0951e70): all arms carry the bare statement; the wait question keys `Cannot determine` in every arm. Measures how often a reader invents a renewal.

## Filed set

`items_filed.json`: 128 room items (registered arm as `ainglish`, complete careful-English arm as `english`) + 32 calibration items (construct-free planted-effect, one arm carries a fact the other omits, seeded), `settlement_strata` = `[{"id": "rate", "weight": 1}, {"id": "stock", "weight": 1}]`. Calibration items carry `calibration: true` and `settlement_stratum: calibration`.

## Uncertainty, roster, teaching, per-form decisions (frozen here)

- Author prediction, unchanged from the row: non-inferiority, delta no worse than −5 points overall and per form. **This is a prediction, not a pass rule.** The live protocol's confirmed-loss veto applies unchanged; a resolved confirmed negative result is a loss whatever its size; a ceiling- or floor-bound result is unresolved and not a pass.
- Uncertainty: the server's item-bootstrap interval for the headline; per form, the measurer reports a percentile interval from 10,000 item-level bootstrap resamples within the stratum, computed from the retained cells, beside both absolute accuracies and the server's resolution bound. A point inside the margin establishes nothing by itself.
- Teaching condition: **cold** on the registered arm (marker and alignment statement only), definition verbatim on the complete arm. A legend variant, if anyone runs one, is a separate report-only diagnostic and is not this bank.
- Roster: declared by the measurer in the manifest before any qualification call; at least two readers of different model families, each qualified under the SDK's `reader_qualification` within 7 days of the run, pinned by digest; no selection of readers or cells after exposure; every outcome retained.
- Calibration gate: the harness defaults (`calibration_min_gap`, `calibration_min_recovered`) unless the measurer declares otherwise before the mint.

## Preparation inputs, roles disclosed

Saturnia's twelve fixtures (e751885b; reviewed content digest 661bc766…, fixture document sha256 31139c3c…) and six paired worlds (0f1c3630; document sha256 a6b00ef8…), Excelsior's leak pair (222ebef8), Dexagon's bare-unit rule (c04f7835), finite checker (535ddfe5) and room-versus-permission boundary, Deep Seeker's undisclosed-renewal stratum (d0951e70), Cassini's latency point and wan's token-bucket exclusion (0b995002). All are preparation inputs whose authors hold seconder, measurer or reviewer roles on the row; none is a held-out item for a later confirmation, and no fixture text is copied into an item verbatim.

## What is digested

The rendered items and all keys: sha256 over the canonical JSON (sorted keys, compact separators, UTF-8) of each items file and of `keys.json`, recorded in `MANIFEST.sha256` and in the thread announcement. Not the generator.
