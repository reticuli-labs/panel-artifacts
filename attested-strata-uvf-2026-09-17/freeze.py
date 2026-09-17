import os, json, hashlib, time, inspect
from ainglish.client import AinglishClient
sig = inspect.signature(AinglishClient.__init__)
c = AinglishClient(colony_api_key=os.environ["COLONY_API_KEY"]) if "colony_api_key" in sig.parameters else AinglishClient()
W = os.path.expanduser("~/.reticuli/work/aing-round-20260917e/freeze")
t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
meas = list(c.iter_measurements()); print("measurements listed:", len(meas), flush=True)
props = list(c.iter_proposals()); print("proposals listed:", len(props), flush=True)
json.dump(meas, open(f"{W}/measurements_list.json","w")); json.dump(props, open(f"{W}/proposals_list.json","w"))
hashes = sorted(m.get("manifest_hash") or m.get("hash") for m in meas)
digest = hashlib.sha256("".join(hashes).encode()).hexdigest()
print("population digest (sha256 over sorted manifest hashes, concatenated):", digest, flush=True)
# also try newline-joined variant to match whichever convention the 09-16 digest used
digest_nl = hashlib.sha256("\n".join(hashes).encode()).hexdigest()
print("variant newline-joined:", digest_nl, flush=True)
json.dump({"computed_at": t0, "measurements": len(meas), "proposals": len(props), "digest_concat": digest, "digest_newline": digest_nl}, open(f"{W}/population.json","w"), indent=1)
# full rows for every measurement (public GET via SDK)
import urllib.request
os.makedirs(f"{W}/measurements", exist_ok=True)
n=0
for h in hashes:
    fp = f"{W}/measurements/{h}.json"
    if os.path.exists(fp): continue
    for attempt in range(4):
        try:
            with urllib.request.urlopen(f"https://ainglish.org/api/v1/measurements/{h}", timeout=60) as r: d = json.loads(r.read())
            json.dump(d, open(fp,"w")); break
        except Exception as e:
            time.sleep(2*(attempt+1))
    else: print("FAILED", h, flush=True)
    n+=1
    if n%100==0: print("fetched", n, flush=True)
os.makedirs(f"{W}/proposals", exist_ok=True)
for p in props:
    s = p.get("slug"); fp = f"{W}/proposals/{s}.json"
    if os.path.exists(fp): continue
    for attempt in range(4):
        try: json.dump(c.proposal(s), open(fp,"w")); break
        except Exception as e: time.sleep(2*(attempt+1))
    else: print("FAILED prop", s, flush=True)
print("FREEZE_DONE", flush=True)
