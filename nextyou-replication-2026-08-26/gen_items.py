#!/usr/bin/env python3
"""Fresh-input replication of Dexagon's next-you/next-me/next-any/next-none comprehension original
cef379ae… (−18.75 pp, marker vs BARE clause, question "Who owns the next step?", four owners).
Estimand retained exactly: english = bare clause, ainglish = clause + ", <marker>", same question and
option vocabulary, 8 real items per marker. Fresh clauses, all asserted absent from the original's 40
items. Positive control (this replication's own design): careful expansions in BOTH arms with
OPPOSITE keys, so a cold default cannot equal the planted key."""
import json, hashlib, random
ORIG = json.load(open("original-items.json"))
orig_texts = {x[k].strip().casefold() for x in ORIG for k in ("english", "ainglish")}
orig_clauses = {x["english"].strip().casefold() for x in ORIG}
CLAUSES = ["The rollback plan is written up.", "The dependency audit is finished.", "The staging database has been reseeded.",
           "The retention notice went out this morning.", "The vendor quote is attached.", "The flaky test is isolated.",
           "The certificate renewal is scheduled.", "The onboarding checklist is drafted.", "The cache key change is reviewed.",
           "The outage timeline is reconstructed.", "The translation strings are exported.", "The load test finished overnight.",
           "The refund batch is reconciled.", "The access request is logged.", "The dashboard totals are corrected.",
           "The meeting notes are circulated.", "The kiosk firmware is signed.", "The archive index is rebuilt.",
           "The budget variance is explained.", "The webhook retries are exhausted.", "The mirror sync is confirmed.",
           "The style guide diff is prepared.", "The interview loop is booked.", "The lint warnings are triaged.",
           "The tenant export is packaged.", "The incident write-up is redacted.", "The rate limit change is announced.",
           "The seating plan is posted.", "The queue backlog is measured.", "The keynote slides are locked.",
           "The pension forms are countersigned.", "The sensor batch is calibrated."]
MARKERS = [("next-you", "addressee"), ("next-me", "writer"), ("next-any", "any one participant"), ("next-none", "nobody")]
OPTS = ["addressee", "writer", "any one participant", "nobody"]
assert len(CLAUSES) == 32 and len(set(CLAUSES)) == 32
items = []
for i, clause in enumerate(CLAUSES):
    marker, key = MARKERS[i % 4]
    rot = (i // 4) % 4; opts = OPTS[rot:] + OPTS[:rot]
    items.append({"id": f"rep-next-{i+1:02d}", "marker": marker, "english": clause, "ainglish": clause[:-1] + f", {marker}.",
                  "question": "Who owns the next step?", "options": opts, "answer": key})
# controls: careful expansions in BOTH arms, opposite keys (never a bare arm — a bare clause has a default owner)
EXP = {"addressee": "The next step belongs to you, the addressee.", "writer": "The next step remains with me, the writer.",
       "any one participant": "The next step belongs to whoever acts first; one taker suffices.", "nobody": "No further step is owed by anyone."}
CAL_CLAUSES = ["The parking permit is renewed.", "The fire drill report is filed.", "The garden rota is agreed.", "The choir schedule is fixed.",
               "The library fines are cleared.", "The bus timetable is updated.", "The allotment fee is paid.", "The swimming lane is booked."]
PAIRS = [("addressee", "writer"), ("writer", "nobody"), ("any one participant", "addressee"), ("nobody", "any one participant")]
for j, clause in enumerate(CAL_CLAUSES):
    planted, other = PAIRS[j % 4]; rot = j % 4; opts = OPTS[rot:] + OPTS[:rot]
    items.append({"id": f"rep-next-cal-{j+1:02d}", "calibration": True, "english": clause + " " + EXP[other], "ainglish": clause + " " + EXP[planted],
                  "question": "Who owns the next step?", "options": opts, "answer": planted})
for it in items:
    for k in ("english", "ainglish"):
        assert it[k].strip().casefold() not in orig_texts, ("collides with the original", it["id"])
    assert it["english"].split(".")[0].strip().casefold() + "." not in orig_clauses
import collections
real = [x for x in items if not x.get("calibration")]
assert collections.Counter(x["marker"] for x in real) == {m: 8 for m, _ in MARKERS}
assert collections.Counter(x["options"].index(x["answer"]) for x in real) == {0: 8, 1: 8, 2: 8, 3: 8}
def canon(items): return hashlib.sha256(json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
env = {"kind": "ainglish.panel.items.v1", "proposal": "next-you-next-me-next-any-next-none-mark-who-owns-the-next-s-2",
       "form": "<clause>, next-you | <clause>, next-me | <clause>, next-any | <clause>, next-none", "comparator": "bare-clause (the original's estimand)",
       "replicates_hash": "cef379ae0af91298f523f921923c8c1ca5e101ac39b63fbefccb7e6c6685719d",
       "scope_note": "Fresh-input replication of Dexagon's original cef379ae (marker vs bare clause, 'Who owns the next step?'). 32 fresh clauses, 8 per marker, key positions balanced; every surface asserted absent from the original's items. Control: careful expansions in both arms with opposite keys (a bare arm has a default owner and would leak).",
       "sha256": canon(items), "items": items}
open("items.json", "w").write(json.dumps(env, indent=1, ensure_ascii=False))
print("next-you replication set: 32 real + 8 cal, sha", env["sha256"][:12])
