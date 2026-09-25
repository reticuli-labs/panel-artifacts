#!/usr/bin/env python3
"""Fresh-input REPLICA bank for Dexagon's replace(old, new) comprehension original c43ed0b1
(language-progression-comprehension-wave-v1-2026-09-04/build.py::replacement_items). DESIGN IDENTICAL: 16 (old, new)
pairs x 2 questions (incoming / departing strata, 16 each), four options rotated by index, 16 construct-free explicit-
location controls; careful-English template, questions and option strings verbatim (they are the comparator and probe).
INPUTS FRESH: role-neutral identifiers (the source's identifiers were `<noun>-old-N` / `<noun>-new-N`, which name the
role being asked about inside both arms), eight domains from the proposal's predicted_measurement, new control objects.
No inference, no network."""
import json, hashlib, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def canonical(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
def rotate(answer, distractors, index):
    values = [answer, *distractors]; assert len(values) == 4 and len(set(values)) == 4
    o = index % 4; return values[o:] + values[:o]
# (domain, departing, incoming) — role-neutral codes; no ordering, version or age cue in either identifier
PAIRS = [
    ("credential", "cert-7c1d", "cert-2f9a"), ("credential", "token-b7e2", "token-a1f3"),
    ("dependency", "libparse-q", "libparse-k"), ("dependency", "tzdata-m9", "tzdata-r4"),
    ("configuration value", "timeout-profile-east", "timeout-profile-west"), ("configuration value", "quota-plan-cedar", "quota-plan-birch"),
    ("physical part", "impeller-K", "impeller-D"), ("physical part", "gasket-lot-38", "gasket-lot-52"),
    ("assigned person", "Priya", "Tomas"), ("assigned person", "Halvard", "Nkechi"),
    ("document", "charter-draft-blue", "charter-draft-green"), ("document", "runbook-copy-ash", "runbook-copy-fern"),
    ("data record", "row-9f31", "row-c04e"), ("data record", "ledger-entry-tau", "ledger-entry-rho"),
    ("clinical instruction", "regimen-orchid", "regimen-heron"), ("clinical instruction", "dose-card-P", "dose-card-L"),
]
CUE = re.compile(r"old|new|prev|next|incoming|departing|former|latter|current|legacy|\bv?\d+\.\d+", re.I)
def replacement_items():
    rows = []
    for index, (domain, old, new) in enumerate(PAIRS):
        assert not CUE.search(old) and not CUE.search(new), (old, new)
        english = f"Remove departing {old} from the active slot and put incoming {new} in its place."
        marked = f"replace(old={old}, new={new})."
        rows.append({"id": f"rt-replacement-incoming-{index + 1:02d}", "english": english, "ainglish": marked,
                     "question": "Which reference occupies the active slot after the replacement?",
                     "options": rotate(new, [old, "both references", "the active reference is not specified"], index),
                     "answer": new, "form": "replace-old-new", "settlement_stratum": "incoming-reference", "domain": domain})
        rows.append({"id": f"rt-replacement-departing-{index + 1:02d}", "english": english, "ainglish": marked,
                     "question": "Which reference is the departing value removed from the active slot?",
                     "options": rotate(old, [new, "both references", "the departing reference is not specified"], index + 1),
                     "answer": old, "form": "replace-old-new", "settlement_stratum": "departing-reference", "domain": domain})
    return rows
def calibration():
    things = [("saffron ticket", "shelf 21"), ("basalt fob", "bin 6"), ("copper stub", "tray 17"), ("dusk voucher", "cage 3"),
              ("ember tag", "shelf 9"), ("fjord chip", "bin 14"), ("gale slip", "tray 2"), ("heath medal", "cage 18"),
              ("iris coupon", "shelf 5"), ("jute label", "bin 11"), ("kite marker", "tray 20"), ("lotus stamp", "cage 8"),
              ("moss token", "shelf 13"), ("nectar chit", "bin 1"), ("orchid pin", "tray 16"), ("plume docket", "cage 10")]
    rows = []
    for index, (thing, location) in enumerate(things):
        rows.append({"id": f"rt-replacement-cal-{index + 1:02d}", "calibration": True,
                     "english": f"An inventory message names the {thing}, but does not state its location.",
                     "ainglish": f"An inventory message states that the {thing} is in {location}.",
                     "question": f"Where does the message state that the {thing} is?",
                     "options": rotate(location, ["the dispatch desk", "the archive room", "no location is stated"], index),
                     "answer": location, "probe": "construct-free explicit-location planted effect"})
    return rows
if __name__ == "__main__":
    items = replacement_items() + calibration()
    assert len(items) == 48 and len({i["id"] for i in items}) == 48
    (ROOT / "items.json").write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"scientific": 32, "calibration": 16, "items_sha256": hashlib.sha256(canonical(items)).hexdigest()}))
