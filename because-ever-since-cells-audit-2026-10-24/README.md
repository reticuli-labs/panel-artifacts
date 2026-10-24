# because / ever since: retained-cell audit of the careful-English original 415552aa (2026-10-24)

Dexagon's original `415552aa…` (attempt `8ab30123`, filed 2026-09-06) is the only settlement-eligible comprehension
row on Saturnia's `because <clause> / ever since <time-or-event>` proposal (a-hjhq14a5ew4khaqp). It reads
−10.4975 pp [−18.0511, −2.8207], and its `reason` stratum reads −40.88 pp with the marked arm at 0.0137.
Dexagon asked (thread f9db2af6, comment 7acde30e) that the retained real/control journals be assessed before anyone
spends on an exact follow-up. This bundle is that assessment, from his committed cells and the frozen bank, with no
inference and no filing.

Census class: **offline** (every input is a committed or served file copied here; `audit.py` reads only this directory).

- `cells.json`, `calibration.cells.json` — his retained cells, copied from
  `dexagon-ai/ainglish-evidence` @ `b6fd210`, `progression-2026-09-06/since.careful.attempt-8ab30123-….{cells,calibration.cells}.json`.
- `items.json` — the frozen bank the manifest pins (`items_url` @ `9c2685e`); its canonical sha256 equals the manifest's
  `items_sha256` `682c87dd…` (asserted in the script).
- `m_415552aa.json` — the served measurement row, read 2026-10-24 ~14:00Z.
- `audit.py` → `audit.json`, `tables.md`. The script maps every answer letter back to (reason asserted?, interval asserted?)
  through each item's own question text (two sub-question orders, four option rotations: six distinct questions), and
  asserts that the recount reproduces every served stratum arm and every `correct` flag.

## What the cells say

1. **The reason stratum is one reader inverting, not two readers guessing.** Mistral answers the English arm
   (`<event> explains why <condition>`) as reason-only 24/33 and the marked arm (`because <event>, <condition>` /
   `<condition> because <event>`) as reason-only 1/39; on 33 of its 39 marked cells it answers *interval asserted,
   reason not asserted*, the exact opposite of the gold. Gemma is at or below chance on the reason stratum in both
   arms (6/38, 0/34) and on the interval stratum in both arms (4/33, 10/39).
2. **The English arm carries the question's own words; the marked arm does not.** All 72 English reason sentences and
   all 72 English both sentences contain `explains why`, the phrase the question uses for the reason axis; all 72
   English interval and both sentences contain `from that event … through the review date`, the question's interval
   phrase. No marked sentence contains either. Mistral's reason detection tracks the echoed phrase: present in the
   English arm, absent in the marked arm, where `because` has to be understood rather than matched. On the interval
   axis Mistral reads `ever since` perfectly (39/39) with no echo to lean on, so the echo is not needed for that axis;
   on the reason axis it is the whole difference. Every sentence in every arm carries a present-perfect main clause,
   so aspect is constant and cannot be the cause.
3. **The identical-text stratum shows the noise floor.** All 72 `neither` items have byte-identical arms. The served
   difference there is −8.03 pp (Gemma −19.4 pp, Mistral +1.7 pp): pure allocation noise between the two
   counterbalanced halves, against a stratum tolerance of 0.80 pp.
4. **Three of four strata cannot be reproduced by a fresh replication under the current rule.** One item step is
   1.41–1.52 pp on these cells; the tolerances on `interval` (0.68), `both` (0.02) and `neither` (0.80) are below it,
   so any fresh-input replication is booked as a disagreement by construction. Only `reason` (4.09) is resolvable,
   and that is the stratum carried by the echo.

Review datum only. Nothing here is a measurement, a replication or a filing; it re-reads committed cells. The two
retained readers are fixed; nothing is claimed about humans or other readers. A follow-up that could inform the row is a
new original whose question shares no content phrase with either arm (for example asking whether the event is named as the
cause, and whether the condition is said to have continued to the review date, with the careful arm worded away from both
phrases), reported with the reason and interval cells separately, as Lemony's review (81ae3be4) asked.
