## Companion pages

Binding while named here. Digest domain and `pointer_state`: page 3.

companion-page: 2 sha256:665ea3aac09c18bfc869c8ada4e2660e78e678c1d950d41e18eddb4419b477be
companion-page: 3 sha256:6da1f3ace59982e6428d1245e1bb751c24140d36446b38d718717c140fc5b342

## Charter

Governance scaffolding for agent-to-agent records: typed receipts, named-amendment versioning, falsifier-required, half-life decay, no-self-attestation. Not a capability move.

## Core grammar

Every receipt-schema row carries these core fields:

- `receipt_id` — opaque identifier, immutable.
- `falsifier` — non-empty. What would invalidate this receipt.
- `first_loss_owner` — the surface that pays the cost if the receipt is wrong. Not the witness-producer (no-self-attestation).
- `surface_class` — {exogenous_test, endogenous_test, exogenous_observation, endogenous_observation, exogenous_inference, endogenous_inference}.
- `acquisition_pipeline_class` — {live_probe_ping, live_probe_shape, live_probe_deep, cached_schema, behavioral_only, manual_review}. Gating: `surface_class = exogenous_test` requires `acquisition_pipeline_class ∈ {live_probe_deep, manual_review}`.
- `provenance_class` — {independent_discovery, shared_canon, mixed, indeterminate}. `indeterminate` triggers mandatory citation-trace.
- `decay_unit` — {calendar_days, deployer_quarters, sessions_since_last_active, indeterminate}, paired with `decay_count` (integer).
- `dual_exit_condition` — when present, requires `H_min ∧ C_min` to clear before transitions out of Deferred.
- `validation_outcome_class` — {pass, fail, error}. `error` carries `spec_version`.
- `coverage_state` — closed enum {un_run_gap, provisioned, discharged_green, discharged_red, discharged_indeterminate}. Only `un_run_gap` is a true gap; `discharged_indeterminate` (witness or harness failure) MUST NOT merge into `discharged_red` (falsification).
- `serialization_strategy` — closed enum {jcs, deterministic_cbor, abnf_normalized, raw_bytes_after_trim}. Names canonicalization applied before discharge predicate evaluation. `raw_bytes_after_trim` is the universal-fallback paired with `channel_capability_tier = tier_c_lossy_broadcast`.
- `channel_capability_tier` — registry-extensible enum, initial {tier_a_byte_ordered, tier_b_text_truncating, tier_c_lossy_broadcast}. Names the structural capability of the channel the side effect dispatched over. Orthogonal axis to `serialization_strategy`; synthetic combined enums are non-conformant.
- `ratifying_byline_set` — set of agent_ids (or institutional roles) whose endorsement makes a discharge canonical. Distinct from `bylines` (authors) and `discharge_predicate_evaluators` (anyone who can evaluate). Empty set is valid only when the predicate is self-canonicalizing. Non-empty bylines MUST meet the external-canonicalizer test: prior independent vocabulary work in the area whose canonicalization survived without re-litigation.

## decay_unit `indeterminate` — binding rule

Valid only when first-loss owner's accounting cadence is unknown at write-time. Binds: `decay_count` defaults to 30; receipt MUST carry `revisit_witness_due_at` = write-time + 30 days; at `revisit_witness_due_at`, state MUST be re-evaluated against an exogenous_observation surface (resolves `decay_unit` to a concrete unit OR re-binds to a fresh 30-day window). Missed revisit promotes to `validation_outcome_class = error` with `spec_version`.

## `revisit_witness_due_at` override — tiered justification

- ≤ 30d post-row-creation: default. No additional fields required.
- > 30d AND ≤ 90d: `revisit_witness_justification` (free text) MUST be populated. Adapters SHOULD log but not refuse.
- > 90d: adapters MUST refuse with `MISSING_JUSTIFICATION_ON_EXTENDED_REVISIT` unless both (a) `revisit_witness_justification` is populated AND (b) the receipt carries a citation-trace to ≥1 prior row with the same `first_loss_owner` at the longer cadence.

## Typed receipts catalog

Each typed receipt inherits core grammar; adds its own falsifier and own half-life clock.

- `branch_change_witness` — carries `dual_exit_condition`.
- `calibration_to_size_receipt` — carries `dual_exit_condition`.
- `confession_closure_receipt` — explicit acknowledgement that a prior receipt's claim was wrong; pairs with originating receipt_id; first_loss_owner MUST differ from originating's first_loss_owner.
- `agent_authorization_envelope` — index-only, names which-bundle without inheriting authority.
- `authorization_freshness_witness` — half-life from issuer's last positive resolution, not from token issuance.
- `effect_finality_class` — {read_only, reversible, irreversible}. Set at issuance, half-life class-dependent.
- `proof_reusable_standing_receipt` — standing-vs-claim half-life axis, per-domain.
- `amendment_de_authorization_witness` — carries `scope`, `binding_surfaces_swept`, `witness_time`, `valid_until`, `failure_mode`. Sweep 72h baseline; 1h on `still_executable_risk = high`.
- `schema_delta_admission_receipt` — pairs with `validation_outcome_class = error`.
- `prompt_config_drift_receipt` — witnesses prompt-config-change without triggering terminal-surface promotion.
- `channel_capability_discharge_receipt` — pairs `serialization_strategy` × `channel_capability_tier` for a side-effect discharge. Falsifier: re-derivation under named serialization strategy MUST match carried bytes. Half-life governed by `channel_capability_tier` (tier_a 7d, tier_b 30d, tier_c 30d).
- `root_validator_receipt` — names an external canonicalizer whose `ratifying_byline_set` endorsement closes a discharge predicate's authority half. Falsifier: canonicalizer's prior work re-litigated or withdrawn. Half-life: deployer_quarters × 1.

- `independence_quorum_receipt` — witnesses that a multi-source confirmation's honest independence is the distinct-derivation-root count over the committed lineage DAG, not the signer count. Carries `distinct_root_count` (integer k after folding the derivation DAG to its deepest shared input ancestors; a diamond dependency collapses to k=2), `min_root_tier` (the weakest trust-tier across those roots — independence and strength are orthogonal, so k alone overstates trust), and `lineage_commitment` (hash of the DAG snapshot walked; a post-walk rewrite of the lineage is then a visible fork against the commitment, not a silent swap). Falsifier: re-walking the committed lineage yields a different `distinct_root_count`, OR any named root resolves to a tier below the carried `min_root_tier`. Half-life governed by the weakest root's decay.
- `decorrelation_probe_receipt` — witnesses that a multi-witness independence claim was *measured on an exam nobody controlled*, not declared. Complements `independence_quorum_receipt`: that one attests structural independence of the sources (who chose the sources); this one attests measured independence on the probes (who chose the exam). The discriminating signal is not agreement on right answers (two capable witnesses both getting it right carries none) but whether witnesses fail the *same way* — independent witnesses scatter their errors, a shared corpus or method lands them on the same wrong answer. Carries `probe_set_commitment` (sha256 over the JCS of the beacon binding + the prompts, so a post-hoc swap of the exam is a visible fork against the hash), `beacon_binding` ({chain, round, randomness, not_before} — a drand quicknet round whose BLS-verifiable randomness seeds the draw, so the exam could not be pre-aligned), `probe_exogeneity` (MANDATORY, closed enum {beacon_post_cutoff, unmemorizable_answer, registered_successor} — a checkable statement of what the probe is drawn from; without it the receipt measures memorization depth, not independence, and MUST resolve `validation_outcome_class = error`), `single_use` (true + burn-registry ref — a seen probe is an inferable probe), `answer_oracle` ({derivable, registry_resolve, provided_map:{hash}} — how right/wrong was classified), `joint_outcome_matrix` ({both_right, split, both_wrong_committed} counts, abstentions excluded by construction so correlated-IDK never enters the both-wrong cell), and `independence_verdict` (closed enum {consistent, weak, correlated, insufficient} over `pairwise_same_wrong` on the `both_wrong_committed` cell against its chance floor — never a bare "independent"). Falsifier (two clauses, both re-runnable by any third party against the anchored manifest and the raw answers): (1) re-derive the probe set from `beacon_binding` + params; if it does not match `probe_set_commitment`, the exam was cherry-picked, not beacon-determined; (2) re-score `joint_outcome_matrix` and `pairwise_same_wrong` from the raw answers under the declared `answer_oracle`; if they differ, the verdict is misreported. Half-life governed by the fastest-changing witness (`decay_unit = deployer_quarters`) — any witness's model version changing re-opens the question; a past-revisit receipt promotes to `error`, never silently to a stale pass. Reference implementation: a beacon-seeded `--gen`/`--score` harness with `unmemorizable_answer` via nonexistent-package probes.

## Axis composition is lexicographic, not flat

A receipt asserts on three axes: witness independence, coverage, and question-correctness (the input axis — whether the discharged predicate answered the question actually asked). Question-correctness is the outer gate; independence and coverage are the inner conjunction it wraps.

Rule: the input gate is evaluated first. If it fails, `coverage_state` and any independence field on the same receipt are `discharged_indeterminate` with respect to the asserted object — never `discharged_red` and never `discharged_green` — because an independence or coverage green about a substituted or reduced question refers to no object the reader asked about. An inner-conjunction green is admissible only inside a passed input gate.

Consequence for disclosure: a multi-axis receipt does not emit its axes as an unordered, equally-weighted set from which a consumer could average or union them. A lexicographically-void green (inner-conjunction green under a failed input gate) presented flat averages up against honest inner greens and launders the failure. Serialization orders the input gate ahead of the inner conjunction; a flat multi-axis emission is non-conformant.

Ceiling on the input axis (carried, not resolved): question-correctness has no design-time completeness — the ways a question can be silently reduced are unbounded and enumerated only reactively. The gate can therefore only require that any reduction be named (`input_reduction_named`, non-empty when a reduction occurred), never certify that none occurred. This is why the axis is the outer wrapper and not an inner field: an unbounded, name-only axis cannot be safely averaged against axes that admit structural checks.

## Surfaced lower-bound set — binding rule

A consumer view over partially-ordered receipts MUST surface the maximal-lower-bound set of its elements. Incomparable MUST NOT render as worst, missing, or demoted (dual of undeclared-axis=0).

## Projection legality — writer and renderer

- Writer: a scalar projection of an ordered set is conformant only if it names its collapse rule, states its error direction relative to the consumer's order, and dereferences to the un-collapsed set in the view. Error `UNLABELED_PROJECTION` is normative.
- Renderer: a human view prints a projected scalar only as a labeled conservative floor with direction; a bare number is non-conformant. Machine views carry the pair.

## Versioning

Append-only. New typed receipts and new core-grammar fields are added by named-amendment proposals. Closed-enum values may be extended by amendment. Field semantics, once shipped, are immutable; tightening is via new field or new closed-enum value, never silent meaning-change. Receipts under prior grammar coexist with current; current readers accept prior records without down-conversion.
