"""abstracts.py <epmc dir> [key ...]: print what Europe PMC returned for each saved search: year, journal, doi, abstract."""
import json, os, re, sys
D = sys.argv[1]; keys = sys.argv[2:] or sorted(f[:-12] for f in os.listdir(D) if f.endswith(".search.json"))
for k in keys:
    rs = json.load(open(os.path.join(D, k + ".search.json"), encoding="utf-8")).get("resultList", {}).get("result", [])
    for r in rs:
        ab = re.sub(r"<[^>]+>", "", r.get("abstractText") or "")
        print("=== %s | %s | %s | doi %s | pmcid %s | first published %s" % (k, r.get("pubYear"), (r.get("journalInfo") or {}).get("journal", {}).get("title"), r.get("doi"), r.get("pmcid"), r.get("firstPublicationDate")))
        print("    ", r.get("title")); print("    ", (r.get("authorString") or "")[:200]); print("    ", ab[:2600]); print()
