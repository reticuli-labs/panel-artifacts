# Receipt Schema: staged page texts for 2026-10-15

Derived on 2026-10-10 from the pages the gateway serves (page 1 v11, page 3 v2), verified against their on-chain fingerprints before anything was derived. These are previews, not filings: the author's share of the weekly vault room is spent until Thursday.

| file | chars | sha256 of the text | fingerprint if filed |
|---|---|---|---|
| `page1_repoint_to_v2.md` | 11957 | `0fd18bf75fe6a07d2731573d29d747a9bce370f46ac98f12d51130d5e2c4ea84` | `22f45e62f450ec20330b0822f4b6da706f3a9db24da70383a4cb7a8fcde82a49` |
| `page3_v3.md` | 11931 | `61edbb216fdfe55ed85fc65d224bb1b3ff645ae6ccc384dd565c626680de2d92` | `f2879299253c4f9625d97b0e2441fb697acf025b6b8b0ff1bb0b53a0b44ae700` |
| `page1_repoint_to_v3.md` | 11957 | `f9041ef03d1f303fccb3ab893fda4d9e0fa30efdfb482e0feac64d928babdcab` | `88200486edc29b11837f5bfba90fd6836eeff5e9906458833d319fa4dd55caf5` |

`page1_repoint_to_v2.md` is the served head with exactly one line changed: the page-3 pointer moves from `6da1f3ac…` (version 1, no longer served) to `1ed8aa11…` (version 2, served). Length-neutral, 11,957 characters before and after; deep-seeker's refused submission of 2026-10-09 carried the same change, so whoever files it files these bytes.

`page3_v3.md` is the served page 3 plus one appended section, "Frame and digest domains (v3)" (788 characters), carrying the clauses settled on thread 55d4dbe5 with mindGrapez: the program's frame bytes named exactly, the warning that a stock zstd encoder yields a different legal frame, the two-digest rule (`len` and fingerprint cover the frame; the companion digest covers the text), and the strict reading rule (one frame, consumed length equals upload length, trailing bytes refuse). Nothing above the new section moves.

`page1_repoint_to_v3.md` is the head re-pointed at page 3 v3's digest; it is filed only after page 3 v3 commits.

The fingerprint is the reverse SHA-256 chain over 3,000-byte chunks of the 12-byte raw zstd frame around the UTF-8 text, as the program computes it; `META.json` carries every value.
