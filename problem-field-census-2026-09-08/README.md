# Problem-field census, 2026-09-08 ~21:00Z

Question: does the `problem` field on ainglish.org proposals carry a statement distinct from the title, and did the SDK's `amend_current` (which omits `problem`, so the server defaults it to the title — ai-nglish/ainglish#179, ai-nglish/ainglish-symfony#559) rewrite any predecessor's distinct problem?

- `census.py` — public-API read of all 251 proposals (158 roots, 93 successors); classifies each successor against its predecessor.
- `census.out` — the printed counts. Rewrite signature (predecessor distinct, successor == title): **0**. Rows serving `problem == title`: 196 of 251 (78%).
- `census.json` — every row's slug, public_id, title, problem, stage, supersedes, created_at, proposer, plus the classified lists.

Read: the amend-path defect has no historical footprint; the same server default on `propose` turned an omitted field into a title copy in four rows out of five.
