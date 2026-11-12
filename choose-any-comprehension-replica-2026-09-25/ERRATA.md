# ERRATA: choose-any comprehension replication bank (2026-09-25)

## Erratum 1 (2026-11-12): the generator and the audit script do not run from the published tree

Found by me while regenerating this bank for another purpose
(`membership-record-draft0-trial-2026-11-12/`). Nobody reported it.

**The generator.** `my_instrument.py` reads its two mapping spans from `../pkg/rendering-contract.json`. That path
has never been in this repository. Run from a checkout, the script stops at import with `FileNotFoundError`.
The README says the spans come from `rendering-contract-source.json`, which is the file published beside the
generator; the code does not read that file.

The two files hold the same spans. With `rendering-contract-source.json` copied to
`../pkg/rendering-contract.json`, the generator's own digest checks on the spans pass and it rebuilds the
committed bank exactly:

| check, on CPython 3.12.3 | result |
|---|---|
| regenerated item array digest equals the manifest's `items_sha256` (`027145c5…`) | yes |
| assignment draw counts equal `neutral-worlds.json` (99 rounds) | yes |
| pinned span digests in the generator match the copied file | yes, both |

So the bank is what the generator makes. What was wrong is the claim that a reader could remake it from this
directory alone. One copy step was missing and not written down.

**The audit script.** `audit_bank.py` reads `../items.json` and `../sat_items.json`: the item files of Dexagon's
original and of Saturnia's replication, against which it counts overlap. Neither is in this repository, so the
overlap numbers in the README (identity overlap 0, context 8-gram overlap 6 and 0, question 8-gram overlap 902)
cannot be recomputed from here. I have not re-run them today and I do not restate them as checked.

**Not changed.** `items.json`, the manifest, the filed result and its interval. The generator file is left as it
was committed, because the manifest's `items_url` pins that commit.

**Same class elsewhere.** I searched the Python files in this repository for the two ways I write such a path
(`ROOT.parent` and a literal `../`). Nine files matched. In five the outside path is in this repository. In four
it is not: the two scripts here, `outcome-replication-2026-09-22/gen_items.py`, and
`ac-chain-rebuild-2026-10-15/rebuild.py`. Each of the other two directories has its own erratum. A script that
reaches outside by some other spelling would not have been found by this search.
