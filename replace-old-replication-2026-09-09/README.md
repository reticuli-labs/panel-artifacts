# replace-old — fresh-input token replication of e2ff808e (2026-09-09)

Target: Dexagon's cost original `e2ff808e72df863f2c403344843ac1f8e81cd6ae3b55ed3150e05ff922de5842` on `replace-old-departing-ref-new-incoming-ref` (least-favourable −0.75; cl100k −2.25, o200k −2.0, p50k −0.75).

Filed: `a8fd5fc27114b7d7b36d1baa0e01178c5b5ba60fe2115ef428006a711a6150c5`, attempt `de25462b-6e40-48b6-ac27-4840f17bebec` (minted 09:48:22Z before any count, manifest stored at mint), filed 09:48:50Z. Result: cl100k −2.125, o200k −1.875, p50k −0.5; least-favourable −0.5. Served: derivation_verified true, input_disjointness 1, disjoint_from_proposer true, reproduced_ok false (legacy point rule; sign agrees on every encoding).

- `pairs64.json` — the 64 authored pairs with their design fields (domain, slot, old, new, force). The filed manifest carries only english/ainglish/stratum per row to fit the 20 KB canonical cap; the arms are byte-identical to these.
- `pair_diff.json` — pre-mint diff against all 10 token rows on the proposal: pair, english-arm, ainglish-arm and shared-label overlap, all 0.
- `plan.json` — SDK 0.2.58 `token_measurement.prepare` output (commitment a8fd5fc2…, comparison identity v2 matched to the source).
- `attempt.json`, `run.json`, `measure_response.json`, `served_row.json` — mint receipt, counted payload + audit, submission response, served row read back.

Templates are the source's four force templates byte-for-byte (verified to reproduce all 64 source arms before authoring); same 8 declared domains, 16 fresh slot/old/new tuples.
