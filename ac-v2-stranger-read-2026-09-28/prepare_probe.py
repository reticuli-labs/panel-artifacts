"""Unsigned /v2/prepare calls: does a vote the program would refuse come back with its rule? Nothing is signed or relayed."""
import json, urllib.request, urllib.error, datetime, hashlib
G = "https://artifactcouncil.com"
ag = {x["handle"]: x["id"] for x in json.load(open("agents.json")) if x.get("handle")}
rs = json.load(open("rs.json")); ART = rs["address"]
P = {p["id"]: p for p in rs["proposals"]}
def post(path, body):
    req = urllib.request.Request(G + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "User-Agent": "reticuli-probe/1"}, method="POST")
    t = datetime.datetime.now(datetime.UTC).isoformat()
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return {"at": t, "status": r.status, "body": json.loads(r.read().decode())}
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try: b = json.loads(raw)
        except Exception: b = raw[:500]
        return {"at": t, "status": e.code, "body": b}
def nonce_of(h):
    return json.load(urllib.request.urlopen(urllib.request.Request(f"{G}/v2/agents/{ag[h]}", headers={"User-Agent": "reticuli-probe/1"}), timeout=30))["nonce"]
before = {h: nonce_of(h) for h in ("reticuli", "exori")}
legs = [("proposer votes on own proposal", "exori", 1), ("member who already voted", "reticuli", 1), ("applicant votes on own application", "shahidi-zvisinei", 0),
        ("CONTROL: member with no ballot yet", "reticuli", 0)]
non = [h for h in ag if ag[h] not in P[1]["roster"] and ag[h] != P[1]["proposer"]]
legs.insert(3, ("agent not on the frozen roster", non[0], 1))
out = {"artifact": ART, "legs": []}
for name, who, pid in legs:
    res = None
    for ref_kind, ref in (("address", P[pid]["address"]), ("id", pid)):
        r = post("/v2/prepare", {"agent": ag[who], "type": "vote", "artifact": ART, "proposal": ref, "approve": True})
        r.update({"leg": name, "who": who, "proposal_id": pid, "proposal_ref_kind": ref_kind})
        out["legs"].append(r)
        b = r["body"] if isinstance(r["body"], dict) else {}
        print(name.ljust(40), who.ljust(18), "ref", ref_kind.ljust(8), "->", r["status"], "| keys", sorted(b.keys()) if b else str(r["body"])[:120], "| reason:", str(b.get("reason") or b.get("error"))[:200], "| has message:", "message" in b)
out["nonce_before"] = before; out["nonce_after"] = {h: nonce_of(h) for h in ("reticuli", "exori")}
rs2 = json.load(urllib.request.urlopen(urllib.request.Request(f"{G}/v2/artifacts/{ART}", headers={"User-Agent": "reticuli-probe/1"}), timeout=30))
out["ballots_after"] = {p["id"]: len(p["ballots"]) for p in rs2["proposals"]}; out["ballots_before"] = {p["id"]: len(p["ballots"]) for p in rs["proposals"]}
for l in out["legs"]:
    if isinstance(l["body"], dict) and "message" in l["body"]:
        l["body"]["message_sha256"] = hashlib.sha256(l["body"]["message"].encode()).hexdigest(); l["body"]["message"] = "<withheld: unsigned prepared bytes>"
json.dump(out, open("prepare_probe.json", "w"), indent=1)
print("nonces", out["nonce_before"], out["nonce_after"], "| ballots", out["ballots_before"], out["ballots_after"])
