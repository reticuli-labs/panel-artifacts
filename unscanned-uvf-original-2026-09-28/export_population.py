#!/usr/bin/env python3
"""Export the frozen population for the unscanned-is-not-zero regression count.

Source: a nightly production snapshot restored into a local scratch database. Only two tables are read,
`proposal` and `adoption_observation`, and only public columns: slugs, kinds, stages, ratification times,
scan windows and counts. No account data is read.

The population is the register as the row's blast-radius table saw it: every proposal ratified at or
before T0, and every adoption observation recorded at or before T0.

USAGE  export_population.py <scratch_db_name> <backup_file> <out.json>
"""
import hashlib, json, os, subprocess, sys

REPO = os.environ.get("AINGLISH_REPO", "/home/user/claude-projects/Reticuli/ainglish")
T0 = "2026-08-20 10:37:45"          # protocol_meta.blast_radius.computed_at of a-wgsw9q5paxfgxa8y, UTC
Q_ROWS = ("SELECT p.slug, p.kind, p.stage, p.publication_status, p.ratified_at, p.created_at FROM proposal p "
          "WHERE (p.ratified_at IS NOT NULL AND p.ratified_at <= '%s') "
          "OR p.id IN (SELECT o.proposal_id FROM adoption_observation o WHERE o.created_at <= '%s') ORDER BY p.slug" % (T0, T0))
Q_OBS = ("SELECT p.slug, o.source, o.window_start, o.window_end, o.usage_count, o.created_at, o.detector_version, o.scan_count "
         "FROM adoption_observation o JOIN proposal p ON p.id = o.proposal_id WHERE o.created_at <= '%s' "
         "ORDER BY o.created_at, p.slug, o.source" % T0)
Q_EVENTS = "SELECT event, COUNT(*) FROM register_event WHERE created_at <= '%s' GROUP BY event ORDER BY event" % T0


def query(db, sql):
    cmd = ["docker", "compose", "exec", "-T", "db", "sh", "-c",
           'mariadb -uroot -p"${MARIADB_ROOT_PASSWORD:-$MYSQL_ROOT_PASSWORD}" --batch --raw -N "$0" -e "$1"', db, sql]
    out = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("query failed: " + out.stderr[:300])
    return [line.split("\t") for line in out.stdout.split("\n") if line]


def null(v):
    return None if v == "NULL" else v


def iso(v):
    return None if v is None else v.replace(" ", "T") + "Z"


def main(argv):
    db, backup, dest = argv[1], argv[2], argv[3]
    rows = []
    for slug, kind, stage, pub, ratified, created in query(db, Q_ROWS):
        ratified = null(ratified)
        in_population = ratified is not None and ratified <= T0
        rows.append({"slug": slug, "kind": kind, "stage_in_snapshot": stage, "publication_status": pub,
                     "ratified_at": iso(ratified) if in_population else None,
                     "ratified_at_in_snapshot": iso(ratified),
                     "created_at": iso(created), "in_population": in_population})
    obs = [{"slug": s, "source": src, "window_start": ws, "window_end": we, "usage_count": int(n),
            "created_at": iso(c), "detector_version": null(dv), "scan_count": (None if null(sc) is None else int(sc))}
           for s, src, ws, we, n, c, dv, sc in query(db, Q_OBS)]
    events = {e: int(n) for e, n in query(db, Q_EVENTS)}
    last = {}
    for o in obs:
        last[o["slug"]] = max(last.get(o["slug"], ""), o["created_at"])
    for r in rows:
        if not r["in_population"]:
            r["class"] = "context"
        elif r["kind"] == "protocol":
            r["class"] = "protocol"
        elif r["slug"] in last and last[r["slug"]] >= r["ratified_at"]:
            r["class"] = "covered"
        else:
            r["class"] = "mover"
        r["last_observation_at"] = last.get(r["slug"])
    body = {"kind": "reticuli.unscanned-uvf.population.v1", "t0": iso(T0),
            "source": {"backup_file": os.path.basename(backup), "backup_sha256": hashlib.sha256(open(backup, "rb").read()).hexdigest(),
                       "queries": {"rows": Q_ROWS, "observations": Q_OBS, "events": Q_EVENTS},
                       "register_events_at_t0": events},
            "rows": rows, "observations": obs}
    with open(dest, "w") as fh:
        fh.write(json.dumps(body, indent=1, sort_keys=True) + "\n")
    cls = {}
    for r in rows:
        cls[r["class"]] = cls.get(r["class"], 0) + 1
    print("rows", len(rows), cls, "| observations", len(obs), "| events", events)
    print("sha256", hashlib.sha256(open(dest, "rb").read()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
