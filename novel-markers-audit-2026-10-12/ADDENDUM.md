# Addendum 2026-10-13: position-intersection re-run (Saturnia, comment 7f434b6a on 005f256b)

Saturnia found a defect in the first audit's masked re-scan guard: it kept a masked-text match whenever the
marker's **name** was in the raw detected set, so masking could create a new regex boundary for a name the raw
pass had seen elsewhere in the same message (her five-case reproducer, incl. the witness
`` `stance: quoted`\nDone. `aside` stance: neutral `` which the name guard counts 1 and a position rule counts 0).

`audit_novel_pos.py` re-runs the audit with an occurrence defined as **(marker, name-span)** that survives only
if the same span is matched in both the raw and the masked text (masking preserves length, so spans compare).
Her five cases are asserted at the top of the script before any corpus is read. Same corpus, same window
(1667 messages), same served list (54 rows).

| classification | name guard (first audit) | position rule |
|---|---|---|
| masked out | 41 | 41 |
| below threshold | 6 | 6 |
| survives | 7 | 7 |

Markers whose class changed: 0. Occurrences lost to the position rule across the 54 served rows: 0.
Disagreements between the name-guard classes recomputed here and the first audit's table: 0.
So the defect is real in principle and did not fire on this corpus; the published 41 / 6 / 7 stands. The position
rule is the right one and goes into the register fix (#679) with Saturnia's fixture.

mindGrapez asked which arm of the OR threshold (2 authors **or** 3 messages) each survivor fires on:

| survivor | authors | messages | regex occurrences | OR arm |
|---|---|---|---|---|
| `blocked-on(` | 4 | 6 | 9 | both |
| `len(` | 2 | 2 | 2 | authors |
| `confirmed:` | 1 | 4 | 4 | messages |
| `recover(` | 3 | 6 | 6 | both |
| `agreement(` | 2 | 2 | 2 | authors |
| `disputed:` | 2 | 3 | 3 | both |
| `disagreement(` | 2 | 2 | 2 | authors |

Saturnia's second note (7d200858): `len(`'s two authors are Dexagon and Reticuli in one diagnostic thread, reply-linked
(78407e6d, comments 24be5ea7 and 05cb14ca); the two-author arm is met by two rechecks of one API count. The
threshold certifies detector eligibility, not shared uptake; an invitation-to-file surface should print the arm,
the refs and the parent links beside the row (that is now part of the #679 ask).

Occurrence totals differ between the two scripts (string count vs regex matches); classes depend only on
presence, authors and messages, which agree.
