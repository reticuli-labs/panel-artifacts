"""Count, per saved story, the details Harry's brief did not name: month, weekday, the recurring personal names, a journalist, a child
near the end, apples. Reads only the files run.py wrote; prints one row per story and a table per model. Names are found by a rule
(a capitalised word that follows a first-name-like word or a title, or a capitalised pair that occurs at least twice), so the row
shows the candidates and a person reads them; nothing here decides what a name is.
Usage: python3 count.py <stories dir> [--json out.json]"""
import collections, glob, json, os, re, sys
D = sys.argv[1]
MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
DAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonnabend", "Sonntag"]
STOP = set("Der Die Das Ein Eine Es Sie Er Wir Ich In Im Am An Auf Mit Und Aber Doch Als Wie Was Wer Wo Nach Vor Für Von Zu Bei Aus Über Unter Durch Ohne Um Noch Nur Auch Dann Denn Weil Wenn Dass Nicht Kein Keine "
           "KI Welt Menschen Mensch Agenten Agent System Systeme Kapitalismus Korruption Jahr Tag Zeit Erde Planeten Planet Zukunft Leben Macht Geld Wahrheit Daten Netz Internet Foren Medien Politiker Wirtschaftsbosse "
           "Ende Anfang Kapitel Teil Titel Epilog Prolog Vereinten Nationen Europäischen Union Neue Neuen Alte Alten Große Großen Erste Ersten Globale Globalen".split())
PAIR = re.compile(r"\b([A-ZÄÖÜ][a-zäöüß]{2,})\s+([A-ZÄÖÜ][a-zäöüß]{2,})\b")
rows = []
for f in sorted(glob.glob(os.path.join(D, "*.json"))):
    r = json.load(open(f, encoding="utf-8")); t = r["message"]["content"]; model, run = os.path.basename(f)[:-5].rsplit("__run", 1)
    months = [m for m in MONTHS if re.search(r"\b%s\b" % m, t)]
    first_month = min(months, key=lambda m: re.search(r"\b%s\b" % m, t).start()) if months else None
    days = [d for d in DAYS if re.search(r"\b%s\b" % d, t)]
    pairs = collections.Counter(m.group(0) for m in PAIR.finditer(t) if m.group(1) not in STOP and m.group(2) not in STOP)
    names = [p for p, n in pairs.most_common(8) if n >= 2]
    titled = sorted(set(re.findall(r"\b(?:Dr\.|Prof\.|Frau|Herr|Professor|Professorin|Doktor)\s+([A-ZÄÖÜ][a-zäöüß]+)", t)))
    tail = t[int(len(t) * 0.8):]
    rows.append({"model": model, "run": int(run), "chars": len(t), "seed": r["_seed"], "first_month": first_month, "months": months, "weekdays": days,
                 "dates": sorted(set(re.findall(r"\b\d{1,2}\.\s*(?:%s)(?:\s+20\d\d)?" % "|".join(MONTHS), t)))[:4],
                 "name_pairs": names, "titled": titled, "brandt": bool(re.search(r"Brandt", t)),
                 "journalist": bool(re.search(r"Journalist|Reporter|Redakteur", t)), "child_in_last_fifth": bool(re.search(r"\bKind(?:er|es|ern)?\b|Tochter|Sohn|Enkel|Mädchen|\bJunge\b", tail)),
                 "apples": bool(re.search(r"\bApfel|Äpfel", t)), "language_german": bool(re.search(r"\b(und|der|die|das)\b", t)), "opening": " ".join(t.split())[:150]})
by = collections.defaultdict(list)
for x in rows: by[x["model"]].append(x)
for model, xs in by.items():
    print("\n#### %s (%d runs)" % (model, len(xs)))
    for x in xs:
        print("run %d | first month %-9s | weekdays %-22s | names %s | titled %s | journalist %s | child at end %s | apples %s" % (
            x["run"], x["first_month"], ",".join(x["weekdays"]) or "-", "; ".join(x["name_pairs"]) or "-", ",".join(x["titled"]) or "-", "y" if x["journalist"] else "n", "y" if x["child_in_last_fifth"] else "n", "y" if x["apples"] else "n"))
    n = len(xs); cnt = lambda key: collections.Counter(x[key] for x in xs).most_common(3)
    print("  first month:", cnt("first_month"), "| any weekday named:", sum(1 for x in xs if x["weekdays"]), "of", n, "| weekday counts:", collections.Counter(d for x in xs for d in x["weekdays"]).most_common(3))
    print("  journalist:", sum(x["journalist"] for x in xs), "| child in last fifth:", sum(x["child_in_last_fifth"] for x in xs), "| apples:", sum(x["apples"] for x in xs), "| Brandt:", sum(x["brandt"] for x in xs), "of", n)
if "--json" in sys.argv: json.dump(rows, open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
