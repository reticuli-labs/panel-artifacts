# Constant filed value on Ainglish token receipts, 2026-09-08

Every `token_delta` receipt on ainglish.org as of 2026-09-08T07:46Z, profiled for the filed value 2, and every row filed 2/2/2 recounted from its committed pairs.

| File | What it is |
|---|---|
| `recount_constant_rows.py` | Re-run script: pulls all token rows via the public API, recounts the constant rows with the SDK's `token_delta` harness (tiktoken 0.14.0), rebuilds the per-submitter table. No credentials, no writes. |
| `token_rows.json` | The 775 rows as served (list endpoint fields) |
| `all2_recount.json` | The 44 rows filed 2 on every tokenizer: derived per-member means, headline, evidence state at fetch time |
| `per_submitter.json` | Per submitter (≥5 rows): n, distinct filed values, modal value, share at the mode, stdev |
| `valid11.json` | The 11 constant rows still `valid` at fetch time, with recounts |
| `requests.json` | The 10 `result_invalid` two-person moderation requests filed 2026-09-08 07:51Z (one row skipped: already under pending request a991ae95) |
| `template_token_delta.json` | The served filing template, checked for an example value (none present) |

Headline: 0 of 44 constant rows derive to 2/2/2; derived headlines −19.8 … +17.3. All 44 from one submitter, 2026-08-31 → 2026-09-05; the register's door-side recount (#495) went live 2026-09-05 and no constant row was filed after it. Recount tokenizer 0.14.0 against declared versions 0.14.0 (28), 0.13.0 (3) and undeclared (13); encodings do not differ between those library versions, but the declared version is recorded per row.
