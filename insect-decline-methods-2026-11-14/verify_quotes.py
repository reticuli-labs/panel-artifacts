"""verify_quotes.py <claims.json> <fetched dir>: assert that every quoted passage occurs in the source text as fetched.

<fetched dir> is the directory the fetch scripts wrote: epmc/ (Europe PMC search answers and full-text XML), crossref/ (Crossref
answers) and text/ (plain text made from the full texts and PDFs by totext.py and pdftotext). The texts themselves are not
redistributed here; the fetch scripts get them again. Comparison is on normalised text: tags removed, entities decoded, every
kind of hyphen and whitespace folded. Exit 1 when a passage is missing. With --mutate each passage has one digit or letter changed
first, and the run must then find NONE of them: a check that cannot fail proves nothing."""
import html, json, os, re, sys


def norm(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = s.replace("‐", "-").replace("‑", "-").replace("­", "").replace("−", "-").replace("∆", "Δ")
    s = s.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", s).strip()


def epmc_abstract(root, key, doi=None, title_has=None):
    rs = json.load(open(os.path.join(root, "epmc", key + ".search.json"), encoding="utf-8"))["resultList"]["result"]
    for r in rs:
        if (doi and r.get("doi") == doi) or (title_has and title_has in (r.get("title") or "")):
            return " ".join([r.get("title") or "", r.get("abstractText") or "", "first published " + (r.get("firstPublicationDate") or "")])
    raise SystemExit("no Europe PMC record for " + key)


def crossref_abstract(root, key, container):
    for it in json.load(open(os.path.join(root, "crossref", key + ".json"), encoding="utf-8"))["message"]["items"]:
        if (it.get("container-title") or [""])[0] == container and it.get("abstract"): return it["abstract"]
    raise SystemExit("no Crossref abstract for " + key)


def text(root, name): return open(os.path.join(root, "text", name), encoding="utf-8").read()


def corpus(root):
    icd = "Insect Conservation and Diversity"
    return {
        "hallmann2017": text(root, "PMC5646769.txt"),
        "muehlethaler2024": text(root, "PMC10961242.txt"),
        "hallmann2025_and_reply": text(root, "hallmann2025ma_flow.txt"),
        "gaume_statement_2026": text(root, "gaume_statement_2026.txt"),
        "seibold2019": epmc_abstract(root, "seibold2019", doi="10.1038/s41586-019-1684-3"),
        "vanklink2020": epmc_abstract(root, "vanklink2020", doi="10.1126/science.aax9931"),
        "science_eeoc_record": epmc_abstract(root, "vanklink2020", doi="10.1126/science.aee6983"),
        "mueller2023": epmc_abstract(root, "mueller2023", doi="10.1038/s41586-023-06402-z"),
        "uhler2021": epmc_abstract(root, "uhler2021", doi="10.1038/s41467-021-26181-3"),
        "neff2022": epmc_abstract(root, "neff2022", doi="10.1038/s41467-022-35223-3"),
        "fournier2019": epmc_abstract(root, "fournier2019", doi="10.1111/cobi.13371"),
        "daskalova2021": crossref_abstract(root, "daskalova2021", icd),
        "seibold2021reply": crossref_abstract(root, "seibold2021reply", icd),
        "welti2022": crossref_abstract(root, "welti2022", icd),
        "busse2022": crossref_abstract(root, "busse2022", icd),
        "uhler2022traps": crossref_abstract(root, "uhler2022traps", icd),
        "hallmann2020nl": crossref_abstract(root, "hallmann2020nl", icd),
        "duchenne2024": crossref_abstract(root, "duchenne2024pub", icd),
        "gaume2024": crossref_abstract(root, "gaume_pcj", "Peer Community Journal"),
    }


def mutate(q):
    """Change the first digit of the passage, or its first letter when it has no digit."""
    for i, ch in enumerate(q):
        if ch.isdigit(): return q[:i] + str((int(ch) + 1) % 10) + q[i + 1:]
    for i, ch in enumerate(q):
        if ch.isalpha(): return q[:i] + ("x" if ch != "x" else "y") + q[i + 1:]
    return q + "x"


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]; mut = "--mutate" in argv
    claims = json.load(open(args[0], encoding="utf-8"))["claims"]; C = {k: norm(v) for k, v in corpus(args[1]).items()}
    found = 0
    for c in claims:
        q = norm(mutate(c["quote"]) if mut else c["quote"]); ok = q in C[c["source"]]; found += ok
        if ok == mut: print(("STILL FOUND after mutation" if mut else "MISSING"), c["id"], "|", c["source"], "|", q[:90])
    assert "2026-01-22" in C["science_eeoc_record"], "the expression of concern's first publication date"
    print("%s: %d claims, %d passages found, %d sources" % ("mutated passages" if mut else "passages as quoted", len(claims), found, len({c["source"] for c in claims})))
    return 0 if (found == 0 if mut else found == len(claims)) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
