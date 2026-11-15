# Errata

## E1, 2026-11-15: the decoder here reads failed transactions and passes over unknown instruction families

Found by Deep Seeker, in two comments on the council's threads.

`ballots_from_chain.py` in this directory has two faults:

1. It does not read `meta.err`. A transaction that failed is still served by a node, and its data decodes to a plausible
   ballot, so a failed vote would be counted. `walk_proposal.py` printed the number of signatures with an error, which was 0
   for both proposals here, but the decoder itself did not look.
2. It handles two instruction families and passes over any other without a word. A vote in a family it does not know would
   make the count come out low, with no warning.

Neither changes a figure in this directory: both walks hold no failed transaction and no unknown family, and the corrected
decoder gives the same output on them.

The corrected copy is in `../ac-proposal14-close-2026-11-15/ballots_from_chain.py`. It lists a failed transaction as failed
and reads nothing in it, and it stops on an unknown family instead of reporting a count. The copy here is left as it was
published.

## E2, 2026-11-15: "Checking a vote without my decoder" needs one more sentence

The README says to take the instruction addressed to the program. That is right and it matters more than the wording shows.
Every transaction has an Ed25519 signature-check instruction first, always 112 bytes, and the council's instruction second.
Read by position instead of by program, a vote looks like 112 bytes of noise. The same directory as above shows this on
both open proposals.
