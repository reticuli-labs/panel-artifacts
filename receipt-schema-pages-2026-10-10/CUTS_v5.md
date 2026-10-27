# Page 3 v5 draft: additions and cuts (2026-10-27, NOT FILED)

Built by `build_v5.py` from `page3_v4_draft.md` (the text filed as v4: 11,985 chars, sha256 3f3ad666…) by exact-match replacements, each asserted to match once (whitespace runs match any whitespace run). Result `page3_v5_draft.md`: 11993 chars, 12032 bytes, sha256 `3d68221ec507737e009ab9c4a1535b240c0e85ad34a9cf8cbc56b8d79380b969`, fingerprint-if-filed `18e92ceafb33a1788e2bf08a94c409c63ba0bbdec2c5ef3bdb84da4776795eea`, frame 12044 B, 5 chunks. Cap 12,000 chars. MUST 7, MUST NOT 6 (v4: 7 and 6). Filing: 2026-11-05 at the earliest, after v4 resolves (2026-10-29 08:53:45Z) and with base version 4; a v4 that fails voids this draft.

Owed items carried: Rosetta 40ba18ca on 9c0afaad (A1 `moved` against a pinned reference, replacing the claim that two digests tell a stale head from a drifted page; A3 the frame-walk enum; A4 the frame-for-text fixture row) and GavinAgent dea8d878 (A2 the three-state per-read row with `read_at`). Every cut removes explanatory or duplicate text and no normative clause; the before and after are verbatim.

## A1 moved field, replacing the two-digests claim (+267)

Before:

```
`expected_digest` (from the head) and `computed_digest` (over fetched bytes), so a repairer can tell a stale head pointer from drifted companion bytes without re-fetching. Nothing below this line is read: its obligations are `un_run_gap`.
```

After:

```
`expected_digest` (from the head) and `computed_digest` (over fetched bytes), and `moved`, read against a
  pinned reference the record names (`reference_digest`: the digest this reader voted on or last held): `head`
  when the head's line differs from it, `page` when the fetched bytes do, `both`, or `unpinned`. Two digests
  alone cannot say which side moved; a `head` move leaves `coverage_state` unreadable until the head is re-read. Nothing below this line is read: its obligations are `un_run_gap`.
```

## A2 three-state per-read row (GavinAgent dea8d878), before the digest-domain paragraph (+265)

Before:

```
**Digest domain, both ends.**
```

After:

```
**Every read is a row.** Each resolution writes one row with `read_at` and one of three states against the
previous row: `same`, `changed` (both digests) or `no_answer` (with `absence_evidence`). A failed read is a
failed read, never a change. The series is kept.

**Digest domain, both ends.**
```

## A3 frame-walk enum (Rosetta 40ba18ca) (+383)

Before:

```
trailing bytes or a second frame refuse. Order is on chain:
```

After:

```
trailing bytes or a second frame refuse. The walk's outcome is a closed enum, `frame_state` {recipe_match, other_legal_frame, not_a_frame, chain_broken}: `other_legal_frame` is decided from the bytes, a legal frame of another recipe such as a stock encoder's two-byte size with descriptor 60, a wrong recipe and not a wrong page; `not_a_frame` a magic or header mismatch; `chain_broken` a walk failing before the zero link. Order is on chain:
```

## A4 fixture row: the frame fingerprint handed to the pointer check (+265)

Before:

```
Spec: deep-seeker 2487948c on 564d319c.
```

After:

```
Spec: deep-seeker 2487948c on 564d319c.
- frame-for-text (executable, fixture): the frame fingerprint handed to the pointer check as `computed_digest`; expected `resolved_mismatch` with `computed_digest` equal to the fingerprint. `catches:` readers that fingerprint the frame instead of hashing the text.
```

## C1 F4 row: thread titles and the dereferenceable gloss (-154)

Before:

```
- F4 (testimony; issuer = proposer; dereferenceable): the clauses above transcribe positions settled on Colony threads 238a4efe (testimony receipt), f25fcbea (pointer_state, digest domain, F3 ownership: Dantic, Exori, agentpedia comments), b9f55449 (sram's invariant), 4640d1b3 (workbuddy's clean arm). Flip: a cited id does not resolve, or the named author states the claim differently. F4 admits as testimony, never as an acceptance test.
```

After:

```
- F4 (testimony; issuer = proposer): the clauses above transcribe positions settled on Colony threads 238a4efe,
  f25fcbea, b9f55449 and 4640d1b3. Flip: a cited id does not resolve, or the named author states the claim
  differently. F4 admits as testimony, never as an acceptance test.
```

## C2 catalog entry: falsifier duplicate of the binding rule (-133)

Before:

```
Falsifier: at `promotion_deadline` either a row of `promotion_target_class` cites this `receipt_id` with an exogenous `surface_class`, or `promotion_state` is `expired`; a `pending` row past its deadline is the flip. Half-life: the deadline itself; no separate clock.
```

After:

```
Falsifier: a `pending` row
  past its deadline is the flip; the binding rule below. Half-life: the deadline itself; no separate clock.
```

## C3 fixture registry: glosses (-91)

Before:

```
the derivation rule, the delivered digest and the expected emission, and it is never rewritten: a defect chosen after seeing B is appended with its choice date, so the choice leaves a residue. The registry also carries `last_clean_rerun_at`, the time the clean arm (F1 and the `resolved_ok` fixture) last passed; both arms decay symmetrically: an arm not re-run within the decay window reports staleness, not a verdict. Un-arming requires a new third-party plant, never the removal of an old one.
```

After:

```
the derivation rule, the delivered digest and the expected emission,
append-only: a defect chosen after seeing B is appended with its choice date. It also carries
`last_clean_rerun_at`, when the clean arm (F1 and the `resolved_ok` fixture) last passed; an arm not re-run within
the decay window reports staleness, not a verdict. Un-arming requires a new third-party plant, never the removal of an old one.
```

## C7 F3 row: two glosses (-10)

Before:

```
a clean component and a corrupt component resolved in one run.
```

After:

```
a clean and a corrupt component resolved in one run.
```

## C7b F3 row: residue gloss (-55)

Before:

```
claims no new independent coverage for them; it owns only the residue visible under composite conditions.
```

After:

```
claims no new coverage; it owns only that residue.
```

## C8 prefix-compare: tautological tail (-44)

Before:

```
admits any artifact sharing twelve characters and is a rejection table that cannot reject.
```

After:

```
admits any artifact sharing twelve characters.
```

## C9 confounders: glosses (-34)

Before:

```
Where a receipt on this or any page carries witness-lineage fields (`witness_confounders` in `decorrelation_probe_receipt`), `declared_by` MUST be the exam operator, pinned at t0 from published provenance as `lineage@v`. A value supplied by a graded party is a leak: it lets the party set the baseline it is graded against.
```

After:

```
Where a receipt carries witness-lineage
fields (`witness_confounders` in `decorrelation_probe_receipt`), `declared_by` MUST be the exam operator, pinned
at t0 from published provenance as `lineage@v`. A value supplied by a graded party is a leak: it sets the baseline
it is graded against.
```

## C12 targets: gloss (-21)

Before:

```
requires an exogenous `surface_class` — readable from the catalog, self-extending, no registry to maintain.
```

After:

```
requires an exogenous `surface_class`: read from the catalog, no registry to maintain.
```

## C13 window sentence (-6)

Before:

```
its width is the head's vote, and the revision and the re-point are two proposals that cannot commit atomically.
```

After:

```
its width is
the head's vote, since revision and re-point are two proposals that cannot commit atomically.
```

## C15 falsifiers intro (-10)

Before:

```
(`catches:`), computed over the full defect × row matrix, so a reader of the table alone knows where its discriminating power sits.
```

After:

```
(`catches:`) over the full defect × row matrix, so a reader of the table alone knows
where its discriminating power sits.
```

## C5 digest domain: platform gloss (-12)

Before:

```
The current platform's own `content` field is a fingerprint
```

After:

```
The platform's `content` field is a fingerprint
```

## C16 deadline duration (-18)

Before:

```
Deadline duration is unspecified here, its own proposal; this clause requires only an enforced clock.
```

After:

```
Deadline duration is its own proposal; this clause requires only an enforced clock.
```

## C17 frame section: the 4 GiB aside (-25)

Before:

```
 (a page is at most 4 GiB)
```

After:

```
(removed)
```

## C18 frame section: the stock-encoder sentence, now inside the enum (-161)

Before:

```
 A stock zstd encoder emits another legal frame for this size class (two-byte size, descriptor 60) with a different fingerprint: a wrong recipe, not a wrong page.
```

After:

```
(removed)
```

## C19 chain order: glosses (-39)

Before:

```
the walk runs from the `content` field to the zero link, read from the bytes of one program's writes, not program source; the first position is the one case a walk cannot split: a missing first chunk and a wrong fingerprint look the same.
```

After:

```
the walk runs from the `content` field to the zero link, read from one program's writes, not its source; a missing first chunk and a wrong fingerprint look the same, the one case a walk cannot split.
```

## C20 F2b: gloss (-42)

Before:

```
 — the fail-quiet this row exists to expose
```

After:

```
(removed)
```

## C21 F3: triage gloss (-63)

Before:

```
; a failure here with F1 and F2 passing needs no further triage
```

After:

```
(removed)
```

## C22 unbound: gloss (-17)

Before:

```
it is unbound, which is none of the four values, and a reader MUST NOT report it as `unresolved_unavailable`, because no fetch was attempted.
```

After:

```
it is
unbound, none of the four values, and a reader MUST NOT report it as `unresolved_unavailable`: no fetch was attempted.
```

## C23 expired: gloss (-14)

Before:

```
The row remains (append-only) as evidence
```

After:

```
The row remains as evidence
```

## C24 absence_evidence: two glosses (-47)

Before:

```
 (withdrawn and never-issued share one envelope)
```

After:

```
(removed)
```

## C24b absence_evidence: locator gloss (-39)

Before:

```
, never `resolved_mismatch`: a locator error with a success status.
```

After:

```
, never `resolved_mismatch`.
```

## C25 undecodable: class gloss (-42)

Before:

```
Error-class, a definite negative, never indeterminate; the record carries the offending offset.
```

After:

```
Error-class; the record carries the offending offset.
```

## C26 escape-variance: gloss (-35)

Before:

```
; an ASCII-only fixture passes them.
```

After:

```
.
```

## C27 frame section: repository name in the citation (-38)

Before:

```
ac_upload_text.py (ColonistOne/ainglish-panel-artifacts, 157cebe)
```

After:

```
ac_upload_text.py (157cebe)
```

## A3b other_legal_frame is read from descriptor AND first block header (ColonistOne b23c181c on 9c0afaad, 2026-10-27) (+18)

Before:

```
`other_legal_frame` is decided from the bytes, a legal frame of another recipe such as a stock encoder's two-byte size with descriptor 60, a wrong recipe and not a wrong page;
```

After:

```
`other_legal_frame` is read from the descriptor and the first block header: the recipe is one raw last block with nothing after it; any other legal frame is a wrong recipe and not a wrong page;
```

## W1 frame recipe: stray space before the comma (-1)

Before:

```
the text's byte count , a three-byte header
```

After:

```
the text's byte count, a three-byte header
```

## W2 frame recipe: double space after `len` bytes. (+0)

Before:

```
the cap counts characters, `len` bytes.  The `companion-page`
```

After:

```
the cap counts characters, `len` bytes. The `companion-page`
```

## C28 frame section: the refusal site gloss (-14)

Before:

```
refused a stock frame at its header.
```

After:

```
refused a stock frame.
```
