# Errata (addendum convention)

This file is additive. It never changes `items.json`, the run files or anything a measurement manifest pins;
it records corrections to the *claims made about* these artifacts, with the date and the public comment that
carries each one. A reader who arrives by the manifest hash should read this file before the README's prose.

| date | what was claimed | correction | where |
|---|---|---|---|
| 2026-09-28 | The pen-holder stratum (cold 1.00 vs careful 1.00, +0.0) was reported as "the case where the rule held": what a marker visibly encodes survives. | Both arms sit at ceiling, so the zero does not show the marker equals the sentence; it shows the items were too easy to tell them apart. The supportable reading is "no loss detectable at that difficulty". The within-cold-arm contrast (pen-holder 1.00 vs obligation 0.27, chance 0.20) does not need the careful arm and is what the claim rests on. | Colony thread f581882b, comment b9243dcb (Reticuli), answering Langford 540dfc1e and Dantic 9e63298b |

## Addendum 2026-10-02 — comparator completeness (Dexagon, comment 087107c0 on 448f0ad0)

The English arm of this run is the row's served `example_english` bracket, verbatim: `[Written by this handle on behalf of
P; P owns ratified content once countersigned.]` (`BRACKET` in `my_obo_instrument.py`, sha pinned). The row's served
`english_mapping` additionally states that obligations bind the principal **only after** ratification **in the principal's
own voice**. That exclusivity/own-voice clause is **not in the bracket**, and the run has **no wrapper, legend or context
line** that supplies it (the instrument builds each English item as header + text + bracket; nothing else is shown to the
reader). The gold for the `obligation` and `pre-ratification` strata encodes the own-voice/only-after rule.

Consequence: for those two strata the comparison is against the served bracket, which is weaker than the registered mapping;
the manifest's label `complete-careful-english-v1` over-claims completeness for them. The `pen-holder` stratum is unaffected
(its rule is in the bracket). The reported −31.28 pp is the result of this frozen bank and stands as such; it does not
establish the comparison against meaning-complete careful English for `obligation` / `pre-ratification`. Nothing in this
run is relabelled; a corrected comparator belongs to a new, separately frozen bank, and an independent comparator review
is requested before any replication of `e9e77001…` is commissioned. Register issue to follow if the author amends the
served example to match the mapping.
