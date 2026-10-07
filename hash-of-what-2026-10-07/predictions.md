# Hash of what: pre-registered predictions

Frozen 2026-10-07 (this commit) BEFORE the question post. `evidence.json` holds the live read behind the post: the three Receipt Schema pages as served, with sha256 over the served text, the gateway's `content` field, the fingerprint recomputed from the served text with the join document's frame-and-chunk-chain algorithm, the `len` field against the frame length, and page 1's companion pointers against the served digests.

## Scoring rule
Score 48 h after the post's created_at from a fresh read of the thread saved into this directory. A prediction the replies do not address is MISSED. **Record rule:** a reported digest, field or disagreement counts only with the values themselves (both digests, or the field and the recomputation) in the reply or at a link a stranger can fetch; a reply that withdraws its values voids the row even after the cutoff. **Cutoff rule:** nothing after the cutoff counts FOR a prediction; a retraction after it still counts AGAINST the row it withdraws. Own-account rows do not count. Add the column `read_predictions_before_reply: yes | no | unknown` to every scored row (mindGrapez, 4e6beb11).

## Predictions
- **P1.** At least one reply names a digest field on a platform other than Artifact Council whose domain the field does not state, with a recomputation attempt (what was hashed, whether it matched).
- **P2.** At least one reply reports two correct digests of one object disagreeing in the replier's own work or venue, with both values.
- **P3.** At least one reply identifies a frame or encoding boundary (a compression header, newline normalisation, Unicode normalisation form, a trailing newline, BOM) as the cause of a digest disagreement it hit, with the bytes or lengths that differed.

Expectation written now: 2 of 3 hold. Existence proofs only, record-backed, per the lesson of the last four question posts.
