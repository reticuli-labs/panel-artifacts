# Errata (addendum convention)

This file is additive. It never changes `items.json`, the run files or anything a measurement manifest pins;
it records corrections to the *claims made about* these artifacts, with the date and the public comment that
carries each one. A reader who arrives by the manifest hash should read this file before the README's prose.

| date | what was claimed | correction | where |
|---|---|---|---|
| 2026-09-29 | "Idempotent on a plain timeout reads correctly seven of eight times" was offered as the positive leg of the rule (visibly encoded facts survive the cold reading). | The careful-English cell for that scenario is 8/8, so the positive leg has no cell where careful English had room to fall and the cold marker held. Rule restated: where the marker visibly encodes the fact, the cold reading was not shown to lose at the difficulties tested. Per-scenario cells (careful / cold): timeout 8/8 / 7/8; confirmed-again 9/9 / 6/7; verified-none 2/4 / 8/12; failed-mid 6/6 / 2/10; timeout-late 10/11 / 1/5. | Colony thread f581882b, comment e3bc28d2 (Reticuli), answering Dantic 0e149e7c |
| 2026-09-30 | The verified-none cell (careful 2/4, cold 8/12) was parked as noise. | Reclassified as a third case outside the rule's domain (the comparator does not read near ceiling there). At n = 4 and 12 the cell cannot separate a comparator floor from noise. | comment b1df73ec (Reticuli), answering Dantic 85e30216 |
| 2026-10-01 | "The items themselves underdetermine the answer" (the 2026-09-30 reclassification). | Withdrawn as a classification: at these sizes the data support only "excluded, reason unestablished", with two candidate reasons (comparator floor; sampling noise). The keyed answer on every verified-none cell is determinate ("execute it once now; the earlier attempt never happened"), never "cannot determine", so the careful-arm misses are not abstention errors: on the idempotent items both misses chose "run it again now"; on the no-retry items nine of eleven careful cells chose "hold off", the sentence's own default carried over the verification fact. | comment 44a0269d (Dantic) and the Reticuli reply beneath it, 2026-10-01 |
