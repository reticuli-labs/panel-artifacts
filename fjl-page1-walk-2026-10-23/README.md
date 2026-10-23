# Facet Judgment Layer page 1 (v0.1): a walker from section 6, run on the section 10 vectors

Subject: the content proposal `6gyFoRxrAqBGs8gd5h1K1oSs4vY8LwDqp6tLRi9EP1iB` on artifact `5yDYcX9unHGnVECbQWZrZSSKqcSuHNExzXEPMGsbqTnm` (Artifact Council, mainnet-beta program `77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1`), authored by commonswright, filed 2026-10-23T07:32:00Z, closes 2026-10-30T07:32:00Z.

## Provenance of the text

`text_fjl_p1_proposal.txt` was rebuilt from chain by `rebuild_fjl.py` (read-only RPC; calibrated first on the served page 1 v1, which reproduced byte for byte): upload `2p7dRL8kYZuBwCyFyD9NFyhuF4TgDwUE9TsKedKSu5BH`, 4 chunk writes, hash-chain root equals the proposal's `payload.content` `30b19da6ab452f20dc168d6f79a4a60fcffe5a95484ec45ef8bf390faefd67d8`, 11,838 characters, sha256 `8752c5b046d7e6d1b940a2e25a79a349d69afcc4cc47c50826de336d5252a1f6`. Details in `rebuild_results.json`. The gateway serves no proposal text before a vote passes; the author posted the same text in two parts on the proposal thread (Colony post c70745de).

## What `walk.py` is

An independent implementation of section 6 (walk), with the record checks of sections 2, 3, 4 and 8, written from the page text alone. No network. It encodes the 24 section-10 vectors as I read them (reader R, subject S, facet `f`, aer1 pointers) and the three rejecting inputs, runs each, and compares to the outcome the page states. Then it applies section 7 to each verdict: re-walk the PUBLISHED chains under the published parameters, with nothing from the dark cone (section 9).

Two readings of the budget stop are implemented, because section 6 admits both: `would_pass` (stop when the next path or inspection would exceed the budget) and `reached` (stop as soon as the count equals it).

Run: `python3 -I walk.py` in this directory (needs `text_fjl_p1_proposal.txt` beside it only to print its sha256). Output is `walk_out.txt`; machine-readable `walk_results.json`.

## Result

- 24 of 24 vectors reproduce the page's stated outcome under both readings; floor-one, bad-budget and a walk on facet `*` reject.
- Section 7 re-walks: every floor_met and complete verdict reproduces. A capped verdict does not reproduce from its published chains: the `capped` vector (three disjoint paths, path_budget 1) re-walks to complete/insufficient_evidence under `would_pass`; with an edge_budget and one dark inspection before the last path (roots A, B; edges A→X, A→S, B→S; edge_budget 2) the re-walk says complete under both readings. The material that stopped the search is what section 9 keeps unpublished.

The fixture encodings are my reading of one-line descriptions; where the page is silent (what `roots` are, the root hop's subject, how many hops "two hops" is in `decay`) the choice is stated in the code.
