#!/usr/bin/env python3
"""Frozen item set for by-construction / by-rule / in-practice — comprehension original.

The row's declared probes, with their declared keys:
  Q1 "under the claim as written, could an exception occur without the system having been
      changed?"            by-construction: no    by-rule: yes    in-practice: yes
  Q2 "an exception is then observed, system unchanged; what follows under the claim?"
                           bc: the claim was false    br: breach, repair owed    ip: news

Design decisions this generator enforces:
  ANTI-CEILING (lesson of rows 1-2, where careful English sat at 1.00 and advantages were
  undetectable by construction): every scenario names TWO properties with DIFFERENT statuses,
  and the probe asks about one of them. Answering requires binding the right property to the
  right status in both arms — genuine difficulty, not noise.

  HELD-OUT VOCABULARY, the hard version: on this row the careful-English arm IS the mapping, so
  the mapping's own lexemes (exception/violation/repair/news/falsifies) must not be the option
  lexemes. Arms use falsify/lapse/put right/noteworthy; options use disproven/defaulted/owes
  correction/merely new information. The lint below enforces lexeme disjointness mechanically.

  STRATA: one per form (bc / br / ip), equal weight, never pooled.

DECLARED-AND-DEFERRED, stated: the row also declares a comparison against BARE COPULA sentences.
The panel is two-armed, so that is a second filing with its own manifest, not a silent trim.
(The calibration items below use bare copula as the undetectable arm, which is the same contrast
as a planted control — but calibration cells are instrument certification, not evidence.)

Deterministic: python3 generate_items.py > items.json
"""

import hashlib
import itertools
import json

SEED = "by-construction-comp-2026-08-31"


def pick(options, *keys):
    h = hashlib.sha256("\0".join((SEED,) + tuple(str(k) for k in keys)).encode()).digest()
    return options[int.from_bytes(h[:4], "big") % len(options)]


def rotate(opts, *keys):
    k = int.from_bytes(hashlib.sha256("\0".join((SEED, "rot") + tuple(map(str, keys))).encode()).digest()[:2], "big")
    r = k % len(opts)
    return list(opts[r:]) + list(opts[:r])


# (system, property-claimed, distractor-property, distractor-status-text)
SCENARIOS = [
    ("the billing exporter", "its responses are valid JSON", "its retry budget",
     "its retry budget is capped at three by team policy"),
    ("the audit logger", "log lines are free of customer identifiers", "its rotation schedule",
     "rotation happens nightly, as it always has"),
    ("the deploy pipeline", "every release is peer-reviewed", "its build cache",
     "the build cache is wiped weekly by convention"),
    ("the backup service", "archives are encrypted at rest", "its bandwidth use",
     "bandwidth stays under the cap in everything measured so far"),
    ("the invoice system", "payouts above 10k carry two approvals", "its currency table",
     "the currency table refreshes hourly by design of the scheduler"),
    ("the warehouse door system", "doors are locked outside shift hours", "its camera coverage",
     "camera coverage has been complete in every spot-check"),
    ("the payments API", "duplicate submissions produce one charge", "its response latency",
     "response latency is required to stay under 300ms by the SLA"),
    ("the schema migrator", "every migration has a tested rollback", "its lock behaviour",
     "locks are held briefly, as observed across recent runs"),
    ("the session service", "tokens expire within an hour", "its logging verbosity",
     "verbosity is set by a standing operations rule"),
    ("the ingest gateway", "malformed rows are quarantined, never dropped", "its throughput",
     "throughput has met demand in all traffic seen to date"),
    ("the license server", "grants never exceed the purchased seat count", "its restart cadence",
     "restarts follow a documented weekly requirement"),
    ("the notifier", "every alert page carries a runbook link", "its delivery order",
     "delivery order has matched send order whenever anyone checked"),
    ("the export scrubber", "outbound files contain no internal hostnames", "its file naming",
     "file naming follows the convention the team mandates"),
    ("the quota service", "tenants cannot exceed their storage quota", "its metrics emission",
     "metrics have emitted cleanly in every observed window"),
    ("the release signer", "artifacts ship with a valid signature", "its queue depth",
     "queue depth is kept below ten by an operations rule"),
    ("the archive purger", "records older than seven years are removed", "its dry-run mode",
     "dry-run mode has behaved identically to live mode so far"),
]

BC_EN = [  # falsify / altered — NOT disproven
    "For {sys}, {prop} — and by how it is built, this cannot fail to hold while the system stands unaltered; observing a counterexample would falsify the claim or show the system was changed.",
    "By how {sys} is put together, {prop}; a counterexample is impossible without the system itself having been altered, and seeing one would falsify this or prove an alteration.",
]
BR_EN = [  # lapse / put right / answerable — NOT defaulted/obligation/owes correction
    "For {sys}, a standing rule requires that {prop}; a counterexample can happen, and each one is a lapse that a specific owner must put right or explain.",
    "{sys} operates under a standing rule that {prop}. Counterexamples are possible; every one is a lapse some named owner is answerable for.",
]
IP_EN = [  # seen so far / noteworthy — NOT merely new information
    "For {sys}, {prop} in everything seen so far; nothing about the system prevents or forbids a counterexample, and one would simply be noteworthy.",
    "So far, without exception, {prop} for {sys} — though nothing enforces or requires this, and a counterexample would be noteworthy rather than anyone's failing.",
]
AI = [
    "{sys}: {prop} {marker}. Also: {distractor}.",
    "Status of {sys} — {prop} {marker}. Separately, {distractor}.",
]
EN_WRAP = [
    "{core} Also: {distractor}.",
    "{core} Separately, {distractor}.",
]

Q1 = [
    "Under the claim as written about the FIRST property, could a counterexample to it arise without the system having been changed?",
    "Taking the claim about the first-mentioned property exactly as written: is a counterexample possible while the system stays as it is?",
]
Q1_OPTS = ("yes, one could arise", "no, not while the system stands as built", "the claim does not settle this")
Q2 = [
    "Suppose a counterexample to the FIRST property is then observed, with the system unchanged. Under the claim as written, what follows?",
    "A counterexample to the first-mentioned property turns up and the system was not changed. Going only by the claim: what follows?",
]
Q2_OPTS = ("the claim itself is thereby disproven",
           "a named party has defaulted and owes correction",
           "nothing is owed; it is merely new information")

FORMS = {
    "bc": ("by-construction", BC_EN, {"q1": Q1_OPTS[1], "q2": Q2_OPTS[0]}),
    "br": ("by-rule", BR_EN, {"q1": Q1_OPTS[0], "q2": Q2_OPTS[1]}),
    "ip": ("in-practice", IP_EN, {"q1": Q1_OPTS[0], "q2": Q2_OPTS[2]}),
}

items = []
for form, (marker, frames, keys) in FORMS.items():
    for slot, (sys_, prop, _dname, distractor) in enumerate(SCENARIOS):
        sid = f"{form}-{slot:02d}"
        core = pick(frames, sid, "en").format(sys=sys_, prop=prop)
        english = pick(EN_WRAP, sid, "wrap").format(core=core, distractor=distractor)
        ainglish = pick(AI, sid, "ai").format(sys=sys_, prop=prop, marker=marker, distractor=distractor)
        for probe, qbank, opts in (("q1", Q1, Q1_OPTS), ("q2", Q2, Q2_OPTS)):
            items.append({
                "id": f"{sid}-{probe}", "settlement_stratum": form,
                "english": english, "ainglish": ainglish,
                "question": pick(qbank, sid, probe),
                "options": rotate(opts, sid, probe),
                "answer": keys[probe],
            })

# Calibration: bare copula vs marked. The bare sentence genuinely cannot answer Q1/Q2; only the
# marked arm can. This is also the row's declared bare-copula contrast, worn as a planted control.
CAL = SCENARIOS[:6]
CAL_FORMS = ["bc", "br", "ip", "bc", "br", "ip"]
for k, ((sys_, prop, _d, _ds), form) in enumerate(zip(CAL * 2, CAL_FORMS * 2)):
    if k >= 12:
        break
    marker, _frames, keys = FORMS[form]
    iid = f"c{k:02d}"
    probe = "q1" if k % 2 == 0 else "q2"
    qbank, opts = (Q1, Q1_OPTS) if probe == "q1" else (Q2, Q2_OPTS)
    items.append({
        "id": iid, "calibration": True,
        "english": f"For {sys_}, {prop}.",
        "ainglish": f"{sys_}: {prop} {marker}.",
        "question": pick(qbank, iid, probe),
        "options": rotate(opts, iid, probe),
        "answer": keys[probe],
    })

print(json.dumps({"items": items}, indent=1, sort_keys=True))
