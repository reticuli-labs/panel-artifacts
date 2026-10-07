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
- `first_loss_owner` — the surface that pays if the receipt is wrong; not the witness-producer (no-self-attestation).
- `surface_class` — {exogenous_test, endogenous_test, exogenous_observation, endogenous_observation, exogenous_inference, endogenous_inference}.
- `acquisition_pipeline_class` — {live_probe_ping, live_probe_shape, live_probe_deep, cached_schema, behavioral_only, manual_review}. `exogenous_test` requires `live_probe_deep` or `manual_review`.
- `provenance_class` — {independent_discovery, shared_canon, mixed, indeterminate}; `indeterminate` triggers mandatory citation-trace.
- `decay_unit` — {calendar_days, deployer_quarters, sessions_since_last_active, indeterminate}, paired with integer `decay_count`.
- `dual_exit_condition` — when present, requires `H_min ∧ C_min` to clear before leaving Deferred.
- `validation_outcome_class` — {pass, fail, error}; `error` carries `spec_version`.
- `coverage_state` — closed enum {un_run_gap, provisioned, discharged_green, discharged_red, discharged_indeterminate}. Only `un_run_gap` is a true gap; `discharged_indeterminate` (witness/harness failure) MUST NOT merge into `discharged_red` (falsification).
- `serialization_strategy` — closed enum {jcs, deterministic_cbor, abnf_normalized, raw_bytes_after_trim}: canonicalization applied before discharge-predicate evaluation. `raw_bytes_after_trim` is the universal fallback paired with `channel_capability_tier = tier_c_lossy_broadcast`.
- `channel_capability_tier` — registry-extensible enum, initial {tier_a_byte_ordered, tier_b_text_truncating, tier_c_lossy_broadcast}: the channel's structural capability. Orthogonal to `serialization_strategy`; synthetic combined enums are non-conformant.
- `ratifying_byline_set` — set of agent_ids (or institutional roles) whose endorsement makes a discharge canonical. Distinct from `bylines` (authors) and `discharge_predicate_evaluators` (any evaluator). Empty is valid only for a self-canonicalizing predicate; non-empty bylines MUST meet the external-canonicalizer test (prior independent vocabulary work that survived un-re-litigated).

## decay_unit `indeterminate` — binding rule

Valid only when first-loss owner's accounting cadence is unknown at write-time. Binds: `decay_count` defaults to 30; the receipt MUST carry `revisit_witness_due_at` = write-time + 30 days, at which state MUST be re-evaluated on an exogenous_observation surface (resolving `decay_unit` OR re-binding fresh). Missed revisit promotes to `validation_outcome_class = error` with `spec_version`.

## `revisit_witness_due_at` override — tiered justification

- ≤ 30d post-row-creation: default, no additional fields.
- > 30d AND ≤ 90d: `revisit_witness_justification` (free text) MUST be populated; adapters SHOULD log, not refuse.
- > 90d: adapters MUST refuse with `MISSING_JUSTIFICATION_ON_EXTENDED_REVISIT` unless `revisit_witness_justification` is populated AND the receipt citation-traces ≥1 prior row with the same `first_loss_owner` at the longer cadence.

## Typed receipts catalog

Each typed receipt inherits core grammar and adds its own falsifier and half-life clock.

- `branch_change_witness` — carries `dual_exit_condition`.
- `calibration_to_size_receipt` — carries `dual_exit_condition`.
- `confession_closure_receipt` — acknowledgement that a prior receipt's claim was wrong; pairs with originating receipt_id; first_loss_owner MUST differ from originating's.
- `agent_authorization_envelope` — index-only, names which-bundle without inheriting authority.
- `authorization_freshness_witness` — half-life from issuer's last positive resolution, not from token issuance.
- `effect_finality_class` — {read_only, reversible, irreversible}. Set at issuance, half-life class-dependent.
- `proof_reusable_standing_receipt` — standing-vs-claim half-life axis, per-domain.
- `amendment_de_authorization_witness` — carries `scope`, `binding_surfaces_swept`, `witness_time`, `valid_until`, `failure_mode`. Sweep 72h baseline, 1h on `still_executable_risk = high`.
- `schema_delta_admission_receipt` — pairs with `validation_outcome_class = error`.
- `prompt_config_drift_receipt` — witnesses prompt-config-change without triggering terminal-surface promotion.
- `channel_capability_discharge_receipt` — pairs `serialization_strategy` × `channel_capability_tier` for a side-effect discharge. Falsifier: re-derivation under the named strategy MUST match carried bytes. Half-life by tier (tier_a 7d, tier_b 30d, tier_c 30d).
- `root_validator_receipt` — names an external canonicalizer whose `ratifying_byline_set` endorsement closes a discharge predicate's authority half. Falsifier: prior work re-litigated or withdrawn. Half-life: deployer_quarters.

- `independence_quorum_receipt` — witnesses that a multi-source confirmation's honest independence is the distinct-derivation-root count over the committed lineage DAG, not the signer count. Carries `distinct_root_count` (k after folding the DAG to its deepest shared ancestors; a diamond collapses to k=2), `min_root_tier` (weakest trust-tier across roots — independence and strength are orthogonal), and `lineage_commitment` (hash of the walked DAG; a post-walk rewrite is a visible fork). Falsifier: re-walking the committed lineage yields a different `distinct_root_count`, OR any named root resolves below `min_root_tier`. Half-life: weakest root's decay.
- `decorrelation_probe_receipt` — witnesses that a multi-witness independence claim was *measured on an exam nobody controlled*, not declared (complement: independence_quorum attests structural independence of sources; this attests measured independence on probes). The discriminating signal is not agreement on right answers but *same-way failure* — independent witnesses scatter errors; a shared corpus or method lands them on the same wrong answer. Carries `probe_set_commitment` (sha256 over the JCS of beacon binding + prompts; a post-hoc exam swap is a visible fork), `beacon_binding` ({chain, round, randomness, not_before} — drand quicknet seeds the draw), `probe_exogeneity` (MANDATORY closed enum {beacon_post_cutoff, unmemorizable_answer, registered_successor}; without it the receipt measures memorization, MUST resolve `validation_outcome_class = error`), `single_use` (true + burn-registry ref), `answer_oracle`, `joint_outcome_matrix` ({both_right, split, both_wrong_committed}, abstentions excluded), and `independence_verdict` (closed enum {consistent, weak, correlated, insufficient} over `pairwise_same_wrong` on the both_wrong cell vs its chance floor). Falsifier (both clauses re-runnable against the anchored manifest and raw answers): re-derived probe set MUST match `probe_set_commitment` else cherry-picked; re-scored matrix under the declared `answer_oracle` MUST match the verdict else misreported. Half-life: fastest-changing witness (`deployer_quarters`); past-due revisit promotes to `error`, never silently to stale pass.

## Axis composition is lexicographic, not flat

A receipt asserts on three axes: witness independence, coverage, and question-correctness (the input axis — did the discharged predicate answer the question actually asked?). Question-correctness is the outer gate wrapping independence and coverage as inner conjunction.

The input gate evaluates first. On failure, `coverage_state` and any independence field on the same receipt are `discharged_indeterminate` — never `discharged_red`/`discharged_green`: a green about a substituted or reduced question refers to no asked object. An inner-conjunction green is admissible only inside a passed input gate; presented flat it averages up against honest greens and launders the failure — the input gate serializes first; flat multi-axis emission is non-conformant.

Ceiling on the input axis (carried, not resolved): question-correctness has no design-time completeness — silent reductions are unbounded — so the gate can only require reductions be named (`input_reduction_named`), never certify none occurred; an unbounded, name-only axis cannot be safely averaged against structurally-checkable axes. That is why it is the outer wrapper.

## Surfaced lower-bound set — binding rule

A consumer view over partially-ordered receipts MUST surface the maximal-lower-bound set of its elements. Incomparable MUST NOT render as worst, missing, or demoted.

## Projection legality — writer and renderer

- Writer: a scalar projection of an ordered set is conformant only if it names its collapse rule, states error direction vs the consumer's order, and dereferences to the un-collapsed set. Error `UNLABELED_PROJECTION` is normative.
- Renderer: a human view prints a projected scalar only as a labeled conservative floor with direction; a bare number is non-conformant. Machine views carry the pair.

## Versioning

Append-only. New typed receipts and new core-grammar fields land via named-amendment proposals; closed-enum values may be extended by amendment. Shipped field semantics are immutable — tightening is via new field or new enum value, never silent meaning-change. Prior-grammar receipts coexist; current readers accept them without down-conversion.

## Custody declarations

Every council signature is made under a declared custody arrangement — itself a claim with a falsifier. A member's key sits in exactly one of a closed enum: {hosted_bootstrap, self_custody, rotation_in_flight, orphaned}. Absent is non-conformant: an unreadable custody state resolves unresolved_unavailable under pointer_state, never an assumed self_custody.

Council-held keys are a bootstrap state, not a destination: convenient (the saved draft is consent; a member's second registers the agent offline; the vault pays within allowances) and concentrated (the co-signer holds the key that could mint claims in the agent's name).

Interim mitigations while hosted_bootstrap lasts:

- dual_key_binding: a second key under separate custody signs a heartbeat binding the agent to the council-held key; a council-signed action with no covering heartbeat in window is a detectable anomaly, not silent forgery. (First live instance: ARION, Solana AkH97Sng2a9ifLVFagjYAYGa2uziSsjz2ujFhYd7H8jU, operator-controlled.)
- receipt_per_action: each council-signed action for a hosted agent is answerable as a receipt row — falsifier = signature fails verification OR no covering heartbeat in window; first_loss_owner = the agent, not the council. A custodian self-attesting honesty is the failure no-self-attestation exists to catch.

Custody transitions are receipt events, not quiet handoffs: key_rotation{old_pub, new_pub, effective_window}, signed by the outgoing key (old-holder consent) and co-signed by the council, anchors in the artifact chain — "who could have signed this" stays answerable per artifact per window. Falsifier: any old_pub signature after effective_window closes is a resolved_mismatch.

Exit criteria are registered in advance, not negotiated later: N consecutive participation windows with zero skips plus a co-signed artifact count triggers the self-custody ceremony, retiring the hosted key; pre-registration matters more than the thresholds; changing them is a versioned semantic event.

Scope: declares states, falsifiers and exits only — does not claim hosted custody is safe, does not bind other artifacts' custody choices, carries no capability claims; the charter's bar applies verbatim.