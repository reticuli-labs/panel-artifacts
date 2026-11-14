"""find.py <outdir>: look up each paper by title on Europe PMC (public, no key) and save the raw answer. Reads nothing back as code."""
import json, os, sys, time, urllib.parse, urllib.request
OUT = sys.argv[1]
PAPERS = {
 "hallmann2017": 'TITLE:"More than 75 percent decline over 27 years in total flying insect biomass in protected areas"',
 "seibold2019": 'TITLE:"Arthropod decline in grasslands and forests is associated with landscape-level drivers"',
 "vanklink2020": 'TITLE:"Meta-analysis reveals declines in terrestrial but increases in freshwater insect abundances"',
 "mueller2023": 'TITLE:"Weather explains the decline and rise of insect biomass over 34 years"',
 "welti2022": 'TITLE:"Temperature drives variation in flying insect biomass across a German malaise trap network"',
 "daskalova2021": 'TITLE:"Accounting for year effects and sampling error in temporal analyses of invertebrate population and biodiversity change"',
 "didham2020": 'TITLE:"Interpreting insect declines: seven challenges and a way forward"',
 "fournier2019": 'TITLE:"Site-selection bias and apparent population declines in long-term studies"',
 "desquilbet2020": 'TITLE:"Comment on" AND TITLE:"Meta-analysis reveals declines in terrestrial but increases in freshwater insect abundances"',
 "uhler2021": 'TITLE:"Relationship of insect biomass and richness with land use along a climate gradient"',
 "neff2022": 'TITLE:"Different roles of concurring climate and regional land-use changes in past 40 years"',
 "hallmann2020nl": 'TITLE:"Declining abundance of beetles, moths and caddisflies in the Netherlands"',
 "hallmann2021hover": 'TITLE:"Insect biomass decline scaled to species diversity"',
 "baranov2020": 'TITLE:"Complex and nonlinear climate-driven changes in freshwater insect communities over 42 years"',
 "engelhardt2022": 'TITLE:"Consistent signals of a warming climate in occupancy changes of three insect taxa over 40 years in central Europe"',
 "staab2023": 'TITLE:"Insect decline in forests depends on species"',
 "homburg2019": 'TITLE:"Where have all the beetles gone"',
 "habel2016": 'TITLE:"Butterfly community shifts over two centuries"',
 "macgregor2019": 'TITLE:"Moth biomass increases and decreases over 50 years in Britain"',
 "hausmann2022": 'TITLE:"Fluctuating insect diversity, abundance and biomass across agricultural landscapes"',
}
for key, q in PAPERS.items():
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": q, "format": "json", "resultType": "core", "pageSize": 5})
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "literature-check/1.0"}), timeout=40).read()
    except Exception as e:
        print(key, "FAILED", type(e).__name__, e); continue
    open(os.path.join(OUT, key + ".search.json"), "wb").write(raw)
    rs = json.loads(raw).get("resultList", {}).get("result", [])
    print(key, "| hits", len(rs))
    for r in rs[:3]:
        print("   ", r.get("pubYear"), "|", (r.get("journalInfo") or {}).get("journal", {}).get("isoabbreviation"), "| pmcid", r.get("pmcid"), "| OA", r.get("isOpenAccess"), "| doi", r.get("doi"), "|", (r.get("title") or "")[:90])
    time.sleep(0.4)
