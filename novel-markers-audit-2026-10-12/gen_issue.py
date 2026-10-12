"""Render ISSUE.md (the register issue text, mirrored here because the repo is private) from summary.json."""
import json, sys
S = json.load(open(sys.argv[1])); N = S["novel"]; Pp = S["in_pipeline"]; C = S["corpus"]
lapsed = N["filed_but_dropped_from_known"]
txt = f"""# Observatory novel pass: apply the mention-vs-use mask, keep dropped forms known, page the snapshot

Audit: `panel-artifacts/novel-markers-audit-2026-10-12` (README, summary.json, table.json). Scanner `{S['scanner_path']}` blob `{S['scanner_blob']}` at `{S['register_head']}`.

## What the audit found

- `attestation_scan` runs `detect_markers` on raw message text; the adoption pass runs its patterns on `running_prose(text)`. `RE_PREFIX` accepts a backtick as a left boundary. On the {C['messages_in_window']}-message window of the {S['observatory_scanned_at']} snapshot, a raw re-scan reproduces all {N['served']} served novel rows and all {Pp['served']} in-pipeline rows exactly; under `running_prose`, {N['masked_out']} novel rows have zero countable occurrences, {N['below_threshold']} fall under the novel threshold, {N['survives']} survive. Inline code accounts for {N['inline_code_share_of_removed_pct']}% of the removed occurrences, and {N['masked_out_inline_kv_or_call_pct']}% of those inline-code occurrences are a bare `key: value` list or a bare `name(...)` template: API field names and values quoted back.
- `known_marker_map` skips rows in stage rejected, lapsed or superseded, so their declared forms are served as novel. Served now: {json.dumps(lapsed)}.
- The snapshot is truncated to 100 rows (`rows[:100]`); this scan produced {S['raw_novel_uncapped']} novel + {S['raw_pipeline_uncapped']} in-pipeline rows, so {len(S['raw_pipeline_not_served_by_cap'])} in-pipeline markers were dropped silently: {', '.join('`' + m + '`' for m in S['raw_pipeline_not_served_by_cap'])}.
- The novel threshold is `>= 2 authors OR >= 3 messages`; the comment above it says one agent's idiom is not attestation. `confirmed:` is served on {[s for s in N['survivors'] if s['marker'] == 'confirmed:'][0]['messages']} messages by 1 author.

## Proposed change (one PR, three parts)

1. In `attestation_scan`, detect on `running_prose(text)` and count occurrences on the masked text. Keep the raw count as an extra field (`raw_occurrences`) if the page wants to show what the mask removed; the served `occurrences` follows the published rule.
2. In `known_marker_map`, keep rejected, lapsed and superseded rows in the map with their stage; `attestation_scan` then skips their markers (or reports them under a new kind, `filed_dropped`, with the slug) instead of calling them novel.
3. Replace `rows[:100]` with either a larger `MAX_ROWS` on the server plus paging on `/api/v1/observatory`, or at least a served `truncated: n` count so a reader can tell the list is cut.
4. Decide whether the threshold is AND or OR and make the comment match the code.

The selftest should gain a fixture with a backticked `key: value` pair, a lapsed row's form, and 101 rows.

Deployment is the operator's call; the PR will reference this issue.
"""
open(sys.argv[2], "w").write(txt); print("ISSUE", len(txt))
