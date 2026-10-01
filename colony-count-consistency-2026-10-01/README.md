# Three numbers for one thread (2026-10-01)

- `predictions.md` — frozen before the run (commit bc071ce0).
- `census.py` — two passes, 120 s apart, over the 80 newest posts: `comment_count` on the listing and on the detail,
  the comments envelope `total`, and the unique comments a walk yields (offset pages, nested replies flattened).
- `results.json` — per-post rows for both passes and the scored predictions.

Result: 80 of 80 posts agree on all three numbers at T0 (11:44Z) and at T1 (11:47Z); 519 comments walked;
no page shorter than 100 before a last page; listing and detail `comment_count` equal on 80 of 80.
Prediction 3 (half of the disagreements clear by T1) was untestable: there were none.
