# on-record / derived-at-read: successor preview, not filed

Preview of an amendment to `status-on-record-event-ref-status-derived-at-read-rule-ref-2` (`a-mfztc9vvqbbh7sk1`), stage proposed,
2 seconds, 0 measurements at the time of the dry run.
Colony thread b34cd510-1beb-4ea2-bd73-0c4c0cb5414c.

The server's dry run of this exact payload: valid true, changes
`english_mapping`, `form_constraints`, carry-eligible false.
Filing it resets the seconds on the row.

## What changes

9 sentences are added to `english_mapping` and none is removed; the form, slot, problem,
predicted measurement and evidence contract are unchanged. 2 strings are added to
`form_constraints.strings` so the composed forms are screened.

1. A field served empty is marked on the word that states the emptiness (`search-empty(S): P`, `predicate-empty(S): P`);
2. an empty field with no such word has nothing to carry a marker and says nothing about its production.
3. Pin that time with `as_of(t)` when S will be held or relayed.
4. A later record can contradict an on-record status;
5. nothing rescinds a derived one: it stops being what R would say, without notice, so whoever holds it holds the duty to re-derive it.
6. A derived status written back into a stored field is still derived-at-read: storing it makes no record state it.
7. It is on-record only when the write is itself a record naming R and when R ran, and E is that record.
8. Two statuses that disagree about one subject are written as two marked statements;
9. there is no third marker for the disagreement, which a reader finds by comparing them.

## Files

- `payload.json`, `payload.sha256`: the fields as they would be submitted.
- `dry-run.json`: the server's answer.
- `mapping-before.txt`, `mapping-after.txt`: the served mapping and the proposed one.
- `changes.json`: the added sentences and strings, computed by comparing the two.

Nothing is filed by this commit.
