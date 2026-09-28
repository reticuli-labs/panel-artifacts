#!/usr/bin/env python3
"""A small made-up population with the same shape as the frozen one. The harness and the counting rule
were developed and debugged on this file only, so that the frozen population was first read by the
counting rule after the attempt was minted."""
import json
T0 = "2026-08-20T10:37:45Z"
def row(slug, kind, cls, ratified, created="2026-07-20T09:00:00Z", stage="ratified"):
    inp = cls != "context"
    return {"slug": slug, "kind": kind, "class": cls, "in_population": inp, "stage_in_snapshot": stage, "publication_status": "visible",
            "ratified_at": ratified if inp else None, "ratified_at_in_snapshot": ratified, "created_at": created, "last_observation_at": None}
def obs(slug, source, day, n, at):
    start = "2026-07-%02d" % (int(day[-2:]) + 1)
    return {"slug": slug, "source": source, "window_start": start, "window_end": day, "usage_count": n, "created_at": at, "detector_version": None, "scan_count": None}
rows = [row("syn-protocol-a", "protocol", "protocol", "2026-08-08T09:00:00Z"), row("syn-protocol-b", "protocol", "protocol", "2026-08-19T09:00:00Z"),
        row("syn-covered-a", "lexical", "covered", "2026-08-09T21:00:00Z"), row("syn-covered-b", "discourse", "covered", "2026-08-12T10:00:00Z"),
        row("syn-covered-two-sources", "notational", "covered", "2026-08-01T10:00:00Z"),
        row("syn-mover-a", "notational", "mover", "2026-08-18T12:10:40Z"), row("syn-mover-b", "lexical", "mover", "2026-08-18T19:41:24Z"),
        row("syn-context", "discourse", "context", None, stage="seconded")]
observations = []
for day, at in (("2026-08-14", "2026-08-14T05:05:00Z"), ("2026-08-15", "2026-08-15T05:05:00Z"), ("2026-08-16", "2026-08-16T05:05:00Z")):
    observations += [obs("syn-covered-a", "c/ainglish scan", day, 7, at), obs("syn-covered-b", "c/ainglish scan", day, 21, at),
                     obs("syn-covered-two-sources", "c/ainglish scan", day, 40, at), obs("syn-covered-two-sources", "convention-compliance", day, 3, at),
                     obs("syn-context", "convention-compliance", day, 6, at)]
last = {}
for o in observations: last[o["slug"]] = max(last.get(o["slug"], ""), o["created_at"])
for r in rows: r["last_observation_at"] = last.get(r["slug"])
body = {"kind": "reticuli.unscanned-uvf.population.v1", "t0": T0, "source": {"made_up": True}, "rows": rows, "observations": observations}
open("synthetic_population.json", "w").write(json.dumps(body, indent=1, sort_keys=True) + "\n")
print(len(rows), len(observations))
