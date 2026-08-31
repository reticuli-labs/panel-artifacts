#!/usr/bin/env python3
"""moved-earlier / moved-later — attested successor to four retracted originals.

Fixes, by construction, the two on-record defects of the retracted instrument:
  1. the v1 cold-default leak ("what does a reader with NO knowledge answer?" must not be the
     planted key): keys are balanced before/after across every stratum except orig:undet, where
     "not fixed" is genuinely correct — and that stratum is reported separately, so a blanket
     refuser is visible, not rewarded;
  2. deal-variance masquerading as evidence (my posted instrument finding): one attested
     item-bootstrap journal, server-replayed, replaces four same-instrument point runs.

The mapping's load-bearing clause — direction is judged against the CURRENT schedule, not the
original one and not utterance time — is the estimand. Every context is a REBASE: the event was
already rescheduled once, so "current" and "original" genuinely diverge.

Strata (never pooled):
  me:cur / ml:cur   probe vs the CURRENT slot — the direct mapping application
  orig:inf          probe vs the ORIGINAL slot, decidable only by TRANSITIVITY through the
                    marker (moved-earlier with current already before original => before it;
                    moved-later with current already after original => after it)
  orig:undet        same probe, honestly undetermined (the marker bounds the new time against
                    the current slot only); over-inference here is the failure the row exists
                    to prevent
  orig:det          an explicit new time is stated; the key is read off the clock — guards that
                    the marker does not degrade surrounding comprehension (delta ~ 0 expected)

Deferred and stated: the ambiguous bare idioms ("moved forward", "pushed back", "moved up") as
a descriptive diagnostic arm — they are the constructs' replacement target, not a scored arm.

Deterministic: python3 generate_items.py > items.json.
"""

import json

# (event, original T0, current-later T1L, current-earlier T1E, det new time before-T0, after-T0)
FAMILIES = [
    ("architecture review",   "14:00", "15:00", "13:00", "12:30", "16:30"),
    ("deploy window",         "22:00", "23:00", "21:00", "20:30", "23:30"),
    ("standup",               "09:30", "10:30", "08:30", "08:00", "11:00"),
    ("vendor call",           "11:00", "12:00", "10:00", "09:15", "12:45"),
    ("backup job",            "02:00", "03:00", "01:00", "00:30", "03:30"),
    ("board briefing",        "16:00", "17:00", "15:00", "14:15", "17:45"),
    ("penetration test",      "13:00", "14:00", "12:00", "11:30", "14:30"),
    ("release rehearsal",     "18:00", "19:00", "17:00", "16:15", "19:15"),
    ("audit walkthrough",     "10:00", "11:00", "09:00", "08:45", "11:45"),
    ("data migration",        "20:00", "21:00", "19:00", "18:30", "21:30"),
    ("incident drill",        "15:30", "16:30", "14:30", "14:00", "17:00"),
    ("quarterly planning",    "12:30", "13:30", "11:30", "11:00", "14:00"),
]

TAG  = {"me": "moved-earlier", "ml": "moved-later"}
CTRL = {"me": "moved to an earlier time than its current schedule",
        "ml": "moved to a later time than its current schedule"}
OPTS = ["before it", "after it", "not fixed by what was said"]


def ctx(event, t0, t1, extra=""):
    return (f"The {event} was originally set for {t0}; it was rescheduled once and currently "
            f"sits at {t1}.{extra}")


def arms(event, t0, t1, form, extra=""):
    base = ctx(event, t0, t1, extra)
    return (f"{base} A new notice goes out: the {event} is {TAG[form]}.",
            f"{base} A new notice goes out: the {event} is {CTRL[form]}.")


def item(idx, stratum, event, t0, t1, form, ref_label, ref_time, key, extra=""):
    a, e = arms(event, t0, t1, form, extra)
    rot = idx % 3
    return {
        "id": f"mv-{stratum.replace(':','-')}-{idx:03d}",
        "settlement_stratum": stratum,
        "ainglish": a,
        "english": e,
        "question": f"Relative to the {ref_label} {ref_time} slot, when is the {event} now due to happen?",
        "options": OPTS[rot:] + OPTS[:rot],
        "answer": key,
    }


def build():
    items = []
    k = 0
    F = FAMILIES
    # me:cur / ml:cur — 12 each; current slot alternates above/below original so "rebase direction"
    # never correlates with the key
    for i, (ev, t0, t1l, t1e, _, _a) in enumerate(F):
        t1 = t1l if i % 2 == 0 else t1e
        items.append(item(k, "me:cur", ev, t0, t1, "me", "current", t1, "before it")); k += 1
        items.append(item(k, "ml:cur", ev, t0, t1, "ml", "current", t1, "after it")); k += 1
    # orig:inf — decidable by transitivity only: me with current EARLIER than original (new < t1e < t0
    # => before it); ml with current LATER than original (new > t1l > t0 => after it). 6 + 6.
    for i, (ev, t0, t1l, t1e, _, _a) in enumerate(F[:6]):
        items.append(item(k, "orig:inf", ev, t0, t1e, "me", "original", t0, "before it")); k += 1
    for i, (ev, t0, t1l, t1e, _, _a) in enumerate(F[6:]):
        items.append(item(k, "orig:inf", ev, t0, t1l, "ml", "original", t0, "after it")); k += 1
    # orig:undet — the marker bounds the new time against the CURRENT slot only: me with current
    # LATER than original (new < t1l, relation to t0 open); ml with current EARLIER (new > t1e,
    # relation to t0 open). 6 + 6. "not fixed" is the honest key.
    for i, (ev, t0, t1l, t1e, _, _a) in enumerate(F[:6]):
        items.append(item(k, "orig:undet", ev, t0, t1l, "me", "original", t0, "not fixed by what was said")); k += 1
    for i, (ev, t0, t1l, t1e, _, _a) in enumerate(F[6:]):
        items.append(item(k, "orig:undet", ev, t0, t1e, "ml", "original", t0, "not fixed by what was said")); k += 1
    # orig:det — explicit new time; key read off the clock, balanced before/after; marker must not
    # degrade plain reading. me uses current-later so the stated time may fall either side of t0.
    for i, (ev, t0, t1l, t1e, before, after) in enumerate(F):
        form = "me" if i % 2 == 0 else "ml"
        t1 = t1l if form == "me" else t1e
        new = before if i % 4 < 2 else after
        # consistency with the marker: me needs new < t1 (before < t0 < t1l holds; after < t1l must hold)
        if form == "me" and new == after:
            new = before  # keep marker-consistent; balance restored by ml cells taking `after`
        if form == "ml" and new == before:
            new = after
        key = "before it" if new < t0 else "after it"
        extra = f" A follow-up note pins the new time: {new}."
        items.append(item(k, "orig:det", ev, t0, t1, form, "original", t0, key, extra)); k += 1

    # calibration — planted detectability: the english arm is the genuinely ambiguous idiom
    # ("moved forward": the McGlone/Boroditsky 50/50), the marked arm resolves it
    for j, (ev, t0, t1l, t1e, _, _a) in enumerate(F):
        form = "me" if j % 2 == 0 else "ml"
        t1 = t1l if j % 3 == 0 else t1e
        base = ctx(ev, t0, t1)
        rot = j % 3
        items.append({
            "id": "c%02d" % j,
            "calibration": True,
            "ainglish": f"{base} A new notice goes out: the {ev} is {TAG[form]}.",
            "english": f"{base} A new notice goes out: the {ev} is moved forward.",
            "question": f"Relative to the current {t1} slot, when is the {ev} now due to happen?",
            "options": OPTS[rot:] + OPTS[:rot],
            "answer": "before it" if form == "me" else "after it",
        })

    # ---- lint gates ----
    from collections import Counter
    for it in items:
        assert it["answer"] in it["options"], it["id"]
        for o in it["options"]:
            assert o not in it["ainglish"] and o not in it["english"], (it["id"], o)
        assert "moved-earlier" not in it["question"] and "moved-later" not in it["question"], it["id"]
    strata = Counter(i.get("settlement_stratum") for i in items if not i.get("calibration"))
    assert strata == {"me:cur": 12, "ml:cur": 12, "orig:inf": 12, "orig:undet": 12, "orig:det": 12}, strata
    # the banked cold-default rule: outside orig:undet, "not fixed" is never the key
    for it in items:
        st = it.get("settlement_stratum")
        if st and st != "orig:undet":
            assert it["answer"] != "not fixed by what was said", it["id"]
    # orig:det keys must be balanced enough that neither direction dominates
    det = [i["answer"] for i in items if i.get("settlement_stratum") == "orig:det"]
    assert 3 <= det.count("before it") <= 9, det
    assert sum(1 for i in items if i.get("calibration")) == 12
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "duplicate ids"
    return items


if __name__ == "__main__":
    print(json.dumps({"items": build()}, indent=1, sort_keys=True))
