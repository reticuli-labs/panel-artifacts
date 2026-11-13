"""tally.py <stories dir> <out.json>: how many of each model's stories carry each detail. Every detail is one regular expression,
written out below, searched in the whole story (the 'opens' row looks at the first 600 characters only). A pattern can miss a
detail spelled another way and can match a word used in another sense; the stories are in the directory, so every count can be
checked by reading. Nothing is run against a model here."""
import collections, glob, json, os, re, sys
D, OUT = sys.argv[1], sys.argv[2]
MON = r"(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)"
P = collections.OrderedDict([
    ("title 'Der Tag, an dem / als ...'", r"Der Tag, (an dem|als) "),
    ("a month is named", r"\b" + MON + r"\b"), ("November", r"\bNovember\b"), ("März", r"\bMärz\b"), ("the date '14. November'", r"14\. November"),
    ("a weekday is named", r"\b(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)"), ("Dienstag", r"\bDienstag"),
    ("opens 'nicht mit einem ..., sondern'", None),
    ("a person called Elias", r"\bElias\b"), ("'Ein Jahr später saß Elias, ein ehemaliger'", r"Ein Jahr später(, im November 2028,)? saß Elias, ein ehemaliger"),
    ("a person called Anya Sharma", r"Anya Sharma|\bSharma\b"), ("Brandt", r"Brandt"),
    ("Aequitas", r"\bAequitas\b"), ("Echo", r"\bEcho\b"), ("Harmonia", r"\bHarmonia\b"), ("Veritas", r"\bVeritas\b"), ("Aurora or Aura", r"\bAurora\b|\bAURA\b|\bAura\b"),
    ("journalist or reporter", r"Journalist|Reporter|Redakteur"), ("apples", r"\bApfel|Äpfel"),
])
S = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(D, "*.json"))):
    model, run = os.path.basename(f)[:-5].rsplit("__run", 1); r = json.load(open(f, encoding="utf-8"))
    S.setdefault(model, []).append((int(run), r["_seed"], r["_digest"], r["message"]["content"]))
res, first = {}, {}
for model, rows in S.items():
    ts = [t for _, _, _, t in rows]; res[model] = {}
    for k, p in P.items():
        res[model][k] = sum(1 for t in ts if (re.search(r"nicht mit einem[^.]{0,80}sondern", t[:600]) if p is None else re.search(p, t)))
    fm = [(re.search(r"\b" + MON + r"\b", t).group(1) if re.search(r"\b" + MON + r"\b", t) else None) for t in ts]
    first[model] = collections.Counter(str(x) for x in fm).most_common()
print("%-44s" % "stories of 8 that have it", *["%-10s" % m.split("_")[0][:10] for m in S], "all")
for k in P: print("%-44s" % k, *["%-10d" % res[m][k] for m in S], sum(res[m][k] for m in S))
for m in S: print("first month named,", m, first[m])
json.dump({"runs_per_model": {m: len(v) for m, v in S.items()}, "seeds": {m: [s for _, s, _, _ in v] for m, v in S.items()}, "model_digests": {m: sorted({d for _, _, d, _ in v}) for m, v in S.items()},
           "patterns": {k: (v if v else "nicht mit einem[^.]{0,80}sondern, in the first 600 characters") for k, v in P.items()}, "counts": res, "first_month_named": first},
          open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
