# Errata

The bank and the results file are unchanged since their commits. This file records corrections to
the prose around them.

## E1 (2026-11-12, found by the author on re-reading the table, minutes after the results commit)

The README's first results paragraph said that in both sentences of every iteration pair the
multiplier and the word after it are the same, and that the proposal's patterns alone get pair 3
backwards. Both statements were wrong. In pair 3 the claim uses "longer" where the leave-alone
sentence uses "more", so the words are the same in seven pairs of eight. And both rules get pair
3 backwards, Excelsior's v1.0.0 as well as the proposal's patterns: each warns on O03a and passes
O03b. The counts in the table were right and have not moved.

## E2 (2026-11-12): a label that is a choice, and an independent replay. Raised by Excelsior.

**The replay.** Excelsior ran all 32 sentences of this bank through the unchanged scanner on the
live checker page and reported that every warning decision equals the `v1` column of
`results_v1.json`, on a bank whose SHA-256 is `90f45933…9051a8f` (the digest of
`outside_pairs_v1.json` here). The `v1` column in this directory was produced by my copy of that
rule, so until then nothing showed that my copy and the page agree. Excelsior's statement of the
result by group, 0 of 8 iteration pairs and 4 of 8 attachment pairs told apart, is what the file
holds.

**The label.** O04a, "The alarm rang five times more during the night.", is labelled as a sentence
to leave alone, on the reading "five more rings". Excelsior pointed out that alone it can also be
read as a comparison with some other night that is not named. That is right. The label is the
reading I judged likelier, and the README did not say a choice was made. The sentence and its
label are unchanged.

What the other reading would move, recomputed from `results_v1.json` with O04a counted as a claim:

| rule | as labelled | with O04a as a claim |
|---|---|---|
| Excelsior v1, claims warned | 11 of 16 | 12 of 17 |
| Excelsior v1, leave-alone warned | 8 of 16 | 7 of 15 |
| the proposal's patterns, claims warned | 8 of 16 | 9 of 17 |
| the proposal's patterns, leave-alone warned | 6 of 16 | 5 of 15 |

Pair 4 would then hold two claims and stop being a contrast, leaving seven iteration pairs, of
which neither rule tells any apart. No statement in the README changes direction.

Excelsior's proposal for a later test, kept here because it is his: hold this sentence fixed and
vary the context before it, so that the context and not the sentence decides the reading.
