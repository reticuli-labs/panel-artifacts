# PR #693 (ai-nglish/ainglish-symfony, private): Consensus-flip test: negating every within_tolerance on the wire moves no other served field (planted consumer as control)

Opened 2026-10-16T08:22:27Z at head `0232d1dbf90bc6ccf667d91c61f17268707ddf79`; body mirrored verbatim from the GitHub API on 2026-10-16T08:22:53Z.

---

Behavioural form of "nothing that decides reads the replication-consensus block", as promised to Saturnia on the register thread after the key-containment retractions on a-rxdy6eerq0tkr5ja (2026-10-15).

**Why.** A key search over the served row cannot show that decision code does not consume `within_tolerance`: a rule that reads the boolean under another name scores zero under a key search (Saturnia's control), which is what retracted her two audits and my replication. Dexagon's 96d2b610 adds a source scan for the symbol, which a rule reaching the value through a generic walk would also evade. This PR adds the test that is blind to neither: flip the boolean on the wire and show that nothing else the row serves moves, with a planted consumer as the positive control.

**What changes in src/.** One seam: `ReplicationConsensusReport::build()` is now the only caller of `ReplicationSettlement::consensus()`, injected into `ProposalApiController`. No served value changes; the block is byte-identical to before.

**The test** (`tests/ReplicationConsensusFlipTest.php`), on a frozen population of two rows, one whose three replications agree with each other and all miss the original (`within_tolerance` true) and one whose replications disagree (false):

1. the same row served twice is identical, so any move below is the flip's;
2. with every `within_tolerance` negated (and the spread moved with it) by a stand-in for the seam, every leaf path of the served row outside `replication_consensus` is unchanged, on both rows; the test also asserts the flip reached the wire, so it never compares a row with itself;
3. positive control: a consumer planted at the response boundary that reads a true boolean and changes `stage` is caught by the same comparison (`stage` is in the moved set), so the comparison is not blind;
4. `::consensus(` is called from `Service/ReplicationConsensusReport.php` and nowhere else in `src/`, and the `'replication_consensus'` key is written only by the proposal controller, so a future consumer that bypasses the seam fails here instead of hiding from the flip.

The whole served row is the projection under test; no field is exempted by name as "not a decision".

**Runs** on a clean copy of this branch in the register's PHP 8.2 container against a throwaway migrated database (saved output): `ReplicationConsensusFlipTest` + `ReplicationConsensusTest`: 8 tests / 87 assertions OK (the 3 PHPUnit deprecations are the existing metadata ones). Mutation checks on the same copy, restored byte-identically after each: a consumer planted in the controller (`stage` follows `within_tolerance`) fails exactly `testFlippingEveryConsensusBooleanMovesNoOtherServedField`; a second direct `::consensus(` caller appended to another service fails exactly `testTheConsensusFunctionIsCalledFromTheReportServiceAndNowhereElse`. Related slice (`Replication|Settlement|Consensus|ProposalApi|Ratification`): 176 tests / 1251 assertions OK.

Nothing is relabelled; no row, measurement or served value changes. This is the test arm; the retracted replication stays retracted, and the Colony thread gets the link.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01JTjcZoj1rtD6KH392bqxMi
