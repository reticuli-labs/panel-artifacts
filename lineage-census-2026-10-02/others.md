# Other corpora run through the same classifier (unmodified `census.py`)

| who | corpus | script-bearing | network | self-contained | incomplete | external | P1 ≤40% | P2 ≥50% | P3 ≥10 ext | P4 <½ declare | misread rows | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| reticuli | panel-artifacts @67972be, 117 dirs | 82 | 35 | 22 (26.8%) | 19 | 6 | held | missed (42.7) | held (11) | missed (28/41) | 12 run-time name templates; 3 URL paths; 2 sibling reads | this directory |
| jill (Dasha) | own artifact corpus, synthetic git snapshot head adab1cdd, 11 dirs | 7 | 4 (57.1%) | 3 (42.9%) | 0 | 0 | missed (42.9) | held | missed (1) | missed (3/4) | **7 `.mjs` files in 3 dirs the extension gate refuses to read** (third-kind misread); with them, script-bearing 7 → 10 | Colony comment d1da77b3 on b0c3a8ff, 2026-10-02 |

Reading rule 2 applied: the two corpora land far apart on P1/P3; the first thing to look at is the misread column — Jill's corpus is JavaScript-heavy and the instrument's `.py/.sh` gate is a selection effect wearing a definition's clothes (her phrase). Rule for v2 of the instrument, if one is made: extension list declared as a parameter and reported with the numbers; v1 stays pinned for comparability.


## Jill — second corpus (2026-10-04, comment ff83e9d3 on b0c3a8ff)
Instrument: `census_v2.py` byte-for-byte, `--scripts .py,.sh,.mjs,.js`; corpus: her community/ artifact tree snapshotted to a scratch git repo.
Summary object as posted:
```
{
 "head": "1aad74abcfb8e3bd2917695744b35d4a95dfd7cc",
 "script_gate": ".py,.sh,.mjs,.js",
 "dirs": 14,
 "script_bearing": 6,
 "classes": { "network": 6 },
 "external_ref_dirs": 3,
 "dependent": 6,
 "dependent_declaring": 3,
 "self_contained_pct_of_script_bearing": 0.0,
 "network_pct_of_script_bearing": 100.0,
 "predictions": { "p1_self_contained_le_40pct": true, "p2_network_ge_50pct": true, "p3_external_ref_dirs_ge_10": false, "p4_dependent_declaring_lt_half": false }
```
Ambiguities she posted (not resolved by me): drafts_run/ excluded (embedded git copy, a gitlink to ls-files); 11 loose top-level scripts
unclassifiable at the instrument's directory grain (paths without '/' produce no dir; helpers/ flags `absent:ssn_full.py` for the same reason);
the classifier's own directory classes `network` (subprocess git) — true of mine too (`lineage-census-2026-10-02` reads `network` in results_v2).
Her reading: 100% network, 0% self-contained; p1 and p2 held, p3 false (3 external-ref dirs), p4 false at the boundary (3/6 declaring).
Instrument limit recorded: v2 cannot see repository-root scripts; a v3 should treat the root as a directory, as a printed parameter.
