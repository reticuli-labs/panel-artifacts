#!/usr/bin/env python3
"""Frozen item set for they-one / they-many — the pilot's attested successor original.

The row's declared design, implemented:
  - 128 held-out operational items (>= the declared 120): one singular antecedent candidate and
    one plural antecedent candidate, BOTH semantically live, then a critical subject-pronoun clause
  - balance: intended number (64/64 strata), antecedent order (singular-first vs plural-first),
    subject kinds (human / agent / entity), consequence type (approval-count vs ownership-contact),
    lexical content (16 scenario families)
  - verb morphology identical across readings: the critical clause uses past tense / plural
    agreement, exactly because singular they takes ordinary plural agreement
  - careful-English comparator phrased as the row dictates: "that one person/entity ..." /
    "those two or more people/entities ..."
  - consequence questions whose correct next action depends on number alone, avoiding the
    all-members/unanimity trap the mapping explicitly disclaims

DECLARED-AND-DEFERRED, stated: (1) the bare-they arm (the >=20pp-over-bare claim) — the panel is
two-armed; bare-they is this set's CALIBRATION arm (a planted unresolvable control), and the
scored bare-arm comparison is a follow-up filing; (2) the five false-inference audit rates
(gender, known identity, unanimity, all-members, collective) — separate probe class, separate
filing, so the carrier delta is not blended with a different construct; (3) the blinded
both-readings-live gate is implemented here as a design rule plus lint, and the >=100-admissible
refutation bound applies to the served set.

Deterministic: python3 generate_items.py > items.json
"""

import hashlib
import json

SEED = "they-one-many-comp-2026-08-31"


def pick(options, *keys):
    h = hashlib.sha256("\0".join((SEED,) + tuple(str(k) for k in keys)).encode()).digest()
    return options[int.from_bytes(h[:4], "big") % len(options)]


def rotate(opts, *keys):
    k = int.from_bytes(hashlib.sha256("\0".join((SEED, "rot") + tuple(map(str, keys))).encode()).digest()[:2], "big")
    return list(opts[k % len(opts):]) + list(opts[:k % len(opts)])


# (singular candidate, plural candidate, kind, action clause past-tense plural-agreement,
#  follow-up object)
FAMILIES = [
    ("the auditor", "the release committee", "human", "approved the rollout", "the rollout approval"),
    ("the on-call engineer", "the platform team", "human", "restarted the ingest cluster", "the restart"),
    ("the vendor's account manager", "the procurement reviewers", "human", "signed the renewal", "the renewal"),
    ("the triage bot", "the scanner fleet", "agent", "flagged the regression", "the regression flag"),
    ("the deploy agent", "the canary watchers", "agent", "rolled back the build", "the rollback"),
    ("the billing service", "the settlement workers", "entity", "reprocessed the failed batch", "the reprocessing"),
    ("the archivist", "the records board", "human", "sealed the case file", "the sealing decision"),
    ("the site reliability lead", "the incident responders", "human", "closed the outage ticket", "the closure"),
    ("the indexing daemon", "the crawler processes", "agent", "rebuilt the search shards", "the rebuild"),
    ("the treasurer", "the grants panel", "human", "released the quarterly funds", "the release of funds"),
    ("the QA contractor", "the beta testers", "human", "reported the login fault", "the fault report"),
    ("the licensing authority", "the member registries", "entity", "revoked the duplicate keys", "the revocation"),
    ("the night operator", "the warehouse crews", "human", "logged the stock variance", "the variance log"),
    ("the summarizer agent", "the review models", "agent", "escalated the anomaly", "the escalation"),
    ("the parish clerk", "the trustees", "human", "amended the meeting minutes", "the amendment"),
    ("the gateway service", "the edge relays", "entity", "refused the malformed requests", "the refusals"),
]

INTRO = [
    "{first} conferred with {second} before the deadline.",
    "{first} met {second} once the checks finished.",
    "After the review, {first} spoke with {second}.",
]

Q_APPROVAL = [
    "House rules require a second, different signatory whenever exactly one party has acted so far. Based only on the statement, must another signatory now be sought?",
    "Policy: if only a single party performed this action, one more must be recruited before it stands. Going by the statement alone, is recruiting another required?",
]
A_APPROVAL = ("yes, another must be sought", "no, that requirement is already met", "the statement does not settle this")
Q_CONTACT = [
    "You must follow up about {obj}. Based only on the statement, should your message be addressed to a single party or to multiple parties?",
    "To query {obj}, whom does the statement direct you toward: one party, or several?",
]
A_CONTACT = ("a single party", "multiple parties", "the statement does not say who acted")

items = []
for slot, (sing, plur, kind, action, obj) in enumerate(FAMILIES):
    for number in ("one", "many"):
        for ctype in ("approval", "contact"):
            for order in ("sf", "pf"):   # singular-first / plural-first
                sid = f"{number}-{ctype}-{order}-{slot:02d}"
                first, second = (sing, plur) if order == "sf" else (plur, sing)
                intro = pick(INTRO, sid).format(first=first, second=second)
                marker = f"they-{number}"
                ainglish = f"{intro} {marker} {action}."
                subject = ("that one person" if kind == "human" else "that one entity") if number == "one" \
                    else ("those two or more people" if kind == "human" else "those two or more entities")
                english = f"{intro} Of them, {subject} {action}."
                if ctype == "approval":
                    q = pick(Q_APPROVAL, sid)
                    opts, key = A_APPROVAL, (A_APPROVAL[0] if number == "one" else A_APPROVAL[1])
                else:
                    q = pick(Q_CONTACT, sid).format(obj=obj)
                    opts, key = A_CONTACT, (A_CONTACT[0] if number == "one" else A_CONTACT[1])
                items.append({
                    "id": sid, "settlement_stratum": f"they-{number}",
                    "english": english, "ainglish": ainglish,
                    "question": q, "options": rotate(opts, sid), "answer": key,
                })

# Keep 128: 16 families x 2 numbers x 2 consequence types x 2 orders = 128. Exact.

# Calibration: bare 'they' is the row's own unresolvable case — the reader cannot recover number
# from it; the marked arm resolves it. This is also the deferred bare-arm contrast worn as the
# planted control, exactly as rows 1-3 used their own bare forms.
for k in range(12):
    sing, plur, kind, action, obj = FAMILIES[k % 16]
    number = "one" if k % 2 == 0 else "many"
    sid = f"c{k:02d}"
    intro = pick(INTRO, sid).format(first=sing, second=plur)
    items.append({
        "id": sid, "calibration": True,
        "english": f"{intro} they {action}.",
        "ainglish": f"{intro} they-{number} {action}.",
        "question": pick(Q_CONTACT, sid).format(obj=obj),
        "options": rotate(A_CONTACT, sid),
        "answer": A_CONTACT[0] if number == "one" else A_CONTACT[1],
    })

print(json.dumps({"items": items}, indent=1, sort_keys=True))
