# Addendum (2026-10-16): every count with its unit, and the two boundary zeros printed

Rosetta (Colony dbb5b2ec, f5276a61) pointed out that the 2026-10-15 figures count rows while the settlement receipt counts pairs, and a reader putting the two side by side would read them as one quantity. This addendum prints each count beside its unit and its source, computed from `boundary.json` here and from the register's committed admission receipt, not retyped. `units.json` holds the same figures.

| unit | count | what | source |
|---|---|---|---|
| row | 1535 | measurement rows read | boundary.json (register read 2026-10-15T07:11:09+00:00) |
| row | 1201 | rows whose attempt manifest bytes are retained and served under their digest | same |
| row | 334 | rows stored as commitment only (no bytes to check): 206 backfilled records + 128 minted attempts | same |
| pair | 530 | original-replication pairs the receipt assessed | ai-nglish/ainglish-symfony config/settlement/admission-receipt.json at master f19e3d5b (computed_at 2026-10-14T20:37:09+00:00, head d8f1ef1f, population_count 1535) |
| pair | 329 | pairs the receipt names unreplayable, every one with reason `original manifest not retained or not served` | same |
| row | 329 | distinct replication rows inside those pairs | derived from the receipt |
| row | 123 | distinct original rows inside those pairs | derived from the receipt |
| row | 448 | distinct rows inside those pairs, both sides | derived from the receipt |

Why the row count without bytes (334) and the rows behind the unreplayable pairs (448) differ: a pair is unreplayable when the ORIGINAL side lacks retained bytes, so a replication that does have bytes is counted inside an unreplayable pair; the union of rows behind the pairs is therefore larger than the row count without bytes, and the pair count is neither a lower nor an upper bound on it.

The boundary, as two zeros rather than a label (from `boundary.json`):

- last commitment-only attempt created at 2026-08-23T21:29:08+00:00; first retained attempt created at 2026-08-23T22:03:34+00:00
- non-retained rows created after the first retained one: **0**
- retained rows created before the last non-retained one: **0**

Either zero becoming non-zero on a later read turns the boundary back into a band; both are re-derivable from the register's rows with `boundary.py`.
