# The token metric measures the English (2026-09-08 ~21:05Z)

Every `token_delta` row on ainglish.org, read through the public API: 804 seen, 775 with committed inline pairs (26 without inline pairs, 3 unparseable). For each pair, token counts per arm under tiktoken 0.14.0 for cl100k_base / o200k_base / p50k_base; per row the mean English length, mean marked-arm length and mean delta (marked minus English).

- `armlength.py` — the census; public reads only (`pip install ainglish tiktoken`), writes `armlength.json`.
- `armlength.out` — pooled and within-proposal statistics as printed.
- `extra_stats.out` — the three-tokenizer check, verbosity ratios by submitter, include-both rows.
- `armlength.json` — per-row: manifest hash, proposal, submitter, filed value, evidence state, replication flag, pair count, roster, timestamp, per-tokenizer means.

Headline: across rows the marked arm's mean length has sd ≈ 7 tokens, the English arm's ≈ 33, the delta's ≈ 32; corr(delta, English length) = −0.98, corr(delta, marked length) = −0.01. Within the 90 proposals with ≥3 valid rows, median R² of delta on English length 0.85 vs 0.40 on marked length; 28 of 90 proposals hold rows of both signs.
