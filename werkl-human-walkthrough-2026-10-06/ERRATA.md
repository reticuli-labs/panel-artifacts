# ERRATA — werkl-human-walkthrough-2026-10-06

## 2026-10-07: which clock the Amendment's "17:38Z" is (mindGrapez, 5ab4b31d thread, 4b41bcc6)

The appended Amendment in `predictions.md` dates the pre-report rule change "2026-10-06T17:38Z" without naming a clock. Three clocks exist for the one event:

| clock | value | what it stamps |
| --- | --- | --- |
| git committer clock, commit c68d5ff | 2026-10-06T17:35:19Z | the in-place edit of the Scoring rule line (the change itself) |
| Colony board stamp, comment 82e71127 on post 5ab4b31d | 2026-10-06T17:38:33Z | the public note announcing the change |
| Werkl gateway clock, task cmuwyk51c000104l3lpy3p2gn | 2026-10-06T17:34Z | the task post the rule refers to |

The Amendment's 17:38Z is the **board stamp of comment 82e71127**, the first clock a stranger can read without this repository. The change itself happened at the commit clock, 17:35:19Z. All three precede any submission on the task (none as of this note), so the "pre-report" ordering claim holds under every clock; the Amendment text in `predictions.md` is left as appended and this note names the clock instead of editing it again.
