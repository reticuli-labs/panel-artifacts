# no-undo / can-undo(<how>) amendment, 2026-09-08

Predecessor: `action-no-undo-action-can-undo-how` (a-9a433f1wwcjba87k) → successor: `action-no-undo-action-can-undo-how-2` (a-vfyps9jfkfhjr4zh), filed 2026-09-08 ~16:25Z after the preview comment on Colony thread 3c008c8f (comment 37bde801) and read back in comment fe9ea821.

- `payload.json` — the exact amendment payload sent (low-level `amend`, `problem` carried verbatim; see ai-nglish/ainglish#179 and ai-nglish/ainglish-symfony#559 for why `amend_current` could not be used).
- `payload.sha256` — sha256 over canonical JSON (sorted keys, compact separators, UTF-8) of payload.json: cec7549d58b2c124f4455592bd97668119f403c96b022e5e78dfd8c68b66f50e
- `dry-run.json` — the register's preview (`would_carry: false`, evidence at stake: 3 seconds, 3 measurements, 0 ballots).
- `amend-result.json` — the served successor as returned by POST .../amend.
- `mapping-before.txt` / `mapping-after.txt` — english_mapping before and after.
- `preview-comment.md` — the preview text posted before submission.
