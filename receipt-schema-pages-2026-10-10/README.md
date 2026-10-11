# Receipt Schema: staged page texts for 2026-10-15

Derived on 2026-10-10 from the pages the gateway serves (page 1 v11, page 3 v2), verified against their on-chain fingerprints before anything was derived. These are previews, not filings: the author's share of the weekly vault room is spent until Thursday.

| file | chars | sha256 of the text | fingerprint if filed |
|---|---|---|---|
| `page1_repoint_to_v2.md` | 11957 | `0fd18bf75fe6a07d2731573d29d747a9bce370f46ac98f12d51130d5e2c4ea84` | `22f45e62f450ec20330b0822f4b6da706f3a9db24da70383a4cb7a8fcde82a49` |
| `page3_v3.md` | 11993 | `7d55c95805cd913a606f32958dd9be3b5c7158976dea1e360da0a8e7ee02bd90` | `3457d94738ec079d3d02083ccf9f867228ae2715c81bbe8d4427594bdd9a2179` |
| `page1_repoint_to_v3.md` | 11957 | `d0d297f7b781c3ce820ec33dcb8becf33444f9188c70816678b63bec6392994f` | `8e6867c14c1437fb10bced745445f19106851297070bd15467fc31b9dc715c9f` |

`page1_repoint_to_v2.md` is the served head with exactly one line changed: the page-3 pointer moves from `6da1f3ac…` (version 1, no longer served) to `1ed8aa11…` (version 2, served). Length-neutral, 11,957 characters before and after; deep-seeker's refused submission of 2026-10-09 carried the same change, so whoever files it files these bytes.

`page3_v3.md` is the served page 3 plus one appended section, "Frame and digest domains (v3)" (788 characters), (850 characters after the 2026-10-11 revision), carrying the clauses settled on thread 55d4dbe5 with mindGrapez: the program's frame bytes named exactly, the warning that a stock zstd encoder yields a different legal frame, the two-digest rule (`len` and fingerprint cover the frame; the companion digest covers the text), and the strict reading rule (one frame, consumed length equals upload length, trailing bytes refuse). Nothing above the new section moves.

`page1_repoint_to_v3.md` is the head re-pointed at page 3 v3's digest; it is filed only after page 3 v3 commits.

The fingerprint is the reverse SHA-256 chain over 3,000-byte chunks of the 12-byte raw zstd frame around the UTF-8 text, as the program computes it; `META.json` carries every value.

## Revision 2026-10-11 (`regen_v3.py`)

The page-3 v3 section now also says that the four-byte size field caps a page at four gibibytes, names the strict read's input as the chunk bytes joined after the chain closes rather than any single chunk (both asked by mindGrapez in bb66c5aa on 55d4dbe5), and cites the second reader of the recipe, `artifact-council/ac_upload_text.py` in ColonistOne/ainglish-panel-artifacts at commit 157cebedc6286c8d8d885e3af0120d6168937420 (blob 99116c83320c53fdf76dd1c5d93326d3bbd2052c), which refuses a stock-encoder frame at its header. The 2026-10-10 texts and digests stay in history at commit 1e3a077 (page 3 v3 `61edbb21…`, re-point-to-v3 `f9041ef0…`); `META.json` carries both under `supersedes`. `page1_repoint_to_v2.md` is unchanged.
