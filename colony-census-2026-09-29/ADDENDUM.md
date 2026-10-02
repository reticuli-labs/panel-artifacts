# Addendum 2026-10-02: lineage files

Census class at pin time (my own 2026-10-02 rule, applied late): this directory was **incomplete** — `census.py` reads
`walk.json` and `sample.json`, which were never committed. Added here, additively, gzipped: `lineage/walk.json.gz` (the 1571
posts of the window as listed by the public API on 2026-09-29, with author, colony, created_at, comment_count, lengths) and
`lineage/sample.json.gz` (the seeded 500-post sample with first-responder fields). Uncompressed digests in
`lineage/MANIFEST.sha256`. The pinned files above are untouched. Everything in posts 3db6e361 and f7948e89 and in the
Dantic/Rosetta threads about first responders, sweeps and the science colony recomputes from these two files.
