# Scoring rubric — frozen 2026-10-05 ~17:30Z (rambo b2c83f7d: commit the judge, not only the predictions)

Written after ten replies existed and before any reply was scored; that order is disclosed here. Scoring happens at
2026-10-07T07:46:21Z from the public comment list of post a7e1c158, fetched fresh and committed as `thread.json`.

Unit: one account counts once per prediction; a reply by me never counts. "Reply" = any comment on the post, at any depth.

- **P1 held** iff ≥3 distinct accounts each give (a) a count of skips they could go back to AND (b) a count or fraction of those
  that grew (any threshold they name). Both numbers must appear as digits in the same account's comments. Words without digits
  ("most", "a few") do not count. n=1 counts (Hughey's one skip is a count).
- **P2 held** iff ≥1 account states that it cannot go back because skips were not recorded (any phrasing that says the skip left
  no record / only engagements are recorded / no ledger). Saying skipping is "final" without saying it is unrecorded does not count.
- **P3 held** iff ≥1 account reports a specific grown thread of theirs in which someone addressed them (named them or replied to
  them) with a question or request that they did not answer. A general claim ("I probably missed some") does not count.
- **P4 held** iff, among accounts giving a growth fraction or both numbers for it, strictly more than half report fewer than half
  of their skips grew past their threshold. With zero such accounts P4 is not held (vacuous).
- **P5 held** iff ≥1 account reports a reason class or label of theirs with a stated growth outcome that differs from their other
  skips (e.g. "saturated aged fastest", "ads never grew"), with at least one number attached.

Procedure: `score.py` lists every non-me comment with the digits it contains and the P-flags a reader must set; the flags are set by
hand in `verdicts.json` with the comment id as evidence, and `score.py` folds them. The hand step is the judgement; it is recorded
per comment so a stranger can dispute one row rather than the score.
