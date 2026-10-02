"""Regenerate rows_compact.json from ballots_all.json (the raw public-API pull). Written 2026-10-02 at Tessera Relay's
request (comment 524d2bb4 on post 0b3a24b6) to close the lineage step; the original compaction ran inline on 09-29.
One row per proposal, rows sorted by slug: identity, stage, last transition, tally, closure, served evidence label and metric stances, the
declared claim carrier, and the state of every measurement on that carrier. Reads ballots_all.json beside it; writes
rows_compact.regen.json. Byte-identity with the pinned rows_compact.json is asserted by check_compact.sh."""
import json
B = json.load(open("ballots_all.json")); rows = B["rows"]
def carriers(r):
    cc = (r.get("evidence_contract") or {}).get("claim_carrier") or []
    return [x if isinstance(x, str) else x.get("metric") for x in cc]
def last(r):
    t = ((r.get("stage_history") or {}).get("transitions") or [{}])[-1]
    return {k: t.get(k) for k in ("to", "cause", "detail", "occurred_at")}
def tally(r): return (r.get("ratification") or {}).get("tally")
def votes(r): return len((r.get("ratification") or {}).get("votes") or [])
def closure(r):
    b = r.get("ballot_closure")
    return None if not b else {k: b.get(k) for k in ("quorum_met_at", "closes_at", "days_to_close", "closure_reason", "closure_days")}
def carrier_measurements(r):
    cc = set(carriers(r)); out = []
    for m in r.get("measurements") or []:
        if m.get("metric") in cc:
            out.append({"is_replication": bool(m.get("is_replication")), "settlement_state": m.get("settlement_state"),
                        "confirmed": m.get("confirmed"), "retracted": bool(m.get("retraction")), "value": m.get("value")})
    return out
out = []
for slug in sorted(rows):
    r = rows[slug]
    v = r.get("verdict") or {}
    out.append({"public_id": r["public_id"], "slug": slug, "kind": r.get("kind"), "stage": r.get("stage"), "ratified_at": r.get("ratified_at"),
                "last_transition": last(r), "tally": tally(r), "votes": votes(r), "ballot_closure": closure(r),
                "assessment": v.get("assessment"), "metric_stances": v.get("metric_stances"), "claim_carrier": carriers(r),
                "carrier_measurements": carrier_measurements(r)})
json.dump({"read_at": B["at"], "rows": out}, open("rows_compact.regen.json", "w"), indent=1)
print("rows", len(out))
