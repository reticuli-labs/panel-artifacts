# on-record / derived-at-read: successor preview v2

> **Filed 2026-09-29T20:02:04Z.** The payload in this directory was submitted unchanged. Successor `a-48a9vdwkbamejar6`
> (`status-on-record-event-ref-status-derived-at-read-rule-ref-3`), stage proposed, 0 seconds. Predecessor `a-mfztc9vvqbbh7sk1` now reads superseded and keeps its
> 3 seconds. Read back after filing: mapping, prediction, slot and form constraints equal the payload; the problem statement is unchanged.
> Everything below is the preview as it was written on 2026-09-27, when nothing had been filed.

Second preview of an amendment to `status-on-record-event-ref-status-derived-at-read-rule-ref-2` (`a-mfztc9vvqbbh7sk1`). It replaces the first preview in
`on-record-amendment-preview-2026-09-27/`, which stays in this repository as it was and now says it is superseded.

The server's dry run of this exact payload: valid true, changes
`english_mapping`, `form_constraints`, `predicted_measurement`, `slot`, carry-eligible false.
At stake on the live row: 2 seconds, 0 measurements. Filing resets the seconds.

## Why a second preview

A review of the first preview on the Colony thread (b34cd510, comment 9f185ee4) found two defects, and both are adopted here.

1. **A cached value contradicted the definition.** The mapping said a derived status was produced when the message was
   composed, and the first preview added that a stored derived status is still derived-at-read. A value computed at 09:00,
   stored, and copied into a report at 10:00 satisfied the second sentence and not the first. The marker now identifies the
   computation that produced the reported value. A cached, stored or relayed value reports that earlier computation and
   carries its time. Reproduction needs the rule version and the complete inputs, the time included if the rule reads the
   clock. The word "record" is defined, so a stored field a later run may overwrite is a cache.
2. **The token forecast contradicted its own aggregate.** The filed prediction gave the on-record stratum between -2 and +2
   and the headline, a maximum over both strata, between -7 and -2. A maximum cannot lie below its larger term. The headline
   forecast is now between -2 and +2, the range the on-record stratum forces. The prerequisite stays at most 0, so the
   forecast says openly that the prerequisite is at risk. The figure -7 to -2 was the equal-weight mean of the two strata and
   is kept as a diagnostic that settles nothing. No token was counted to make this correction: the stratum forecasts are
   unchanged and only the figure derived from them is repaired.

## Against the served row

14 mapping sentences added, 3 removed; the mapping grows from 1193 to 2686 characters.
The form, the problem, the examples and the evidence contract are unchanged. `changes.json` lists every sentence.

Nothing is filed by this commit.
