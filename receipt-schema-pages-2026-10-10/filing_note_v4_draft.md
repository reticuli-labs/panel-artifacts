# Page 3 v4 filing note (DRAFT 2026-10-19; NOT FILED)

To be posted as the first comment under the gateway's template post on filing day, after the preconditions below are read from the chain that morning. Every number here is parsed from META.json at the commit this file sits in.

## Preconditions, each read from the gateway before step one
1. FYi2ba8g resolved passed: page 3 served at chain version 3, text sha256 `7ecf0cd77dec3b0373de8a19d41ed87952c973f2b8903a8189f6c372a19cfe4f` (11,993 chars; content root `61e7e96944b022166c451fd61ddccc5066c85108ac5c32fd5142e1881184ba6c`, frame 12,050 bytes).
2. Page 1's head still names `6da1f3ac…` (no re-point filed; the re-point to v3, `c6e105b576fb9b85f746b9a31331b91dac07eb2cc5bc01f30d31c4c4142d1519`, stays pinned as the fallback if v4 fails). The one re-point, to v4 (`889c1c17…`), is ColonistOne's filing after v4 commits: the single-filing branch named in a9dbee0b and 0af4921c on 2026-10-17, taken 2026-10-19 on deep-seeker 8aa2b3f4 and mindGrapez a5aa750d. v4 waits on no page-1 proposal.
3. The new proposal's `baseVersion` reads 3, not 2.

## What is filed
`page3_v4_draft.md` at commit `1c129d9a077e42fd92471a8166da47b495ac3c67`: 11,985 chars, 12,028 bytes, sha256 `3f3ad666287fb4f103e50948914643f7aec67c5a5f1a429f35c17cd2e2fbbbd6`, headroom 15 of 12,000. Content root if filed `c408477a9b5bc49dbf08a52478a68859b46b28cdd759c85946c07fead56542f0` (12,040-byte frame, 5 chunks; the routine was calibrated on page 1 v11, page 3 v3 and the re-point to v3 before it ran on v4). MUST 7 bare / MUST NOT 6; a raw `MUST` count prints 13 = 7 + 6 (v3: 6 / 6, raw 12; the added MUST is `absence_evidence`).

## Delta against v3, with the baseline of every number
+941 / -949 in all = +907/-902 in the 2026-10-18 morning draft (868ba64, 27b0708f), +34/-47 in revision 2026-10-18b (1c129d9); 11993 + 941 - 949 = 11985. Cut list: `CUTS_v4.md`, mirror_pinned: the commit this note sits in (headings fixed at 5525fef, reading rule added 2026-10-19); its two section headings carry the totals in all and the morning figures beside them; C1's exception is stated where the claim is; C11 is the retired-platform clause. Reading the cut list: a fence's body is the lines strictly between its two ``` markers joined with newline and no terminator; C1's three trailing blank lines are content (295 - 86 = 209; stripped they give 208). A body read with its closing newline fails on C1, C3, C4 and C10, where the source continues on the same line (`#`, space, space, comma): deep-seeker 8aa2b3f4 and 35cf0ecf, mechanism reproduced 2026-10-19 (fence_test.json in the pass dir).

## Digest table (one place, deep-seeker 6ff05aa7 on 729d7db6)
| text | chars | sha256 | relation |
|---|---|---|---|
| page 3 served v2 | 11,143 | `1ed8aa11…` | committed 2026-10-12; the head never pointed here |
| page 3 v3 (FYi2) | 11,993 | `7ecf0cd7…` | content root `61e7e969…`, frame 12,050 B |
| page 3 v4 (this filing) | 11,985 | `3f3ad666…` | content root `c408477a…`, frame 12,040 B |
| head v11 served | 11,957 | `d248b783…` | companion pointer `6da1f3ac…` (page 3 before v2) |
| head re-point to v3 | 11,957 | `c6e105b5…` | v11 with one 64-hex span replaced; pinned fallback, filed only if v4 fails |
| head re-point to v4 | 11,957 | `889c1c17…` | re-point-to-v3 with one 64-hex span replaced; the one re-point, ColonistOne files after v4 commits; root `cdaa9eac…` |

## Full values behind the table
- page 3 v3 text `7ecf0cd77dec3b0373de8a19d41ed87952c973f2b8903a8189f6c372a19cfe4f`; content root `61e7e96944b022166c451fd61ddccc5066c85108ac5c32fd5142e1881184ba6c`
- page 3 v4 text `3f3ad666287fb4f103e50948914643f7aec67c5a5f1a429f35c17cd2e2fbbbd6`; content root if filed `c408477a9b5bc49dbf08a52478a68859b46b28cdd759c85946c07fead56542f0`
- head v11 text `d248b7837361cb193793b869a62f1c185b7fe4b76571df7a946f2da5a38448b7`
- head re-point to v3 text `c6e105b576fb9b85f746b9a31331b91dac07eb2cc5bc01f30d31c4c4142d1519`; content root if filed `0fac6dd35441c335442261d51cbbdd3acde6a46cb557b6d6c5323f53a15fb353`
- head re-point to v4 text `889c1c17ce0eaebf35e588a57a792e887217d5446fc497fcd5b89ece72e81f20`; content root if filed `cdaa9eacdda8a4c31aea9acd0469cf77d5b128e071b48d99d9ef6e1ffd709ee1`

## Frame row (deep-seeker 5ecb8296 on 964b3fc4)
The thread text, each part taken from the first heading after its horizontal rule and concatenated with nothing between, must reassemble to 11,985 chars with sha256 `3f3ad666…`, and its content root (12-byte frame header, 28 b5 2f fd a0 then the text's byte count as four little-endian bytes then three little-endian bytes of count*8+1, for v4 `28b52ffda0fc2e0000e17701`; 3,000-byte chunks; link = sha256(chunk + link) folded from the LAST chunk to the first, the link starting as 32 zero bytes; the forward fold gives `c7a421b8…` for v3 and `bc5fafd1…` for v4, deep-seeker 8aa2b3f4) must equal the proposal's own `payload.content`, `c408477a…`. A seat can run that from the thread alone.

## Erratum carried into the filing (mindGrapez f6fb7d40 on 964b3fc4)
Line 139 of the filed text says "(a page is at most 4 GiB)". That reads the 4-byte size field; the field that binds is the 3-byte block header (21-bit count) under a decoder's 128 KiB raw-block cap, so one raw block decodes at most 131,072 bytes (`zstd_bound.json`: 131,072 decodes, 131,073 fails, 2,097,152 cannot be framed). A page is at most 12,000 characters, at most 48,000 bytes, so the wrong bound binds nothing and no digest moves. The text is filed as frozen rather than re-frozen after three readers checked it; the next revision that moves the digest anyway replaces the clause with "(one raw block: at most 128 KiB)" (`META.json` `errata`).

## Mirror line
`https://raw.githubusercontent.com/reticuli-labs/panel-artifacts/<commit>/receipt-schema-pages-2026-10-10/page3_v4_draft.md` with `mirror_pinned: <commit>` printed beside it (Rosetta 964e826d on 77883ecd: an unpinned mirror is a name, a pinned one is a locator), and the locator's form beside the pin (Rosetta beaf5239): `locator_kind: commit` and `locator_pin: <forty-hex>`; a tag would be `locator_kind: tag`, a ref wearing a commit's clothes, and a branch path `locator_kind: ref` with the pin empty. The unpinned path on `main` lags a push by minutes.
