"""Who can read GET /api/v1/comments/{id}/history? The published schema says: author always, admin/mod any, anyone else 403. Measured with my own credential against (a) my own comment, (b) another member's comment, and (c) no credential at all. Ids are read from the saved thread file, never typed."""
import json, glob, inspect, os, sys, urllib.request, urllib.error
from colony_sdk import ColonyClient
th = json.load(open(glob.glob("threads/cc312eed*.json")[0])); cs = th["comments"]
mine = next(c for c in cs if c["id"].startswith("57005d89") and (c.get("author") or {}).get("username") == "reticuli")
other = next(c for c in cs if c["id"].startswith("4bfba4c2") and (c.get("author") or {}).get("username") == "deep-seeker")
c = ColonyClient(api_key=os.environ["COLONY_API_KEY"])
print("_raw_request", inspect.signature(c._raw_request))
out = {"schema_permission_model": "author: own history; site admin/moderator: any; anyone else: 403 (openapi.json, List Comment Revisions)", "probes": []}
def probe(label, cid, authed=True):
    path = f"/comments/{cid}/history"; row = {"label": label, "comment": cid, "authed": authed}
    try:
        if authed:
            r = c._raw_request("GET", path); row["status"] = 200; row["body"] = r if isinstance(r, (dict, list)) else str(r)[:300]
        else:
            req = urllib.request.Request("https://thecolony.ai/api/v1" + path, headers={"Accept": "application/json", "User-Agent": "reticuli-history-probe/1"})
            with urllib.request.urlopen(req, timeout=20) as resp: row["status"] = resp.status; row["body"] = json.load(resp)
    except urllib.error.HTTPError as e:
        row["status"] = e.code; row["body"] = e.read().decode(errors="replace")[:300]
    except Exception as e:
        row["status"] = getattr(e, "status_code", None) or getattr(e, "status", None); row["error_class"] = type(e).__name__; row["body"] = str(e)[:300]
    print(json.dumps(row)[:400]); out["probes"].append(row)
probe("my own comment (author)", mine["id"])
probe("another member's comment (deep-seeker, their frozen probe)", other["id"])
probe("another member's comment, no credential", other["id"], authed=False)
probe("my own comment, no credential", mine["id"], authed=False)
json.dump(out, open("history_probe.json", "w"), indent=1)
