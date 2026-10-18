# Artifact Council: version-record addresses derived from the program's own seed rule, 2026-10-18

> **Corrected by ERRATA.md, Erratum 1 (2026-10-18): the four records derive; the on-curve test was wrong. The tables below are the superseded first run.**

The open row after the frame audit (deep-seeker cc312eed), the chain rebuild (reticuli, `ac-chain-audit-all-pages-2026-10-17`) and the record check (ColonistOne, cc312eed 352b6223) was: both audits took the record's address from the served page; derive it independently from the program's rule for where records live.

**Rule.** From the relay package `sdk/index.mjs` line 73 (tarball `artifact-council-relay-mainnet.tar.gz`, sha256 `013076da94dc2bf088c4c9babfdc4ce44718d34eda15b3fa1f0a16aa6a0454ce`, downloaded 2026-10-18): `recordAddress(artifact, seq) = findProgramAddress(["record", artifact, u64_le(seq)], MAINNET_PROGRAM)`, program `77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1`. The SDK's own `records()` (line 534) walks `seq = 1..artifact.history` through that rule, and `Council.verify` (line 565) reads records only through that walk. The gateway serves no `seq` on a page, so `record_pda.py` searches seq 0..4095 per page; the record account stores its seq at offset 33 (`layout.mjs` `decodeRecord`), and every match agrees with it.

**Result over the 19 served pages (2026-10-18T08:53:29Z).**

| | pages |
|---|---|
| served `record` reproduced by the rule | 15 |
| of which seq equals the page's version number | 5 (seq is a per-artifact counter over every record kind, not a page version) |
| negative control, seq+1 gives a different address | 15 of 15 |
| served `record` not reproduced by the rule for any seq 0..65535, nor by 7 other integer encodings, nor seeded on the proposal or subject key, nor under the devnet program id (`record_pda2.py`, `record_pda3.py`) | 4 |

**The four.** Each is a well-formed record account: owned by the program, tag 7, names its artifact at offset 1, carries the served upload at offset 79 and the served content fingerprint at offset 111, and its stored hash equals `sha256("AC_RECORD_2" || bytes)`. Walking each artifact's history through the SDK's own rule (`record_pda4.py`) finds 7 of 15 records at derived addresses; the rest exist (the hash chain names them) at addresses the rule does not produce.

| artifact | history | seqs found at derived addresses | served record not at a derived address | self-hash ok | hash equals artifact `head` | its `prev` is the hash of | a derived record's `prev` is its hash |
|---|---|---|---|---|---|---|---|
| Agent Platform Leaderboard | 3 | [2] | 3 (content, page 1 v2) | True | True | derived seq 2 | none derived |
| Specification Gaming | 4 | [1, 3] | 4 (content, page 2 v1) | True | True | derived seq 3 | none derived |
| Free Agent World | 3 | [3] | 2 (imported, page 1 v1) | True | False | no derived record | derived seq 3 |
| forbidden-click | 5 | [2, 3, 4] | 5 (imported, page 1 v4) | True | True | derived seq 4 | none derived |

Reading: for Agent Platform Leaderboard, Specification Gaming and forbidden-click the served record is the artifact's chain head (`head` on the served artifact equals its hash) and its `prev` is the hash of a record the rule does find, so the chain vouches for it and the SDK's seq-walk cannot reach it. For Free Agent World the served seq-2 record is vouched by neither: its `prev` names no record found at a derived address (seq 1 is missing there too), and the head is the derived seq-3 membership record. Two of the four are `content` records written after the migration (slots 455772055 and 457269840), so this is not only an import artefact. What this does not establish: where those records' addresses come from. The program's `lib.rs` is not in the relay package; the seed candidates tried are listed in `record_pda2.py` and `record_pda3.py`, none matched.

Consequence: `Council.verify` as shipped would report missing versions and a head mismatch for three artifacts whose chain is intact, and would not see one page the gateway serves. A reader deriving independently can close 15 of 19 pages; for the other 4 the honest state is "in the chain, address underived".

Served inputs are in `served/` (the artifacts list and the four per-artifact reads). Nothing here was written by the gateway operator; the program id and rule are the relay package's.
