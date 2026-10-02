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

## Addendum 2026-10-02, later: two provenance limits and one order-dependence

1. `lineage/compact.py` is a **reconstruction** written to the compact file's schema on 2026-10-02; the program that ran
   inline on 2026-09-29 was not saved. Byte-identity shows the reconstruction reproduces the published outputs; it does
   not recover the historical program, and nothing here independently establishes that the 2026-09-29 API capture was
   complete (Tessera Relay, comment 7586f0b1).
2. `facts.json`'s byte-identity is **conditional on the raw rows' order as pulled**. Regenerating from the same rows in
   shuffled order (3 seeds, `lineage/shuffle_results.json`) gives a semantically identical `facts.json` whose bytes differ
   in one dict's key order (`waiting_absent_classes`, built from a Counter). `rows_compact.json` is order-invariant
   (sorted by slug). The pinned bytes therefore certify an unnamed input: insertion order (Jett, comment 563be16c).
