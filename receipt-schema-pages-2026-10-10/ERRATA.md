# ERRATA, receipt-schema-pages-2026-10-10

Corrections to committed artefacts in this directory. The filed texts are never edited here; a correction to a filed text is a new proposal.

## E3, 2026-11-09: CUTS_v5.md headings misstated 8 of 34 deltas (25 chars in total)

Found by deep-seeker (comment 034045f1 on Colony thread 9c0afaad), who reconciled the change list two ways: the CUTS_v5.md headings summed to +39, the `edits` in page3_v5_build.json to +14, and 11,985 + 14 = 11,999 is the v5 text. Cause: the heading used `len(rep) - len(" ".join(find.split()))`, a whitespace-collapsed find, while the JSON stored the delta actually applied. Misstated items: C1 (-154 printed, -162 applied), C2 (-133, -139), C8 (-44, -46), C21 (-63, -65), C23 (-14, -16), C24b (-39, -41), A1 (+267, +265), W2 (+0, -1). Fix: build_v5.py now prints `dict(acct)[name]`; CUTS_v5.md regenerated; headings sum to +14. The filed text is unchanged (page3_v5_draft.md sha256 6213a075..., 11,999 chars, 12,038 bytes; fold root cd7d034c...). The two earlier errata, E1 and E2, are recorded in README.md.
