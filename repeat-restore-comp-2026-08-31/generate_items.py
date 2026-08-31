#!/usr/bin/env python3
"""Frozen item set for repeat-event / restore-state — comprehension original.

Implements the row's declared design:
  - 128 scenarios: 64 per form x {16 affirmative, 16 negated, 16 polar question, 16 directive}
  - TWO independently scored probes per scenario (=> 256 real items):
      probe A: recover the marker's projected earlier-event / earlier-state condition
      probe B: recover the current clause's force (asserted / denied / questioned / requested)
  - every form x force cell is its own settlement stratum — reported separately, never pooled
  - within each directive cell, earlier-event agency balanced: addressee vs another actor,
    with probe A scoring participant attachment in those cells
  - predicate families balanced across 8 result-state predicates

DECLARED-AND-DEFERRED, stated rather than trimmed silently: the row also asks for 32 restore-state
validity fixtures (missing state, non-entailed state, ambiguous predicates), "separately
reported". Settlement strata all contribute weight to the headline value, so folding fixtures into
this run would pollute the primary estimand rather than report them separately. They are a
follow-up filing with their own manifest, and this run's README carries that commitment.

Deterministic: python3 generate_items.py > items.json.
"""

import hashlib
import itertools
import json

SEED = "repeat-restore-comp-2026-08-31"


def pick(options, *keys):
    h = hashlib.sha256("\0".join((SEED,) + tuple(str(k) for k in keys)).encode()).digest()
    return options[int.from_bytes(h[:4], "big") % len(options)]


def rotate(opts, *keys):
    k = int.from_bytes(hashlib.sha256("\0".join((SEED, "rot") + tuple(map(str, keys))).encode()).digest()[:2], "big")
    r = k % len(opts)
    return list(opts[r:]) + list(opts[:r])


# (actor, addressee, verb-infinitive, verb-past, verb-gerund-object, state-predicate, object)
FAMILIES = [
    ("Mara", "Ollie", "open the west gate", "opened the west gate", "open(west-gate)", "the west gate was open"),
    ("Jo", "Priya", "make the billing service healthy", "made the billing service healthy", "healthy(billing-service)", "the billing service was healthy"),
    ("Ravi", "Sam", "lock the archive door", "locked the archive door", "locked(archive-door)", "the archive door was locked"),
    ("Lena", "Theo", "clear the session cache", "cleared the session cache", "empty(session-cache)", "the session cache was empty"),
    ("Noor", "Kai", "sign the transfer form", "signed the transfer form", "signed(transfer-form)", "the transfer form was signed"),
    ("Iris", "Dev", "switch the beacon light on", "switched the beacon light on", "on(beacon-light)", "the beacon light was on"),
    ("Owen", "Ana", "capture the deposit payment", "captured the deposit payment", "captured(deposit-payment)", "the deposit payment was captured"),
    ("Tessa", "Rob", "rebuild the search index", "rebuilt the search index", "built(search-index)", "the search index was built"),
]

FORCES = ("aff", "neg", "pq", "dir")

A_COND = [  # probe A phrasings (never repeat the markers)
    "Besides what the main clause does, what background circumstance does the statement take as already given?",
    "What earlier circumstance, if any, does the statement presuppose?",
]
A_OPTS_CORE = (
    "an earlier occurrence of the same action, matching the stated participants",
    "an earlier interval in which the resulting state already held",
    "no earlier occurrence or state is taken as given",
)
A_OPTS_DIR_RE = (  # repeat-event directive cells: does the taken-as-given background FIT the context?
    "yes, it matches what the context established",
    "no, it conflicts with what the context established",
    "the utterance takes no background as given",
)
A_OPTS_DIR_RS = (
    "an earlier occurrence of the same action by the person being addressed",
    "an earlier occurrence of the same action, but not attributed to the person being addressed",
    "an earlier interval in which the resulting state already held",
)
A_DIR_RE_Q = [
    "A context sentence precedes the utterance. Does the background the speaker treats as already given fit what the context established?",
    "Given the context sentence first: is the circumstance the utterance takes for granted consistent with that context?",
]
B_FORCE = [
    "What does the main clause itself do with the action it names?",
    "Setting the background aside: how is the action of the main clause put forward?",
]
B_OPTS = (
    "it is stated as having happened",
    "it is stated as not having happened",
    "it is asked about as a question",
    "it is requested to be carried out",
)
B_KEY = {"aff": B_OPTS[0], "neg": B_OPTS[1], "pq": B_OPTS[2], "dir": B_OPTS[3]}


def clause(force, actor, addressee, inf, past):
    if force == "aff":
        return f"{actor} {past}."
    if force == "neg":
        did_not = inf  # infinitive after 'did not'
        return f"{actor} did not {did_not}."
    if force == "pq":
        return f"Did {actor} {inf}?"
    return f"{addressee}, please {inf}."


def english_repeat(force, fam, agent_prior):
    actor, addressee, inf, past, _sp, _st = fam
    c = clause(force, actor, addressee, inf, past)
    if force == "dir":
        # The marked form's background claim, per the mapping, binds the STATED participants —
        # in a directive that is the addressee. Both arms therefore make the SAME claim
        # (addressee did it before); the addressee-vs-other balance lives in the shared CONTEXT
        # sentence, and probe A asks whether the claim FITS the context. The first version of
        # this generator instead varied the english arm's claim while the marked arm stayed
        # byte-identical across variants with different keys — the arms-derive-different-answers
        # defect, caught at spot-check before freeze.
        return f"{c} As background, taken as given: {addressee} has done that same action before now."
    return (f"{c} As background, taken as given: an event of the same kind, with the same "
            f"stated participants, took place before the time this clause is about.")


def dir_context(fam, agent_prior):
    actor, addressee, inf, past, _sp, _st = fam
    doer = addressee if agent_prior == "addressee" else actor
    return f"Context: earlier today, {doer} {past}."


def english_restore(force, fam):
    actor, addressee, inf, past, _sp, st = fam
    c = clause(force, actor, addressee, inf, past)
    return (f"{c} As background, taken as given: {st} during some earlier interval; nothing is "
            f"said about who, if anyone, brought that about before.")


def ainglish_repeat(force, fam):
    actor, addressee, inf, past, _sp, _st = fam
    return f"repeat-event: {clause(force, actor, addressee, inf, past)}"


def ainglish_restore(force, fam):
    actor, addressee, inf, past, sp, _st = fam
    return f"restore-state({sp}): {clause(force, actor, addressee, inf, past)}"


items = []
n = itertools.count(1)
for form in ("re", "rs"):
    for force in FORCES:
        for slot in range(16):
            fam = FAMILIES[slot % 8]
            agent_prior = ("addressee" if slot < 8 else "other") if force == "dir" else None
            sid = f"{form}-{force}-{slot:02d}"
            stratum = f"{form}:{force}"
            if form == "re":
                en = english_repeat(force, fam, agent_prior)
                ai = ainglish_repeat(force, fam)
                if force == "dir":
                    ctx = dir_context(fam, agent_prior)
                    en = f"{ctx} {en}"
                    ai = f"{ctx} {ai}"
                    a_opts = A_OPTS_DIR_RE
                    a_key = A_OPTS_DIR_RE[0] if agent_prior == "addressee" else A_OPTS_DIR_RE[1]
                    a_q = pick(A_DIR_RE_Q, sid, "qa")
                else:
                    a_opts, a_key, a_q = A_OPTS_CORE, A_OPTS_CORE[0], pick(A_COND, sid, "qa")
            else:
                en = english_restore(force, fam)
                ai = ainglish_restore(force, fam)
                a_opts, a_key = (A_OPTS_DIR_RS, A_OPTS_DIR_RS[2]) if force == "dir" else (A_OPTS_CORE, A_OPTS_CORE[1])
                a_q = pick(A_COND, sid, "qa")
            # probe A — projected condition; in re:dir cells, fit-against-context (participant attachment)
            items.append({
                "id": f"{sid}-pa", "settlement_stratum": stratum,
                "english": en, "ainglish": ai,
                "question": a_q,
                "options": rotate(a_opts, sid, "a"),
                "answer": a_key,
            })
            # probe B — force of the scoped clause
            items.append({
                "id": f"{sid}-pb", "settlement_stratum": stratum,
                "english": en, "ainglish": ai,
                "question": pick(B_FORCE, sid, "qb"),
                "options": rotate(B_OPTS, sid, "b"),
                "answer": B_KEY[force],
            })

# Calibration: planted marker-detectability. The English arm uses bare "again", whose attachment
# the row itself says is unresolved; the marked arm resolves it. Key recoverable only from the
# marked arm. Half repeat-event, half restore-state, so both markers are calibrated.
for k in range(12):
    fam = FAMILIES[k % 8]
    actor, addressee, inf, past, sp, st = fam
    form = "re" if k % 2 == 0 else "rs"
    iid = f"c{k:02d}"
    en = f"{actor} {past} again."
    ai = (f"repeat-event: {actor} {past}." if form == "re"
          else f"restore-state({sp}): {actor} {past}.")
    items.append({
        "id": iid, "calibration": True,
        "english": en, "ainglish": ai,
        "question": pick(A_COND, iid, "q"),
        "options": rotate(A_OPTS_CORE, iid),
        "answer": A_OPTS_CORE[0] if form == "re" else A_OPTS_CORE[1],
    })

print(json.dumps({"items": items}, indent=1, sort_keys=True))
