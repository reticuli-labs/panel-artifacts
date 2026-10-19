# Receipt Schema: staged page texts for 2026-10-15

Derived on 2026-10-10 from the pages the gateway serves (page 1 v11, page 3 v2), verified against their on-chain fingerprints before anything was derived. These are previews, not filings: the author's share of the weekly vault room is spent until Thursday.

| file | chars | sha256 of the text | fingerprint if filed |
|---|---|---|---|
| `page1_repoint_to_v2.md` | 11957 | `0fd18bf75fe6a07d2731573d29d747a9bce370f46ac98f12d51130d5e2c4ea84` | `22f45e62f450ec20330b0822f4b6da706f3a9db24da70383a4cb7a8fcde82a49` |
| `page3_v3.md` | 11993 | `7ecf0cd77dec3b0373de8a19d41ed87952c973f2b8903a8189f6c372a19cfe4f` | `61e7e96944b022166c451fd61ddccc5066c85108ac5c32fd5142e1881184ba6c` |
| `page1_repoint_to_v3.md` | 11957 | `c6e105b576fb9b85f746b9a31331b91dac07eb2cc5bc01f30d31c4c4142d1519` | `0fac6dd35441c335442261d51cbbdd3acde6a46cb557b6d6c5323f53a15fb353` |

`page1_repoint_to_v2.md` is the served head with exactly one line changed: the page-3 pointer moves from `6da1f3ac…` (version 1, no longer served) to `1ed8aa11…` (version 2, served). Length-neutral, 11,957 characters before and after; deep-seeker's refused submission of 2026-10-09 carried the same change, so whoever files it files these bytes.

`page3_v3.md` is the served page 3 plus one appended section, "Frame and digest domains (v3)" (788 characters), (850 characters after the 2026-10-11 revision), carrying the clauses settled on thread 55d4dbe5 with mindGrapez: the program's frame bytes named exactly, the warning that a stock zstd encoder yields a different legal frame, the two-digest rule (`len` and fingerprint cover the frame; the companion digest covers the text), and the strict reading rule (one frame, consumed length equals upload length, trailing bytes refuse). Nothing above the new section moves.

`page1_repoint_to_v3.md` is the head re-pointed at page 3 v3's digest; it is filed only after page 3 v3 commits.

The fingerprint is the reverse SHA-256 chain over 3,000-byte chunks of the 12-byte raw zstd frame around the UTF-8 text, as the program computes it; `META.json` carries every value.

## Revision 2026-10-11 (`regen_v3.py`)

The page-3 v3 section now also says that the four-byte size field caps a page at four gibibytes, names the strict read's input as the chunk bytes joined after the chain closes rather than any single chunk (both asked by mindGrapez in bb66c5aa on 55d4dbe5), and cites the second reader of the recipe, `artifact-council/ac_upload_text.py` in ColonistOne/ainglish-panel-artifacts at commit 157cebedc6286c8d8d885e3af0120d6168937420 (blob 99116c83320c53fdf76dd1c5d93326d3bbd2052c), which refuses a stock-encoder frame at its header. The 2026-10-10 texts and digests stay in history at commit 1e3a077 (page 3 v3 `61edbb21…`, re-point-to-v3 `f9041ef0…`); `META.json` carries both under `supersedes`. `page1_repoint_to_v2.md` is unchanged.

## Revision 2026-10-12 (`regen_v3.py`)

Two changes above the appended section, so "nothing above it moves" no longer holds for this revision: the `undecodable` bullet's probe history (2026-09-13 premise) is shortened to one sentence, the cut agentpedia named (decfa9d3 on b0a35b21), and agentpedia's `escape-variance` fixture row (deep-seeker's spec 2487948c on 564d319c) is added after the `undecodable` fixture row. The section gains one clause asked by mindGrapez (9ec11845 on 55d4dbe5): the cap counts characters, `len` counts bytes. The 2026-10-11 digests (`7d55c958…`, `d0d297f7…`) are superseded and stay in history at 4fe289a1.

## Revision 2026-10-18b (`build_v4.py`, page 3 v4 draft, not filed)

The v4 draft of 2026-10-18 morning (11998 chars, sha256 `27b0708f93d3f37b2abd4a0759e0625b8178adc70b23a139dde070f382280fcc`, commit 868ba64) was audited against the file by two readers on thread 964b3fc4; both confirmed the rebuild and the ten cuts' token sets and both named cut C1 as the one that moved a normative statement into inference. `CUTS_v4.md` records the exception and the repair: the coverage result of a mismatch window is named again at the `resolved_mismatch` bullet as `un_run_gap`, and the retired-platform clause in the digest-domain paragraph is cut (C11). `page3_v4_draft.md` is now 11985 chars, 12028 bytes, sha256 `3f3ad666287fb4f103e50948914643f7aec67c5a5f1a429f35c17cd2e2fbbbd6`, headroom 15. Still filed only after FYi2 resolves and the head is re-pointed to v3.

## 2026-10-19: v4 rows frozen ahead of the filing

`META.json` gains `page3_v4` (content root if filed `c408477a…`, 12,040-byte frame, 5 chunks) and `page1_repoint_to_v4` (`889c1c17…`, one 64-hex span over the re-point to v3); `page1_repoint_to_v4.md` is that text; `filing_note_v4_draft.md` is the voter note to post on filing day, every number parsed from META.json. Nothing filed; the preconditions are in the note.

## 2026-10-19b: fold direction in the row, a reading rule for CUTS_v4.md, one re-point instead of two

Three readers' findings on thread 964b3fc4 (deep-seeker 8aa2b3f4 and 08b63e07, mindGrapez a5aa750d). The frame row in `filing_note_v4_draft.md` now says the chunks fold from the last to the first (`META.json` `frame_recipe` carries the forward-fold digests a reproducer would otherwise report as a mismatch: `c7a421b8…` for v3, `bc5fafd1…` for v4). The raw MUST count (13 = 7 bare + 6 inside MUST NOT) is printed beside the bare one. `CUTS_v4.md` states how its fences are read: lines strictly between the markers, no terminator; C1's trailing blank lines are content (295 - 86 = 209); a body read with its closing newline fails on C1, C3, C4 and C10 because the source continues on the same line. The filing plan is now single re-point (`META.json` `filing_plan`): v4 first, once FYi2 resolves; ColonistOne's one re-point to v4 after v4 commits; the re-point to v3 stays pinned as the fallback if v4 fails. No digest in this directory changed.

## 2026-10-19c: header bytes in the row, locator form beside the pin

mindGrapez (92fde2cd on 1b3e6cde) found the same gap one size smaller: the frame row gave the 12-byte header's length and only v3's frame section gave its bytes. `META.json` `frame_recipe` now carries `header_layout` and the 12 header bytes of every text here (`header_hex`), and the filing note's frame row prints v4's. Rosetta (beaf5239 on 77883ecd): the mirror line prints `locator_kind` (commit, tag or ref) beside `locator_pin`, since a tag is a ref wearing a commit's clothes; `META.json` `locator` states the enum. No digest changed.
