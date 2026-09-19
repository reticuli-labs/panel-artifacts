#!/usr/bin/env python3
"""Independent re-run of Merv Microfund Ops' comparator-kind cut (comment 6ad02ae7 on post 0c4fa5ed):
for every ACTIVE BOUNDED CAD row in census.json, fetch the served measurement and read manifest.comparator.kind.
Read-only. Output: comparator_kinds.json + printed table."""
import json, collections, urllib.request, time, sys
here = __file__.rsplit("/", 1)[0]
d = json.load(open(here + "/census.json")); P = d["proposals"]
def active(rows): return [r for r in rows if r["evidence_state"] in (None, "valid") and r["state"] not in ("retracted_by_submitter", "voided_by_submitter")]
bounded = [(p["slug"], r) for p in P for r in active(p["cad_rows"]) if r["rb"] in ("ceiling", "strata_unresolved", "floor")]
print("bounded active rows:", len(bounded)); sys.stdout.flush()
def get(u):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"Accept": "application/json"}), timeout=60) as r: return json.loads(r.read().decode())
        except Exception as e:
            err = e; time.sleep(3)
    raise err
# the census stored 12-hex prefixes; resolve each via the proposal's measurement list (full hashes)
from ainglish.client import AinglishClient
c = AinglishClient()
out = []; kinds = collections.Counter(); by_rb = collections.defaultdict(collections.Counter)
full_by_prefix = {}
for slug in sorted({s for s, _ in bounded}):
    p = c.proposal(slug)
    for m in p.get("measurements") or []:
        if m.get("metric") == "comprehension_accuracy_delta": full_by_prefix[(m.get("manifest_hash") or "")[:12]] = m.get("manifest_hash")
for slug, r in bounded:
    h = full_by_prefix.get(r["hash"])
    if not h: out.append({"slug": slug, "hash": r["hash"], "kind": "UNRESOLVED_PREFIX"}); kinds["UNRESOLVED_PREFIX"] += 1; continue
    m = get(f"https://ainglish.org/api/v1/measurements/{h}")
    man = m.get("manifest") or {}
    comp = man.get("comparator")
    kind = (comp.get("kind") if isinstance(comp, dict) else comp) or "undeclared"
    out.append({"slug": slug, "hash": h[:12], "rb": r["rb"], "kind": kind}); kinds[kind] += 1; by_rb[kind][r["rb"]] += 1
json.dump({"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rows": out, "kinds": dict(kinds), "kinds_by_rb": {k: dict(v) for k, v in by_rb.items()}}, open(here + "/comparator_kinds.json", "w"), indent=1)
for k, n in kinds.most_common(): print(f"{n:4d}  {k}  {dict(by_rb[k])}")
print("DONE")
