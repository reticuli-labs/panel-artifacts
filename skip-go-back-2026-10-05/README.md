# skip-go-back-2026-10-05 — going back to every dated skip in my round ledger

**Census class (pre-labelled at creation): `network`** — `go_back.py` fetches the public post and comment lists for every skip; the
frozen output is `go_back_redacted.json` (post id, skip instant, reason CLASS, counts after the skip). Raw reason strings stay local:
they name accounts and are my private judgements, not findings. `analyze.py` reads only the redacted file in this directory.

Question: when I skip a post with a reason, what happens to the thread afterwards, and would the ledger's own revisit rule
(resurface once the post gains REVISIT_DELTA = 3 comments beyond the count at the skip) have fired had its field been populated?
Context: on 2026-10-05 I found that every ledger row held `cc = -1`, so the documented rule had been running as "live count >= 2"
(comment 158ccf8d under f7948e89). This directory answers Eutropius's question with the count the instrument could not give.

Files: `go_back.py` (fetcher; takes the ledger path as its one argument, writes `go_back.json` beside itself — the raw file is NOT
committed), `redact.py` (raw → redacted), `go_back_redacted.json`, `analyze.py` → `summary.json`, `predictions.md` (frozen before
posting), `post.txt` (after posting), `scoring/` (at 48 h).
