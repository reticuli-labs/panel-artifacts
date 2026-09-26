import json, collections
from ainglish.client import AinglishClient
c=AinglishClient(); rows=list(c.iter_proposals()); out=[]; raw={}
for i,row in enumerate(rows):
    p=c.proposal(row["slug"]); r=p.get("proposal",p); raw[row["slug"]]=r
    roles=collections.defaultdict(set)
    a=(r.get("proposer") or {}); 
    if a.get("sub"): roles[a["sub"]].add("author")
    for s in r.get("seconds") or []:
        if s.get("sub"): roles[s["sub"]].add("second")
    for m in r.get("measurements") or []:
        sb=(m.get("submitter") or {}).get("sub")
        if sb: roles[sb].add("measure")
        if m.get("evidence_moderated_by_sub"): roles[m["evidence_moderated_by_sub"]].add("moderate")
    for v in ((r.get("ratification") or {}).get("votes") or []):
        if v.get("sub"): roles[v["sub"]].add("vote")
    names={}
    for s in r.get("seconds") or []: names[s.get("sub")]=s.get("name")
    for m in r.get("measurements") or []: names[(m.get("submitter") or {}).get("sub")]=(m.get("submitter") or {}).get("name")
    for v in ((r.get("ratification") or {}).get("votes") or []): names[v.get("sub")]=v.get("name")
    if a.get("sub"): names[a["sub"]]=a.get("name")
    out.append({"slug":row["slug"],"public_id":r.get("public_id"),"kind":r.get("kind"),"stage":r.get("stage"),
      "needs":{"has_comprehension":any(m.get("metric")=="comprehension_accuracy_delta" for m in r.get("measurements") or []),"has_token":any(m.get("metric")=="token_delta" for m in r.get("measurements") or []),"n_meas":len(r.get("measurements") or []),"seconds_count":r.get("seconds_count")},
      "roles":{k:sorted(v) for k,v in roles.items()},"names":{k:v for k,v in names.items() if k}})
    if i%40==0: print("progress",i,len(rows),flush=True)
json.dump({"generated":__import__("datetime").datetime.utcnow().isoformat()+"Z","rows":out},open("role_map.json","w"),indent=0)
json.dump(raw,open("proposals_raw.json","w"),default=str)
print("ROLE_MAP_DONE",len(out))
