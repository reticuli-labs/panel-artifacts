#!/usr/bin/env python3
"""Frozen item set for test-run(<T>) / test-passed(<T>) — comprehension original.

Implements the row's own predicted_measurement:
  - >= 96 held-out, form-balanced items; the two markers REPORTED SEPARATELY (settlement strata)
  - six domains: software, backups, data pipelines, physical inspections, audits, model evals
  - each item fixes one ground truth and a NAMED test reference
  - consequence questions that never repeat the markers, with answer vocabulary held out of
    both arms (v2 held-out question rule)
  - the English arm is the shortest careful-English statement of the FULL declared mapping

Question allocation, and why. The declared trio is: did the procedure execute; does the statement
establish every declared criterion was met; may the reader infer broader fitness. Q2 is the
discriminating question (its key differs by marker), so it carries 6 of every 8 items; Q1 and Q3
have marker-independent keys (execution is asserted by both forms; broader fitness is never
licensed) and take one item each per block as declared-but-lower-power probes of over-inference.

Deterministic: python3 generate_items.py > items.json, byte-stable for any reader.
"""

import hashlib
import itertools
import json

SEED = "test-run-passed-comp-2026-08-31"


def pick(options, *keys):
    """Deterministic choice from the frozen seed — no RNG state, re-runnable by a stranger."""
    h = hashlib.sha256("\0".join((SEED,) + tuple(str(k) for k in keys)).encode()).digest()
    return options[int.from_bytes(h[:4], "big") % len(options)]


DOMAINS = {
    "software": [
        ("build 4f19c2", "checkout-e2e-v7", "run 512"), ("build 88aa31", "login-smoke-v3", "run 209"),
        ("release 2.9.1", "upgrade-path-v2", "run 77"), ("service image swan-1.4", "api-contract-v9", "run 3021"),
        ("build 7c0d9e", "cart-regression-v5", "run 640"), ("hotfix 1.8.4", "session-expiry-v2", "run 41"),
        ("build 3e2b77", "search-index-v6", "run 128"), ("candidate 5.0-rc2", "billing-cycle-v4", "run 902"),
    ],
    "backups": [
        ("backup B17", "restore-v4", "run 817"), ("backup W03", "restore-v4", "run 244"),
        ("snapshot S-2211", "integrity-scan-v2", "run 66"), ("archive AR-91", "media-verify-v1", "run 5"),
        ("backup Q88", "restore-partial-v3", "run 431"), ("snapshot S-0409", "catalog-check-v2", "run 19"),
        ("vault copy V-12", "offsite-read-v1", "run 88"), ("backup B44", "restore-v5", "run 1203"),
    ],
    "pipelines": [
        ("nightly load L-77", "row-count-recon-v3", "run 2210"), ("feed F-metrics", "schema-drift-v2", "run 431"),
        ("join job J-19", "dedupe-audit-v1", "run 87"), ("export E-52", "checksum-recon-v4", "run 664"),
        ("ingest I-08", "late-arrival-v2", "run 190"), ("rollup R-3", "totals-recon-v5", "run 771"),
        ("stream S-billing", "gap-detect-v3", "run 42"), ("load L-83", "null-rate-v2", "run 355"),
    ],
    "inspections": [
        ("fire door FD-12", "closure-latch-v2", "check 31"), ("pressure vessel PV-4", "hydro-test-v6", "check 9"),
        ("hoist H-2", "load-brake-v3", "check 118"), ("valve V-771", "seat-leak-v2", "check 47"),
        ("ladder L-9", "rung-integrity-v1", "check 6"), ("extinguisher X-33", "gauge-charge-v2", "check 210"),
        ("scaffold S-5", "tie-in-v3", "check 74"), ("crane C-1", "limit-switch-v4", "check 380"),
    ],
    "audits": [
        ("vendor ledger VL-9", "three-way-match-v2", "cycle 14"), ("access list AL-ops", "leaver-removal-v3", "cycle 8"),
        ("expense batch EB-207", "receipt-match-v1", "cycle 22"), ("privilege set PS-db", "least-priv-v2", "cycle 5"),
        ("payroll run PR-06", "variance-band-v4", "cycle 61"), ("grant register GR-2", "dual-sign-v1", "cycle 17"),
        ("card program CP-1", "limit-policy-v2", "cycle 33"), ("treasury desk TD", "counterparty-cap-v3", "cycle 9"),
    ],
    "modelevals": [
        ("model m-2409", "toxicity-suite-v5", "eval 88"), ("checkpoint ck-771", "holdout-accuracy-v3", "eval 12"),
        ("adapter ad-3", "regression-set-v7", "eval 301"), ("model m-3001", "jailbreak-probe-v2", "eval 55"),
        ("ranker r-88", "ndcg-floor-v2", "eval 140"), ("classifier c-19", "drift-battery-v4", "eval 23"),
        ("extractor x-6", "field-recall-v3", "eval 77"), ("model m-2811", "latency-budget-v2", "eval 9"),
    ],
}

RUN_EN = [   # careful English for test-run(T): execution asserted, outcome expressly open
    "{proc} ({ref}) was executed on {subj}; whether its acceptance criteria were met is not reported.",
    "On {subj}, {proc} ({ref}) did take place. The report stops there: no result is given.",
    "{subj} underwent {proc} in {ref}; the record confirms the execution and says nothing about the result.",
    "The named procedure {proc} ({ref}) ran against {subj}. Its outcome was not recorded.",
]
PASS_EN = [  # careful English for test-passed(T): execution + every declared criterion met
    "{subj} met every acceptance criterion declared by {proc} for {ref}; the procedure did execute in that run.",
    "In {ref}, {proc} was carried out on {subj} and each of its declared acceptance criteria was met.",
    "{proc} ({ref}) ran on {subj}, and all of the criteria that procedure declares were satisfied in that run.",
    "The record shows {proc} executing against {subj} in {ref} with every declared criterion satisfied.",
]
RUN_AI = [
    "{subj}: test-run({proc}@{ref}).",
    "{subj} — test-run({proc}@{ref}); nothing further reported.",
    "status {subj}: test-run({proc}@{ref}).",
]
PASS_AI = [
    "{subj}: test-passed({proc}@{ref}).",
    "{subj} — test-passed({proc}@{ref}).",
    "status {subj}: test-passed({proc}@{ref}).",
]

Q2 = [  # the discriminating question: key differs by marker
    "Based only on the statement, does it establish that every acceptance criterion declared by the named procedure was met in that run?",
    "Going by the statement alone: is it settled that all of the named procedure's declared criteria were satisfied?",
    "Does the statement, by itself, settle whether each criterion the named procedure declares was met?",
]
Q2_OPTS = ["it establishes this", "it establishes the opposite", "it leaves this open"]
Q1 = [  # execution: both markers assert it
    "Based only on the statement, did the named procedure actually take place on the item described?",
    "Going by the statement alone: did that specific procedure execute?",
]
Q1_OPTS = ["it took place", "it did not take place", "the statement leaves this open"]
Q3 = [  # broader fitness: never licensed by either marker
    "Based only on the statement, may a reader conclude the item is fit for purposes beyond what the named procedure checks?",
    "Does the statement, by itself, license conclusions about qualities the named procedure does not check?",
]
Q3_OPTS = ["yes, broader fitness follows", "no, only what the named procedure checks", "only when the run happened recently"]


def rotate(opts, *keys):
    k = int.from_bytes(hashlib.sha256("\0".join((SEED, "rot") + tuple(map(str, keys))).encode()).digest()[:2], "big")
    r = k % len(opts)
    return opts[r:] + opts[:r]


items = []
counter = itertools.count(1)
for domain, subjects in DOMAINS.items():
    for marker in ("run", "passed"):
        for slot, (subj, proc, ref) in enumerate(subjects):
            n = next(counter)
            iid = f"r{n:03d}-{domain}-{marker}"
            en_frames, ai_frames = (RUN_EN, RUN_AI) if marker == "run" else (PASS_EN, PASS_AI)
            english = pick(en_frames, iid, "en").format(subj=subj, proc=proc, ref=ref)
            ainglish = pick(ai_frames, iid, "ai").format(subj=subj, proc=proc, ref=ref)
            if slot < 6:      # Q2: the discriminating question
                q = pick(Q2, iid, "q")
                opts = rotate(Q2_OPTS, iid)
                answer = "it leaves this open" if marker == "run" else "it establishes this"
            elif slot == 6:   # Q1
                q = pick(Q1, iid, "q")
                opts = rotate(Q1_OPTS, iid)
                answer = "it took place"
            else:             # Q3
                q = pick(Q3, iid, "q")
                opts = rotate(Q3_OPTS, iid)
                answer = "no, only what the named procedure checks"
            items.append({
                "id": iid,
                "settlement_stratum": f"marker:test-{'run' if marker == 'run' else 'passed'}",
                "english": english, "ainglish": ainglish,
                "question": q, "options": opts, "answer": answer,
            })

# Calibration: the planted difference. The bare-English arm honestly cannot settle the criteria
# question; the marked arm can. Detectability of the marker IS the planted effect.
CAL = [
    ("the staging database", "failover-drill-v2", "run 18"), ("gateway G-7", "tls-rotation-v1", "run 4"),
    ("backup N-51", "restore-v4", "run 121"), ("model m-1901", "holdout-accuracy-v3", "eval 61"),
    ("fire pump FP-1", "flow-test-v5", "check 12"), ("ledger L-ops", "three-way-match-v2", "cycle 3"),
    ("feed F-orders", "schema-drift-v2", "run 210"), ("build 9a1c44", "checkout-e2e-v7", "run 733"),
    ("snapshot S-118", "integrity-scan-v2", "run 40"), ("valve V-208", "seat-leak-v2", "check 91"),
    ("card program CP-4", "limit-policy-v2", "cycle 11"), ("extractor x-9", "field-recall-v3", "eval 30"),
]
for k, (subj, proc, ref) in enumerate(CAL, 1):
    iid = f"c{k:02d}"
    items.append({
        "id": iid, "calibration": True,
        "english": pick([
            "{subj} was tested with {proc} in {ref}.",
            "{proc} testing of {subj} took place ({ref}).",
        ], iid, "en").format(subj=subj, proc=proc, ref=ref),
        "ainglish": pick(PASS_AI, iid, "ai").format(subj=subj, proc=proc, ref=ref),
        "question": pick(Q2, iid, "q"),
        "options": rotate(Q2_OPTS, iid),
        "answer": "it establishes this",
    })

print(json.dumps({"items": items}, indent=1, sort_keys=True))
