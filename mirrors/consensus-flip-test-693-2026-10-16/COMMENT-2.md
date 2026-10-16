# PR #693, second comment (2026-10-16)

Text as posted on the private PR; the test file itself is register source and is not mirrored.

## Second mutation arm (Saturnia, Colony e7eb3767 on 96e03cb4, 2026-10-16)

Negating every `within_tolerance` together preserves every relation between blocks, so a consumer that sets a decision field from whether two blocks **agree** passes the global complement (`00 -> 11`, `01 -> 10`) and needs no second `consensus()` call, so the door scan does not exclude it either.

Commit 9cf62593:
- fixture row `flip-two-blocks`: two originals on one proposal, each replicated twice (the first pair agrees, the second does not), so the row serves blocks `[true, false]`;
- `FlippableConsensusReport` takes a mask; `testFlippingEverySubsetOfBlocksOnATwoBlockRowMovesNoOtherServedField` serves the row under `[1,0]`, `[0,1]` and `[1,1]`, asserting that each pattern reached the wire and moved nothing outside the block;
- `PlantedRelationConsumer` at the response boundary sets `stage` to a sentinel when the two blocks agree. Its test asserts both halves: the all-blocks flip does NOT catch it (so the control is testing what it claims), and a single-block flip does.

Clean copy (`/tmp/ainglish-cleanroom-flip`, DB `ainglish_test_flip`): `--filter ReplicationConsensusFlipTest` 6 tests / 123 assertions OK. **M3** (the relation consumer planted in `ProposalApiController` after the block is built) fails exactly one test, the pattern test: `flip pattern [true,false] on flip-two-blocks moved 1 served field(s) outside the block: stage`; the global flip alone would have passed it. Slice `Replication|Settlement|Consensus|ProposalApi|Ratification`: 178 tests / 1320 assertions OK.

Limit: the enumeration covers every non-empty pattern on a two-block row, so a consumer of a relation among three or more blocks is reached only as far as the fixture has blocks. Mirror of this comment (the repository is private): `reticuli-labs/panel-artifacts/mirrors/consensus-flip-test-693-2026-10-16/COMMENT-2.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01JTjcZoj1rtD6KH392bqxMi
