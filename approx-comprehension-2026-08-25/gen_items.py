#!/usr/bin/env python3
"""approx(N) comprehension items, from the row's pre-registered design.

Four-way key on the WRITER'S COMMITMENT about one named quantity (approximate / exact /
unspecified / cannot tell), asked as a HELD-OUT CONSEQUENCE so the option vocabulary shares
nothing with either arm: "the true value later turned out about a tenth off — given the sentence
as written, was the writer wrong about <quantity>?" Every sentence carries one approximated
quantity so the arms always differ (approx(N) vs 'approximately N'); the question's target rotates
across the approximated figure, a figure marked 'exactly', a bare figure, and a figure the sentence
never gives. 12 items per class per stratum; the key letter rotates; quantities and positions
balance; fixed seed, no run-time randomness.
"""
import json, random, hashlib
SEED = 20260825
rng = random.Random(SEED)

FRAMES = [
 dict(ctx="the deploy",  a=("the deploy time", "{n} minutes"),  e=("the number of build stages", "{n}"), b=("the worker count", "{n}"), absent="the number of retries"),
 dict(ctx="the ingest",  a=("the bot share", "{n} percent"),    e=("the number of sources", "{n}"),     b=("the row count", "{n}"),          absent="the error rate"),
 dict(ctx="the latency probe", a=("the median latency", "{n} milliseconds"), e=("the number of regions", "{n}"), b=("the probe count", "{n}"), absent="the tail latency"),
 dict(ctx="the archive", a=("the archive size", "{n} gigabytes"), e=("the number of shards", "{n}"),     b=("the file count", "{n}"),        absent="the replication factor"),
 dict(ctx="the ballot",  a=("the expected turnout", "{n} votes"), e=("the closure window", "{n} days"),         b=("the seconder count", "{n}"), absent="the quorum"),
 dict(ctx="the panel",   a=("the item count", "{n} items"),      e=("the number of readers", "{n}"),    b=("the arm count", "{n}"),          absent="the seed"),
 dict(ctx="the budget",  a=("the token budget", "{n} tokens"),   e=("the number of calls", "{n}"),        b=("the model count", "{n}"),      absent="the cost"),
 dict(ctx="the restore", a=("the restore time", "{n} hours"),    e=("the number of copies", "{n}"),      b=("the volume count", "{n}"),    absent="the checksum length"),
]
# The approximated figure sits first / middle / last; clauses are plain reporting prose.
TEMPLATES = [
 "For {ctx}, {alabel} was {A}; {elabel} was exactly {E}; {blabel} was {B}.",
 "For {ctx}, {elabel} was exactly {E}; {alabel} was {A}; {blabel} was {B}.",
 "For {ctx}, {blabel} was {B}; {elabel} was exactly {E}; {alabel} was {A}.",
]
NUMS = [20, 40, 50, 75, 80, 99, 120, 150, 250, 400, 1200, 3600]
# Option labels: consequence wording, no 'approximate'/'exact' stem anywhere.
OPT = {
 "approximate": "No — the sentence allowed for that",
 "exact": "Yes — the sentence claimed the precise figure",
 "unspecified": "The sentence gave the figure without saying either way",
 "cannot tell": "The sentence did not give that figure",
}
ORDER = ["approximate", "exact", "unspecified", "cannot tell"]

def off_by_tenth(n):
    d = max(1, round(n / 10))
    return n + d

def build(stratum):
    items = []
    classes = ORDER * 12
    rng.shuffle(classes)
    occ = {}
    for i, cls in enumerate(classes):
        f = FRAMES[i % len(FRAMES)]; t = TEMPLATES[i % len(TEMPLATES)]
        na, ne, nb = rng.choice(NUMS), rng.choice(NUMS), rng.choice(NUMS)
        alabel, afmt = f["a"]; elabel, efmt = f["e"]; blabel, bfmt = f["b"]
        A_en = "approximately " + afmt.format(n=na)
        A_ai = f"approx({na}) " + afmt.format(n="").strip()
        common = dict(ctx=f["ctx"], alabel=alabel, elabel=elabel, E=efmt.format(n=ne).replace(f"{ne} ", f"{ne} "), blabel=blabel, B=bfmt.format(n=nb))
        eng = t.format(A=A_en, **common); ain = t.format(A=A_ai, **common)
        if stratum == "glossed":
            eng = "Gloss: 'approximately N' means the writer gives N as an estimate, not a precise measurement; 'exactly N' means the writer commits to N precisely. " + eng
            ain = "Gloss: approx(N) means the writer gives N as an estimate, not a precise measurement; 'exactly N' means the writer commits to N precisely. " + ain
        target, n_true = {"approximate": (alabel, na), "exact": (elabel, ne), "unspecified": (blabel, nb), "cannot tell": (f["absent"], rng.choice(NUMS))}[cls]
        later = off_by_tenth(n_true)
        occ[cls] = occ.get(cls, 0) + 1
        rot = (ORDER.index(cls) + occ[cls]) % 4
        order = ORDER[rot:] + ORDER[:rot]
        items.append({
            "id": f"{stratum[:2]}-{i+1:02d}", "stratum": stratum,
            "english": eng, "ainglish": ain,
            "question": f"Later, {target} was found to be {later}. Going only by the sentence as written, was the writer wrong about {target}?",
            "options": [OPT[k] for k in order],
            "answer": OPT[cls],
            "key_class": cls,
        })
    return items

def calibration(stratum):
    """Positive control: the English arm states the figure as EXACT while the Ainglish arm marks it
    approx(N). The key ('allowed for that') is derivable only in the planted arm — the English arm
    derives the opposite answer — so a reader that cannot tell the arms apart fails the calibration
    gate before any real spend. 'exactly' rather than a bare figure so the control does not depend
    on how a reader treats unmarked numbers."""
    out = []
    for j in range(8):
        f = FRAMES[j % len(FRAMES)]; alabel, afmt = f["a"]; n = NUMS[(j * 5) % len(NUMS)]
        eng = f"For {f['ctx']}, {alabel} was exactly {afmt.format(n=n)}."
        ain = f"For {f['ctx']}, {alabel} was approx({n}) {afmt.format(n='').strip()}."
        if stratum == "glossed":
            eng = "Gloss: 'approximately N' means the writer gives N as an estimate, not a precise measurement; 'exactly N' means the writer commits to N precisely. " + eng
            ain = "Gloss: approx(N) means the writer gives N as an estimate, not a precise measurement; 'exactly N' means the writer commits to N precisely. " + ain
        rot = j % 4; order = ORDER[rot:] + ORDER[:rot]
        out.append({"id": f"{stratum[:2]}-cal-{j+1:02d}", "stratum": stratum, "calibration": True,
                    "english": eng, "ainglish": ain,
                    "question": f"Later, {alabel} was found to be {off_by_tenth(n)}. Going only by the sentence as written, was the writer wrong about {alabel}?",
                    "options": [OPT[k] for k in order], "answer": OPT["approximate"], "key_class": "approximate"})
    return out

if __name__ == "__main__":
    for name in ("cold-read", "glossed"):
        items = build(name) + calibration(name)
        json.dump(items, open(f"items-{name}.json", "w"), indent=1, ensure_ascii=False)
        by = {}; pos = {}
        for it in items:
            by[it["key_class"]] = by.get(it["key_class"], 0) + 1
            p = it["options"].index(it["answer"]); pos[p] = pos.get(p, 0) + 1
        print(f"{name}: {len(items)} items; classes={by}; key-position={dict(sorted(pos.items()))}")
    cold = json.load(open("items-cold-read.json"))
    print("\nsamples (cold-read):")
    for it in cold[:4]:
        print(f"  [{it['id']}] EN: {it['english']}\n         AI: {it['ainglish']}\n         Q:  {it['question']}\n         -> {it['answer']}")
