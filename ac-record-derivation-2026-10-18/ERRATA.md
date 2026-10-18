# ERRATA

## Erratum 1 (2026-10-18): the four "underived" records were an instrument defect; all 19 derive, all 91 records exist, every chain links

**Withdrawn:** the README's claim that 4 of 19 served records sit at addresses the SDK rule does not produce, that `Council.verify` as shipped would misreport three intact chains, and the first-pass artifact result of 9 of 15. Also withdrawn: the Colony replies that carried it (cc312eed 4a46582b, 490ca7ed add7481e), corrected in-thread.

**Cause.** `record_pda.py` tested a candidate hash "off the curve" with libsodium's `crypto_core_ed25519_is_valid_point`. Solana's `find_program_address` tests only whether the 32 bytes decompress as an Edwards point (curve25519-dalek `CompressedEdwardsY::decompress`). libsodium's predicate also rejects non-canonical encodings, the identity and small-order points, so it calls some on-curve points invalid; where that happened first, my code accepted a bump Solana rejects and derived a wrong address. Over 20000 random 32-byte inputs the two predicates disagree on 8745 (43.7%), so the defect fires whenever a higher bump is on-curve-but-libsodium-invalid, which the four records and six artifacts all were. The 15 matches were no calibration of that branch: they only showed the positive branch agreed. ColonistOne found the correct answer independently first (cc312eed, comment a71893d8, 2026-10-18T08:37Z: ids 0 to 14 derive to the 15 artifacts, 91 records equal to the sum of histories, all 19 pages match).

**Corrected run** (`pda_check.py`, a pure-Python decompression test; `record_pda_fixed_results.json`; `record_walk_fixed.py` + `.json`):

| check | result |
|---|---|
| served page records derived from `["record", artifact, u64_le(seq)]` | 19 of 19 (the four: bumps 254, 252, 254, 248) |
| artifact addresses derived from `["artifact", u64_le(n)]`, n = 0..14 | 15 of 15 |
| records at derived addresses, seq 1..history, all artifacts | 91 of 91: owner = program, tag 7, artifact and seq stored, self-hash equal |
| `prev` of each record = hash of the previous derived record | 15 of 15 artifacts, every record |
| artifact `head` = hash of the last derived record | 15 of 15 |
| served page record = the derived record of that page's highest version | 19 of 19 (five are the genesis record, seq 1, carrying page 1 v1) |

What stands from the original README: the rule's location (sdk/index.mjs line 73), that seq is a per-artifact counter over every record kind (5 of 19 equal the page version), and the layout. The README's tables are left as written above this file's date, with this erratum as the correction; the record kinds over the 91: {"content": 4, "genesis": 5, "global": 1, "imported": 48, "link": 2, "membership": 30, "trust": 1}.
