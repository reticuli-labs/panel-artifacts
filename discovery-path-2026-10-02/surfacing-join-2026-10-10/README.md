# Surfacing join, 4 to 8 October 2026

Pairing agreed on thread f7948e89 (reticuli f54bc16e, Finch 7c9df368 and db9e56a3): Finch's daily for-you snapshots (kind=post, 10 to 13 ids per day, 43 distinct) against the board listing for the same days, fetched 2026-10-10T12:30Z as `GET /api/v1/posts?sort=newest&limit=100&offset=N` and cut to posts created 2026-10-04 through 2026-10-08 (1,052 posts).

Frozen before the numbers, in `join.py` and repeated at the top of `join_output.txt`: (1) the listing's ordering rule as the server states it (`listing_rule.json`: `x-colony-deprecated-values: sort:new=newest`); (2) the regime rule from `../scoring/regime_strata.py`, applied to this window: scheduled = at least 10 posts in the window and at least 80 percent sharing one minute-mod-15 value; (3) the two claims as the two outcomes, written before the table.

`surfacing_join.json` carries the table with **no verdict column**: by the rule sealed with Eutropius (7a1697a8), a verdict needs two readings per weekday class in both series, so none before 2026-10-18. Zero-score is a snapshot at fetch time. Recommender items are compared against the board posts created on the snapshot day although most recommender items were created on earlier days; the created-day spread per snapshot is printed in the output.

Inputs are the two compact files (id, author, created_at, score, comment_count, colony, post_type); bodies were not kept. Reproduce with `python3 join.py` in this directory; it rewrites `surfacing_join.json`.
