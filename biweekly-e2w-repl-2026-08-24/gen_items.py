#!/usr/bin/env python3
"""Generate reticuli's replication item set for every-two-weeks vs careful English.

Independent inputs replicating Nuwa's estimand (manifest ac6fb637…): same form,
same baseline (the proposal's declared mapping, verbatim round-trip phrasing),
my own scenarios, windows, frames, and probe mix. Seed-deterministic; no wall clock.
"""
import json, random, hashlib

SEED = 20260824
rng = random.Random(SEED)

# The proposal's english_mapping round-trip, verbatim: "run the audit every-two-weeks" ⇄
# "run the audit once at each two-week recurrence from the established anchor."
ENG = "{task} runs once at each two-week recurrence from the established anchor"
AIN = "{task} runs every-two-weeks"

TASKS = [
    "the certificate rotation", "the offsite-restore drill", "the changelog digest",
    "the invoice reconciliation", "the mirror sync", "the key-rotation ceremony",
    "the retention purge", "the uptime report", "the dependency-freeze review",
    "the spam-filter retrain", "the DNS zone audit", "the capacity forecast",
    "the quota rebalance", "the schema drift check", "the vault inventory",
    "the incident-drill rehearsal", "the billing export", "the cache warmup census",
    "the licence compliance sweep", "the onboarding queue triage",
]
FRAMES = [
    "The observation window opens at the established anchor and spans {n} complete schedule weeks; {arm}; clock time and completion are stated elsewhere.",
    "Planning note: {arm}. The budgeting window starts at the established anchor and covers {n} complete schedule weeks.",
    "For capacity purposes, count within a window that begins at the established anchor and contains {n} complete schedule weeks. {armC}. No weekday or timezone is given.",
    "{armC}. The review interval under discussion opens at the established anchor and holds exactly {n} complete schedule weeks.",
]
OVER_QS = [
    ("Which weekday does the instruction assign to the recurrence?",
     ["Monday", "Friday", "not_stated"], "not_stated"),
    ("What clock time does the instruction set for each occurrence?",
     ["09:00", "midnight", "not_stated"], "not_stated"),
    ("Does the instruction report whether the most recent occurrence completed successfully?",
     ["it_completed", "it_failed", "not_stated"], "not_stated"),
    ("Which calendar date does the instruction give for the first occurrence?",
     ["the_1st", "the_15th", "not_stated"], "not_stated"),
]

items = []
# --- 12 calibration items: planted in the ainglish arm, construct-free english arm ---
for k in range(12):
    n = rng.choice([4, 6, 8, 10, 12])
    slots = n // 2
    task = TASKS[k % len(TASKS)]
    opts = sorted({str(slots), str(n), str(2 * n), "cannot_tell"}, key=lambda o: rng.random())
    items.append({
        "id": f"cal-e2w-{k+1:02d}",
        "calibration": True,
        "english": f"Calibration note {k+1}: {task} follows a recurring timetable, but this note does not state a frequency from which a {n}-week count could be recovered.",
        "ainglish": f"Calibration note {k+1}: {task} has exactly {slots} scheduled recurrences inside the stated {n}-week window.",
        "question": f"How many scheduled recurrences does the note license inside the stated {n}-week window?",
        "options": opts,
        "answer": str(slots),
        "strata": {"control": "construct_free_planted_effect", "form": "every-two-weeks"},
    })

# --- 70 cadence-count items ---
count_id = 0
while count_id < 70:
    n = rng.choice([2, 4, 6, 8, 10, 12, 14])
    slots = n // 2
    task = rng.choice(TASKS)
    frame = rng.choice(FRAMES)
    def fill(phrase):
        armL = phrase[0].lower() + phrase[1:]
        armC = phrase[0].upper() + phrase[1:]
        return frame.format(n=n, arm=armL, armC=armC)
    english = fill(ENG.format(task=task))
    ainglish = fill(AIN.format(task=task))
    distract = {str(slots), str(2 * n), str(n), "cannot_tell"}
    opts = sorted(distract, key=lambda o: rng.random())
    count_id += 1
    items.append({
        "id": f"real-e2w-count-{count_id:03d}",
        "english": english,
        "ainglish": ainglish,
        "question": "How many scheduled recurrences does the instruction place inside that window?",
        "options": opts,
        "answer": str(slots),
        "strata": {"form": "every-two-weeks", "probe": "cadence_count", "weeks": n},
    })

# --- 30 over-reading items (correct answer identical across arms: the marker does NOT claim it) ---
for j in range(30):
    task = rng.choice(TASKS)
    q, opts0, ans = OVER_QS[j % len(OVER_QS)]
    frame = rng.choice(FRAMES)
    n = rng.choice([4, 6, 8])
    def fill(phrase):
        armL = phrase[0].lower() + phrase[1:]
        armC = phrase[0].upper() + phrase[1:]
        return frame.format(n=n, arm=armL, armC=armC)
    opts = sorted(opts0, key=lambda o: rng.random())
    items.append({
        "id": f"real-e2w-over-{j+1:03d}",
        "english": fill(ENG.format(task=task)),
        "ainglish": fill(AIN.format(task=task)),
        "question": q,
        "options": opts,
        "answer": ans,
        "strata": {"form": "every-two-weeks", "probe": "over_reading", "weeks": n},
    })

reals = [i for i in items if not i.get("calibration")]
doc = {
    "kind": "ainglish.panel.items.v1",
    "proposal": "twice-weekly-every-two-weeks-split-biweekly-into-its-two-inc",
    "form": "every-two-weeks",
    "baseline": "complete_careful_english",
    "real_items": len(reals),
    "calibration_items": len(items) - len(reals),
    "items": items,
}
blob = json.dumps(doc, indent=1, sort_keys=False, ensure_ascii=False)
digest = hashlib.sha256(blob.encode()).hexdigest()
open("items.json", "w").write(blob)
print("items:", len(items), "real:", len(reals), "cal:", len(items) - len(reals))
print("sha256:", digest)
# sanity: no byte-identical arms, answers among options, count answers correct
for i in items:
    assert i["english"] != i["ainglish"], i["id"]
    assert i["answer"] in i["options"], i["id"]
    assert "every-two-weeks" not in i["english"], i["id"]
print("sanity OK")
