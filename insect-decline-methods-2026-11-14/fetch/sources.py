"""sources.py <dl dir> <out json>: the source list, with citation fields copied from the saved index answers (Europe PMC, Crossref).
Nothing here is typed from memory except the keys and the note on how much of each source was read."""
import json, re, sys
R, OUT = sys.argv[1].rstrip("/") + "/", sys.argv[2]


def epmc(key, doi):
    for r in json.load(open(R + "epmc/%s.search.json" % key, encoding="utf-8"))["resultList"]["result"]:
        if r.get("doi") == doi:
            j = (r.get("journalInfo") or {})
            return {"authors": r.get("authorString"), "title": r.get("title"), "journal": (j.get("journal") or {}).get("title"), "year": r.get("pubYear"), "volume": j.get("volume"), "pages": r.get("pageInfo"), "doi": r.get("doi"), "first_published": r.get("firstPublicationDate"), "index": "Europe PMC"}
    raise SystemExit("no record " + key)


def crossref(key, container):
    for it in json.load(open(R + "crossref/%s.json" % key, encoding="utf-8"))["message"]["items"]:
        if (it.get("container-title") or [""])[0] == container:
            au = ", ".join("%s %s" % (a.get("family", ""), "".join(w[0] for w in a.get("given", "").split())) for a in it.get("author", []))
            return {"authors": au, "title": re.sub(r"\s+", " ", (it.get("title") or [""])[0]), "journal": container, "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0], "volume": it.get("volume"), "pages": it.get("page"), "doi": it.get("DOI"), "index": "Crossref"}
    raise SystemExit("no record " + key)


icd = "Insect Conservation and Diversity"
S = {
 "hallmann2017": dict(epmc("hallmann2017", "10.1371/journal.pone.0185809"), read="full text (Europe PMC open-access XML)"),
 "seibold2019": dict(epmc("seibold2019", "10.1038/s41586-019-1684-3"), read="abstract only (the article is behind a paywall)"),
 "daskalova2021": dict(crossref("daskalova2021", icd), read="abstract only"),
 "seibold2021reply": dict(crossref("seibold2021reply", icd), read="abstract only"),
 "vanklink2020": dict(epmc("vanklink2020", "10.1126/science.aax9931"), read="abstract only"),
 "science_eeoc_record": dict(epmc("vanklink2020", "10.1126/science.aee6983"), read="bibliographic record only: title and date. The notice's own wording was not retrievable (the publisher's page refused the request)"),
 "gaume2024": dict(crossref("gaume_pcj", "Peer Community Journal"), read="abstract only"),
 "gaume_statement_2026": {"authors": "Gaume L, Desquilbet M", "title": "Statement emailed to Retraction Watch, as published by Retraction Watch in January 2026", "read": "full text of the statement"},
 "mueller2023": dict(epmc("mueller2023", "10.1038/s41586-023-06402-z"), read="abstract only (the article is behind a paywall)"),
 "hallmann2025_and_reply": dict(epmc("hallmann2025ma", "10.1038/s41586-024-08528-0"), read="full text of the Matters Arising and of the authors' reply printed after it (publisher's PDF in the KNAW research portal)", reply=epmc("hallmann2025ma", "10.1038/s41586-024-08529-z")),
 "duchenne2024": dict(crossref("duchenne2024pub", icd), read="abstract of the published version; abstract and opening of the preprint"),
 "muehlethaler2024": dict(epmc("muehlethaler2024", "10.1002/ece3.11182"), read="full text (Europe PMC open-access XML)"),
 "welti2022": dict(crossref("welti2022", icd), read="abstract only"),
 "busse2022": dict(crossref("busse2022", icd), read="abstract only"),
 "uhler2022traps": dict(crossref("uhler2022traps", icd), read="abstract only"),
 "uhler2021": dict(epmc("uhler2021", "10.1038/s41467-021-26181-3"), read="abstract; the full text was fetched and searched for one term"),
 "neff2022": dict(epmc("neff2022", "10.1038/s41467-022-35223-3"), read="abstract"),
 "hallmann2020nl": dict(crossref("hallmann2020nl", icd), read="abstract only"),
 "fournier2019": dict(epmc("fournier2019", "10.1111/cobi.13371"), read="abstract only"),
}
json.dump({"fetched": "2026-11-14", "note": "Citation fields are copied from the index named in each entry, not typed from memory.", "sources": S}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for k, v in S.items(): print(k, "|", v.get("year"), "|", v.get("journal"), "|", (v.get("authors") or "")[:50], "|", v.get("doi"))
