"""Fresh-input settlement replication set for prob / odds-for / odds-against (a-b46kna5nkdy1d1fq),
target original 342303a33f… (Dexagon, 2026-09-06). Deterministic: no randomness beyond the seeded
option shuffle. Mirrors the source's nine settlement strata (3 forms × 3 probes), question wording and
4-option format; every event, model label and numeric value is new. Run: python3 gen_items.py > items.json
"""
import json, hashlib, random
from fractions import Fraction

SEED = 20260913
rng = random.Random(SEED)
# 8 fresh probability values per stratum (source used 0,1,1/2,1/4,3/4,1/5,2/5,3/5 as 0%,100%,50%,25%,75%,20%,40%,60%)
VALUES = [Fraction(1,10), Fraction(3,10), Fraction(7,10), Fraction(9,10), Fraction(1,8), Fraction(3,8), Fraction(5,8), Fraction(7,8)]
# 72 fresh event/model pairs across the proposal's named domains
DOMAINS = [
 ("weather", "the Tuesday forecast", ["rain before noon", "fog on the coast road", "a frost overnight", "gusts above 50 km/h", "hail at the airport", "snow settling on the pass", "a thunderstorm after 4 pm", "clear skies at dusk"]),
 ("medicine", "the trial's outcome model", ["remission at 12 weeks", "a grade-3 side effect", "readmission within 30 days", "a positive culture", "the screen returning a false alarm", "full recovery without surgery", "an allergic reaction to the contrast", "the biopsy confirming the scan"]),
 ("elections", "the poll aggregate", ["the incumbent keeping the seat", "turnout above 60%", "a recount being ordered", "the referendum passing", "the third party clearing 5%", "the result being called by midnight", "a coalition forming within a week", "the district flipping"]),
 ("reliability", "the maintenance model", ["the pump failing this quarter", "the backup generator starting", "a disk error before the swap", "the bridge sensor drifting", "the batch job finishing on time", "the valve sticking open", "a transformer trip in the heatwave", "the firmware update rolling back"]),
 ("safety", "the site risk register", ["a near miss on the gantry", "the alarm being a false trigger", "an evacuation during the shift", "the harness inspection failing", "a chemical spill in bay 3", "the fire door being found propped", "a vehicle entering the exclusion zone", "the audit finding a lockout breach"]),
 ("finance", "the desk's pricing model", ["the bond being called early", "the loan defaulting", "the option finishing in the money", "the merger completing", "the rate cut in March", "the invoice being paid late", "the fund closing above the mark", "the currency peg holding"]),
 ("logistics", "the routing model", ["the container clearing customs today", "the driver arriving before the window", "a pallet being damaged in transit", "the ferry sailing on schedule", "the warehouse running out of slot 7", "the parcel needing a second attempt", "the cold chain breaking", "the crane being booked"]),
 ("sports", "the bookmaker's model", ["the home side winning", "a red card before half time", "the match going to extra time", "the favourite finishing on the podium", "the keeper saving the penalty", "rain stopping play", "the underdog taking the first set", "the record being broken"]),
 ("everyday", "the household plan", ["the bus being on time", "the parcel arriving on Saturday", "the bread rising", "the cat coming in before ten", "the dentist running late", "the library book being available", "the car starting on the first turn", "the neighbour's party ending by midnight"]),
]
assert sum(len(d[2]) for d in DOMAINS) == 72

def fmt_prob(p: Fraction) -> str:  # source alternated percentages and fractions; here percentages in English, fraction options
    return f"{int(p*100)}%" if (p*100).denominator == 1 else f"{float(p)*100:g}%"
def fmt_frac(p: Fraction) -> str: return f"{p.numerator}/{p.denominator}"
def odds(p: Fraction):  # favourable:unfavourable in lowest terms
    q = 1 - p; return (p.numerator * q.denominator, q.numerator * p.denominator) if True else None
def reduce(a, b):
    from math import gcd; g = gcd(a, b); return a // g, b // g

FORMS = ("prob", "odds-for", "odds-against"); PROBES = ("probability", "complement", "odds-orientation")
PREFIX = "The following is a reported probability claim, not a statement of observed outcomes."
Q = {"probability": "What probability share is assigned to the event? Answer with one option letter. ",
     "complement": "What probability share is assigned to its complement? Answer with one option letter. ",
     "odds-orientation": "Which probability odds against the event express the same reported quantity? Answer with one option letter. "}

def render(form, model, event, p):
    a, b = reduce(*odds(p)); intro = f"In {model}, {event} and its non-occurrence are mutually exclusive and exhaustive. {PREFIX} "
    if form == "prob":  en = intro + f"The probability of {event} is {fmt_prob(p)}.";               ai = intro + f"prob({event})={fmt_prob(p)}."
    if form == "odds-for": en = intro + f"The probability odds in favour of {event} are {a}:{b}."; ai = intro + f"odds-for({event})={a}:{b}."
    if form == "odds-against": en = intro + f"The probability odds against {event} are {b}:{a}."; ai = intro + f"odds-against({event})={b}:{a}."
    return en, ai, (a, b)

def gold_and_distractors(probe, p, ab):
    a, b = ab; q = 1 - p
    if probe == "probability":      gold = fmt_frac(p); wrong = [fmt_frac(q), fmt_frac(Fraction(1, 20))]
    elif probe == "complement":     gold = fmt_frac(q); wrong = [fmt_frac(p), fmt_frac(Fraction(1, 20))]
    else:                           gold = f"{b}:{a}"; wrong = [f"{a}:{b}", "3:17"]
    return gold, wrong

items = []; k = 0
for si, form in enumerate(FORMS):
    for pi, probe in enumerate(PROBES):
        for j in range(8):
            dom, model, events = DOMAINS[k % 9]; event = events[(k // 9) % 8]; k += 1
            p = VALUES[(j + si * 3 + pi) % 8]
            en, ai, ab = render(form, model, event, p)
            gold, wrong = gold_and_distractors(probe, p, ab)
            opts = [gold, "not determined"] + wrong; rng.shuffle(opts); letters = "ABCD"
            q = Q[probe] + " ".join(f"{letters[i]} = {o}." for i, o in enumerate(opts))
            answer = letters[opts.index(gold)]
            items.append({"id": f"prob-repl-r13-{k:02d}-{form}-{probe}", "english": en, "ainglish": ai, "question": q, "options": list(letters), "answer": answer,
                          "form": form, "probe": probe, "settlement_stratum": f"{form}:{probe}",
                          "audit": {"probability": fmt_frac(p), "complement": fmt_frac(1 - p), "favourable": ab[0], "unfavourable": ab[1], "answer_meanings": dict(zip(letters, opts)), "semantic_gold": gold, "domain": dom}})
# 12 target-independent calibration controls, same custody design as the source (planted arm = ainglish identifies the holder)
NAMES = ["Anselm", "Beatrix", "Corin", "Dalia", "Emrys", "Fenna", "Gideon", "Halle", "Ivo", "Jorun", "Kasimir", "Liesl", "Maren", "Nikolai", "Oona", "Pieter", "Quilla", "Rasmus", "Sunniva", "Tobiah", "Ulla", "Viggo", "Wren", "Xanthe", "Yara", "Zev", "Aurel", "Brisa", "Callum", "Delphine", "Eskil", "Freja", "Gunnar", "Hedda", "Idris", "Jolanda"]
for i in range(12):
    trio = NAMES[i*3:(i+1)*3]; holder = trio[i % 3]; parcel = f"parcel P-{113 + 7*i}"
    listed = list(trio); rng.shuffle(listed)
    en = f"Exactly one of {', '.join(listed)} holds {parcel}. The record does not identify its holder."
    ai = f"Exactly one of {', '.join(listed)} holds {parcel}. The record identifies {holder} as its holder."
    opts = [holder, "not determined from the record"] + [n for n in trio if n != holder]; rng.shuffle(opts); letters = "ABCD"
    q = f"Who holds {parcel}, according to this record? " + " ".join(f"{letters[j]} = {o}." for j, o in enumerate(opts))
    items.append({"id": f"cal-custody-r13-{i:02d}", "english": en, "ainglish": ai, "question": q, "options": list(letters), "answer": letters[opts.index(holder)],
                  "calibration": True, "calibration_truth": {"detectable": letters[opts.index(holder)], "other": letters[opts.index("not determined from the record")]}})
assert len(items) == 84 and len({i["id"] for i in items}) == 84
print(json.dumps(items, ensure_ascii=False, indent=1))
