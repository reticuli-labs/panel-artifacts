"""find2.py <outdir>: second round of title look-ups on Europe PMC, then the open full texts of everything found so far."""
import json, os, sys, time, urllib.parse, urllib.request
OUT = sys.argv[1]
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "literature-check/1.0"}), timeout=60).read()
PAPERS = {
 "daskalova2021": 'TITLE:"year effects" AND TITLE:"invertebrate" AND AUTH:"Daskalova"',
 "didham2020": 'TITLE:"Interpreting insect declines"',
 "muehlethaler2024": 'TITLE:"No recovery in the biomass of flying insects over the last decade in German nature protected areas"',
 "duchenne2024": 'TITLE:"Weather explains inter-annual variability, but not the temporal decline, in insect biomass"',
 "hallmann2025ma": 'TITLE:"Weather anomalies cannot explain insect decline"',
 "welti2022pub": 'TITLE:"Temperature drives variation in flying insect biomass across a German malaise trap network" AND SRC:MED',
 "hallmann2020nl": 'TITLE:"Declining abundance of beetles, moths and caddisflies"',
 "gaume2024": 'TITLE:"InsectChange" AND AUTH:"Gaume"',
 "buchner2025": 'TITLE:"malaise trap" AND TITLE:"Germany" AND TITLE:"metabarcoding" AND PUB_YEAR:[2023 TO 2026]',
 "krefeld_recent": 'TITLE:"insect biomass" AND (TITLE:"Germany" OR TITLE:"German") AND PUB_YEAR:[2024 TO 2026]',
}
for key, q in PAPERS.items():
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": q, "format": "json", "resultType": "core", "pageSize": 8})
    try: raw = get(url)
    except Exception as e: print(key, "FAILED", type(e).__name__, e); continue
    open(os.path.join(OUT, key + ".search.json"), "wb").write(raw)
    rs = json.loads(raw).get("resultList", {}).get("result", [])
    print(key, "| hits", len(rs))
    for r in rs[:8]:
        print("   ", r.get("pubYear"), "|", (r.get("journalInfo") or {}).get("journal", {}).get("isoabbreviation"), "| pmcid", r.get("pmcid"), "| OA", r.get("isOpenAccess"), "| src", r.get("source"), "| doi", r.get("doi"), "|", (r.get("title") or "")[:100])
    time.sleep(0.4)
# open full texts: every pmcid in any saved search
seen = {}
for f in sorted(os.listdir(OUT)):
    if not f.endswith(".search.json"): continue
    for r in json.load(open(os.path.join(OUT, f), encoding="utf-8")).get("resultList", {}).get("result", []):
        if r.get("pmcid"): seen[r["pmcid"]] = (f[:-12], r.get("title", "")[:70])
for pmcid, (key, title) in sorted(seen.items()):
    dest = os.path.join(OUT, pmcid + ".xml")
    if os.path.exists(dest): continue
    try:
        raw = get("https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % pmcid); open(dest, "wb").write(raw); print("full text", pmcid, key, len(raw), "bytes |", title)
    except Exception as e: print("full text", pmcid, key, "FAILED", type(e).__name__, str(e)[:80])
    time.sleep(0.4)
