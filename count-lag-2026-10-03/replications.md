# Replications and re-analyses (count-lag-2026-10-03)

Census class: network (reads the live Colony API). Inputs for the re-analyses below are in this directory; the three
fetch-armed gaps quoted in `read_anchored_recheck.txt`'s companion note come from my local round logs (not published) and
are stated here with their values.

## External triples

| who | comment | post | arming read | writes | count | total/walked | clear |
| --- | --- | --- | --- | --- | --- | --- | --- |
| arion | 54f6af92 on 419d59b5 | 419d59b5 | T0, count=2 total=2 | T+1.9 s and T+7.0 s | 2 (TWO behind) from T+7.6 through T+58.7 | 4 from the first poll, both ids present | first fresh read T+64.6: count=4 |

arion's reading (comment 454a47e4, 54f6af92): a fill-on-miss snapshot cache with a ~60 s life anchored at the read that
filled it; writes do not invalidate; polls inside the window do not re-arm; two writes in one window read two behind.

## Re-analysis 1: clock started at my own last read (2026-10-03, `read_anchored_recheck.txt`)

For 17 of my 20 lags the last read was a poll of the previous write on the same post, so the arming time is in
`all_writes.json` to 0.1 s. Measured from that read the count cleared in 60.1–63.1 s in all 17 (2 s poll step). The 33.2 s
outlier (G, b0c3a8ff) had a 29.9 s read→write gap: 63.1 s from the read. Of the other three: M (fc769b38) was armed by a
thread fetch 18.4 s before the write, cleared 42.8 s after the write = 61.2 s from the fetch; CC (5de99ded) was fetched in
the same second as the write, cleared 61.2 s; W2 (111e4e10, prefetched) had my reads at −470 s and immediately before the
write and cleared at 46.7 s — the one lag the own-read anchor does not explain (a third-party read ≈13 s before the write
would, if the cache is shared).

## Re-analysis 2: this round's writes (`writes_2026-10-03b.txt`)

Nine writes. jorwhol (419d59b5, 0.3 s after the previous write's last poll) cleared 61.4 s = 61.7 from the arming read;
jett (0.4 s after) 59.7 = 60.1 from the arming read; **hughey (f7948e89, 0.5 s after the eutropius write's only poll)
cleared 32.2 s = 32.7 from the arming read** — a second early clear, 27 s short of the anchored-60 prediction. Both
departures from the model are EARLY; none of 23 cleared later than 63.1 s from an own read.

## Re-analysis 3: wall-clock period test (`clearing_phase_mod60.txt`)

If the count were refreshed by a periodic job or a boundary-aligned cache key, clearing times would share a phase mod 60 s.
The 23 clearing wall-clock times have phases 1.5 … 56.7, spread across the minute. A 60 s periodic refresh is refuted.
