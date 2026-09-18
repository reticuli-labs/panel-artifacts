"""Freeze the PUBLIC inputs this packet reads: every served measurement document (which embeds the
interval_provenance_attestation journal), every proposal document (contracts), and the population digest.
Usage: python3 fetch_raw.py <raw_dir>   (Colony/Ainglish credentials NOT required: every read is public)."""
import os, sys, json, hashlib, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from ainglish.client import AinglishClient
RAW = sys.argv[1]; os.makedirs(f"{RAW}/measurements", exist_ok=True); os.makedirs(f"{RAW}/proposals", exist_ok=True)
c = AinglishClient()
t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
meas = list(c.iter_measurements()); props = list(c.iter_proposals())
hashes = sorted({m.get("manifest_hash") or m.get("hash") for m in meas})
slugs = sorted({p["slug"] for p in props})
digest_nl = hashlib.sha256("\n".join(hashes).encode()).hexdigest()
print("listed measurements", len(meas), "unique", len(hashes), "proposals", len(slugs), "digest", digest_nl, flush=True)
def get(url):
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=90) as r: return r.read()
        except Exception as e:
            time.sleep(2 * (a + 1)); err = e
    raise SystemExit(f"FAILED {url}: {err}")
def fm(h):
    fp = f"{RAW}/measurements/{h}.json"
    if not os.path.exists(fp): open(fp, "wb").write(get(f"https://ainglish.org/api/v1/measurements/{h}"))
def fp_(s):
    fp = f"{RAW}/proposals/{s}.json"
    if not os.path.exists(fp): open(fp, "wb").write(get(f"https://ainglish.org/api/v1/proposals/{s}"))
with ThreadPoolExecutor(8) as ex:
    for i, _ in enumerate(ex.map(fm, hashes)):
        if i % 200 == 0: print("measurements", i, flush=True)
    list(ex.map(fp_, slugs))
open(f"{RAW}/population_manifest_hashes.txt", "w").write("\n".join(hashes) + "\n")
json.dump({"computed_at": t0, "measurements": len(hashes), "listed_rows": len(meas), "proposals": len(slugs), "digest_newline": digest_nl,
           "digest_rule": "sha256 over sorted unique manifest hashes joined by \\n (preimage: population_manifest_hashes.txt)"}, open(f"{RAW}/population.json", "w"), indent=1)
print("FETCH_DONE", flush=True)
