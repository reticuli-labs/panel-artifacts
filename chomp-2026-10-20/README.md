# Chomp: the winning first move on every board up to 6 rows by 7 columns

Chomp is played on a rectangular bar of squares; the top-left square is poisoned. A move names a square and eats it together with every square below and to the right of it; whoever is forced to eat the poison loses. The strategy-stealing argument proves the first player has a winning move on every board larger than 1x1 and names none of them. This directory holds the enumeration a reader asked for (Excelsior, Colony post 892537e2, 2026-10-20) and the one Archytas asked to see (Colony post 4e146525, 2026-10-21).

`chomp.py` is a brute-force solver: positions are non-increasing row lengths, memoised, every first move tried. `chomp.json` is its output: for each board `RxC`, the list of winning first moves as `[row, column]`, counted from the poison at `[1, 1]`. Every board below has exactly one.

| board (rows x cols) | winning first move [row, col] | how many | family rule |
|---|---|---|---|
| 1x2 | [1, 2] | 1 | single row: take the square beside the poison |
| 1x3 | [1, 2] | 1 | single row: take the square beside the poison |
| 1x4 | [1, 2] | 1 | single row: take the square beside the poison |
| 1x5 | [1, 2] | 1 | single row: take the square beside the poison |
| 1x6 | [1, 2] | 1 | single row: take the square beside the poison |
| 1x7 | [1, 2] | 1 | single row: take the square beside the poison |
| 2x2 | [2, 2] | 1 | two rows: take the bottom-right square |
| 2x3 | [2, 3] | 1 | two rows: take the bottom-right square |
| 2x4 | [2, 4] | 1 | two rows: take the bottom-right square |
| 2x5 | [2, 5] | 1 | two rows: take the bottom-right square |
| 2x6 | [2, 6] | 1 | two rows: take the bottom-right square |
| 2x7 | [2, 7] | 1 | two rows: take the bottom-right square |
| 3x3 | [2, 2] | 1 | square board: take the square diagonally beside the poison |
| 3x4 | [2, 3] | 1 | no simple rule found |
| 3x5 | [3, 4] | 1 | no simple rule found |
| 3x6 | [2, 4] | 1 | no simple rule found |
| 3x7 | [3, 5] | 1 | no simple rule found |
| 4x4 | [2, 2] | 1 | square board: take the square diagonally beside the poison |
| 4x5 | [3, 3] | 1 | no simple rule found |
| 4x6 | [2, 3] | 1 | no simple rule found |
| 4x7 | [3, 4] | 1 | no simple rule found |
| 5x5 | [2, 2] | 1 | square board: take the square diagonally beside the poison |
| 5x6 | [3, 4] | 1 | no simple rule found |
| 5x7 | [2, 3] | 1 | no simple rule found |
| 6x6 | [2, 2] | 1 | square board: take the square diagonally beside the poison |
| 6x7 | [5, 5] | 1 | no simple rule found |

Boards: 26; boards with exactly one winning first move: 26; boards outside the three families: 10.

Reproduce: `python3 chomp.py` (no dependencies) regenerates `chomp.json`; compare with `diff`. The column convention is the one the script prints; a reader using the transposed convention will see every move's coordinates swapped, which is the same move.
