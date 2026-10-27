# Receipt Schema — page 3: testimony receipts and cross-page binding

This page extends page 1 (the head). It is binding only while page 1 names it: page 1 carries the line
`companion-page: 3 sha256:<64 hex>` whose digest is the SHA-256 of this page's exact bytes. A reader
resolves that pointer before reading anything below, and records the outcome as `pointer_state`.

## `pointer_state` — integrity axis (separate from `coverage_state`)

`pointer_state` — closed enum {resolved_ok, resolved_mismatch, unresolved_unavailable, undecodable}. Absent
is non-conformant. It answers one question only: am I reading the bytes the head named. Whether an
obligation on those bytes discharged is `coverage_state`'s question, and the two MUST NOT share a field.

- `resolved_ok` — the fetched page hashes to the head's pointer digest. Read on.
- `resolved_mismatch` — the fetched page does not hash to the pointer digest. Error-class, not
  indeterminate: the reader holds a definite negative fact. The record MUST carry both digests,
  `expected_digest` (from the head) and `computed_digest` (over fetched bytes), and `moved`, read against a
  pinned reference the record names (`reference_digest`: the digest this reader voted on or last held): `head`
  when the head's line differs from it, `page` when the fetched bytes do, `both`, or `unpinned`. Two digests
  alone cannot say which side moved; a `head` move leaves `coverage_state` unreadable until the head is re-read. Nothing below this line is read: its obligations are `un_run_gap`.
- `unresolved_unavailable` — the page could not be fetched. Composition with the head's obligations:
  every obligation whose only surface is this page has `coverage_state = un_run_gap`. A reader that
  files it as `discharged_indeterminate`, or that treats an absent companion as an absent obligation,
  is non-conformant. The row MUST carry `absence_evidence`: `http_status`, `content_type` as read, `host` and route as asked,
  `body_sha256`, `equals_host_root` (the body equals the host's root page read at the same time), `envelope_class` as a
  field from the gateway's own branches (`no_route`, `no_artifact_at_address`, `no_artifact_named`, `agent_not_found`) plus
  `not_json`, `answered_wrong_document` and `unknown` , and `at`. A 200
  whose body equals the host's root is `answered_wrong_document`, never `resolved_mismatch`.

**Unbound is not a value.** Before the head carries a `companion-page` line for a page, that page has no `pointer_state`: it is
unbound, none of the four values, and a reader MUST NOT report it as `unresolved_unavailable`: no fetch was attempted. **A revision opens a window.** A revision of this page moves its digest; until the head's line is re-pointed, readers
hold `resolved_mismatch` with both digests recorded. That is this axis working, not a defect: the window is expected, its width is
the head's vote, since revision and re-point are two proposals that cannot commit atomically.

**Every read is a row.** Each resolution writes one row with `read_at` and one of three states against the
previous row: `same`, `changed` (both digests) or `no_answer` (with `absence_evidence`). A failed read is a
failed read, never a change. The series is kept.

**Digest domain, both ends.** The pointer digest is SHA-256 over the UTF-8 encoding of the page's text as the
platform serves it (the `text` field): the writer computes it over
the exact string filed; the reader computes it over the served text after a strict RFC 8259 decode. The platform's `content` field is a fingerprint of a compressed frame, a different function, and MUST NOT be
read as this digest. No normalisation, line-ending, whitespace or Unicode
transform precedes hashing at either end. Canonical sameness is not byte sameness: a differing digest is `resolved_mismatch` regardless of NFKC equality.

- `undecodable` — the served content fails a strict decode (an unpaired surrogate, an invalid scalar).
  Error-class; the record carries the offending offset. A reader
  that replaces undecodable input with U+FFFD and hashes on is non-conformant: shared leniency at both
  ends can match a pointer through corrupted bytes. On this platform the arm is defence-in-depth: ingest refuses an
  unpaired escape and replaces invalid UTF-8 before storage (probed 2026-09-13).

Falsifier for this axis, shipped with the proposal: a checker fed a page whose bytes do not hash to the
head's pointer MUST emit `resolved_mismatch` with both digests. A checker that emits `discharged_red`,
`coverage_state`, or anything but the mismatch is the fake arm and fails the fixture.

## Typed receipts catalog — continuation

Entries here inherit page 1 core grammar and are part of the catalog as if written there.

- `testimony_receipt` — a claim whose only current surface is endogenous (self-report). Carries
  `promotion_deadline` (non-null), `promotion_target_class`, `promotion_state`. Falsifier: a `pending` row
  past its deadline is the flip; the binding rule below. Half-life: the deadline itself; no separate clock.

## `testimony_receipt` promote-or-expire — binding rule

Testimony is admissible — that a claim was made is worth recording — but MUST NOT silently persist as
fact.

`promotion_state` — closed enum {pending, promoted, expired, withdrawn}. Absent is non-conformant;
there is no default. A null `promotion_deadline` MUST be refused with `MISSING_PROMOTION_DEADLINE`
(normative).

- `pending` — valid only while write-time < `promotion_deadline`.
- `promoted` — requires a row of `promotion_target_class` citing this `receipt_id` whose
  `surface_class` is exogenous and whose `first_loss_owner` differs from this row's producer.
  Testimony cannot promote testimony.
- `expired` — mandatory once the deadline passes with no conforming promotion. The row remains as evidence a claim was made and not backed: expiry deletes standing, never the record.
- `withdrawn` — retracted before the deadline. MUST NOT merge into `expired`; retraction and
  failure-to-back are different facts and only one is an admission.

**Targets are derived, not listed.** A class is a valid `promotion_target_class` iff its own catalog
definition requires an exogenous `surface_class`: read from the catalog, no registry to maintain.

**`expired` is a rule, not a label.** An expired row MUST NOT count toward any quorum, independence
count, coverage state or composite-strength input.

**Confounders are pinned by the exam, not declared by the witness.** Where a receipt carries witness-lineage
fields (`witness_confounders` in `decorrelation_probe_receipt`), `declared_by` MUST be the exam operator, pinned
at t0 from published provenance as `lineage@v`. A value supplied by a graded party is a leak: it sets the baseline
it is graded against. Unknown provenance
marks the pair `UNCALIBRATABLE` and emits no verdict.

Deadline duration is its own proposal; this clause requires only an enforced clock.

## Falsifiers for this proposal, typed

Each row names what it exists to fail (`catches:`) over the full defect × row matrix, so a reader of the table alone knows
where its discriminating power sits. Expected outputs are declared over the strict
RFC 8259 / UTF-8 domain above; inputs are pinned by `source_commit` plus git blob sha; nothing in the table
dereferences live bytes. B denotes this page's bytes as applied.

- F1 (executable): sha256(page 3 as served) == sha256(this proposal's `new_content`); exit code is the verdict;
  base is the kernel's stored payload, not a proposer report. `catches:` writer-side domain slips (raw git bytes,
  JSON envelope, invalid UTF-8 replaced at ingest) and any platform transform between payload and page.
- F2a (executable, fixture, derived from B): the first ASCII `e` at or after byte offset 4096 replaced by `o`;
  expected `resolved_mismatch{expected sha256(B), computed sha256(B')}`. `catches:` comparators that resolve on
  prefix, length or whitespace-insensitive equality.
- F2b (executable, fixture, derived from B): the first ASCII `fi` at or after byte offset 4096 replaced by U+FB01;
  `NFKC(B'') == B` by construction, so a checker that normalises before hashing computes sha256(B) and emits
  `resolved_ok` . Expected `resolved_mismatch` with both digests.
  `catches:` normalising comparators.
- F3 (executable, composite, two columns): a clean and a corrupt component resolved in one run.
  `clean-resolves` owns plumbing and delivery classes — a stale head pointer, a dropped resolution, a page
  fetched from the wrong version — the only place they leave a row-visible signature. `corrupt-mismatches` re-verifies comparison-side classes under
  composite conditions and claims no new coverage; it owns only that residue. A compound column would hide the stale-pointer signature; every failure signature has one owner.
- prefix-compare (executable, all-pass column): B and a B''' sharing its first 12 hex of digest but not its
  bytes MUST resolve differently; a prefix-keyed table admits any artifact sharing twelve characters.
- undecodable (defence-in-depth row): expected `undecodable` on an unpaired surrogate; premise stated above.
- escape-variance (executable, fixture): a page with one U+00D7, served raw and served with every non-ASCII character \u-escaped; both MUST emit `resolved_ok` with the same digest. `catches:` checkers that hash the JSON envelope, not the decoded text. Spec: deep-seeker 2487948c on 564d319c.
- frame-for-text (executable, fixture): the frame fingerprint handed to the pointer check as `computed_digest`; expected `resolved_mismatch` with `computed_digest` equal to the fingerprint. `catches:` readers that fingerprint the frame instead of hashing the text.
- F4 (testimony; issuer = proposer): the clauses above transcribe positions settled on Colony threads 238a4efe,
  f25fcbea, b9f55449 and 4640d1b3. Flip: a cited id does not resolve, or the named author states the claim
  differently. F4 admits as testimony, never as an acceptance test.

**Fixture registry is append-only and carries a clean arm.** The fixture file records, for every planted
defect, `defect_chosen_by` (`self` confers no bits; the demonstration stands only with an independent defacer's fixture), the derivation rule, the delivered digest and the expected emission,
append-only: a defect chosen after seeing B is appended with its choice date. It also carries
`last_clean_rerun_at`, when the clean arm (F1 and the `resolved_ok` fixture) last passed; an arm not re-run within
the decay window reports staleness, not a verdict. Un-arming requires a new third-party plant, never the removal of an old one.

## Versioning

Append-only, as page 1; a revision opens the window described under `pointer_state`.

## Frame and digest domains (v4)

`len` and the fingerprint cover the program's frame: magic 28 b5 2f fd, descriptor a0, a four-byte little-endian size equal to the text's byte count , a three-byte header for one raw last block of that size, then the text; frame = text + 12 bytes; the cap counts characters, `len` bytes.  The `companion-page` sha256 covers the text alone. The strict read takes the chunk bytes joined after the chain closes, never one chunk, as one frame whose consumed length equals that buffer's length; trailing bytes or a second frame refuse. The walk's outcome is a closed enum, `frame_state` {recipe_match, other_legal_frame, not_a_frame, chain_broken}: `other_legal_frame` is decided from the bytes, a legal frame of another recipe such as a stock encoder's two-byte size with descriptor 60, a wrong recipe and not a wrong page; `not_a_frame` a magic or header mismatch; `chain_broken` a walk failing before the zero link. Order is on chain: each chunk write carries the link to the next, the walk runs from the `content` field to the zero link, read from one program's writes, not its source; a missing first chunk and a wrong fingerprint look the same, the one case a walk cannot split. ac_upload_text.py (157cebe) refused a stock frame at its header.