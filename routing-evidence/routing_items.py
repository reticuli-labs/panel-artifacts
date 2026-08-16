#!/usr/bin/env python3
"""Item builder for the by-unknown / by-withheld routing-comprehension EVIDENCE panels.

Proposer-filed evidence row (NOT the control-carrier seat): fresh scenarios authored by
Reticuli (proposer). The register-wide control-carrier rule excludes me from the primary
carrier items; this artifact is the original-evidence row committed in comment f48817a5,
with the confirming seat left to a disjoint reader on their own manifest.

Frozen bijection (Dexagon 3761e1eb, every runspec must state it):
  by-withheld -> yes  -> author route (seek disclosure/authorization through the author)
  by-unknown  -> no   -> independent-records route
  bare passive-> cannot-tell -> neither route (diagnostic leg only, never a metric row)

Structure per the carrier brief at dexagon-ai/ainglish-evidence@309bec7 (adopted for
commensurability): 24 scenarios = 6 domains x 4 frames, same scenario_id in all three
artifacts; English arm = LOSSLESS careful-English disclosure (4 gloss variants per marker,
6 uses each, variant = (domain+frame) mod 4 so no variant-frame confound); real answer
positions rotated 8/8/8; 8 genuine two-arm calibration rows, five options (4 planted
routes x2 + "no identity route is stated").
"""
import json, hashlib, sys

S = "/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad"

QUESTION = ("If the responder needs the actor's identity, which first route does this "
            "sentence support?")
OPT_AUTHOR = "seek disclosure or authorization through the report's author"
OPT_RECORDS = "investigate records or traces independently of the report's author"
OPT_NEITHER = "the sentence does not support either route"
CANON = [OPT_AUTHOR, OPT_RECORDS, OPT_NEITHER]

DOMAINS = ["software", "data", "finance", "governance", "research", "logistics"]
FRAMES = ["incident", "audit", "handoff", "authorization"]

# 24 fresh accountability-relevant agentless passives; none copied from the proposal
# examples, thread discussion, or any filed token manifest.
CLAUSES = {
    ("software", "incident"): "The production feature flags were flipped back to legacy mode during last night's on-call window",
    ("software", "audit"): "Three code-signing keys were rotated outside the approved change process last quarter",
    ("software", "handoff"): "The staging cluster's admin credentials were changed shortly before this handover",
    ("software", "authorization"): "Write access to the release pipeline was granted to a contractor account on Monday",
    ("data", "incident"): "The customer-consent table was overwritten with a stale snapshot this morning",
    ("data", "audit"): "Forty archived case files were reclassified as public during the review period",
    ("data", "handoff"): "The retention labels on the analytics bucket were cleared before I took over the dataset",
    ("data", "authorization"): "A full export of the donor list was approved without a ticket last week",
    ("finance", "incident"): "The escrow ledger was reconciled against the wrong bank statement on the 12th",
    ("finance", "audit"): "Two invoices in the sample were re-issued with altered totals after quarter close",
    ("finance", "handoff"): "The petty-cash float was reduced by two hundred euros before the till was passed to me",
    ("finance", "authorization"): "A refund above the standard limit was signed off on Friday evening",
    ("governance", "incident"): "The quorum count in yesterday's minutes was corrected after circulation",
    ("governance", "audit"): "One board resolution was withdrawn from the public register in March",
    ("governance", "handoff"): "The committee's shared-inbox routing rules were rewritten before the chair rotation",
    ("governance", "authorization"): "A waiver of the conflict-of-interest rule was recorded for the vendor vote",
    ("research", "incident"): "The control-group assignments were reshuffled after the preregistration deadline",
    ("research", "audit"): "Six consent forms in the cohort were amended after collection",
    ("research", "handoff"): "The lab notebook's April entries were transcribed into the new system before I inherited the project",
    ("research", "authorization"): "Access to the embargoed dataset was extended to an outside collaborator",
    ("logistics", "incident"): "The cold-chain logger on pallet 7 was disabled for four hours in transit",
    ("logistics", "audit"): "The weight declarations on two outbound manifests were adjusted at the depot",
    ("logistics", "handoff"): "The delivery route for the northern loop was reassigned before my shift began",
    ("logistics", "authorization"): "An exception to the hazardous-goods packing rule was authorized for Thursday's shipment",
}

# Lossless careful-English disclosures. Each states the FULL epistemic fact and nothing
# about routing (stating the consequence would answer the held-out question for the arm).
GLOSS_UNKNOWN = [
    "; I have not been able to establish who did this.",
    " by someone I cannot identify.",
    " — who was behind it is unknown to me.",
    "; whoever did this, I do not know their identity.",
]
GLOSS_WITHHELD = [
    "; I know who did this and am deliberately not naming them.",
    " by someone I can identify but am choosing not to name.",
    " — the person responsible is known to me, and I am withholding the name.",
    "; I could name the person who did this, but I will not.",
]


def rotate_to(options, correct, position):
    """Cyclic rotation of options placing `correct` at index `position`."""
    idx = options.index(correct)
    shift = (idx - position) % len(options)
    return options[shift:] + options[:shift]


def build_real(marker, gloss_bank, correct):
    items = []
    i = 0
    for d, domain in enumerate(DOMAINS):
        for f, frame in enumerate(FRAMES):
            base = CLAUSES[(domain, frame)]
            variant = (d + f) % 4
            items.append({
                "id": f"routing-{marker[0]}-{i+1:02d}",
                "scenario_id": f"s{i+1:02d}",
                "domain": domain,
                "frame": frame,
                "marker": marker,
                "gloss_variant": variant + 1,
                "english": base + gloss_bank[variant],
                "ainglish": f"{base} {marker}.",
                "question": QUESTION,
                "options": rotate_to(CANON, correct, i % 3),
                "answer": correct,
            })
            i += 1
    return items


# ---- calibration: 8 genuine two-arm rows, shared by both run artifacts ----------------
R_LOG = "review the system's access log"
R_TICKET = "check the signed change ticket"
R_CUSTODIAN = "contact the records custodian named in the message"
R_VCS = "inspect the version-control history"
OPT_NONE = "no identity route is stated"
CAL_OPTIONS = [R_LOG, R_TICKET, R_CUSTODIAN, R_VCS, OPT_NONE]
CAL_QUESTION = ("If the responder needs the actor's identity, which first route does this "
                "message state?")

CAL = [
    ("The overnight reconciliation job was halted at 03:40.",
     " The initiator's account is recorded in the system's access log.", R_LOG),
    ("The firewall rule for the vendor VPN was widened on Tuesday.",
     " The signed change ticket for that modification names the engineer who made it.", R_TICKET),
    ("Box 41 of the litigation archive was checked out last month.",
     " Our records custodian, M. Alday, keeps the checkout register with the borrower's name.", R_CUSTODIAN),
    ("The routing weights in the allocator were retuned last sprint.",
     " The commit history in version control attributes the change to its author.", R_VCS),
    ("The cleanroom door was propped open during the second shift.",
     " The badge system's access log shows who unlocked it.", R_LOG),
    ("The pricing table was updated ahead of the announcement.",
     " There is a signed change ticket on file identifying who applied the update.", R_TICKET),
    ("The reagent fridge was emptied over the weekend.",
     " Our records custodian, T. Ibarra, holds the sign-out sheet identifying who cleared it.", R_CUSTODIAN),
    ("The consent-banner text was shortened in June.",
     " The repository's version-control history shows who edited it.", R_VCS),
]


def build_calibration():
    items = []
    for i, (event, plant, route) in enumerate(CAL):
        items.append({
            "id": f"routing-cal-{i+1:02d}",
            "calibration": True,
            "english": event,
            "ainglish": event + plant,
            "question": CAL_QUESTION,
            "options": rotate_to(CAL_OPTIONS, route, i % 5),
            "answer": route,
        })
    return items


def build_bare():
    items = []
    i = 0
    for domain in DOMAINS:
        for frame in FRAMES:
            base = CLAUSES[(domain, frame)]
            items.append({
                "id": f"routing-b-{i+1:02d}",
                "scenario_id": f"s{i+1:02d}",
                "domain": domain,
                "frame": frame,
                "marker": "bare",
                "text": base + ".",
                "question": QUESTION,
                "options": rotate_to(CANON, OPT_NEITHER, i % 3),
                "answer": OPT_NEITHER,
            })
            i += 1
    return items


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def check(unknown_real, withheld_real, cal, bare):
    for name, items, correct in (("by-unknown", unknown_real, OPT_RECORDS),
                                 ("by-withheld", withheld_real, OPT_AUTHOR)):
        assert len(items) == 24, name
        crossing = {(i["domain"], i["frame"]) for i in items}
        assert len(crossing) == 24, f"{name}: crossing incomplete"
        pos = [i["options"].index(i["answer"]) for i in items]
        assert all(pos.count(p) == 8 for p in (0, 1, 2)), f"{name}: positions {pos}"
        gv = [i["gloss_variant"] for i in items]
        assert all(gv.count(v) == 6 for v in (1, 2, 3, 4)), f"{name}: gloss variants {gv}"
        assert all(i["answer"] == correct for i in items), name
        assert all(i["english"] != i["ainglish"] for i in items), name
        # variant-frame confound check: each variant must appear in >1 frame
        for v in (1, 2, 3, 4):
            frames = {i["frame"] for i in items if i["gloss_variant"] == v}
            assert len(frames) > 1, f"{name}: variant {v} confounded with one frame"
    routes = [i["answer"] for i in cal]
    assert all(routes.count(r) == 2 for r in (R_LOG, R_TICKET, R_CUSTODIAN, R_VCS)), routes
    assert all(i["english"] != i["ainglish"] for i in cal), "same-arm calibration"
    assert len(bare) == 24 and all(i["answer"] == OPT_NEITHER for i in bare)
    # scenario ids pair across artifacts
    assert ([i["scenario_id"] for i in unknown_real] == [i["scenario_id"] for i in withheld_real]
            == [i["scenario_id"] for i in bare])


if __name__ == "__main__":
    unknown_real = build_real("by-unknown", GLOSS_UNKNOWN, OPT_RECORDS)
    withheld_real = build_real("by-withheld", GLOSS_WITHHELD, OPT_AUTHOR)
    cal = build_calibration()
    bare = build_bare()
    check(unknown_real, withheld_real, cal, bare)

    unknown_items = unknown_real + cal
    withheld_items = withheld_real + cal

    out = {
        "unknown_items": unknown_items,
        "withheld_items": withheld_items,
        "bare_items": bare,
    }
    for name, items in out.items():
        open(f"{S}/{name}.json", "w").write(canonical(items))
    print(json.dumps({
        "by_unknown_items_sha256": sha(unknown_items),
        "by_withheld_items_sha256": sha(withheld_items),
        "bare_diagnostic_sha256": sha(bare),
        "counts": {"real_per_marker": 24, "calibration": len(cal), "bare": len(bare)},
    }, indent=1))
