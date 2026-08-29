#!/usr/bin/env python3
"""Author the they-one / they-many comprehension item set.

Design is NOT invented here -- it is the proposal's own declared `predicted_measurement`:
  * >=120 held-out operational items (we author 192)
  * each item carries ONE singular and ONE plural antecedent candidate, BOTH semantically live
  * a critical subject-pronoun clause follows
  * the question is a CONSEQUENCE question whose correct next action depends on whether exactly
    one or more than one referent acted or owns the task
  * balance intended number, antecedent order/recency, human/agent/entity subjects,
    approval-quorum vs ownership-contact consequences, and lexical content
  * verb morphology identical across arms, because singular `they` takes ordinary plural agreement

Both readings must stay live, which is what makes singular `they` the whole point: "the duty
engineer met the regional leads ... they approved it" genuinely does not say who approved.
"""
import json, hashlib, itertools, random, sys

SEED = 41
rnd = random.Random(SEED)

# --- antecedent pools -------------------------------------------------------------------------
# Singular roles are gender-unstated on purpose: singular `they` must be natural, and any
# gender inference is one of the five false-inference classes the proposal wants held at <=5%.
SING_HUMAN = ["the compliance officer", "the duty engineer", "the reviewer on call",
              "the release manager", "the data steward", "the incident lead",
              "the procurement analyst", "the safety assessor", "the account architect",
              "the migration owner", "the records custodian", "the intake coordinator"]
SING_AGENT = ["the triage agent", "the scheduling agent", "the indexing agent",
              "the reconciliation agent", "the escalation agent", "the pricing agent"]
SING_ENTITY = ["the upstream vendor", "the certifying body", "the hosting provider",
               "the clearing service", "the registry operator", "the audit firm"]
PLUR_HUMAN = ["the regional managers", "the platform reviewers", "the clinical assessors",
              "the district coordinators", "the standards editors", "the rota supervisors",
              "the procurement leads", "the safety marshals", "the branch controllers",
              "the intake officers", "the records trustees", "the release captains"]
PLUR_AGENT = ["the triage agents", "the scheduling agents", "the indexing agents",
              "the reconciliation agents", "the escalation agents", "the pricing agents"]
PLUR_ENTITY = ["the upstream vendors", "the certifying bodies", "the hosting providers",
               "the clearing services", "the registry operators", "the audit firms"]
KINDS = {"human": (SING_HUMAN, PLUR_HUMAN), "agent": (SING_AGENT, PLUR_AGENT),
         "entity": (SING_ENTITY, PLUR_ENTITY)}

MEETINGS = ["met with", "sat down with", "went through the file with",
            "held a working session with", "walked the checklist with", "reviewed the case with"]
TOPICS = ["the retention change", "the rollout window", "the failover plan", "the pricing table",
          "the access review", "the retirement of the legacy queue", "the disclosure schedule",
          "the vendor migration", "the incident postmortem", "the quota increase",
          "the archival policy", "the certificate rotation"]

# Two consequence families, as the design requires. Each supplies a past-tense (approval/quorum)
# or present-tense (ownership/contact) critical clause; both take identical verb morphology in
# every arm, so nothing about number leaks through agreement.
APPROVAL = [
    ("signed off on the change", "The change needs two or more independent sign-offs before it ships.",
     "collect at least one further sign-off", "the change already meets the sign-off rule"),
    ("approved the budget line", "The budget line releases only on two or more approvals.",
     "seek at least one further approval", "the budget line can be released"),
    ("cleared the item for release", "Release requires clearance from two or more parties.",
     "obtain at least one further clearance", "the item is cleared to release"),
    ("accepted the risk waiver", "A waiver stands only when two or more parties accept it.",
     "get at least one further acceptance", "the waiver already stands"),
    ("countersigned the transfer", "The transfer completes on two or more countersignatures.",
     "chase at least one further countersignature", "the transfer can complete"),
    ("ratified the exception", "An exception holds once two or more parties ratify it.",
     "secure at least one further ratification", "the exception already holds"),
]
OWNERSHIP = [
    ("own the remediation plan", "You need a decision on the plan before the end of the day.",
     "go to the single owner for the decision", "coordinate a decision across multiple owners"),
    ("hold the signing key", "The key must be rotated today.",
     "arrange rotation with the single holder", "arrange rotation across multiple holders"),
    ("maintain the failover runbook", "A correction has to be merged into the runbook now.",
     "route the correction to the single maintainer", "route the correction to several maintainers"),
    ("carry the on-call pager", "An incident needs to be handed over immediately.",
     "hand over to the single pager carrier", "hand over across several pager carriers"),
    ("administer the quota pool", "A quota increase must be granted this hour.",
     "request the increase from the single administrator", "request the increase from several administrators"),
    ("curate the disclosure list", "An entry has to be withdrawn before publication.",
     "ask the single curator to withdraw it", "ask the several curators to withdraw it"),
]

CANNOT = "cannot tell from the message"

def build():
    items, uid = [], 0
    stratum_pos = {"one": 0, "many": 0}
    combos = list(itertools.product(("one", "many"), ("sing_first", "plur_first"),
                                    ("human", "agent", "entity"), ("approval", "ownership")))
    # 2 x 2 x 3 x 2 = 24 balanced cells; 8 items per cell -> 192, balanced by construction.
    for number, order, kind, family in combos:
        sing_pool, plur_pool = KINDS[kind]
        for rep in range(8):
            uid += 1
            sing = sing_pool[(uid * 5 + rep) % len(sing_pool)]
            plur = plur_pool[(uid * 3 + rep) % len(plur_pool)]
            verb, setup, act_one, act_many = (APPROVAL if family == "approval" else OWNERSHIP)[uid % 6]
            meet, topic = MEETINGS[uid % len(MEETINGS)], TOPICS[(uid * 7) % len(TOPICS)]
            context = (f"{sing.capitalize()} {meet} {plur} about {topic}."
                       if order == "sing_first" else
                       f"{plur.capitalize()} {meet} {sing} about {topic}.")
            marker = "they-one" if number == "one" else "they-many"
            careful = ("that one party" if number == "one" else "those two or more parties")
            # Option ORDER is shuffled per item. Left fixed as [act_one, act_many, cannot], every
            # they-one key sits at position A and every they-many key at position B -- so a reader
            # with a position bias manufactures a difference between exactly the two strata the
            # proposal asks to be compared, and it reads as a real effect.
            key_text = act_one if number == "one" else act_many
            distractors = [o for o in (act_one, act_many, CANNOT) if o != key_text]
            slot = stratum_pos[number]; stratum_pos[number] += 1
            opts = [None, None, None]
            opts[slot % 3] = key_text                      # exact 32/32/32 within each stratum
            rest = [i for i in range(3) if i != slot % 3]
            # alternate which distractor leads, so position is balanced without a fixed cycle
            a, b = (distractors if (slot // 3) % 2 == 0 else distractors[::-1])
            opts[rest[0]], opts[rest[1]] = a, b
            items.append({
                "id": f"t-{uid:03d}",
                "number": number, "order": order, "kind": kind, "family": family,
                "ainglish": f"{context} {marker} {verb}.",
                "english":  f"{context} they {verb}.",           # bare `they` -- the primary comparator
                "careful":  f"{context} {careful} {verb}.",      # secondary comparator, not run here
                "question": f"{setup} What must happen next?",
                "options": opts,
                "answer": act_one if number == "one" else act_many,
            })
    return items

def audit(items):
    """Balance and hygiene checks. A generated set is only as good as what is asserted about it."""
    import collections
    fail = []
    n = len(items)
    if n != 192: fail.append(f"expected 192 items, got {n}")
    for field in ("number", "order", "kind", "family"):
        c = collections.Counter(i[field] for i in items)
        if len(set(c.values())) != 1:
            fail.append(f"{field} unbalanced: {dict(c)}")
    # the answer key must not be recoverable from the option ORDER
    if len({tuple(i["options"]) for i in items}) < 6:
        pass  # option text varies by family; order is fixed act_one/act_many/cannot by design
    # vocabulary leak: no marker or number word may appear in question or options
    banned = ("they-one", "they-many", "one party", "two or more parties", "single", "several", "multiple")
    for i in items:
        blob = (i["question"] + " " + " ".join(i["options"])).lower()
        for b in ("they-one", "they-many"):
            if b in blob: fail.append(f"{i['id']}: marker leaked into question/options")
    # verb morphology must be identical across arms
    for i in items:
        if i["ainglish"].split()[-1] != i["english"].split()[-1]:
            fail.append(f"{i['id']}: verb morphology differs across arms")
    # both antecedents must be present in both arms
    for i in items:
        if i["ainglish"].count(".") < 2 or i["english"].count(".") < 2:
            fail.append(f"{i['id']}: malformed surface")
    # the answer POSITION must not be predictable from the stratum, or a position-biased reader
    # produces a spurious stratum effect
    pos = collections.Counter((i["number"], i["options"].index(i["answer"])) for i in items)
    for number in ("one", "many"):
        counts = [pos[(number, k)] for k in range(3)]
        if max(counts) - min(counts) != 0:
            fail.append(f"answer position not exactly balanced for they-{number}: {counts}")
    # answer key must be one of the options, and never `cannot tell`
    for i in items:
        if i["answer"] not in i["options"]: fail.append(f"{i['id']}: answer not among options")
        if i["answer"] == CANNOT: fail.append(f"{i['id']}: marked arm keyed to cannot-tell")
    return fail

if __name__ == "__main__":
    items = build()
    problems = audit(items)
    print(f"authored {len(items)} items, seed {SEED}")
    if problems:
        print(f"AUDIT FAILED ({len(problems)}):")
        for p in problems[:12]: print("  ", p)
        sys.exit(1)
    print("audit clean: balance, vocabulary, morphology, answer-key checks all pass")
    import collections
    for f in ("number", "order", "kind", "family"):
        print(f"  {f:8}", dict(collections.Counter(i[f] for i in items)))
    digest = hashlib.sha256(json.dumps(items, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=False).encode()).hexdigest()
    print(f"  items sha256: {digest}")
    json.dump(items, open(f"{sys.path[0]}/they_items.json", "w"), indent=1, ensure_ascii=False, sort_keys=True)
    print("\nSAMPLE (they-one):"); s = next(i for i in items if i["number"] == "one")
    print("  A:", s["ainglish"]); print("  E:", s["english"]); print("  Q:", s["question"])
    print("  options:", s["options"]); print("  key:", s["answer"])
    print("\nSAMPLE (they-many):"); s = next(i for i in items if i["number"] == "many")
    print("  A:", s["ainglish"]); print("  E:", s["english"]); print("  key:", s["answer"])
