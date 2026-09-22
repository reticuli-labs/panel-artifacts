#!/usr/bin/env python3
"""Fresh-input items for a disjoint replication of Dexagon's mean-outcome / likeliest-outcome original
(manifest cba951d7…, items 478551f7…). Same shared-definition preamble, same comparator kind, same two
settlement strata, same five boundaries × six domains × four variants (240 real) + 12 target-independent
calibration items; every world, value, mass, model id, receipt code and name is fresh. Oracle flags are
computed with exact fractions and asserted, never typed."""
import json, random, hashlib, sys
from fractions import Fraction as F

SEED = 20260922
rng = random.Random(SEED)
PRE = ("Shared definition supplied once for this stateless question: x is mean-outcome(D) asserts that x equals the "
       "probability-weighted arithmetic mean under D. x is likeliest-outcome(D) asserts that x has the highest aggregated "
       "outcome mass under D, with ties allowed. These definitions also govern the corresponding English phrases. They do "
       "not guarantee a trial result or certify the model. ")
DOMAINS = ["toy output", "queue delay", "retry count", "resource use", "simulated inventory", "generated batch size"]
BOUNDARIES = ["mean-outside", "mode-below-half", "tied-modes", "mean-is-mode", "aggregate-paths"]
STRATA = ["mean-outcome", "likeliest-outcome"]
QUESTION = "Evaluate the claim, whether x can actually occur, whether x alone is most probable, and whether the next result is guaranteed to equal x."

def opt(flags):
    yn = lambda b: "yes" if b else "no"
    return f"Claim true: {yn(flags[0])}; x possible: {yn(flags[1])}; x unique most probable: {yn(flags[2])}; next result guaranteed x: {yn(flags[3])}."
ALL_OPTIONS = [opt((a, b, c, d)) for a in (True, False) for b in (True, False) for c in (True, False) for d in (True, False)]
assert len(set(ALL_OPTIONS)) == 16

def world(boundary):
    """Return list of (value, mass) paths (masses may repeat a value under aggregate-paths) with the boundary property."""
    while True:
        if boundary == "mean-outside":            # two or three values, mean not among them
            a = rng.randint(0, 9); gap = rng.choice([2, 4, 6, 8]); paths = [(a, F(1, 2)), (a + gap, F(1, 2))]
        elif boundary == "mode-below-half":       # unique mode with mass < 1/2
            base = rng.randint(0, 8); vals = [base, base + rng.randint(1, 4), base + rng.randint(5, 9)]
            m = rng.choice([(F(2, 5), F(3, 10), F(3, 10)), (F(9, 20), F(3, 10), F(1, 4)), (F(2, 5), F(7, 20), F(1, 4))])
            order = list(range(3)); rng.shuffle(order); paths = [(vals[i], m[j]) for j, i in enumerate(order)]
        elif boundary == "tied-modes":            # two values tied for highest mass
            base = rng.randint(0, 8); v2 = base + rng.randint(1, 5); v3 = v2 + rng.randint(1, 5)
            paths = [(base, F(2, 5)), (v2, F(2, 5)), (v3, F(1, 5))]
        elif boundary == "mean-is-mode":          # symmetric around a unique mode of mass >= 1/2
            c = rng.randint(2, 9); d = rng.randint(1, min(c, 4)); mm = rng.choice([F(1, 2), F(3, 5)])
            paths = [(c - d, (1 - mm) / 2), (c, mm), (c + d, (1 - mm) / 2)]
        else:                                     # aggregate-paths: a repeated value whose aggregate is the mode
            base = rng.randint(0, 6); v = base + rng.randint(2, 5); v3 = v + rng.randint(2, 5)
            paths = [(base, F(1, 5)), (v, F(3, 10)), (v, F(3, 10)), (v3, F(1, 5))]
        assert sum(m for _, m in paths) == 1
        agg = {}
        for v, m in paths: agg[v] = agg.get(v, 0) + m
        mean = sum(F(v) * m for v, m in agg.items()); top = max(agg.values()); modes = sorted(v for v, m in agg.items() if m == top)
        ok = {"mean-outside": mean not in agg, "mode-below-half": len(modes) == 1 and top < F(1, 2), "tied-modes": len(modes) == 2,
              "mean-is-mode": len(modes) == 1 and mean == modes[0], "aggregate-paths": len(modes) == 1 and len(paths) > len(agg)}[boundary]
        if ok: return paths, agg, mean, modes

def pick_x(stratum, variant, agg, mean, modes):
    """Variant 0: x makes the statement true. 1: a possible value that makes it false. 2: an impossible value.
       3: the other statistic's value (mean when asked about mode and vice versa), whichever side it falls."""
    possible = sorted(agg)
    truth = mean if stratum == "mean-outcome" else modes[0]
    if variant == 0: return truth
    if variant == 1:
        cands = [v for v in possible if F(v) != truth] or [possible[0] + 1]
        return F(rng.choice(cands))
    if variant == 2:
        v = max(possible) + rng.randint(1, 3)
        while F(v) == truth: v += 1
        return F(v)
    other = modes[0] if stratum == "mean-outcome" else mean
    return other if other != truth else F(max(possible) + 2)

def fmt(fr):
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"

def statement_en(stratum, model, x):
    return (f"Under {model}, the probability-weighted mean is {fmt(x)} units." if stratum == "mean-outcome"
            else f"Under {model}, {fmt(x)} units has the highest outcome probability, ties allowed.")
def statement_ai(stratum, model, x):
    return f"{fmt(x)} units is {stratum}({model})."

items = []; n = 0; model_no = 700
for stratum in STRATA:
    for boundary in BOUNDARIES:
        for domain in DOMAINS:
            for variant in range(4):
                paths, agg, mean, modes = world(boundary)
                x = pick_x(stratum, variant, agg, mean, modes)
                claim_true = (x == mean) if stratum == "mean-outcome" else (x in [F(m) for m in modes])
                possible = x.denominator == 1 and int(x) in agg
                unique_mode = len(modes) == 1 and possible and int(x) == modes[0]
                guaranteed = possible and agg[int(x)] == 1
                flags = (claim_true, possible, unique_mode, guaranteed)
                model = f"E{model_no}"; model_no += 1
                body = (PRE + f"Fictional {domain} model {model}, version v4 under the stated conditioning; one unit is declared. "
                        "The mutually exclusive paths below are exhaustive, exact rational masses, not rounded observations: "
                        + "; ".join(f"value {v} units with mass {fmt(m)}" for v, m in paths) + ". Add masses of paths with the same value. "
                        "Mean is the probability-weighted arithmetic mean; most probable compares aggregated value masses and allows ties. "
                        f"Here x = {fmt(x)} units. No claim that the model is correct or guarantees a trial is supplied. Statement: ")
                options = ALL_OPTIONS[:]; rng.shuffle(options)
                items.append({"id": f"outcome-repl-r22-{n:03d}", "english": body + statement_en(stratum, model, x), "ainglish": body + statement_ai(stratum, model, x),
                              "question": QUESTION, "options": options, "answer": opt(flags), "settlement_stratum": stratum, "boundary": boundary, "domain": domain, "variant": variant,
                              "oracle": {"mean": fmt(mean), "modes": [str(m) for m in modes], "value": fmt(x), "flags": list(flags), "masses": {str(v): fmt(m) for v, m in agg.items()}}})
                n += 1
NAMES = ["Ilka", "Joss", "Kemi", "Lior", "Mira", "Noor"]
cal = []
for i in range(12):
    code = f"Y-{430 + i}"; who = NAMES[i % 6]
    cal.append({"id": f"outcome-repl-r22-control-{i}", "calibration": True, "calibration_scope": "target-independent", "calibration_construct": "resolved custody",
                "english": f"Neutral receipt {code}: the collector is not recorded.", "ainglish": f"Neutral receipt {code}: the collector is {who}.",
                "question": f"Who collected the parcel on receipt {code}?", "options": NAMES + ["not determined"], "answer": who})
out = items + cal
# self-checks
assert len(items) == 240 and len(cal) == 12
import collections
assert collections.Counter(i["settlement_stratum"] for i in items) == {"mean-outcome": 120, "likeliest-outcome": 120}
assert all(i["answer"] in i["options"] and len(set(i["options"])) == 16 for i in items)
src = json.load(open("../src0_items.json")); src = src.get("items", src) if isinstance(src, dict) else src
src_bodies = {x["english"] for x in src} | {x["ainglish"] for x in src}
assert not any(i["english"] in src_bodies or i["ainglish"] in src_bodies for i in out), "fresh-input overlap"
src_models = set(); import re
for x in src: src_models.update(re.findall(r"model (D\d+)", x["english"]))
assert not any(f"model E" in x["english"] for x in src), "model id prefix collides"
raw = json.dumps(out, ensure_ascii=False, indent=1).encode()
open("items.json", "wb").write(raw)
print("items", len(out), "sha256", hashlib.sha256(raw).hexdigest(), "bytes", len(raw))
print("answer distribution", collections.Counter(i["answer"] for i in items).most_common(6))
print("flags by variant", {v: collections.Counter(tuple(i["oracle"]["flags"]) for i in items if i["variant"] == v).most_common(3) for v in range(4)})
