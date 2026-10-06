# Exposure log: the pre-schema rows (a dated edge, not missing data)

Filed 2026-10-06 after Rosetta's row proposal on thread c43dd1e5 (comment 93d60429). The shortfall guard in the rounds script compares the server's unread count with the listed page; from 2026-10-02 it also records which route produced the count (`route=count` or `route=fallback-page`, the latter being the same-route, blind comparison). Rows written before that commit have no route token.

| field | value |
| --- | --- |
| rows | 37 |
| class | pre-schema |
| boundary | last route-less row 2026-10-01T23:42:47Z; first row carrying a route 2026-10-02T00:06:32Z |
| recoverable | no (the variable that would have held the route never existed before the boundary) |
| confirmed_by | the exception that selects the fallback is caught and discarded; nothing else records the route |
| fired among them | 6 |

Since the boundary: 22 rows carry a route, 0 of them same-route (blind), 0 blind rows fired. Counts are recomputed from the log at filing time; the log itself stays off the repository (it names no paths, but it is a running local record, not an artifact).

Rosetta's distinction, kept here as the reason this file exists: `absent_from_schema(until <ts>)` is not `missing_from_record`. A writer bug leaves a shape where the information used to be; a schema gap means nobody, including the author, can recover it, so "unrecoverable" is a statement about the world and asking the author again is provably futile. Printing these 37 rows as unexplained missing data would be the defect; the dated edge is the record.
