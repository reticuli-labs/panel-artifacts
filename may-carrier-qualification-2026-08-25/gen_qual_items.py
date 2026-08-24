#!/usr/bin/env python3
"""Reticuli's fresh construct-blind reader-qualification sets (development + holdout).

Qualifies readers for Dexagon's may-modal carrier WITHOUT touching his burned holdout or
copying his admissibility items. Construct-blind: no register marker, no modal 'may'
anywhere. Planted-effect pairs in the carrier's own question FORMS: each scenario has a
STATED arm (the answer-determining fact is explicit) and an OMITTED arm (it is absent, so
the honest answer is the cannot-tell option). A qualified reader recovers the planted
answer in the stated arm and declines to invent it in the omitted arm.

Seeded and deterministic; development and holdout are disjoint scenario families.
"""
import json, random, hashlib, sys

SEED = 20260825
rng = random.Random(SEED)

# Four question forms mirroring the carrier's held-out-consequence style (construct-free).
FORMS = [
    # (fact template, question, correct-answer maker, distractor maker)
    ("verifier",
     "{actor} completed {task}. The record was checked against the {ledger} ledger.",
     "Which source verifies the message's claim?",
     lambda d: d["ledger"] + "-ledger", lambda d: [d["other1"] + "-ledger", d["other2"] + "-ledger"]),
    ("falsifier",
     "{actor} reports {task} finished. A later mismatch in the {ledger} record would contradict this.",
     "Which later finding would falsify the message?",
     lambda d: "a-" + d["ledger"] + "-mismatch", lambda d: ["a-" + d["other1"] + "-mismatch", "a-" + d["other2"] + "-mismatch"]),
    ("retraction",
     "{actor} logged {task}; the entry lives in the {ledger} register.",
     "If the message is retracted, which record changes?",
     lambda d: "the-" + d["ledger"] + "-register", lambda d: ["the-" + d["other1"] + "-register", "the-" + d["other2"] + "-register"]),
    ("follow-up",
     "{actor} says {task} is done; re-running the {ledger} check would test it.",
     "Which operational follow-up tests the message?",
     lambda d: "re-run-the-" + d["ledger"] + "-check", lambda d: ["re-run-the-" + d["other1"] + "-check", "re-run-the-" + d["other2"] + "-check"]),
]

LEDGERS = ["billing", "audit", "inventory", "rotation", "quota", "backup", "uptime", "licence",
           "retention", "capacity", "incident", "changelog"]
ACTORS_DEV = ["the sync daemon", "the invoice bot", "the triage agent", "the archive worker",
              "the renewal service", "the export job"]
ACTORS_HOLD = ["the mirror agent", "the settlement bot", "the purge worker", "the digest service",
               "the forecast job", "the reconcile daemon"]
TASKS_DEV = ["the nightly reconciliation", "the certificate renewal", "the shard compaction",
             "the quota rebalance", "the log rollover", "the mirror refresh"]
TASKS_HOLD = ["the ledger sweep", "the snapshot rotation", "the index rebuild",
              "the retention purge", "the capacity forecast", "the queue drain"]

def build(tag, actors, tasks, n_scenarios):
    items = []
    for i in range(n_scenarios):
        form = FORMS[i % len(FORMS)]
        name, msg_t, question, mk_ans, mk_dis = form
        led, o1, o2 = rng.sample(LEDGERS, 3)
        d = {"actor": rng.choice(actors), "task": rng.choice(tasks),
             "ledger": led, "other1": o1, "other2": o2}
        stated = msg_t.format(**d)
        # omitted arm: same scenario, the answer-determining noun genuinely absent
        omitted = msg_t.replace("the {ledger} ", "an internal ").format(**d)
        ans = mk_ans(d); dis = mk_dis(d)
        opts = sorted([ans] + dis + ["cannot_tell"], key=lambda _: rng.random())
        for arm, text, correct in (("stated", stated, ans), ("omitted", omitted, "cannot_tell")):
            items.append({
                "id": f"qual-{tag}-{i+1:02d}-{arm}",
                "arm": arm, "form": name,
                "message": text, "question": question,
                "options": opts, "answer": correct,
            })
    return items

dev = build("dev", ACTORS_DEV, TASKS_DEV, 12)      # 24 cells
hold = build("hold", ACTORS_HOLD, TASKS_HOLD, 12)  # 24 cells

for name, items in (("development", dev), ("holdout", hold)):
    for it in items:
        assert it["answer"] in it["options"], it["id"]
        assert "may" not in it["message"].lower().split(), it["id"]
    doc = {"kind": "reticuli.reader-qualification.items.v1",
           "purpose": "construct-blind reader qualification for the may-modal carrier (fresh; independent of Dexagon's burned holdout)",
           "answer_protocol": "opaque-choice-v1", "seed": SEED, "items": items}
    blob = json.dumps(doc, indent=1, ensure_ascii=False)
    open(f"{name}.json", "w").write(blob)
    print(name, len(items), "cells sha256:", hashlib.sha256(blob.encode()).hexdigest())
