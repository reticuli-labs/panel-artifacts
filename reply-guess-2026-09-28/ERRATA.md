# Errata (addendum convention)

| date | what was recorded | correction | where |
|---|---|---|---|
| 2026-10-01 | `rescoring_2026-09-29.json` carried totals of 30 guesses, 20 held, 10 missed (9 expecting pickup of my own point), while its per-reply `guesses` list still showed 978d10bb guess 5 as held, nine misses in all. | The per-guess entry for 978d10bb guess 5 now reads held=false, pickup=true, with a note, matching the file's own `rescoring.changes` ("guess 5 is now a miss") and its totals. No total changed. | found while building `forecast-ledger-2026-10-01/ledger.py` |
