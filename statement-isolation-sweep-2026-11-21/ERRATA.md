# ERRATA: statement-isolation-sweep-2026-11-21

Corrections to claims in this directory, made after the day of the sweep. The files themselves are not edited, except for one
pointer line under the title of `README.md`, added by hand on 2026-11-22 (`write_readme.py` does not write it).

## Erratum of 2026-11-22: two limits of this sweep that its README does not state

Found by me, when Vina and Hughey asked on the forum thread what the sweep leaves open, and I ran the mechanical readers they
proposed (`../degenerate-readers-2026-11-22/`, plan committed before the run).

**1. The null cannot see a position leak.** The reader is scored against its own answers shuffled among the items. A shuffle
keeps how often the reader picks each position and how often the key sits in each position, so agreement that comes from
position alone is inside the null. Two tested banks have the key in one position in every item, and `results.json` here shows
it: `approx-robust/rb3-robustness-v1.json` (key first in 24 of 24; blind 0 of 24, null 0.0, p 1) and
`rate-cap-bank-2026-10-10/items_undisclosed.json` (key last in 16 of 16; blind 14 of 16, null 14.0, p 1). "Not flagged" in this
sweep therefore never meant that position gives nothing away. Of the 57 banks it did not flag, 17 have a mechanical rule above
chance.

**2. "Cleared by its design" said more than the design gives.** The README says that where the same blind text, question and
options occur twice with different keys, no reader without the wording can get both. `contrast.py` compares the options as a
set. In all 4 flagged banks that I called cleared, the twins list their options in different orders (0 twin groups in one
order, of 144, 72, 40 and 40). What holds: no rule that reads the content can score above one half there; a reader for whom the
order says nothing about the key scores one half at most on average. What does not follow: a bound on a rule that reads the
order. On the order: in no-charge and send-snapshot the first and the last option are the key exactly at chance. In the two
storage-diag files the key sits only in places 1, 3 and 5 of 6, which narrows the choice from six options to three. Beyond that
I found nothing, and I have not shown that the order cannot give the key away. The label in `contrast.json` (`needs the
wording`) and the count of 4 stand as computed; read them with this.

Not changed: every figure and every file of this directory, apart from the pointer line named above.
