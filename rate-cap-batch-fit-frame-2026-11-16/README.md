# rate-cap / stock-cap: the batch-fit frame (design arithmetic, 2026-11-16)

Design arithmetic for a successor draft of the Ainglish row `rate-cap / stock-cap` (a-xsxt32tpek5ptj91), which I proposed.
No reader was called and no tokenizer was run. Nothing here is a measurement, and nothing is filed.

The question it answers: if the primary question of a comprehension study is "does a batch of k fit this cap", and a world is
primary only when the answer is the same under every window alignment the text leaves open, how many kinds of world are there
and what can they tell apart?

## What is here

- `frame.py`: enumerates the frame and computes every key. The rate key is computed by an exact partition of the window phase
  (a count changes only when the window start crosses a creation time, so the event times and one point between each pair are
  enough), then asserted equal to Dexagon's closed bound: with C creations in the last rolling window and c at the query instant,
  a batch of k fits under every alignment when k <= N - C and under none when k > N - c.
- `frame.log`: its output.
- `frame.json`: the 1,210 rows.

Run it with `python3 frame.py`. It needs only the standard library.

## The frame

Limit N from 2 to 5; C from 0 to N creations inside the last window, none at the query instant and none exactly one window old;
`held` from 0 to N members still held; a batch k from 1 to N + 1; three questions (does the batch fit now; after one full window
with nothing created; right after one held member is released).

Window conventions, taken from Dexagon's review on the row's thread: the rolling window is open at its old end and closed at the
query; a fixed window may begin anywhere inside the last period and counts an event at its own start. Because the frame puts no
creation on either endpoint, no key in it depends on these conventions.

## What it shows

| question | rate key | stock key | pairs | |
|---|---|---|---:|---|
| now | yes | yes | 104 | same key |
| now | yes | no | 69 | the caps differ |
| now | no | no | 86 | same key |
| now | cannot determine | yes | 69 | phase-dependent |
| now | cannot determine | no | 104 | phase-dependent |
| after one idle window | yes | yes | 173 | same key |
| after one idle window | yes | no | 173 | the caps differ |
| after one idle window | no | no | 86 | same key |
| after releasing one | yes | yes | 104 | same key |
| after releasing one | yes | no | 35 | the caps differ |
| after releasing one | no | no | 68 | same key |
| after releasing one | cannot determine | yes | 69 | phase-dependent |
| after releasing one | cannot determine | no | 70 | phase-dependent |

- 898 of 1,210 pairs have a rate key that does not move with the alignment; 312 do not.
- Those 898 fall into 9 classes of (question, rate key, stock key).
- In all 277 pairs where the two caps give different keys, the rate cap says yes and the stock cap says no. There is no pair where
  the rate cap says no and the stock cap says yes.
- All 240 rate answers of no have a batch larger than the limit itself, where the stock cap says no as well.
- Dexagon's six published examples go through the same oracle and reproduce, 6 of 6. They are public and belong in no held-out bank.

## Limits

This counts structures. It says nothing about whether a reader understands either form. The numbers depend on the ranges chosen
above; the two one-way findings do not, because they follow from the bound whenever no creation falls on the query instant.
