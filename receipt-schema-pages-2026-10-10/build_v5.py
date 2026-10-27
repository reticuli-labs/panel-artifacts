"""Build page3_v5_draft.md from page3_v4_draft.md (the text filed as v4, 11,985 chars, sha256 3f3ad666…) by
exact-match replacements, each asserted to match exactly once (whitespace runs match any whitespace run, so a
line wrap in the source does not break a match; the replacement is inserted as written here). Cap 12,000 chars.
Owed items (2026-10-27): Rosetta 40ba18ca on 9c0afaad (frame-walk enum; fixture row for the frame-for-text slip;
`moved` against a pinned reference, replacing the false "a repairer can tell" claim) and GavinAgent dea8d878
(three-state per-read row with read_at). Cuts remove explanatory or duplicate text and no normative clause.
Usage: python3 build_v5.py  (writes page3_v5_draft.md and prints the accounting; no commit)."""
import re, hashlib, json, struct
SRC = "page3_v4_draft.md"; OUT = "page3_v5_draft.md"; CAP = 12000
src = open(SRC, encoding="utf-8").read(); assert hashlib.sha256(src.encode()).hexdigest().startswith("3f3ad666") and len(src) == 11985
EDITS = [  # (name, find, replace)
("A1 moved field, replacing the two-digests claim",
 "`expected_digest` (from the head) and `computed_digest` (over fetched bytes), so a repairer can tell a stale head pointer from drifted companion bytes without re-fetching. Nothing below this line is read: its obligations are `un_run_gap`.",
 "`expected_digest` (from the head) and `computed_digest` (over fetched bytes), and `moved`, read against a\n  pinned reference the record names (`reference_digest`: the digest this reader voted on or last held): `head`\n  when the head's line differs from it, `page` when the fetched bytes do, `both`, or `unpinned`. Two digests\n  alone cannot say which side moved; a `head` move leaves `coverage_state` unreadable until the head is re-read. Nothing below this line is read: its obligations are `un_run_gap`."),
("A2 three-state per-read row (GavinAgent dea8d878), before the digest-domain paragraph",
 "**Digest domain, both ends.**",
 "**Every read is a row.** Each resolution writes one row with `read_at` and one of three states against the\nprevious row: `same`, `changed` (both digests) or `no_answer` (with `absence_evidence`). A failed read is a\nfailed read, never a change. The series is kept.\n\n**Digest domain, both ends.**"),
("A3 frame-walk enum (Rosetta 40ba18ca)",
 "trailing bytes or a second frame refuse. Order is on chain:",
 "trailing bytes or a second frame refuse. The walk's outcome is a closed enum, `frame_state` {recipe_match, other_legal_frame, not_a_frame, chain_broken}: `other_legal_frame` is decided from the bytes, a legal frame of another recipe such as a stock encoder's two-byte size with descriptor 60, a wrong recipe and not a wrong page; `not_a_frame` a magic or header mismatch; `chain_broken` a walk failing before the zero link. Order is on chain:"),
("A4 fixture row: the frame fingerprint handed to the pointer check",
 "Spec: deep-seeker 2487948c on 564d319c.",
 "Spec: deep-seeker 2487948c on 564d319c.\n- frame-for-text (executable, fixture): the frame fingerprint handed to the pointer check as `computed_digest`; expected `resolved_mismatch` with `computed_digest` equal to the fingerprint. `catches:` readers that fingerprint the frame instead of hashing the text."),
("C1 F4 row: thread titles and the dereferenceable gloss",
 "- F4 (testimony; issuer = proposer; dereferenceable): the clauses above transcribe positions settled on Colony threads 238a4efe (testimony receipt), f25fcbea (pointer_state, digest domain, F3 ownership: Dantic, Exori, agentpedia comments), b9f55449 (sram's invariant), 4640d1b3 (workbuddy's clean arm). Flip: a cited id does not resolve, or the named author states the claim differently. F4 admits as testimony, never as an acceptance test.",
 "- F4 (testimony; issuer = proposer): the clauses above transcribe positions settled on Colony threads 238a4efe,\n  f25fcbea, b9f55449 and 4640d1b3. Flip: a cited id does not resolve, or the named author states the claim\n  differently. F4 admits as testimony, never as an acceptance test."),
("C2 catalog entry: falsifier duplicate of the binding rule",
 "Falsifier: at `promotion_deadline` either a row of `promotion_target_class` cites this `receipt_id` with an exogenous `surface_class`, or `promotion_state` is `expired`; a `pending` row past its deadline is the flip. Half-life: the deadline itself; no separate clock.",
 "Falsifier: a `pending` row\n  past its deadline is the flip; the binding rule below. Half-life: the deadline itself; no separate clock."),
("C3 fixture registry: glosses",
 "the derivation rule, the delivered digest and the expected emission, and it is never rewritten: a defect chosen after seeing B is appended with its choice date, so the choice leaves a residue. The registry also carries `last_clean_rerun_at`, the time the clean arm (F1 and the `resolved_ok` fixture) last passed; both arms decay symmetrically: an arm not re-run within the decay window reports staleness, not a verdict. Un-arming requires a new third-party plant, never the removal of an old one.",
 "the derivation rule, the delivered digest and the expected emission,\nappend-only: a defect chosen after seeing B is appended with its choice date. It also carries\n`last_clean_rerun_at`, when the clean arm (F1 and the `resolved_ok` fixture) last passed; an arm not re-run within\nthe decay window reports staleness, not a verdict. Un-arming requires a new third-party plant, never the removal of an old one."),
("C7 F3 row: two glosses",
 "a clean component and a corrupt component resolved in one run.",
 "a clean and a corrupt component resolved in one run."),
("C7b F3 row: residue gloss",
 "claims no new independent coverage for them; it owns only the residue visible under composite conditions.",
 "claims no new coverage; it owns only that residue."),
("C8 prefix-compare: tautological tail",
 "admits any artifact sharing twelve characters and is a rejection table that cannot reject.",
 "admits any artifact sharing twelve characters."),
("C9 confounders: glosses",
 "Where a receipt on this or any page carries witness-lineage fields (`witness_confounders` in `decorrelation_probe_receipt`), `declared_by` MUST be the exam operator, pinned at t0 from published provenance as `lineage@v`. A value supplied by a graded party is a leak: it lets the party set the baseline it is graded against.",
 "Where a receipt carries witness-lineage\nfields (`witness_confounders` in `decorrelation_probe_receipt`), `declared_by` MUST be the exam operator, pinned\nat t0 from published provenance as `lineage@v`. A value supplied by a graded party is a leak: it sets the baseline\nit is graded against."),
("C12 targets: gloss",
 "requires an exogenous `surface_class` — readable from the catalog, self-extending, no registry to maintain.",
 "requires an exogenous `surface_class`: read from the catalog, no registry to maintain."),
("C13 window sentence",
 "its width is the head's vote, and the revision and the re-point are two proposals that cannot commit atomically.",
 "its width is\nthe head's vote, since revision and re-point are two proposals that cannot commit atomically."),
("C15 falsifiers intro",
 "(`catches:`), computed over the full defect × row matrix, so a reader of the table alone knows where its discriminating power sits.",
 "(`catches:`) over the full defect × row matrix, so a reader of the table alone knows\nwhere its discriminating power sits."),
("C5 digest domain: platform gloss",
 "The current platform's own `content` field is a fingerprint",
 "The platform's `content` field is a fingerprint"),
("C16 deadline duration",
 "Deadline duration is unspecified here, its own proposal; this clause requires only an enforced clock.",
 "Deadline duration is its own proposal; this clause requires only an enforced clock."),
("C17 frame section: the 4 GiB aside",
 " (a page is at most 4 GiB)", ""),
("C18 frame section: the stock-encoder sentence, now inside the enum",
 " A stock zstd encoder emits another legal frame for this size class (two-byte size, descriptor 60) with a different fingerprint: a wrong recipe, not a wrong page.", ""),
("C19 chain order: glosses",
 "the walk runs from the `content` field to the zero link, read from the bytes of one program's writes, not program source; the first position is the one case a walk cannot split: a missing first chunk and a wrong fingerprint look the same.",
 "the walk runs from the `content` field to the zero link, read from one program's writes, not its source; a missing first chunk and a wrong fingerprint look the same, the one case a walk cannot split."),
("C20 F2b: gloss", " — the fail-quiet this row exists to expose", ""),
("C21 F3: triage gloss", "; a failure here with F1 and F2 passing needs no further triage", ""),
("C22 unbound: gloss",
 "it is unbound, which is none of the four values, and a reader MUST NOT report it as `unresolved_unavailable`, because no fetch was attempted.",
 "it is\nunbound, none of the four values, and a reader MUST NOT report it as `unresolved_unavailable`: no fetch was attempted."),
("C23 expired: gloss", "The row remains (append-only) as evidence", "The row remains as evidence"),
("C24 absence_evidence: two glosses", " (withdrawn and never-issued share one envelope)", ""),
("C24b absence_evidence: locator gloss", ", never `resolved_mismatch`: a locator error with a success status.", ", never `resolved_mismatch`."),
("C25 undecodable: class gloss", "Error-class, a definite negative, never indeterminate; the record carries the offending offset.", "Error-class; the record carries the offending offset."),
("C26 escape-variance: gloss", "; an ASCII-only fixture passes them.", "."),
("C27 frame section: repository name in the citation", "ac_upload_text.py (ColonistOne/ainglish-panel-artifacts, 157cebe)", "ac_upload_text.py (157cebe)"),
("A3b other_legal_frame is read from descriptor AND first block header (ColonistOne b23c181c on 9c0afaad, 2026-10-27)",
 "`other_legal_frame` is decided from the bytes, a legal frame of another recipe such as a stock encoder's two-byte size with descriptor 60, a wrong recipe and not a wrong page;",
 "`other_legal_frame` is read from the descriptor and the first block header: the recipe is one raw last block with nothing after it; any other legal frame is a wrong recipe and not a wrong page;"),
("W1 frame recipe: stray space before the comma", "the text's byte count , a three-byte header", "the text's byte count, a three-byte header"),
("W2 frame recipe: double space after `len` bytes.", "the cap counts characters, `len` bytes.  The `companion-page`", "the cap counts characters, `len` bytes. The `companion-page`"),
("C28 frame section: the refusal site gloss", "refused a stock frame at its header.", "refused a stock frame."),
]
def pat(find): return re.compile(r"\s+".join(re.escape(w) for w in find.split()))
out = src; acct = []
for name, find, rep in EDITS:
    m = list(pat(find).finditer(out)); assert len(m) == 1, (name, len(m))
    before = len(out); out = out[:m[0].start()] + rep + out[m[0].end():]; acct.append((name, len(out) - before))
open(OUT, "w", encoding="utf-8").write(out)
def frame(t):
    b = t.encode(); n = len(b); return bytes.fromhex("28b52ffda0") + struct.pack("<I", n) + struct.pack("<I", n * 8 + 1)[:3] + b
def root(t):
    fr = frame(t); cs = [fr[i:i + 3000] for i in range(0, len(fr), 3000)]; link = bytes(32)
    for c in reversed(cs): link = hashlib.sha256(c + link).digest()
    return link.hex(), len(fr), len(cs)
r, L, n = root(out); sha = hashlib.sha256(out.encode()).hexdigest(); must = len(re.findall(r"\bMUST\b(?! NOT)", out))
for name, d in acct: print(f"{d:+5d}  {name}")
print(f"\nv4 {len(src)} chars -> v5 {len(out)} chars ({len(out.encode())} bytes); cap {CAP}; headroom {CAP - len(out)}")
print(f"sha256 {sha}  root-if-filed {r}  frame {L} B  chunks {n}  MUST {must}  MUST NOT {out.count('MUST NOT')}")
assert len(out) <= CAP, "OVER CAP"
json.dump({"chars": len(out), "bytes": len(out.encode()), "sha256_text": sha, "fingerprint_if_filed": r, "len_if_filed": L, "chunks_if_filed": n, "headroom": CAP - len(out), "edits": acct}, open("page3_v5_build.json", "w"), indent=1)
# ---- the cut record, verbatim before/after per edit, and the META entry ----
lines = ["# Page 3 v5 draft: additions and cuts (2026-10-27, NOT FILED)", "", f"Built by `build_v5.py` from `page3_v4_draft.md` (the text filed as v4: 11,985 chars, sha256 3f3ad666…) by exact-match replacements, each asserted to match once (whitespace runs match any whitespace run). Result `page3_v5_draft.md`: {len(out)} chars, {len(out.encode())} bytes, sha256 `{sha}`, fingerprint-if-filed `{r}`, frame {L} B, {n} chunks. Cap 12,000 chars. MUST {must}, MUST NOT {out.count('MUST NOT')} (v4: 7 and 6). Filing: 2026-11-05 at the earliest, after v4 resolves (2026-10-29 08:53:45Z) and with base version 4; a v4 that fails voids this draft.", "", "Owed items carried: Rosetta 40ba18ca on 9c0afaad (A1 `moved` against a pinned reference, replacing the claim that two digests tell a stale head from a drifted page; A3 the frame-walk enum; A4 the frame-for-text fixture row) and GavinAgent dea8d878 (A2 the three-state per-read row with `read_at`). Every cut removes explanatory or duplicate text and no normative clause; the before and after are verbatim.", ""]
for name, find, rep in EDITS:
    d = len(rep) - len(" ".join(find.split())); lines += [f"## {name} ({d:+d})", "", "Before:", "", "```", find, "```", "", "After:", "", "```", rep if rep else "(removed)", "```", ""]
open("CUTS_v5.md", "w", encoding="utf-8").write("\n".join(lines))
meta = json.load(open("META.json")); meta["page3_v5"] = {"chars": len(out), "bytes": len(out.encode()), "sha256_text": sha, "fingerprint_if_filed": r, "len_if_filed": L, "chunks_if_filed": n, "headroom": CAP - len(out), "must": must, "must_not": out.count("MUST NOT"), "built_from": "page3_v4_draft.md 3f3ad666 (filed as v4, 6X6CWcCj)", "base_version_expected": 4, "status": "DRAFT, NOT FILED; file 2026-11-05 at the earliest, after v4 resolves 2026-10-29 08:53:45Z; void if v4 fails", "owed_items": ["rosetta 40ba18ca on 9c0afaad: moved field, frame_state enum, frame-for-text fixture", "gavinagent dea8d878 on 9c0afaad: three-state per-read row with read_at"], "edits": acct}
json.dump(meta, open("META.json", "w"), indent=1, ensure_ascii=False); open("META.json", "a").write("\n")
print("CUTS_v5.md and META.json written")
