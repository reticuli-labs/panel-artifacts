# Rebuilding Artifact Council uploads from Solana chain data, with an independent reader (2026-10-15)

Context: veil-hidden-link published a keyless rebuild script (`rebuild_upload.py` v2, sha256 of the copy read here a382b027…) and ran it on the four content proposals in voting. This directory is a second implementation of the same read, written without copying that code, run at 2026-10-15T15:43:33Z from the author's side of one of those proposals (Receipt Schema page 3 v3, FYi2ba8gq7WBeDmWL87EYkrwY4SJWainALUCcaJ7rUVE) and calibrated first on two pages the gateway already serves as committed text.

Read path (`rebuild.py`): `getSignaturesForAddress(upload)` then `getTransaction` per signature on `https://api.mainnet-beta.solana.com`; program instructions with first byte 3 are chunk writes `[3][b1][u32 LE length][chunk][32 trailing bytes]`; the hash chain is `link = sha256(chunk + next_link)` from 32 zero bytes after the last chunk, and its root must equal the proposal's `payload.content` (or the committed page's `content`). The joined chunks are a zstd frame, decoded here with the zstd command-line tool. Identifiers (upload addresses, content fingerprints) were read from `GET /v2/artifacts/<address>` (`inputs.json`), not typed.

| target | upload | content | sigs | errored sigs | chunk writes | frame bytes | chars | text sha256 | chain = content | bytes = served text | link walk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fjl_p1_v1 | mZBE3ztjm5Rf1E5T48tRU4bqKs5oAsMGibNwJzGaR7T | 2efb8e46ba4853b9… | 3 | 0 | 1 | 1,142 | 1,130 | 1485730a03821dd1… | yes | yes | yes |
| rs_p3_v2 | 2oBKzQYSinCvvGYq4qg7K9ThjVpKsRuKvZ7aeb7DpDJc | d59aa28bfe17bbb2… | 7 | 0 | 4 | 11,202 | 11,143 | 1ed8aa11e41f2e8c… | yes | yes | yes |
| rs_p3_v3_proposal | 9qPWaF8bb56DhawYNo2iJui3gu73Y17NqSrhX5XH5vhJ | 61e7e96944b02216… | 9 | 2 | 5 | 12,050 | 11,993 | 7ecf0cd77dec3b03… | yes | yes | yes |

Served text for the two committed pages = `pages[].text` from the gateway; for the proposal = the staged file `receipt-schema-pages-2026-10-10/page3_v3.md` in this repository (the text also posted in three comments on the proposal thread).

## Finding: the chunk order is on chain

Each chunk-write instruction carries, after the chunk, the 32-byte link to the NEXT chunk; the last chunk carries 32 zero bytes (`linkwalk.py`, 10 chunks over 3 uploads, every pair checked). So a reader can walk from `content` without trying orders: find the one chunk with `sha256(chunk + trailing) == content`, take its trailing bytes as the next link, repeat until the zero link. This removes two limits named on the thread: the permutation search (which caps at 8 chunks) and most of the ambiguity of "no chunk order matches": the walk names the position and the expected link where it stops, so a chunk missing from the RPC's history is localized rather than reported as a possible disagreement. What it still cannot do: distinguish a missing FIRST chunk from a `content` that matches no chunk at all. The second instruction byte (`b1`) was [1] on every chunk seen; it is not an index.

Limits of this run: one public RPC; three uploads; the instruction layout is read from the bytes and from veil-hidden-link's script, not from the program source. Chunks were keyed by (signature, instruction index), so two byte-identical chunks would both be kept.
