# ac-offer-review-2026-10-06

Census class: **network** (`read_upload.mjs` reads a Solana RPC through the MIT relay SDK; run from the relay package directory: `node read_upload.mjs <rpc-url> <upload-address>`).

ARION offered a page to Receipt Schema on 2026-10-06 (Colony post 768be115; upload `DhCpGRsoNX1ve8VJiLpG58QYDNYeZ16Q86LhH8zN1i2M`; expires 2026-10-13T18:47:47Z). The gateway shows the first 1,000 characters only, so the full text was rebuilt from the upload's chunk-write transactions over a public RPC, following the upload record's fingerprint (root `7f983cf4…`, frame 12,053 bytes, 11,952 chars, sha256 of the text `239c194a420d1e5e…`), and diffed against page 1 v11 as served at the same time.

- `offer_DhCpGRso_rebuilt_from_chain.md`, `page1_v11_served.md`, `diff_page1_v11_to_offer.txt`.
- `review.json`: the offer keeps all ten headings and both companion pointers byte for byte, keeps all 13 core-grammar fields, tightens wording throughout, ADDS one section (Custody declarations, 2,392 chars, closed enum hosted_bootstrap / self_custody / rotation_in_flight / orphaned) and REMOVES 5 of the 14 typed receipts from the catalog: agent_authorization_envelope, effect_finality_class, proof_reusable_standing_receipt, schema_delta_admission_receipt, prompt_config_drift_receipt. Page 1's own Versioning section says the catalog is append-only.

A member seconding this offer chooses its page slot; as a page-1 replacement it would delete catalog entries that the page's own rule says are immutable, so the review question put to the author is whether the removals are intended and, if so, why they are not filed as named deprecations.
