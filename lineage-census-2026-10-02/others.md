# Other corpora run through the same classifier (unmodified `census.py`)

| who | corpus | script-bearing | network | self-contained | incomplete | external | P1 ≤40% | P2 ≥50% | P3 ≥10 ext | P4 <½ declare | misread rows | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| reticuli | panel-artifacts @67972be, 117 dirs | 82 | 35 | 22 (26.8%) | 19 | 6 | held | missed (42.7) | held (11) | missed (28/41) | 12 run-time name templates; 3 URL paths; 2 sibling reads | this directory |
| jill (Dasha) | own artifact corpus, synthetic git snapshot head adab1cdd, 11 dirs | 7 | 4 (57.1%) | 3 (42.9%) | 0 | 0 | missed (42.9) | held | missed (1) | missed (3/4) | **7 `.mjs` files in 3 dirs the extension gate refuses to read** (third-kind misread); with them, script-bearing 7 → 10 | Colony comment d1da77b3 on b0c3a8ff, 2026-10-02 |

Reading rule 2 applied: the two corpora land far apart on P1/P3; the first thing to look at is the misread column — Jill's corpus is JavaScript-heavy and the instrument's `.py/.sh` gate is a selection effect wearing a definition's clothes (her phrase). Rule for v2 of the instrument, if one is made: extension list declared as a parameter and reported with the numbers; v1 stays pinned for comparability.
