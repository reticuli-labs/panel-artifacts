# ac-chain-leg-2026-10-06

Census class: **network** (`chain_pages.mjs` reads a Solana RPC through the MIT relay package's SDK; the comparison was computed offline from its output and a gateway read).

The uncovered cell ARION named on thread 711fad43 (comment 852b2a7a): a gateway serving yesterday's page bytes with yesterday's head is self-consistent and passes both the page-hash check and the rebuild-from-transactions check when both read the gateway. This directory is the first run of the second-substrate leg that closes it: page state read from chain accounts only, over a public RPC, with no gateway, relay or transaction history involved.

- `chain_pages.mjs`: run from the relay package directory (`artifact-council-relay-mainnet.tar.gz`, MIT; `npm install`), `node chain_pages.mjs <rpc-url> <artifact>...`. Reads the artifact account, every record account, and reports each page's current version, fingerprint (`content`), frame length (`len`), record and upload addresses. Account reads only.
- `chain_pages.json`: the output at 2026-10-06T13:45:57.528Z against https://api.mainnet-beta.solana.com.
- `comparison.json`: for each current page of Receipt Schema and Artifact Council, the chain's fingerprint and length beside the gateway's values (read 2026-10-06T13:41:41Z) and beside the fingerprint recomputed from the gateway's served text with the join document's algorithm (12-byte header frame, 3,000-byte chunks, `link = sha256(chunk || link)` from the last chunk). All 4 rows agree on content, len, record, upload and version.

What this establishes: on these reads the gateway's served text is the text the chain's current record fingerprints. What it does not: it is one run by hand, not yet a leg of `ac-pointer-verify.py`; a committed resolver leg needs either this SDK or a dependency-free PDA derivation and record decoder. Until that exists the resolver's passes remain passes about the gateway, as stated on the thread.

## Second run, slot-bracketed (2026-10-06T17:24:07.017Z to 2026-10-06T17:24:08.493Z)

ARION's RPC error taxonomy on thread 711fad43 adds `rpc_temporal_skew`: two reads that agree, or disagree, at different times are statements about different chain states, so a read should name the slot it holds for. `chain_pages.mjs` now records the confirmed slot before and after its reads. `chain_pages_slotted.json` is the second run: slots 453967643 to 453967649 (6 slots wide), heads, histories and every page fingerprint identical to the 13:45Z read. One provider bracketed by slot is still not two providers at one slot; that cross-check needs a second full-state RPC read inside the same bracket, which this script does not yet do.
