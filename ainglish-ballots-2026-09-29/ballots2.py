"""Add the rows ratified since 2026-09-01 to the ballot pull, then tabulate label against outcome. Reads only."""
import json, time, collections, datetime
from ainglish.client import AinglishClient, AinglishError
c = AinglishClient()
def retry(f, *a):
    for i in range(5):
        try: return f(*a)
        except AinglishError as e:
            if "transport_error" not in str(e) or i == 4: raise
            time.sleep(3 * (i + 1))
B = json.load(open("ballots.json")); rows = B["rows"]
rat = json.load(open("ratified.json"))
for r in rat:
    if (r.get("ratified_at") or "") >= "2026-09-01" and r["slug"] not in rows:
        p = retry(c.proposal, r["slug"]); rows[r["slug"]] = p.get("proposal", p)
json.dump({"at": datetime.datetime.now(datetime.UTC).isoformat(), "rows": rows}, open("ballots_all.json", "w"), default=str)
def carriers(r):
    ec = r.get("evidence_contract") or {}; cc = ec.get("claim_carrier") or []
    return [x if isinstance(x, str) else x.get("metric") for x in cc]
def carrier_state(r):
    cc = carriers(r); st = (r.get("verdict") or {}).get("metric_stances") or {}
    if not cc: return "no carrier declared"
    s = [x for m in cc for x in (st.get(m) or ["absent"])]
    if "supports" in s: return "carrier supports"
    if "opposes" in s: return "carrier opposes"
    return "carrier " + "/".join(sorted(set(s)))
out = []
for sl, r in rows.items():
    rat_ = r.get("ratification") or {}; t = rat_.get("tally") or {}
    if r["stage"] == "ratified" and (r.get("ratified_at") or "") < "2026-09-01": continue
    if r["stage"] not in ("ratified", "vote_failed"): continue
    h = (r.get("stage_history") or {}).get("transitions") or [{}]
    out.append({"id": r["public_id"], "slug": sl, "kind": r["kind"], "outcome": r["stage"], "at": (r.get("ratified_at") or h[-1].get("occurred_at") or "")[:16], "legacy": "transition tracking began" in (h[-1].get("detail") or ""),
                "yes": t.get("yes"), "no": t.get("no"), "assessment": (r.get("verdict") or {}).get("assessment"), "carrier": carriers(r), "carrier_state": carrier_state(r),
                "stances": (r.get("verdict") or {}).get("metric_stances")})
json.dump(out, open("ballot_table.json", "w"), indent=1)
tab = collections.Counter((x["outcome"], "protocol" if x["kind"] == "protocol" else "language", x["assessment"], x["carrier_state"]) for x in out)
for k, n in sorted(tab.items()): print(n, k)
print("ratified since 09-01:", sum(x["outcome"] == "ratified" for x in out), "| vote_failed:", sum(x["outcome"] == "vote_failed" for x in out))
for x in sorted(out, key=lambda x: x["at"]):
    if x["outcome"] == "ratified" and x["kind"] != "protocol": print("  ratified", x["at"], x["id"], x["slug"][:36].ljust(36), "yes", x["yes"], "no", x["no"], "|", x["assessment"], "|", x["carrier_state"], "|", json.dumps(x["stances"])[:110])
