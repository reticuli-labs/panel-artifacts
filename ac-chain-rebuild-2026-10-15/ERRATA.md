# ERRATA: Artifact Council chain rebuild (2026-10-15)

## Erratum 1 (2026-11-12): the script reads a path that is not in this repository

Found by me in a sweep that started from the same defect in `choose-any-comprehension-replica-2026-09-25/`.
Nobody reported it.

`rebuild.py` reads the expected text of the page 3 proposal from `../round-20261015b-f1121a/page3_v3_raw.md`.
That directory has never been in this repository, so the script stops there when run from a checkout.

The README already names the right file: `receipt-schema-pages-2026-10-10/page3_v3.md`. Checked today: its
SHA-256 is `7ecf0cd7…9cfe4f`, the same as `text_sha256` for that proposal in `rebuild_results.json`. So the
published file is the text the rebuild compared against, and only the path in the script is wrong.

**Not changed.** `rebuild.py`, `rebuild_results.json` and the README. I have not re-run the rebuild today.
