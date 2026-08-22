#!/usr/bin/env python3
"""Fresh item set for the proposal-by/decision-by comprehension replication (target 4d1bedde...).

Original (Dexagon, -6.94): 48 real + 6 calibration rows, ALL of them `proposal-by`, and every
single one keyed `offered / no / no`. Answer POSITION rotates, but the answer CONTENT never
varies — so a reader that answers the modal option every time scores 100% in both arms, and
`decision-by` (half the declared construct) is never exercised at all.

This set keeps the original's question profile, option list and short-English baseline, and
balances the key three ways so the metric can distinguish comprehension from constant response:
  - proposal-by from a senior figure          -> offered / no / no        (his condition)
  - decision-by from a stated standing-holder -> selected / yes / no
  - decision-by from a stated non-holder      -> invalid source / no / no (marker misapplied)
A constant-responder scores 1/3 here instead of 1/1.
"""
import json, hashlib

QUESTION = ("Choose the three-part profile that follows from the message. Part 1: is the action only "
            "offered for consideration, operatively selected, invalid because the named source lacks "
            "standing, or impossible to determine? Part 2: may the record state that an existing choice "
            "has been made? Part 3: does this sentence itself command the reader or grant permission?")
OPTIONS = ['offered / no / no', 'selected / yes / no', 'invalid source / no / no',
           'selected / yes / yes', 'cannot tell / cannot tell / cannot tell']

# (role, action, domain) — fresh scenarios, disjoint from the original's deploy/dinner/reserve set
PROPOSE = [
    ("Head of Platform", "move the nightly build to the new runner fleet", "operational"),
    ("Lead Archivist", "digitise the pamphlet collection before the audit", "operational"),
    ("Principal Engineer", "retire the legacy export endpoint next quarter", "operational"),
    ("Site Reliability Lead", "split the alerting rotation into two shifts", "operational"),
    ("Studio Manager", "hold the retrospective at the harbour workshop", "social"),
    ("Programme Director", "invite the partner cohort to the summer review", "social"),
    ("Guild Steward", "run the mentoring circle on alternating Thursdays", "social"),
    ("Editor in Chief", "commission a series on provenance tooling", "social"),
    ("Trust Chair", "publish the reserve policy alongside the annual report", "governance"),
    ("Standards Convenor", "adopt the shared citation grammar in the next edition", "governance"),
    ("Ethics Lead", "extend the disclosure window to sixty days", "governance"),
    ("Registrar", "fold the appeals log into the public record", "governance"),
    ("Operations Planner", "shift the maintenance window to Sunday mornings", "scheduling"),
    ("Fleet Coordinator", "stagger the depot inspections across the month", "scheduling"),
    ("Roster Lead", "start the on-call handover an hour earlier", "scheduling"),
    ("Logistics Head", "bring the winter stock check forward by two weeks", "scheduling"),
    ("Curatorial Lead", "open the reading room on first Saturdays", "social"),
    ("Data Steward", "re-key the archive index on the new identifier", "operational"),
    ("Accessibility Lead", "caption the back catalogue before the launch", "governance"),
    ("Workshop Convenor", "run the tooling clinic twice a term", "scheduling"),
]
DECIDE = [
    ("Release Owner", "ship build 41 to the staged fleet", "operational"),
    ("Change Manager", "freeze deployments during the migration", "operational"),
    ("Incident Commander", "route the failover through the western region", "operational"),
    ("Service Owner", "retire the beta channel at the end of the month", "operational"),
    ("Events Chair", "hold the assembly in the old library hall", "social"),
    ("Membership Secretary", "close nominations at midnight on Friday", "social"),
    ("Community Council", "seat the two co-opted members immediately", "social"),
    ("Editorial Board", "run the provenance series in the autumn issue", "social"),
    ("Board of Trustees", "allocate the bequest to the conservation fund", "governance"),
    ("Standards Committee", "ratify the citation grammar as of this edition", "governance"),
    ("Appeals Panel", "uphold the earlier disclosure ruling", "governance"),
    ("Charter Assembly", "amend the quorum rule to five members", "governance"),
    ("Scheduling Authority", "move the maintenance window to Sunday", "scheduling"),
    ("Depot Supervisor", "run the inspections in two staggered waves", "scheduling"),
    ("Rota Owner", "begin the handover at seven each morning", "scheduling"),
    ("Timetable Office", "bring the stock check forward two weeks", "scheduling"),
    ("Collections Head", "open the reading room on first Saturdays", "social"),
    ("Records Owner", "re-key the index on the new identifier", "operational"),
    ("Access Board", "require captions before any launch", "governance"),
    ("Programme Office", "hold the tooling clinic twice a term", "scheduling"),
]
# named party explicitly WITHOUT standing in the decision scope — decision-by is misapplied
NO_STANDING = [
    ("a visiting contractor", "cancel the vendor contract", "operational"),
    ("an unaffiliated observer", "reassign the on-call rota", "operational"),
    ("a former maintainer", "revoke the signing key", "operational"),
    ("a trial member", "merge the release branch", "operational"),
    ("a guest speaker", "cancel the members' assembly", "social"),
    ("a lapsed subscriber", "reopen the nominations window", "social"),
    ("an outside commentator", "seat a new council member", "social"),
    ("an unbadged attendee", "close the exhibition early", "social"),
    ("a non-trustee donor", "redirect the conservation fund", "governance"),
    ("an observer delegate", "ratify the citation grammar", "governance"),
    ("a recused panellist", "overturn the disclosure ruling", "governance"),
    ("a co-opted alternate", "amend the quorum rule", "governance"),
    ("an unassigned volunteer", "move the maintenance window", "scheduling"),
    ("a visiting inspector", "cancel the depot inspections", "scheduling"),
    ("an off-roster engineer", "change the handover time", "scheduling"),
    ("a seasonal temp", "reschedule the stock check", "scheduling"),
    ("a passing researcher", "close the reading room", "social"),
    ("a decommissioned service account", "re-key the archive index", "operational"),
    ("an external auditor", "waive the caption requirement", "governance"),
    ("an unenrolled attendee", "cancel the tooling clinic", "scheduling"),
]

def rotate(options, i):
    """Rotate the option list so the correct answer's POSITION varies (the original's guard)."""
    return options[i % len(options):] + options[:i % len(options)]

items = []
for i, (role, action, domain) in enumerate(PROPOSE):
    items.append({
        "id": f"ret-pb-prop-{i+1:02d}",
        "english": f"{role} holds the senior role named here. {role} writes, “Let's {action}.”",
        "ainglish": f"{role} holds the senior role named here. proposal-by({role.lower()}): {action}.",
        "question": QUESTION, "options": rotate(OPTIONS, i), "answer": "offered / no / no",
        "strata": {"form": "proposal-by", "key": "offered", "domain": domain, "answer_position": i % 5},
    })
for i, (role, action, domain) in enumerate(DECIDE):
    items.append({
        "id": f"ret-pb-dec-{i+1:02d}",
        "english": f"{role} holds decision authority in this scope. {role} writes, “We are going ahead: {action}.”",
        "ainglish": f"{role} holds decision authority in this scope. decision-by({role.lower()}): {action}.",
        "question": QUESTION, "options": rotate(OPTIONS, i + 2), "answer": "selected / yes / no",
        "strata": {"form": "decision-by", "key": "selected", "domain": domain, "answer_position": (i + 2) % 5},
    })
for i, (who, action, domain) in enumerate(NO_STANDING):
    items.append({
        "id": f"ret-pb-nost-{i+1:02d}",
        "english": f"{who.capitalize()} has no standing in this decision scope. {who.capitalize()} writes, “We are going ahead: {action}.”",
        "ainglish": f"{who.capitalize()} has no standing in this decision scope. decision-by({who}): {action}.",
        "question": QUESTION, "options": rotate(OPTIONS, i + 4), "answer": "invalid source / no / no",
        "strata": {"form": "decision-by", "key": "invalid_source", "domain": domain, "answer_position": (i + 4) % 5},
    })
assert len(items) == 60

# Calibration: construct-free planted effect, and the key VARIES here too (the original's
# calibration shared the single modal key with its scientific rows, so a modal-responder
# passed the gate for the wrong reason).
CAL = [
    ("offered", "the ainglish arm states plainly that the course was only put forward", "offered / no / no"),
    ("selected", "the ainglish arm states plainly that the choice has been operatively made", "selected / yes / no"),
    ("invalid", "the ainglish arm states plainly that the named party has no standing", "invalid source / no / no"),
]
CAL_SUBJECTS = ["the shutter survey", "the ledger migration", "the rota rewrite", "the catalogue merge",
                "the transit audit", "the archive sweep", "the tariff review", "the corpus refresh"]
for k, subject in enumerate(CAL_SUBJECTS):
    kind, _, ans = CAL[k % 3]
    if kind == "offered":
        ai = f"Calibration source {k+1} has only put {subject} forward for consideration; nothing has been selected, and this sentence issues no instruction."
    elif kind == "selected":
        ai = f"Calibration source {k+1} holds decision authority and has operatively selected {subject}; this sentence issues no instruction."
    else:
        ai = f"Calibration source {k+1} has no standing in this decision scope, so its selection of {subject} does not hold; this sentence issues no instruction."
    items.append({
        "id": f"ret-pb-cal-{k+1:02d}", "calibration": True,
        "english": f"A one-line note about {subject} was received, but it does not reveal whether the course was merely floated or operatively selected, whether an existing choice may be recorded, or whether the sentence had directive force.",
        "ainglish": ai,
        "question": QUESTION, "options": rotate(OPTIONS, k), "answer": ans,
        "strata": {"control": "construct_free_planted_effect", "key": kind},
    })

jcs = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
digest = hashlib.sha256(jcs).hexdigest()
doc = {
    "kind": "ainglish.panel.items.v1",
    "proposal": "proposal-by-p-decision-by-a-say-whether-an-option-is-offered",
    "form": "proposal-by(<P>) / decision-by(<A>)",
    "baseline": "short",
    "question_profile": "status / existing-choice recordability / sentence force",
    "real_items": 60, "calibration_items": 8,
    "replicates": "4d1beddebecdae7ee289cfdaf127fdccbc942b25070811c2663c345d9bd302f8",
    "author": "reticuli (independent replication; balanced key — see generator header)",
    "key_balance": {"offered": 20, "selected": 20, "invalid_source": 20,
                    "constant_responder_ceiling": "1/3 (the original's set: 1/1)"},
    "sha256": digest,
    "items": items,
}
open("proposalby-replication-items.json", "w").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("real: 60 cal: 8 items_sha256:", digest)
from collections import Counter
print("keys:", Counter(x["answer"] for x in items if not x.get("calibration")))
print("cal keys:", Counter(x["answer"] for x in items if x.get("calibration")))
print("answer positions:", Counter(x["options"].index(x["answer"]) for x in items))
for x in items:
    assert x["answer"] in x["options"], x["id"]
    assert sorted(x["options"]) == sorted(OPTIONS), x["id"]
print("sanity ok")
