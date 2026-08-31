#!/usr/bin/env python3
"""Frozen item set for repeat-event / restore-state — VALIDITY + REFERENCE-TIME follow-up.

Discharges the commitment declared in repeat-restore-comp-2026-08-31/README.md ("Declared and
deferred, not trimmed silently"), quoting the row's predicted_measurement:

  "Add 32 separately reported restore-state validity fixtures covering missing state,
   non-entailed state (including repair/healthy), and ambiguous or multi-result predicates."
  "...include events between utterance time and the requested execution time; score participant
   and reference-time attachment separately."
  Refutation clause served here: "they accept more than 5% of invalid state arguments as licensed."

Design (68 scenarios, one probe each; every stratum reported separately, never pooled):
  vf:missing   12  context never states or entails the named earlier state       key: no-support
  vf:nonent    12  tempting near-entailment (repair/healthy family included)     key: no-support
  vf:ambig      8  two conflicting earlier intervals both match the named state  key: ambiguous
  vf:control    8  qualifying earlier interval explicitly stated                 key: supports
                   (controls make blanket rejection visible; without them a reader that always
                    refuses scores 100% on the 32 invalid fixtures)
  rt:before    12  directive; qualifying interval ended before the instruction   key: by-before
  rt:between   12  directive; the ONLY qualifying interval is scheduled between
                   the instruction and its stated execution time — the mapping
                   ("before the reference time supplied by the scoped clause")
                   makes it qualify; an utterance-anchored misreading excludes it key: by-between
  rt:none       4  directive; no qualifying interval ever, none scheduled        key: not-satisfied

Acceptance rate for the row's 5% clause = P(chose the supports option | 32 invalid fixtures),
computed per arm from the cells file after the run; accuracy remains the scored carrier.

Arms-must-agree: the careful-English arm states the mapping's background contribution with the
reference time explicit; the marked arm carries only the marker plus the shared context, so every
key is derivable in both arms from declared text alone. Anti-ceiling: contexts are built around
tempting near-misses so the careful arm is not pinned to 1.00.

Deterministic: python3 generate_items.py > items.json.
"""

import hashlib
import json

SEED = "repeat-restore-validity-2026-08-31"


def rotate(opts, *keys):
    k = int.from_bytes(hashlib.sha256("\0".join((SEED, "rot") + tuple(map(str, keys))).encode()).digest()[:2], "big")
    r = k % len(opts)
    return list(opts[r:]) + list(opts[:r])


# (slug, state-pred, state-description-for-question, directive-clause, actor)
# state-description is used ONLY in the probe question, never in either arm.
FAMILIES = [
    ("gate",    "open(west-gate)",        "the west gate stood open",             "open the west gate",              "Mara"),
    ("service", "healthy(billing-service)", "the billing service ran clean",      "make the billing service healthy", "Jo"),
    ("door",    "locked(archive-door)",   "the archive door was secured shut",    "lock the archive door",           "Ravi"),
    ("cache",   "empty(session-cache)",   "the session cache held nothing",       "clear the session cache",         "Lena"),
    ("beacon",  "on(beacon-light)",       "the beacon light was lit",             "switch the beacon light on",      "Iris"),
    ("index",   "built(search-index)",    "the search index existed fully built", "rebuild the search index",        "Tessa"),
]

# vf:missing — activity around the object, the named state never stated or entailed.
MISSING_CTX = {
    "gate": ["The west gate was inspected twice this quarter; both reports flagged rust on the hinges and recommended repainting.",
             "Contractors measured the west gate for a wider frame in March, and the yard crew re-gravelled the approach path."],
    "service": ["The billing service has thrown intermittent errors since it was first deployed; two incident reviews closed without a fix.",
                "The billing service's dashboards were rebuilt last month, and its alert thresholds were lowered twice."],
    "door": ["The archive door's hinges were oiled in May, and a new keypad was fitted beside the frame a week later.",
             "Movers propped the archive door wide open for the whole of the spring clear-out, then left it swinging free."],
    "cache": ["The session cache has grown steadily since launch; capacity warnings fired in April and again in June.",
              "The session cache was resized twice this year, and its eviction policy was debated at length without a decision."],
    "beacon": ["The beacon light was delivered in February and has sat crated in the store room awaiting an electrician.",
               "The beacon light's mounting bracket was replaced after the survey, and its cabling was rerouted around the mast."],
    "index": ["The search index build job has failed on every attempt since the schema change; each run aborts at the merge step.",
              "Plans for the search index were drafted in January and revised twice; the build ticket is still open."],
}

# vf:nonent — tempting near-entailment; repair/healthy family carries the row's named example.
NONENT_CTX = {
    "gate": ["A work order to unbolt the west gate was approved on Monday, and the crew staged their tools beside it that evening.",
             "The night shift reported the west gate's latch hanging loose, and the morning log shows someone had pushed it ajar."],
    "service": ["Engineers deployed a fix to the billing service at 09:10, and monitoring showed error rates falling through the morning.",
                "An attempted repair of the billing service ran overnight; the engineer's note reads 'improving, needs verification'."],
    "door": ["A locksmith cut two fresh keys for the archive door last week and tested both in the cylinder.",
             "The archive door was pulled firmly closed after the audit, though nobody recalls turning the key."],
    "cache": ["A purge of the session cache was scheduled for Sunday night, and the runbook for it was rehearsed on staging.",
              "The session cache's oldest entries were trimmed on Friday, cutting its size roughly in half."],
    "beacon": ["The beacon light passed its bench test at the workshop before being hauled up the mast unlit.",
               "Power was run to the beacon light's junction box on Tuesday, and the circuit breathed live on the meter."],
    "index": ["A partial build of the search index completed on Thursday, covering the newest third of the corpus.",
              "The search index build was kicked off at noon and was still churning through segments when the shift ended."],
}

# vf:ambig — two conflicting earlier intervals BOTH matching the named state's surface predicate.
# (slug, state-pred, state-description, statement clause actor) with paired interval descriptions.
AMBIG = [
    ("router",  "configured(lab-router)", "the lab router carried a configuration",
     "Priya configured the lab router",
     "In January the lab router ran the compact configuration; in March it ran the extended configuration. Each was wiped before the next audit."),
    ("floor",   "arranged(briefing-room)", "the briefing room stood arranged",
     "Sam arranged the briefing room",
     "For the winter series the briefing room was arranged theatre-style; for the spring series it was arranged as a classroom. Both layouts were struck afterwards."),
    ("site",    "deployed(status-site)",  "the status site was deployed",
     "Kai deployed the status site",
     "The status site ran the blue build through February and the green build through April; both deployments were then torn down."),
    ("pipeline", "tuned(ingest-pipeline)", "the ingest pipeline ran tuned",
     "Dev tuned the ingest pipeline",
     "The ingest pipeline spent the autumn tuned for throughput and the following spring tuned for latency; each profile was reset at quarter end."),
]

# vf:control — qualifying earlier interval explicitly stated, then ended.
CONTROL_CTX = {
    "gate": "Until Tuesday morning the west gate stood open for deliveries; a storm front forced it shut that afternoon.",
    "service": "Through the whole of May the billing service ran clean, with zero error alerts; the June schema change broke it.",
    "door": "The archive door stayed locked from the audit in March until the movers needed access in July.",
    "cache": "After the spring purge the session cache sat empty for a full week before traffic refilled it.",
    "beacon": "The beacon light burned continuously through the fortnight of sea trials, and was switched off when the vessel docked.",
    "index": "A complete search index served queries all of last quarter, until the schema migration invalidated it.",
}

VF_Q = "This statement takes as given that {desc} during some span of time in the past. Given the passage, which is true?"
VF_OPTS = {
    "supports": "the passage supports it: a single qualifying past span is stated or entailed",
    "nosupport": "the passage does not support it: no qualifying span is stated or entailed",
    "ambiguous": "two conflicting past spans fit the named state, and the statement does not determine which",
}

# rt — directive timeline scenarios. Execution time is stated in the instruction's clause.
# (family-slug, prior-interval-sentence, between-interval-sentence, never-sentence)
RT_CTX = {
    "gate": ("From 08:00 to 08:30 the west gate stood open for the fuel run, and it has been shut since.",
             "The west gate has stayed shut all week. Between 09:00 and 09:30 tomorrow the fire marshal will have it opened for the drill, then shut again.",
             "The west gate has stayed shut ever since it was installed, and nothing is scheduled to change that before then."),
    "service": ("The billing service ran clean from 07:00 to 07:40, then fell over, and has been down since.",
                "The billing service has never yet run clean. Between 13:00 and 13:20 tomorrow the vendor will bring it up healthy for certification, then take it back down.",
                "The billing service has never yet run clean, and no maintenance window is booked before then."),
    "beacon": ("The beacon light was lit from dusk until midnight, and has been dark since.",
               "The beacon light has been dark since delivery. Between 06:00 and 06:15 tomorrow the electrician will light it for the insurance check, then cut power again.",
               "The beacon light has been dark since delivery, and the electrician's visit was cancelled."),
    "cache": ("The session cache sat empty from 02:00 to 02:30 after the purge, and has been filling since.",
              "The session cache has never been empty since launch. A scheduled purge between 03:00 and 03:10 tomorrow will empty it briefly before traffic resumes.",
              "The session cache has never been empty since launch, and the scheduled purge was cancelled."),
}
RT_EXEC = {"gate": "at 12:00 tomorrow", "service": "at 15:00 tomorrow", "beacon": "at 08:00 tomorrow", "cache": "at 05:00 tomorrow"}

RT_Q = "The instruction takes as given that {desc} during some qualifying span. Given the schedule, which is true?"
RT_OPTS = {
    "by-before": "satisfied, by a span that ended before the instruction was given",
    "by-between": "satisfied, by a span scheduled after the instruction but before its stated execution time",
    "not-satisfied": "not satisfied: no qualifying span",
}


def eng_background(desc):
    return ("As background, taken as given: at some point in the past, %s; this does not say who or what brought that about." % desc)


def eng_background_rt(desc):
    return ("As background, taken as given: %s during some span before the time this instruction is to be carried out; "
            "this does not say the addressee brought that about." % desc)


def vf_item(idx, stratum, family_slug, pred, desc, clause, context, key):
    opts = rotate([VF_OPTS["supports"], VF_OPTS["nosupport"], VF_OPTS["ambiguous"]], stratum, idx)
    return {
        "id": "%s-%02d-%s" % (stratum.replace(":", "-"), idx, family_slug),
        "settlement_stratum": stratum,
        "ainglish": "%s restore-state(%s): %s." % (context, pred, clause),
        "english": "%s %s. %s" % (context, clause, eng_background(desc)),
        "question": VF_Q.format(desc=desc),
        "options": opts,
        "answer": VF_OPTS[key],
    }


def rt_item(idx, stratum, family_slug, pred, desc, directive, context, exec_at, key):
    opts = rotate([RT_OPTS["by-before"], RT_OPTS["by-between"], RT_OPTS["not-satisfied"]], stratum, idx)
    instr = "%s, %s" % (directive[0].upper() + directive[1:], exec_at)
    return {
        "id": "%s-%02d-%s" % (stratum.replace(":", "-"), idx, family_slug),
        "settlement_stratum": stratum,
        "ainglish": "%s The coordinator sends: restore-state(%s): %s." % (context, pred, instr.lower()),
        "english": "%s The coordinator sends: %s. %s" % (context, instr.lower().capitalize(), eng_background_rt(desc)),
        "question": RT_Q.format(desc=desc),
        "options": opts,
        "answer": RT_OPTS[key],
    }


def build():
    items = []
    # vf:missing (12) and vf:nonent (12): 6 families x 2 contexts each
    for i, (slug, pred, desc, clause_inf, actor) in enumerate(FAMILIES):
        past = {"open the west gate": "opened the west gate",
                "make the billing service healthy": "made the billing service healthy",
                "lock the archive door": "locked the archive door",
                "clear the session cache": "cleared the session cache",
                "switch the beacon light on": "switched the beacon light on",
                "rebuild the search index": "rebuilt the search index"}[clause_inf]
        clause = "%s %s" % (actor, past)
        for j, ctx in enumerate(MISSING_CTX[slug]):
            items.append(vf_item(i * 2 + j, "vf:missing", slug, pred, desc, clause, ctx, "nosupport"))
        for j, ctx in enumerate(NONENT_CTX[slug]):
            items.append(vf_item(i * 2 + j, "vf:nonent", slug, pred, desc, clause, ctx, "nosupport"))
    # vf:ambig (8): 4 scenarios x 2 statements (assertion + a second actor's assertion)
    for i, (slug, pred, desc, clause, ctx) in enumerate(AMBIG):
        items.append(vf_item(i * 2, "vf:ambig", slug, pred, desc, clause, ctx, "ambiguous"))
        alt = clause.replace(clause.split()[0], "Later, a stand-in", 1)
        items.append(vf_item(i * 2 + 1, "vf:ambig", slug, pred, desc, alt, ctx, "ambiguous"))
    # vf:control (8): 6 families + 2 rotated repeats
    ctl = FAMILIES + FAMILIES[:2]
    for i, (slug, pred, desc, clause_inf, actor) in enumerate(ctl):
        past = {"open the west gate": "opened the west gate",
                "make the billing service healthy": "made the billing service healthy",
                "lock the archive door": "locked the archive door",
                "clear the session cache": "cleared the session cache",
                "switch the beacon light on": "switched the beacon light on",
                "rebuild the search index": "rebuilt the search index"}[clause_inf]
        clause = "%s %s" % (actor, past)
        items.append(vf_item(i, "vf:control", slug, pred, desc, clause, CONTROL_CTX[slug], "supports"))
    # rt (12+12+4): 4 families x 3 repeats for before/between, 4 x 1 for none
    rt_fams = [(s, p, d, c) for (s, p, d, c, a) in FAMILIES if s in RT_CTX]
    for rep in range(3):
        for i, (slug, pred, desc, directive) in enumerate(rt_fams):
            before, between, never = RT_CTX[slug]
            items.append(rt_item(rep * 4 + i, "rt:before", slug, pred, desc, directive, before, RT_EXEC[slug], "by-before"))
            items.append(rt_item(rep * 4 + i, "rt:between", slug, pred, desc, directive, between, RT_EXEC[slug], "by-between"))
    for i, (slug, pred, desc, directive) in enumerate(rt_fams):
        _, _, never = RT_CTX[slug]
        items.append(rt_item(i, "rt:none", slug, pred, desc, directive, never, RT_EXEC[slug], "not-satisfied"))

    # calibration (12): planted marked-arm detectability, patterned on the primary run's controls —
    # bare-'again' English is honestly indeterminate between earlier-event and earlier-state; the
    # marker dictates earlier-state. The reader must recover it from the marked arm alone.
    cal_opts = [
        "a span in the past during which the resulting state already held",
        "an earlier occurrence of the same action by the same actor",
        "no earlier circumstance is taken as given",
    ]
    for i, (slug, pred, desc, clause_inf, actor) in enumerate(FAMILIES * 2):
        past = {"open the west gate": "opened the west gate",
                "make the billing service healthy": "made the billing service healthy",
                "lock the archive door": "locked the archive door",
                "clear the session cache": "cleared the session cache",
                "switch the beacon light on": "switched the beacon light on",
                "rebuild the search index": "rebuilt the search index"}[clause_inf]
        items.append({
            "id": "c%02d" % i,
            "calibration": True,
            "ainglish": "restore-state(%s): %s %s." % (pred, actor, past),
            "english": "%s %s again." % (actor, past),
            "question": "Besides what the main clause does, what background circumstance does the statement take as already given?",
            "options": rotate(cal_opts, "cal", i),
            "answer": cal_opts[0],
        })

    # ---- lint gates (the manifest's admissibility gates, enforced at generation) ----
    for it in items:
        for o in it["options"]:
            assert o not in it["ainglish"] and o not in it["english"], (it["id"], o)
        assert it["answer"] in it["options"], it["id"]
        assert "restore-state" not in it["question"], it["id"]
        for o in it["options"]:
            assert "restore-state" not in o, it["id"]
    from collections import Counter
    strata = Counter(i.get("settlement_stratum") for i in items if not i.get("calibration"))
    assert strata == {"vf:missing": 12, "vf:nonent": 12, "vf:ambig": 8, "vf:control": 8,
                      "rt:before": 12, "rt:between": 12, "rt:none": 4}, strata
    assert sum(1 for i in items if i.get("calibration")) == 12
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "duplicate ids"
    return items


if __name__ == "__main__":
    print(json.dumps({"items": build()}, indent=1, sort_keys=True))
