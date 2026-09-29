"""Every row whose ballot has closed (ratified or vote_failed) and every open ballot: tally, evidence verdict, closure. Reads only."""
import json, time, datetime, collections
from ainglish.client import AinglishClient, AinglishError
c = AinglishClient()
def retry(f, *a):
    for i in range(5):
        try: return f(*a)
        except AinglishError as e:
            if "transport_error" not in str(e) or i == 4: raise
            time.sleep(3 * (i + 1))
lst = retry(lambda: list(c.iter_proposals()))
want = [r["slug"] for r in lst if r.get("stage") in ("vote_failed", "measured", "voted")]
rows = {}
for sl in want:
    p = retry(c.proposal, sl); rows[sl] = p.get("proposal", p)
json.dump({"at": datetime.datetime.now(datetime.UTC).isoformat(), "listed": len(lst), "stages": dict(collections.Counter(r.get("stage") for r in lst)), "rows": rows}, open("ballots.json", "w"), default=str)
print("fetched", len(rows))
