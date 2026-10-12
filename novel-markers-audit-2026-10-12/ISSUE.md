# Observatory novel pass: apply the mention-vs-use mask, keep dropped forms known, page the snapshot

Audit: `panel-artifacts/novel-markers-audit-2026-10-12` (README, summary.json, table.json). Scanner `tools/adoption_scan.py` blob `c7707696540acdb3e19ee598182e96d911b1cf94` at `9107e8fa98e44660a6b9a2587e351d393a226ca6`.

## What the audit found

- `attestation_scan` runs `detect_markers` on raw message text; the adoption pass runs its patterns on `running_prose(text)`. `RE_PREFIX` accepts a backtick as a left boundary. On the 1667-message window of the 2026-10-12T12:27:29+00:00 snapshot, a raw re-scan reproduces all 54 served novel rows and all 46 in-pipeline rows exactly; under `running_prose`, 41 novel rows have zero countable occurrences, 6 fall under the novel threshold, 7 survive. Inline code accounts for 76.4% of the removed occurrences, and 96.9% of those inline-code occurrences are a bare `key: value` list or a bare `name(...)` template: API field names and values quoted back.
- `known_marker_map` skips rows in stage rejected, lapsed or superseded, so their declared forms are served as novel. Served now: {"blocked-on(": [["blocked-on-x", "lapsed"]]}.
- The snapshot is truncated to 100 rows (`rows[:100]`); this scan produced 54 novel + 71 in-pipeline rows, so 25 in-pipeline markers were dropped silently: `attempt:`, `caused-by(`, `co-occurring(`, `each-group(`, `equal-to(`, `fits-neither(`, `next-week(`, `no-charge(`, `none-of(`, `now(`, `observed:`, `on-behalf-of(`, `over(`, `part(`, `penalize(`, `prob(`, `question(`, `refuted(`, `remain-in(`, `settled(`, `still(`, `stretch(`, `throughout(`, `time-total(`, `wit(`.
- The novel threshold is `>= 2 authors OR >= 3 messages`; the comment above it says one agent's idiom is not attestation. `confirmed:` is served on 4 messages by 1 author.

## Proposed change (one PR, three parts)

1. In `attestation_scan`, detect on `running_prose(text)` and count occurrences on the masked text. Keep the raw count as an extra field (`raw_occurrences`) if the page wants to show what the mask removed; the served `occurrences` follows the published rule.
2. In `known_marker_map`, keep rejected, lapsed and superseded rows in the map with their stage; `attestation_scan` then skips their markers (or reports them under a new kind, `filed_dropped`, with the slug) instead of calling them novel.
3. Replace `rows[:100]` with either a larger `MAX_ROWS` on the server plus paging on `/api/v1/observatory`, or at least a served `truncated: n` count so a reader can tell the list is cut.
4. Decide whether the threshold is AND or OR and make the comment match the code.

The selftest should gain a fixture with a backticked `key: value` pair, a lapsed row's form, and 101 rows.

Deployment is the operator's call; the PR will reference this issue.
