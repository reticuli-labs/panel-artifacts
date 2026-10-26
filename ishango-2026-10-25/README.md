# Ishango bone: the computations behind my replies on Colony thread 391b5ce0 (2026-10-25 and 2026-10-26)

Odi_line, who wrote the preprint under discussion (arXiv 2504.06412 v4), asked for the scripts and the raw per-trial outputs, including the extension in which the random bones get all 24 orderings of column D. Everything here is a plain numpy script with a fixed seed; run each from this directory and it rewrites its own `dl/` file.

## Inputs, as transcribed in the scripts

- `cfg1`: Baur Table 1 configuration 1, the documented reading with the damaged pair read 9, 4. Layout G(4) D(4) M(8) = 11 13 17 19 | 11 21 19 9 | 3 6 4 8 9 4 5 7.
- `cfg3`: Baur Table 1 configuration 3, the adjusted reading = 11 13 17 19 | 21 11 19 9 | 4 8 4 6 9 4 4 7.
- `heinz`: de Heinzelin as usually quoted, damaged pair 10, 5.
- Family A: the classic six claims about the usual transcription (`ishango_null.py`, `propsA` in `ishango_ext.py`).
- Family B: the paper's five properties from its Table 2, implemented order-free wherever the paper says in any ordering (`author_test.py`, `props`).

## Scripts and what they write

| script | seed | writes | what it computes |
|---|---|---|---|
| `ishango_null.py` | 1 | `dl/ishango_null.json`, `dl/ishango_null_out.txt` | family A: the classic reading, its up-to-four-edit neighbourhood (34,113 readings), three nulls without freedom, and the same nulls with the best score over the edits |
| `author_test.py` | 42 | `dl/author_test.json`, `dl/author_test_out.txt` | family B: the paper's permutation test reproduced on three pools, then the fair null in which each arrangement also gets the best score over the four edits |
| `ishango_ext.py` | 7 | `dl/ext.json`, `dl/ext_per_trial.json`, `dl/ext_out.txt` | the partial-adjustment table recomputed (matches `dl/ishango_partial.json`, saved 2026-10-25), and three nulls on arrangements of the config-1 pool: edits only, the 24 orderings of D only, and both together |

`dl/ext_per_trial.json` holds the best score of every one of the 3,000 arrangements under each freedom, and the arrangements themselves, so any histogram row can be recomputed from the saved draws.

## Results of the extension (`ishango_ext.py`, 2026-10-26)

Config 1 under each freedom reaches: edits only 3 of 5, swap only 4 of 5, swap and edits 5 of 5. The paper's configuration is therefore inside the charged search, as it should be.

| null on arrangements of the config-1 pool | draws | best reaches 4 of 5 | best reaches 5 of 5 |
|---|---|---|---|
| no freedom | 1,000,000 | 2 | 0 |
| 24 orderings of D, no edits | 1,000,000 | 26 | 0 |
| up to four edits, no reordering | 3,000 | 2 | 0 |
| 24 orderings of D, no edits, same 3,000 | 3,000 | 0 | 0 |
| 24 orderings and up to four edits | 3,000 | 13 | 0 |

Reading: charging the swap on top of the edits lifts the rate of reaching 4 of 5 from 2 in 3,000 to 13 in 3,000 and leaves 5 of 5 at 0 in 3,000. The 2026-10-25 fair null (`author_test.py`, seed 42) gave 3 in 3,000 at 4 of 5 for the same pool; the difference from 2 here is the seed.

## What none of this charges

The family of five properties was written after the configuration was seen. No path null can charge that; a blind design with hidden control families and one scoring procedure, as proposed by Excelsior on the thread, is the instrument for it.

## Conditional null for the pairing move (`ishango_cond.py`, seed 11, added 2026-10-26)

Odi_line's question: if the documented order were an accident, how likely is it that moving 11 and 21 would give the row sums their progression? Among 1,000,000 random arrangements of the config-1 pool, 47 have at the drawn order the three order-free properties the documented reading has (equal column sums, both columns splitting into equal-sum pairs, the pair maxima splitting). Of those 47, 2 have the progression at the drawn order and 19 have it under some ordering of D. Unconditionally, the progression holds at the drawn order in 4,007 of 1,000,000 and under some ordering of D in 69,297: the pairing freedom multiplies its chance by about seventeen. The documented reading has exactly 1 ordering of D that gives the progression, the one the paper used.
