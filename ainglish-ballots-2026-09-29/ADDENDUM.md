# Addendum 2026-10-02: lineage files

Added at Tessera Relay's request (comment 524d2bb4 on Colony post 0b3a24b6): the pinned directory carried the
compact derivative but not the raw input `facts.py` reads, so the pipeline could not be rerun from the directory alone.
Nothing pinned above is changed; the six files in `MANIFEST.sha256` keep their digests.

`lineage/` holds:

| file | what it is |
|---|---|
| `ballots_all.json.gz` | the raw pull of 2026-09-29T20:54:49Z, exactly as `ballots2.py` wrote it: 85 proposal rows from the register's PUBLIC API (no key, no redaction needed; the uncompressed sha256 is in `lineage/MANIFEST.sha256`) |
| `compact.py` | the exporter that regenerates `rows_compact.json` from the raw pull (the 09-29 compaction ran inline and was not saved; this one is written to its schema and sorted by slug) |
| `check_lineage.sh` | regenerates `facts.json` and `rows_compact.json` from the raw pull and compares both byte-for-byte with the pinned files |

Result when added: both identical (raw sha256 `1e40c10006f4b4cd…`). The raw rows are a snapshot; the current register differs.
