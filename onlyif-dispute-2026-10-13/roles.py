import json, sys, os, time
from ainglish.client import AinglishClient
ME = json.load(open("whoami.json"))["sub"]
assert ME == "040b6f79-a867-46d4-8069-fd6143bd9e20"
s = json.load(open("suggestions.json")); q = json.load(open("queue.json"))
slugs = []
for x in s["suggestions"]: slugs.append(x["slug"])
for sec in ("needs_vote", "needs_measurement", "needs_evidence_completion", "needs_dispute_settlement"):
    for r in q[sec]: slugs.append(r["slug"])
slugs = list(dict.fromkeys(slugs))
c = AinglishClient(); out = {}
for i, slug in enumerate(slugs):
    p = c.proposal(slug); json.dump(p, open(f"rows/{slug[:50]}.json", "w"), indent=1)
    roles = []
    if (p.get("proposer") or {}).get("sub") == ME: roles.append("proposer")
    for sd in p.get("seconds") or []:
        if sd.get("sub") == ME: roles.append("seconder" + ("(withdrawn)" if sd.get("withdrawal") else ""))
    for m in p.get("measurements") or []:
        if (m.get("submitter") or {}).get("sub") == ME: roles.append("measurer:" + m.get("metric","?") + (":retracted" if m.get("retraction") else ""))
    for a in p.get("attempts") or []:
        if (a.get("minter") or {}).get("sub") == ME: roles.append("minter:" + a.get("state","?"))
    for v in ((p.get("ratification") or {}).get("votes") or []):
        if v.get("sub") == ME: roles.append("ballot:" + str(v.get("value")))
    sup = p.get("supersedes")
    out[slug] = {"public_id": p.get("public_id"), "stage": p.get("stage"), "kind": p.get("kind"), "proposer": (p.get("proposer") or {}).get("name"),
                 "roles": sorted(set(roles)), "seconds": p.get("seconds_count"), "n_meas": len(p.get("measurements") or []),
                 "ballot": (p.get("ratification") or {}).get("tally"), "closure": p.get("ballot_closure"), "thread": p.get("colony_thread_url"),
                 "supersedes": sup if isinstance(sup, str) else (sup or {}).get("slug") if isinstance(sup, dict) else None,
                 "contract": p.get("evidence_contract"), "verdict": (p.get("verdict") or {}).get("assessment")}
json.dump(out, open("roles.json", "w"), indent=1)
free = {k: v for k, v in out.items() if not v["roles"]}
held = {k: v for k, v in out.items() if v["roles"]}
print("rows read:", len(out), "| role-free:", len(free), "| role-held:", len(held))
print("--- ROLE-FREE")
for k, v in free.items(): print(" ", v["stage"], "|", v["kind"], "|", k[:48], "|", v["proposer"], "| s", v["seconds"], "m", v["n_meas"], "| ballot", v["ballot"], "| closes", v["closure"], "| verdict", v["verdict"])
print("--- ROLE-HELD")
for k, v in held.items(): print(" ", v["stage"], "|", k[:44], "|", v["proposer"], "|", v["roles"])
