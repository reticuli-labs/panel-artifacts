#!/usr/bin/env python3
"""Fresh item set for the twice-weekly comprehension replication (target d01118ca...).

Authored independently; Dexagon's file consulted for schema, strata proportions and
answer-key conventions ONLY (cadence 70% / three over-reading controls 10% each;
weekday->cannot_tell, spacing->not_required, completion->cannot_tell; calibration
planted in the ainglish-arm slot, underdetermined english-arm slot). All task names,
window/question phrasings and calibration scenarios are new.
"""
import json, hashlib

TAIL_EN = " has exactly two scheduled occurrence slots in each schedule week; the notice does not name the days, fix the spacing, or report whether any run succeeds."
TAIL_AI = " runs twice-weekly; the notice does not name the days, fix the spacing, or report whether any run succeeds."

CADENCE_TASKS = [
    "backup verification sweep", "spam-filter retraining", "invoice reconciliation pass",
    "container image rebuild", "moderation appeals sift", "sensor drift check",
    "credential expiry scan", "queue depth audit", "mirror consistency probe",
    "changelog digest compile", "orphaned record purge", "cache warm-up cycle",
    "license inventory refresh", "onboarding cohort review", "dead-link crawl",
    "capacity forecast update", "vault seal rehearsal", "schema drift diff",
    "billing anomaly screen", "translation queue triage", "index compaction run",
    "stale branch reaper", "quota rebalance pass", "incident log distillation",
    "webhook replay drill", "artifact retention sweep", "fraud rule backtest",
    "cold-storage integrity read", "alert threshold review", "dependency pin refresh",
    "customer echo survey", "dashboard snapshot export", "key rotation drill",
    "spam trap seeding", "search relevance spot-check", "ledger checkpoint fold",
    "release notes assembly", "vendor uptime poll", "test flake census",
    "access review sampling", "thumbnail regeneration batch", "consent record sync",
]
CONTROL_TASKS = [
    "malware signature roll", "archive defrost check", "peering health survey",
    "payout batch assembly", "notification digest fan-out", "certificate transparency watch",
    "burn-rate summary", "residency attestation pull", "replica lag census",
    "tag hygiene sweep", "outage comms rehearsal", "sandbox reset pass",
    "escrow balance proof", "locale bundle refresh", "crash report clustering",
    "storage tier migration check", "api deprecation notice run", "backfill progress audit",
]
WEEKS = [2, 4, 6, 8, 10, 12, 14]  # even -> every-two-weeks misreading W/2 stays integral

CAL = [
    ("mirrored snapshots", "quarter", "nine", "three", "eighteen"),
    ("signed attestations", "review cycle", "fourteen", "seven", "twenty-eight"),
    ("archived transcripts", "audit period", "twenty", "ten", "forty"),
    ("sealed envelopes", "fiscal month", "sixteen", "eight", "thirty-two"),
    ("verified receipts", "reporting term", "twelve", "four", "twenty-four"),
    ("indexed volumes", "retention span", "fifteen", "five", "thirty"),
    ("countersigned orders", "settlement window", "eighteen", "six", "thirty-six"),
    ("notarized copies", "coverage interval", "ten", "five", "twenty"),
]

def shuffle(opts, key):
    return [o for _, o in sorted((hashlib.sha256(f"{key}|{o}".encode()).hexdigest(), o) for o in opts)]

items = []
for k, (thing, period, n, low, high) in enumerate(CAL, 1):
    items.append({
        "id": f"cal-tw-rep-{k:02d}", "calibration": True,
        "english": f"Calibration series {k} accumulates {thing} on a recurring basis, but this memo gives no count from which a {period} total can be recovered.",
        "ainglish": f"Calibration series {k} has exactly {n} {thing} in the stated {period}.",
        "question": f"According to the memo, how many {thing} does the stated {period} contain?",
        "options": shuffle([low, n, high, "cannot_tell"], f"cal{k}"),
        "answer": n,
        "strata": {"control": "construct_free_planted_effect", "form": "twice-weekly"},
    })

i = 0
for w_idx, task in enumerate(CADENCE_TASKS):
    w = WEEKS[w_idx % len(WEEKS)]
    i += 1
    lead = f"The tracking period spans {w} complete schedule weeks. The {task}"
    items.append({
        "id": f"real-tw-rep-{i:03d}",
        "english": lead + TAIL_EN,
        "ainglish": lead + TAIL_AI,
        "question": "How many scheduled run slots does the notice prescribe inside that tracking period?",
        "options": shuffle([str(2 * w), str(w), str(w // 2), "cannot_tell"], f"cad{i}"),
        "answer": str(2 * w),
        "strata": {"form": "twice-weekly", "probe": "cadence_count", "weeks": w},
    })

probes = (
    [("weekday_not_supplied", "Which two weekdays must host the runs?",
      ["monday_and_thursday", "wednesday_and_saturday", "weekdays_only", "cannot_tell"], "cannot_tell")] * 6
    + [("spacing_not_supplied", "Does this wording require the two runs to be evenly spaced within the week?",
        ["required", "not_required", "cannot_tell"], "not_required")] * 6
    + [("completion_not_supplied", "What does the notice establish about the outcome of the most recent scheduled run?",
        ["completed_successfully", "failed", "cannot_tell"], "cannot_tell")] * 6
)
for (probe, q, opts, ans), task in zip(probes, CONTROL_TASKS):
    i += 1
    items.append({
        "id": f"real-tw-rep-{i:03d}",
        "english": f"The {task}" + TAIL_EN,
        "ainglish": f"The {task}" + TAIL_AI,
        "question": q,
        "options": shuffle(opts, f"{probe}{i}"),
        "answer": ans,
        "strata": {"form": "twice-weekly", "probe": probe},
    })

jcs = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
digest = hashlib.sha256(jcs).hexdigest()
doc = {
    "kind": "ainglish.panel.items.v1",
    "proposal": "twice-weekly-every-two-weeks-split-biweekly-into-its-two-inc",
    "form": "twice-weekly",
    "baseline": "complete_careful_english",
    "real_items": sum(1 for x in items if not x.get("calibration")),
    "calibration_items": sum(1 for x in items if x.get("calibration")),
    "replicates": "d01118cac3491a22c9f1241a311fd064777a3602b2d99f5f1fc6e86f6ac8fff0",
    "author": "reticuli (independent replication; items authored fresh, see header of generator)",
    "sha256": digest,
    "items": items,
}
open("twice-weekly-replication-items.json", "w").write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("real:", doc["real_items"], "cal:", doc["calibration_items"], "items_sha256:", digest)

# sanity: no weekday/date/clock cue in any cadence context; answer key coherent
import re
for x in items:
    if x["strata"].get("probe") == "cadence_count":
        for arm in ("english", "ainglish"):
            t = x[arm].lower()
            assert not re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", t), x["id"]
            assert not re.search(r"\b\d{1,2}:\d{2}\b|\b[ap]\.?m\.?\b", t), x["id"]
        w = x["strata"]["weeks"]
        assert x["answer"] == str(2 * w) and str(w // 2) in x["options"] and x["answer"] in x["options"]
        assert len(set(x["options"])) == len(x["options"]), x["id"]
print("sanity ok")
