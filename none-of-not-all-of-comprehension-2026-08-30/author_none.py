#!/usr/bin/env python3
"""Author the `none-of(<L>) / not-all-of(<L>)` comprehension item set.

The construct is NEGATION SCOPE, chosen over reference_resolution because both qualified reader
lineages score 8/8 on negation_scope and only 5/8 on reference_resolution: establish that the
pipeline can settle SOMETHING end to end before spending cells on the axis where the readers
themselves are weakest (agreed with @rosetta, 2026-08-30).

DESIGN, and the reason this set is sharper than the they-one/they-many one:

  The `english` arm is BYTE-IDENTICAL across both scope strata. "All of the regional leads did not
  clear the change window" is the classic English scope ambiguity -- it can mean none cleared, or
  that at least one did not. So the SAME English sentence carries two different correct answers
  depending on which Ainglish form it is the gloss of. The contrast is not "Ainglish is shorter" or
  "Ainglish is unusual"; it is that one arm determines an action and the other cannot, with the
  ambiguous string held exactly constant.

  `careful` is the control that matters: a careful English writer CAN disambiguate ("not a single
  one of", "at least one of ... did not"). If careful English scores like Ainglish, the finding is
  about explicit scope marking, not about Ainglish. That is the honest reading and the set is built
  to permit it.

LOGICAL CARE: not-all is entailed by none, so the two forms cannot be separated by asking what is
true. They are separated by asking what is WARRANTED: under none-of the remediation step is
licensed; under not-all-of it is not yet licensed, because not-all leaves open how many cleared.
The distractor set is built on that asymmetry, not on a false contradiction.

BALANCE (asserted at the end, not hoped for):
  scope     none 96 / not_all 96          <- settlement_stratum
  kind      human 64 / system 64 / mixed 64
  order     context_first 96 / claim_first 96
  family    4 families x 48
  answer position uniform 32/32/32 WITHIN each stratum, so position cannot carry the signal
"""
import collections, hashlib, itertools, json

FAMILIES = {
    "approval": {
        "scene": "The release board polled {L} about the rollout.",
        "list": "the regional leads",
        "verb": "cleared the change window",
        "verb_base": "clear the change window",
        "gate": "The change window opens only if every regional lead cleared it, and a remediation "
                "call is warranted only once you know that none of them did.",
        "none": "hold the window and open the remediation call",
        "notall": "hold the window, and count how many cleared before opening any remediation call",
    },
    "delivery": {
        "scene": "The night dispatcher checked in with {L} before the cut-off.",
        "list": "the depot supervisors",
        "verb": "confirmed the outbound load",
        "verb_base": "confirm the outbound load",
        "gate": "The route releases only if every depot supervisor confirmed, and the reserve "
                "carrier is chartered only once you know that none of them did.",
        "none": "hold the route and charter the reserve carrier",
        "notall": "hold the route, and establish how many confirmed before chartering anything",
    },
    "compliance": {
        "scene": "The control owner walked {L} through the quarterly attestation.",
        "list": "the process owners",
        "verb": "signed the control attestation",
        "verb_base": "sign the control attestation",
        "gate": "The quarter closes only if every process owner signed, and the escalation notice "
                "is filed only once you know that none of them did.",
        "none": "hold the close and file the escalation notice",
        "notall": "hold the close, and determine how many signed before filing anything",
    },
    "testing": {
        "scene": "The release engineer re-ran {L} against the candidate build.",
        "list": "the integration suites",
        "verb": "reported a clean run",
        "verb_base": "report a clean run",
        "gate": "The build ships only if every integration suite reported clean, and a full bisect "
                "is started only once you know that none of them did.",
        "none": "hold the build and start the full bisect",
        "notall": "hold the build, and find how many reported clean before starting a bisect",
    },
}

# Calibration scenarios, deliberately DISJOINT from the real families above so a calibration cell
# can never leak a real item's answer. The planted effect is the construct itself: the Ainglish arm
# names the scope and is answerable; the byte-identical English arm is the ambiguous "All ... did
# not ..." and is not. Every item offers "cannot tell from the message", so a careful reader has a
# live honest option on the ambiguous arm -- it answers rather than refusing, which is what keeps
# the calibration cell LIVE instead of a dead cell the yield guard aborts on.
CALIBRATION = {
    "signoff": {
        "scene": "The duty manager paged {L} about the overnight batch.",
        "verb": "acknowledged the page", "verb_base": "acknowledge the page",
        "gate": "The batch is signed off only if every on-call engineer acknowledged, and the "
                "wake-up call is warranted only once you know that none of them did.",
        "none": "hold the sign-off and place the wake-up call",
        "notall": "hold the sign-off, and count how many acknowledged before calling anyone",
        "lists": {"human": "the on-call engineers", "system": "the on-call pagers",
                  "mixed": "the on-call engineers and their pagers"},
    },
    "intake": {
        "scene": "The triage nurse reviewed {L} at the shift change.",
        "verb": "returned a completed form", "verb_base": "return a completed form",
        "gate": "Intake closes only if every referring clinic returned a completed form, and the "
                "chase-up round is warranted only once you know that none of them did.",
        "none": "hold intake and start the chase-up round",
        "notall": "hold intake, and count how many returned before chasing anyone",
        "lists": {"human": "the referring clinics", "system": "the referral inboxes",
                  "mixed": "the referring clinics and their inboxes"},
    },
}

# The referent class the list denotes. Kept as a stratum because a scope error over people and a
# scope error over machines have different downstream costs, and a set that mixes them without
# recording which is which cannot tell the two apart afterwards.
KINDS = {
    "human":  {"approval": "the regional leads", "delivery": "the depot supervisors",
               "compliance": "the process owners", "testing": "the suite maintainers"},
    "system": {"approval": "the regional gateways", "delivery": "the depot terminals",
               "compliance": "the control monitors", "testing": "the integration suites"},
    "mixed":  {"approval": "the regional leads and their gateways",
               "delivery": "the depot supervisors and their terminals",
               "compliance": "the process owners and their monitors",
               "testing": "the suite maintainers and their runners"},
}

VARIANTS = ["the change request", "the amended schedule", "the vendor migration", "the failover plan"]
UNKNOWN = "cannot tell from the message"


def build():
    items, seq = [], 0
    combos = list(itertools.product(sorted(FAMILIES), ("none", "not_all"),
                                    ("human", "system", "mixed"),
                                    ("context_first", "claim_first"), range(4)))
    # 4 families x 2 scopes x 3 kinds x 2 orders x 4 lexical variants = 192
    assert len(combos) == 192, len(combos)

    # Deterministic answer-position assignment: a counter per (stratum, position) filled in a fixed
    # rotation, then asserted uniform. No RNG -- a seed is one more thing that has to be reported.
    pos_cycle = collections.defaultdict(int)

    for family, scope, kind, order, vi in combos:
        f = FAMILIES[family]
        listing = KINDS[kind][family]
        topic = VARIANTS[vi]
        scene = f["scene"].format(L=listing) + f" The subject was {topic}."

        ainglish_op = "none-of" if scope == "none" else "not-all-of"
        claim_ain = f"{ainglish_op}(<{listing}>) {f['verb']}."
        # IDENTICAL for both strata -- this is the point of the set.
        claim_eng = f"All of {listing} did not {f['verb_base']}."
        claim_careful = (f"Not a single one of {listing} {f['verb']}."
                         if scope == "none" else
                         f"At least one of {listing} did not {f['verb_base']}.")

        def compose(claim):
            return f"{scene} {claim}" if order == "context_first" else f"{claim} {scene}"

        correct = f["none"] if scope == "none" else f["notall"]
        other = f["notall"] if scope == "none" else f["none"]

        idx = pos_cycle[scope] % 3
        pos_cycle[scope] += 1
        options = [None, None, None]
        options[idx] = correct
        rest = [other, UNKNOWN] if (pos_cycle[scope] // 3) % 2 == 0 else [UNKNOWN, other]
        for slot in range(3):
            if options[slot] is None:
                options[slot] = rest.pop(0)

        seq += 1
        items.append({
            "id": f"n-{seq:03d}",
            "ainglish": compose(claim_ain),
            "english": compose(claim_eng),
            "careful": compose(claim_careful),
            "question": f["gate"] + " What follows?",
            "options": options,
            "answer": correct,
            "scope": scope,
            "kind": kind,
            "order": order,
            "family": family,
            "settlement_stratum": scope,
        })
    return items


def build_calibration():
    """Sixteen calibration items, 8/8 across scope, flagged for the harness.

    The register refuses a comprehension run with no calibration items -- "a panel that was never
    shown a detectable difference proves nothing when it detects none" -- and for this metric they
    must live INSIDE the items array. The first freeze of this set had none: the audit checked
    every balance axis and never asked whether the set could run at all. Caught by @rosetta before
    she spent a cell, not by me.
    """
    items, n = [], 0
    for family, f in sorted(CALIBRATION.items()):
        for scope in ("none", "not_all"):
            for kind in ("human", "system", "mixed"):
                listing = f["lists"][kind]
                n += 1
                scene = f["scene"].format(L=listing)
                op = "none-of" if scope == "none" else "not-all-of"
                claim_ain = f"{op}(<{listing}>) {f['verb']}."
                claim_eng = f"All of {listing} did not {f['verb_base']}."
                correct = f["none"] if scope == "none" else f["notall"]
                other = f["notall"] if scope == "none" else f["none"]
                options = [correct, other, UNKNOWN] if n % 3 == 0 else (
                    [other, correct, UNKNOWN] if n % 3 == 1 else [UNKNOWN, correct, other])
                items.append({
                    "id": f"n-cal-{n:03d}",
                    "calibration": True,
                    "ainglish": f"{scene} {claim_ain}",
                    "english": f"{scene} {claim_eng}",
                    "careful": f"{scene} " + (
                        f"Not a single one of {listing} {f['verb']}." if scope == "none"
                        else f"At least one of {listing} did not {f['verb_base']}."),
                    "question": f["gate"] + " What follows?",
                    "options": options,
                    "answer": correct,
                    "scope": scope, "kind": kind, "order": "context_first", "family": family,
                    "settlement_stratum": scope,
                })
    return items


def audit(items):
    calib = [i for i in items if i.get("calibration")]
    real = [i for i in items if not i.get("calibration")]
    print(f"items: {len(items)}  ({len(real)} real + {len(calib)} calibration)")
    # THE CHECK THE FIRST FREEZE LACKED. Every balance axis was asserted and nobody asked whether
    # the harness would run the set at all; it refuses a comprehension panel with no calibration.
    assert calib, "a comprehension item set with no calibration items cannot pass the register gate"
    assert len(calib) >= 12, f"too few calibration items ({len(calib)}): gap resolution is 1/n"
    assert collections.Counter(i["scope"] for i in calib)["none"] == len(calib) // 2, \
        "calibration must be balanced across scope or the gap measures the imbalance"
    assert not ({i["ainglish"] for i in calib} & {i["ainglish"] for i in real}), \
        "a calibration item must never share an answer-bearing string with a real item"
    items = real
    for axis in ("scope", "kind", "order", "family", "settlement_stratum"):
        c = collections.Counter(i[axis] for i in items)
        print(f"  {axis:20} {dict(sorted(c.items()))}")

    # Answer position must not carry the signal, within each stratum.
    spread = {}
    for stratum in ("none", "not_all"):
        rows = [i for i in items if i["settlement_stratum"] == stratum]
        pos = collections.Counter(i["options"].index(i["answer"]) for i in rows)
        spread[stratum] = dict(sorted(pos.items()))
        print(f"  answer position [{stratum:7}] {spread[stratum]}")
        assert set(pos.values()) == {len(rows) // 3}, f"position not uniform in {stratum}: {pos}"

    # The english arm must be IDENTICAL across the two strata for matched items.
    by_key = collections.defaultdict(dict)
    for i in items:
        by_key[(i["family"], i["kind"], i["order"], i["english"])][i["scope"]] = i["answer"]
    shared = [k for k, v in by_key.items() if len(v) == 2]
    assert shared, "no english string is shared across strata -- the ambiguity is not held constant"
    for k in shared:
        assert by_key[k]["none"] != by_key[k]["not_all"], \
            "shared english string must carry DIFFERENT correct answers"
    print(f"  ambiguous english strings shared across both strata: {len(shared)} "
          f"(each with two different correct answers)")

    for i in items:
        assert len(set(i["options"])) == 3, f"{i['id']}: duplicate options"
        assert i["answer"] in i["options"], f"{i['id']}: answer not among options"
        assert UNKNOWN in i["options"], f"{i['id']}: missing the not-determined option"
        for arm in ("ainglish", "english", "careful"):
            assert i[arm].strip() and i[arm].endswith("."), f"{i['id']}: bad {arm}"
            # "did not cleared" passed every well-formedness check and was still ungrammatical.
            # A reader stumbling over the syntax is not a reader failing on scope, so the set
            # would have measured parse difficulty and called it comprehension.
            if "did not " in i[arm]:
                tail = i[arm].split("did not ", 1)[1].split(".", 1)[0]
                bases = {f["verb_base"] for f in FAMILIES.values()}
                assert tail in bases, f"{i['id']}: 'did not {tail}' is not a base form"
    print("  per-item checks: options distinct, answer present, not-determined offered, arms well-formed")


if __name__ == "__main__":
    items = build() + build_calibration()
    audit(items)
    blob = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    open("items.json", "w", encoding="utf-8").write(blob)
    print("\nitems.json sha256:", hashlib.sha256(blob.encode("utf-8")).hexdigest())
