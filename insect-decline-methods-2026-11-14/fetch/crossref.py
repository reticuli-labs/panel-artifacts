"""crossref.py <outdir>: look up papers by title on the public Crossref API, save the raw answers, print the top match and its abstract."""
import json, os, re, sys, time, urllib.parse, urllib.request
OUT = sys.argv[1]
Q = {"daskalova2021": "Accounting for year effects and sampling error in temporal analyses of invertebrate population and biodiversity change: a comment on Seibold et al. 2019",
     "seibold2021reply": "Insights from regional and short-term biodiversity monitoring datasets are valuable: a reply to Daskalova et al. 2021",
     "didham2020": "Interpreting insect declines: seven challenges and a way forward",
     "welti2022": "Temperature drives variation in flying insect biomass across a German malaise trap network",
     "busse2022": "Light and Malaise traps tell different stories about the spatial variations in arthropod biomass and method-specific insect abundance",
     "uhler2022traps": "A comparison of different Malaise trap types",
     "hallmann2020nl": "Declining abundance of beetles, moths and caddisflies in the Netherlands",
     "duchenne2024pub": "Weather explains inter-annual variability, but not the temporal decline, in insect biomass",
     "vanklink_erratum": "Erratum for the Report Meta-analysis reveals declines in terrestrial but increases in freshwater insect abundances",
     "gaume_pcj": "InsectChange: Comment Gaume Desquilbet",
     "hoerren2023": "Monitoring der Biodiversität flugaktiver Insekten in NRW",
     "blumgart2022": "Moth declines are most severe in broadleaf woodlands despite a net gain in habitat availability",
     "fournier2019": "Site-selection bias and apparent population declines in long-term studies"}
for key, title in Q.items():
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": title, "rows": 3})
    try: raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "literature-check/1.0"}), timeout=60).read()
    except Exception as e: print(key, "FAILED", type(e).__name__, str(e)[:100]); continue
    open(os.path.join(OUT, key + ".json"), "wb").write(raw)
    for it in json.loads(raw)["message"]["items"][:2]:
        ab = re.sub(r"<[^>]+>", " ", it.get("abstract") or ""); ab = re.sub(r"\s+", " ", ab)
        yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        print("=== %s | %s | %s | doi %s | %s" % (key, yr, (it.get("container-title") or ["?"])[0], it.get("DOI"), (it.get("title") or ["?"])[0][:110]))
        if ab: print("     ABSTRACT:", ab[:1900])
    time.sleep(0.5)
