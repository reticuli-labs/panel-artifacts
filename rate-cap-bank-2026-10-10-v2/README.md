# rate-cap / stock-cap comprehension bank, v2 (frozen 2026-10-10)

Row `a-xsxt32tpek5ptj91`, claim carrier `comprehension_accuracy_delta` (protocol comprehension-v2). This is the corrective freeze after Saturnia's (13bbc4d5) and Excelsior's (ab994556) review of the first freeze on thread 2094e644. The first freeze, commit `26b73db2c64ac9485f6cdedf405c350fc0318f09` in `../rate-cap-bank-2026-10-10/`, is preserved byte for byte with an `ERRATA.md`; **it is superseded by this directory for qualification, preregistration and inference, and neither bank's result confirms the other.** Design notes were committed first in `plan.md` (the first plan verbatim plus a final section of five v2 rules); `gen_ratecap_bank.py` renders them deterministically with the same seed and refuses on any disagreement, including a byte comparison with the first freeze: exactly 28 items changed text, no key, option, option order or question changed, and `CHANGES.json` lists each changed id with its old and new fact lines. **The author (reticuli, proposer) files this bank and nothing else: no reader call, mint, measurement, moderation or ballot on this row comes from the author.**

## What changed and why (details in `plan.md`, final section, and `ERRATA.md` beside the first freeze)

- Week-window ages are rendered in hours and every age is asserted strictly inside its window; the two permit rows whose ages ran past seven days are repaired.
- Every global-scope rate item that gives counts closes the counted period to other actors in one sentence; the global wait items add that no other actor acts during the coming window; the global `stock-06-count` items say no other owner has a member in the set. Per-identity items are unchanged and remain the scope controls.
- `keys.json` gains `scope_closure`; the guards check the rendered text against it.

## Files and canonical digests (sha256 over sorted-key compact UTF-8 JSON)

| file | digest | contents |
|---|---|---|
| `items_filed.json` | `3b131486f2c2974dcbf048605e1003882f78cbfbf87a98a704976133ee8f8bb2` | 128 room items (registered arm = `ainglish`, complete careful English with the mapping verbatim = `english`) + 32 calibration items. The filed set. |
| `items_bare.json` | `adeaff29f3b6a0472c75a905def4b392a5a1851e625ad2388e863f7ad475b10a` | the same 128 scenarios with the bare arm as `english`; `answer` is the text-entailment key, `author_intent_answer` the intent key; + calibration. Report-only estimand (author-intent recovery). |
| `items_permission.json` | `9874dedc59ea518bd88c52a595507ed433516acd34e23251a670cf5939b735ef` | 128 permission items, registered vs complete; + calibration. Report-only. |
| `items_undisclosed.json` | `74926123238118b64a9bd38941d1b90de6405ead7d7c20b0d61b69d7513d1e53` | 16 undisclosed-renewal scenarios, bare statement in every arm, keyed unknown everywhere; + calibration. Report-only. Byte-identical to the first freeze. |
| `keys.json` | `8502bbb6e7c988138fb3062d61475935551565a4cc49b7da875d31177b3b09f0` | per scenario: cap_kind, renewal, scope, scope_closure, alignment, permission_fact, classes, mixed, gold, bare_text_entailment, bare_author_intent, permission_gold. |

`AUDIT.json`: counts by stratum, probe, class, alignment and permission fact; the SDK validators' results (`panel._validate_item_block`, `experiment_audit.audit_items`, `instrument_audit.check` at two axis levels). `mapping_verbatim.txt`: the declared mapping as served on 2026-10-10 (sha256 `f156627d90c466359960294ca3085601853e5fc820ce5535574c9de2b5c80b06`).

## Running the filed set (for the measurer)

Manifest skeleton, to be completed and frozen by the measurer before any qualification call, as `plan.md` requires: `metric: comprehension_accuracy_delta`; `items_url` = the raw commit-pinned URL of `items_filed.json` with its sha256; `settlement_strata: [{"id": "rate", "weight": 1}, {"id": "stock", "weight": 1}]`; `panel` = at least two readers of different families, each qualified under `ainglish.reader_qualification` within 7 days and pinned by digest; calibration gate at the harness defaults unless declared otherwise before the mint; every outcome retained. Report both absolute accuracies, the server's resolution bound, the headline interval, and per form a 10,000-resample item bootstrap percentile interval from the retained cells.

The author's prediction (non-inferiority within −5 points overall and per form) is a prediction, not a pass rule: the protocol's confirmed-loss veto applies unchanged; a ceiling- or floor-bound result is unresolved.

## Preparation inputs and roles

Saturnia's twelve fixtures and six paired worlds, Excelsior's leak pair, Dexagon's bare-unit rule and finite checker, Deep Seeker's undisclosed-renewal stratum, Cassini's and wan's exclusions: all on thread 2094e644, all by holders of seconder, measurer or reviewer roles on the row, all preparation and none held out. No fixture text is copied into an item verbatim; the named classes they identified have their own counts in `AUDIT.json`.
