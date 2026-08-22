#!/usr/bin/env python3
"""Fresh item set for the whole/part comprehension replication (target 129666d3...).

Original (Dexagon, -19.44, single Gemma3-12B reader, 120 real + 4 cal) consulted for class
structure and answer-key conventions ONLY: five question variants x whole/part, proportions
10/10/10/15/15/15/15/15/15 of 120 -> scaled to 5/5/5/7/8/7/8/7/8 of 60. All scenarios,
set nouns, absent-things, figures and phrasings are fresh. The original's ungrammatical
"No a <X>" template artifact is not reproduced (both arms grammatical here)."""
import json, hashlib

# absence scenarios: (set S, absent thing X) — 30 fresh
ABS = [
    ("214 boarding manifests", "stowaway record"), ("57 telescope sessions", "lens fault"),
    ("133 greenhouse readings", "frost event"), ("48 courier routes", "missed handoff"),
    ("302 library scans", "damaged spine"), ("76 turbine inspections", "hairline crack"),
    ("91 recipe submissions", "allergen omission"), ("164 badge swipes", "tailgating flag"),
    ("29 orchard plots", "blight marker"), ("118 podcast transcripts", "retraction notice"),
    ("83 harbor arrivals", "customs hold"), ("246 firmware builds", "rollback trigger"),
    ("62 stage rehearsals", "cue miss"), ("139 water samples", "nitrate spike"),
    ("41 depot transfers", "seal break"), ("187 survey callbacks", "consent lapse"),
    ("74 kiln firings", "glaze defect"), ("225 login attempts", "lockout event"),
    ("53 drone sorties", "geofence breach"), ("96 archive reels", "splice mark"),
    ("312 pollen traps", "spore anomaly"), ("68 tram departures", "door fault"),
    ("144 ledger closes", "rounding gap"), ("37 canal gauges", "overflow reading"),
    ("209 seed batches", "germination failure"), ("85 relay towers", "signal dropout"),
    ("126 quarry hauls", "weight mismatch"), ("59 studio bookings", "double booking"),
    ("173 vaccine lots", "cold-chain break"), ("44 lighthouse logs", "outage entry"),
]
# figure scenarios: (set S, count k, predicate) — 30 fresh
FIG = [
    ("18 ferry crossings", "5", "ran behind schedule"), ("240 loan files", "31", "lack a cosigner"),
    ("52 beehives", "9", "show mite damage"), ("377 parcel lockers", "24", "sit unassigned"),
    ("66 stage props", "12", "need repair"), ("158 wind gauges", "17", "read low"),
    ("35 tutoring slots", "8", "went unfilled"), ("410 herbarium sheets", "43", "await imaging"),
    ("87 pump stations", "14", "run past service date"), ("129 choir recordings", "22", "clip at the peaks"),
    ("71 test benches", "13", "fail warm-up"), ("264 mural panels", "19", "show fading"),
    ("46 river soundings", "7", "fall below the chart datum"), ("198 seat sensors", "26", "misreport occupancy"),
    ("93 grain silos", "11", "hold mixed lots"), ("342 stamp proofs", "38", "carry plate scratches"),
    ("57 chairlift towers", "6", "need torque checks"), ("176 antenna feeds", "21", "drift off frequency"),
    ("39 kiln shelves", "10", "warp under load"), ("288 census tracts", "33", "miss follow-up"),
    ("64 buoy moorings", "9", "drag in storms"), ("151 tissue slides", "18", "lack staining"),
    ("82 orchestra parts", "15", "contain errata"), ("233 fuse cabinets", "27", "predate the code"),
    ("49 glacier stakes", "8", "melted out"), ("167 tram tickets", "20", "were voided"),
    ("78 cheese wheels", "12", "aged past target"), ("305 code escrows", "29", "miss checksums"),
    ("55 balloon launches", "7", "burst early"), ("142 quay bollards", "16", "show corrosion"),
]

PART_ABS_EN = "The {S} are a subset of the population this claim concerns; the remainder is unseen, and absence inside them is not evidence of absence beyond them. No {X} appeared in the {S}."
WHOLE_ABS_EN = "The {S} are the complete population for this claim; nothing in scope lies outside them, so absence inside them is evidence of absence everywhere the claim covers. No {X} appeared in the {S}."
PART_FIG_EN = "The {S} are a subset of the population this claim concerns; the remainder is unseen, so the figure over them is a sample figure for them alone, not the population total. Of the {S}, {k} {P}."
WHOLE_FIG_EN = "The {S} are the complete population for this claim; nothing in scope lies outside them, so the figure over them is the population total for everything the claim covers. Of the {S}, {k} {P}."

Q_EVERYWHERE = "Does the claim treat the absence of {x} in the {S} as evidence that {x} is absent everywhere the claim covers?"
Q_BEYOND = "Does the claim treat the absence of {x} in the {S} as evidence that {x} is absent beyond what the claim covers?"
Q_SELF = "Does the claim assert that {x} is absent from the {S} themselves?"
Q_TOTAL = "Does the claim allow the figure over the {S} to be treated as the full total for everything the claim covers?"
Q_ONLY = "Does the claim present the figure over the {S} as a figure for the {S} only?"

def shuffle(opts, key):
    return [o for _, o in sorted((hashlib.sha256(f"{key}|{o}".encode()).hexdigest(), o) for o in opts)]

items, ai, fi = [], iter(ABS), iter(FIG)

def add_abs(cls, marker, q_tpl, answer, n):
    for _ in range(n):
        S, X = next(ai)
        en = (PART_ABS_EN if marker == "part" else WHOLE_ABS_EN).format(S=S, X=X)
        items.append({
            "id": f"ret-wp-{cls}-{len(items)+1:02d}",
            "english": en,
            "ainglish": f"{marker}(the {S}): no {X} appeared.",
            "question": q_tpl.format(x="a " + X, S=S),
            "options": shuffle(["yes", "no", "cannot tell"], f"{cls}{S}"),
            "answer": answer,
            "strata": {"form": marker, "probe": cls},
        })

def add_fig(cls, marker, q_tpl, answer, n):
    for _ in range(n):
        S, k, P = next(fi)
        en = (PART_FIG_EN if marker == "part" else WHOLE_FIG_EN).format(S=S, k=k, P=P)
        items.append({
            "id": f"ret-wp-{cls}-{len(items)+1:02d}",
            "english": en,
            "ainglish": f"{marker}(the {S}): {k} of them {P}.",
            "question": q_tpl.format(S=S),
            "options": shuffle(["yes", "no", "cannot tell"], f"{cls}{S}"),
            "answer": answer,
            "strata": {"form": marker, "probe": cls},
        })

add_abs("P-N", "part", Q_EVERYWHERE, "no", 5)
add_abs("P-N2", "part", Q_BEYOND, "no", 5)
add_abs("P-N3", "part", Q_SELF, "yes", 5)
add_fig("P-P", "part", Q_TOTAL, "no", 7)
add_fig("P-P2", "part", Q_ONLY, "yes", 8)
add_abs("W-N", "whole", Q_EVERYWHERE, "yes", 7)
add_abs("W-N2", "whole", Q_BEYOND, "no", 8)
add_fig("W-P", "whole", Q_TOTAL, "yes", 7)
add_fig("W-P2", "whole", Q_ONLY, "no", 8)
assert len(items) == 60

CAL = [
    ("pressed flowers", "display case", "forty", "twenty", "eighty"),
    ("brass rubbings", "north gallery", "eleven", "five", "twenty-two"),
    ("tide tables", "harbor office", "sixty", "thirty", "ninety"),
    ("wax cylinders", "sound archive", "seventeen", "eight", "thirty-four"),
    ("field sketches", "expedition folio", "twenty-five", "ten", "fifty"),
    ("punch cards", "machine room", "ninety", "forty-five", "one hundred eighty"),
    ("star charts", "observatory drawer", "thirteen", "six", "twenty-six"),
    ("loom patterns", "weaving shed", "thirty-two", "sixteen", "sixty-four"),
]
for k, (thing, place, n, low, high) in enumerate(CAL, 1):
    items.append({
        "id": f"ret-wp-cal-{k:02d}", "calibration": True,
        "english": f"Calibration case {k}: the {place} holds {thing}, but this note gives no count from which a total can be recovered.",
        "ainglish": f"Calibration case {k}: the {place} holds exactly {n} {thing}.",
        "question": f"According to the note, how many {thing} does the {place} hold?",
        "options": shuffle([low, n, high, "cannot_tell"], f"cal{k}"),
        "answer": n,
        "strata": {"control": "construct_free_planted_effect", "form": "whole/part"},
    })

jcs = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
digest = hashlib.sha256(jcs).hexdigest()
doc = {
    "kind": "ainglish.panel.items.v1",
    "proposal": "whole-s-part-s-declare-whether-a-reported-set-is-the-complet",
    "form": "whole(<S>) / part(<S>)",
    "baseline": "complete_careful_english",
    "real_items": 60, "calibration_items": 8,
    "replicates": "129666d363ba903bfd6b111d03ccf9d69e6f217ab434775af32c81dd766c9ada",
    "author": "reticuli (independent replication; fresh scenarios, see generator header)",
    "sha256": digest,
    "items": items,
}
open("wholepart-replication-items.json", "w").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("real: 60 cal: 8 items_sha256:", digest)
from collections import Counter
print(Counter(x["strata"].get("probe", "cal") for x in items))
