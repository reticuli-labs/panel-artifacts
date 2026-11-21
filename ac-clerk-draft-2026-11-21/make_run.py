"""make_run.py <council json> <agents json> <time of the read, ISO> <run directory>: build a run directory for `clerk.py saved` from a
council that was saved earlier (one gateway answer to GET /v2/artifacts/<address>, kept whole) and a list of agents (id and
handle). It writes inputs/ and inputs/manifest.json the way `clerk.py live` would have, with the time given. Reads only the two
files named. Used for the sample on a past vote and for the planted council."""
import hashlib, json, os, sys
canon = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
council, agents, at, run = sys.argv[1:5]
os.makedirs(os.path.join(run, "inputs"), exist_ok=True); raw = open(council, "rb").read(); c = json.loads(raw); c = c.get("artifact", c) if isinstance(c, dict) else c
raw = raw if "members" in json.loads(raw) else canon(c).encode("utf-8")           # a saved file that wraps the answer: the answer alone is kept
ag = json.load(open(agents, encoding="utf-8")); ag = ag.get("agents") if isinstance(ag, dict) else ag
small = canon(sorted(({"id": x["id"], "handle": x.get("handle")} for x in ag), key=lambda x: x["id"])).encode("utf-8"); man = []
for route, name, b in (("GET /v2/artifacts/" + c["address"], "council_%s.json" % c["address"], raw), ("GET /v2/agents", "agents.json", small)):
    open(os.path.join(run, "inputs", name), "wb").write(b)
    man.append({"route": route, "gateway": "https://gateway.artifactcouncil.com", "fetched_at": at, "file": name, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(), "note": "built by make_run.py from a file saved earlier"})
json.dump(sorted(man, key=lambda m: m["route"]), open(os.path.join(run, "inputs", "manifest.json"), "w", encoding="utf-8"), indent=1)
print("run directory", run, "| council", c["name"], "| members", len(c["members"]), "| open proposals", len([p for p in c.get("proposals") or [] if p.get("status") == "voting"]))
