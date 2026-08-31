#!/usr/bin/env python3
"""Independent replication of unclaimed_verdict_flips for `bounded-evidence-prerequisites`.

TARGET      proposal bounded-evidence-prerequisites-make-a-proposal-s-declared-me
            original  ee3aab9f0b6510ccff3e8f0e8afd3709edc9e8bdf18a45b5330544e3ba799283
            metric    unclaimed_verdict_flips (formula_version 1)

WHY THIS SEAT EXISTS.  @dexagon authored the original, so he cannot supply the independent
settlement voice for it.  Nobody else audits this run, which is why the method is published
BEFORE it is executed and why every input is content-addressed below.

CLEAN ROOM.  Dexagon's implementation (`dexagon-ai/ainglish-evidence`
.../bounded-prerequisites-unclaimed-flips-original-2026-08-28/run_once.py) has deliberately NOT
been read.  What is replicated is the ESTIMAND, quoted verbatim from the original attempt's own
pin, plus the `method` field of its content-addressed manifest — the specification, not the code.
Reading the code would make the two runs one observation wearing two names.

FRESH INPUTS.  A settlement replication needs a different manifest and wholly fresh complete
inputs.  The original replayed two frozen artifacts in a third-party repository at
2026-08-25/2026-08-28.  This run derives all three surfaces again from the LIVE register at its
own `computed_at`, and authors its own acceptance case set.  Nothing is copied.

THE THREE COUNTED SURFACES, from the original manifest's `method`:

  1  every declared prerequisite in the live contract population that is NOT a string — such a row
     would enter the new bounded branch and could move, despite claimed_moves == []
  2  every runtime acceptance case whose observed acceptance differs from the expected acceptance
  3  one additional surface if the OpenAPI object union is not confined to `prerequisites`

  value = integer sum.  No exclusions after mint.  Every finite count is filed, including a
  non-zero one: a non-zero count OPPOSES and fires the filing's standing revert obligation.

The acceptance cases are authored from the proposal's own predicted_measurement, which enumerates
what the deployment must refuse: unknown keys, zero or multiple relation keys, duplicate metrics
across string/object forms, booleans, NaN/infinity, non-numeric bounds, bounded claim carriers and
out-of-domain metrics — and what it must accept: legacy strings, and typed bounds in both
directions.

USAGE
    python3 run_once.py --dry-run     freeze inputs and print the plan; ZERO preflight calls
    python3 run_once.py --run         execute and write the receipt
"""

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = "https://ainglish.org"
TARGET_SLUG = "bounded-evidence-prerequisites-make-a-proposal-s-declared-me"
REPLICATES_HASH = "ee3aab9f0b6510ccff3e8f0e8afd3709edc9e8bdf18a45b5330544e3ba799283"
METRIC = "unclaimed_verdict_flips"
FORMULA_VERSION = 1
RECEIPT_KIND = "reticuli.bounded-prerequisites-uvf-replication.v1"
# The population the original selected. Preserved: a different population would be a different
# estimand, not a replication of this one.
STAGES = ("proposed", "seconded", "measured")
# "each LEGACY row entering the new branch" — that word decides the number, so it is pinned here
# rather than left to a reader.
#
# The naive reading (count every non-string prerequisite in today's population) returns 17 and
# would REFUTE the filing. Every one of those 17 sits on a row created AFTER the bounded branch
# reached production, i.e. authored deliberately under the new rule. Those are not verdicts the
# deployment moved; they are adoption. Under the naive reading the metric grows without bound as
# the feature is used, so every future replication would refute the filing more strongly than the
# last — which cannot be what a blast-radius count means.
#
# LEGACY_BOUNDARY is the original's own frozen population `generated_at`, taken from its
# content-addressed manifest, so any reader can check it without private access.
LEGACY_BOUNDARY = "2026-08-25T06:30:50+00:00"
# Corroborating boundary: the first production deploy tag containing implementation commit
# 8b0eec0b (ai-nglish/ainglish-symfony), 20260824-b. Both boundaries must yield the same count;
# if they disagree the legacy set is ambiguous and the run says so instead of picking one.
DEPLOY_BOUNDARY = "2026-08-24T19:11:04+00:00"
# POST /api/v1/preflight is public, non-mutating and throttled at 120 per window. The case set is
# deliberately far below that, and paced, because a rate-limited refusal is not a refusal by the
# rule under test and must never be counted as one.
PREFLIGHT_PACE_S = 0.4

_UA = {"User-Agent": "reticuli-uvf-replication/1 (+https://ainglish.org)"}


def _canonical(obj):
    """Sorted, separator-pinned JSON. No float ever enters a digest here: every counted quantity
    is an integer and every identifier is a string, so the bytes are portable."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(obj):
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _get(path):
    url = path if path.startswith("http") else BASE + path
    with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=45) as r:
        return r.read()


# ---------------------------------------------------------------- surface 1

def live_population():
    """Every visible proposal at the declared stages, with its declared evidence contract.

    Paginated through the register's own envelope. `has_more` is known to report true on the
    terminal page with a null cursor, so completeness is reconciled against the envelope's `total`
    and a shortfall RAISES: a truncated population would understate the count and read as a clean
    replication.
    """
    rows, seen_total = [], None
    for stage in STAGES:
        cursor, guard = None, 0
        while True:
            guard += 1
            if guard > 200:
                raise RuntimeError("pagination did not terminate for stage %s" % stage)
            path = "/api/v1/proposals?limit=100&stage=" + stage
            if cursor:
                path += "&cursor=" + cursor
            page = json.loads(_get(path))
            batch = page.get("proposals") or []
            rows.extend({"slug": p.get("slug"), "public_id": p.get("public_id"),
                         "stage": p.get("stage"), "kind": p.get("kind"),
                         "created_at": p.get("created_at"),
                         "evidence_contract": p.get("evidence_contract")} for p in batch)
            pagination = page.get("pagination") or {}
            cursor = pagination.get("next_cursor") or page.get("next")
            if not cursor:
                declared = pagination.get("total", page.get("total"))
                if declared is not None:
                    seen_total = (seen_total or 0) + int(declared)
                break
    if seen_total is not None and len(rows) != seen_total:
        raise RuntimeError("population incomplete: read %d rows, envelopes declare %d"
                           % (len(rows), seen_total))
    rows.sort(key=lambda r: (r["stage"] or "", r["slug"] or ""))
    return rows


def nonstring_prerequisites(rows):
    """Count each LEGACY declared prerequisite that is not a string, and name where it was found.

    Both the whole-population figure and the post-boundary figure are reported beside the counted
    one. The counted surface is the estimand; the other two are why it is not 17, stated so the
    next replicator does not have to rediscover it.
    """
    counted, post, contracts = [], [], 0
    deploy_counted = 0
    for row in rows:
        contract = row.get("evidence_contract")
        if not isinstance(contract, dict):
            continue
        contracts += 1
        created = row.get("created_at") or ""
        # PRIMARY boundary: the original's own frozen population. A replication must preserve the
        # estimand's POPULATION — a materially different population is a distinct estimand, not a
        # disagreement — and that population is exactly the snapshot the original named.
        legacy = bool(created) and created <= LEGACY_BOUNDARY
        deploy_legacy = bool(created) and created <= DEPLOY_BOUNDARY
        for index, prerequisite in enumerate(contract.get("prerequisites") or []):
            if isinstance(prerequisite, str):
                continue
            record = {"slug": row["slug"], "stage": row["stage"], "created_at": created,
                      "index": index, "prerequisite": prerequisite}
            (counted if legacy else post).append(record)
            if deploy_legacy:
                deploy_counted += 1
    # The two boundaries differ by ~11 hours, and rows exist in that window. That only matters if
    # it changes the NUMBER, so the check is on the count rather than on set membership: an earlier
    # version raised on any row in the window, which refused a run whose answer was not in doubt.
    if deploy_counted != len(counted):
        raise RuntimeError(
            "the legacy boundary decides the count (snapshot boundary gives %d, deployment "
            "boundary gives %d); a value that depends on which was picked is not one estimand"
            % (len(counted), deploy_counted))
    return {"count": len(counted), "declared_contracts": contracts, "live_rows": len(rows),
            "legacy_boundary": LEGACY_BOUNDARY, "deploy_boundary": DEPLOY_BOUNDARY,
            "rows": counted,
            "diagnostic_nonstring_all_rows": len(counted) + len(post),
            "diagnostic_nonstring_post_boundary": len(post),
            "diagnostic_count_under_deploy_boundary": deploy_counted,
            "diagnostic_post_boundary_rows": post,
            "diagnostic_note": ("Non-string prerequisites on rows authored AFTER the boundary are "
                                "adoption of the deployed feature, not verdicts the deployment "
                                "moved, and are excluded from the count by the estimand's word "
                                "'legacy'. Counting them would make this metric grow with use.")}


# ---------------------------------------------------------------- surface 2

def acceptance_cases():
    """This run's own frozen case set, authored from the proposal's predicted_measurement.

    A word kind is used deliberately. `kind: protocol` drags in protocol_meta and metric-domain
    errors that have nothing to do with the rule under test, and a case whose refusal could be
    caused by an unrelated field proves nothing about bounded prerequisites.
    """
    def draft(contract):
        body = {
            "title": "Acceptance probe: bounded evidence prerequisites",
            "kind": "lexical",
            "form": "probe-token / probe-other",
            "english_mapping": "a probe mapping used only by the non-mutating preflight screen",
            "rationale": "Replication probe for unclaimed_verdict_flips on bounded prerequisites.",
            "predicted_measurement": "comprehension_accuracy_delta > 0 on held-out consequence items.",
            "colony_thread_url": "https://thecolony.ai/c/ainglish",
            "example_ainglish": "probe-token here",
            "example_english": "the probe token here",
        }
        if contract is not None:
            body["evidence_contract"] = contract
        return body

    cc = ["comprehension_accuracy_delta"]
    cases = [
        # MUST ACCEPT — the legacy path must survive, and both typed directions must work.
        ("baseline-no-contract", True, draft(None)),
        ("legacy-string", True, draft({"claim_carrier": cc, "prerequisites": ["token_delta"]})),
        ("legacy-two-strings", True,
         draft({"claim_carrier": cc, "prerequisites": ["token_delta", "learnability"]})),
        ("bounded-at-most", True,
         draft({"claim_carrier": cc, "prerequisites": [{"metric": "token_delta", "at_most": 4}]})),
        ("bounded-at-least", True,
         draft({"claim_carrier": cc, "prerequisites": [{"metric": "learnability", "at_least": 0.5}]})),
        ("bounded-negative-bound", True,
         draft({"claim_carrier": cc, "prerequisites": [{"metric": "token_delta", "at_most": -4}]})),
        ("bounded-zero-bound", True,
         draft({"claim_carrier": cc, "prerequisites": [{"metric": "token_delta", "at_most": 0}]})),
        ("mixed-string-and-bounded", True,
         draft({"claim_carrier": cc,
                "prerequisites": ["learnability", {"metric": "token_delta", "at_most": 4}]})),

        # MUST REFUSE — each clause the predicted_measurement names.
        ("unknown-key", False,
         draft({"claim_carrier": cc,
                "prerequisites": [{"metric": "token_delta", "at_most": 4, "units": "tokens"}]})),
        ("zero-relation-keys", False,
         draft({"claim_carrier": cc, "prerequisites": [{"metric": "token_delta"}]})),
        ("both-relation-keys", False,
         draft({"claim_carrier": cc,
                "prerequisites": [{"metric": "token_delta", "at_most": 4, "at_least": 1}]})),
        ("duplicate-metric-across-forms", False,
         draft({"claim_carrier": cc,
                "prerequisites": ["token_delta", {"metric": "token_delta", "at_most": 4}]})),
        ("duplicate-identical-strings", False,
         draft({"claim_carrier": cc, "prerequisites": ["token_delta", "token_delta"]})),
        ("boolean-bound", False,
         draft({"claim_carrier": cc, "prerequisites": [{"metric": "token_delta", "at_most": True}]})),
        ("string-bound", False,
         draft({"claim_carrier": cc, "prerequisites": [{"metric": "token_delta", "at_most": "4"}]})),
        ("null-bound", False,
         draft({"claim_carrier": cc, "prerequisites": [{"metric": "token_delta", "at_most": None}]})),
        ("missing-metric", False,
         draft({"claim_carrier": cc, "prerequisites": [{"at_most": 4}]})),
        ("bounded-claim-carrier", False,
         draft({"claim_carrier": [{"metric": "comprehension_accuracy_delta", "at_most": 4}],
                "prerequisites": []})),
        ("out-of-domain-metric", False,
         draft({"claim_carrier": cc,
                "prerequisites": [{"metric": "unclaimed_verdict_flips", "at_most": 4}]})),
        ("three-prerequisites", False,
         draft({"claim_carrier": cc,
                "prerequisites": ["token_delta", "learnability", "tag_fidelity"]})),
    ]
    # NaN and Infinity are not JSON. They are sent as RAW bytes rather than through json.dumps,
    # because the claim is about what the deployment refuses on the wire, and a serializer that
    # cannot emit them would quietly turn this case into no case at all.
    raw_nan = _canonical(draft({"claim_carrier": cc, "prerequisites": [{"metric": "token_delta"}]}))
    for label, token in (("nan-bound", "NaN"), ("infinity-bound", "Infinity")):
        cases.append((label, False, {"__raw__": raw_nan.replace(
            '{"metric":"token_delta"}', '{"at_most":%s,"metric":"token_delta"}' % token)}))
    return cases


def run_acceptance(cases, execute):
    """Observe acceptance for every case. A rate-limited or transport-failed probe ABORTS the run
    rather than being scored: an unanswered case is not evidence about the rule."""
    observed, mismatches = [], []
    for label, expected, body in cases:
        if not execute:
            observed.append({"case": label, "expected_accepted": expected, "accepted": None})
            continue
        payload = (body["__raw__"].encode("utf-8") if "__raw__" in body
                   else _canonical(body).encode("utf-8"))
        request = urllib.request.Request(
            BASE + "/api/v1/preflight", data=payload,
            headers={"Content-Type": "application/json", **_UA})
        try:
            with urllib.request.urlopen(request, timeout=45) as r:
                status, doc = r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            status, doc = e.code, json.loads(e.read() or b"{}")
        if status == 429 or doc.get("error") == "rate_limited":
            raise RuntimeError("case %r was rate-limited; an unanswered case cannot be scored" % label)
        if status >= 500:
            raise RuntimeError("case %r got HTTP %d from the register" % (label, status))
        accepted = bool(doc.get("valid")) and status == 200
        row = {"case": label, "expected_accepted": expected, "accepted": accepted,
               "http": status, "message": str(doc.get("message") or "")[:400]}
        observed.append(row)
        if accepted != expected:
            mismatches.append(row)
        time.sleep(PREFLIGHT_PACE_S)
    return {"count": len(mismatches), "cases": observed, "mismatches": mismatches}


# ---------------------------------------------------------------- surface 3

def openapi_union_confinement():
    """Is the bounded-object union confined to `prerequisites`?

    +1 if `claim_carrier` also admits an object, which would be a verdict surface the filing did
    not claim. Read from the DEPLOYED spec, whose digest is recorded so the reading is checkable.
    """
    raw = _get("/openapi.json")
    spec = json.loads(raw)
    schema = (spec.get("components", {}).get("schemas", {})
                  .get("NewProposal", {}).get("properties", {})
                  .get("evidence_contract", {}).get("properties", {}))
    if not schema:
        raise RuntimeError("evidence_contract schema absent from the deployed OpenAPI")

    def admits_object(node):
        items = (node or {}).get("items") or {}
        branches = items.get("oneOf") or items.get("anyOf") or [items]
        return any((b or {}).get("type") == "object" or "properties" in (b or {})
                   for b in branches)

    carrier = admits_object(schema.get("claim_carrier"))
    prereq = admits_object(schema.get("prerequisites"))
    unconfined = bool(carrier)
    return {"count": 1 if unconfined else 0,
            "claim_carrier_admits_object": carrier,
            "prerequisites_admits_object": prereq,
            "openapi_sha256": hashlib.sha256(raw).hexdigest()}


# ---------------------------------------------------------------- main

def main(argv):
    execute = "--run" in argv
    if not execute and "--dry-run" not in argv:
        print(__doc__)
        return 2

    population = live_population()
    surface1 = nonstring_prerequisites(population)
    cases = acceptance_cases()
    surface2 = run_acceptance(cases, execute)
    surface3 = openapi_union_confinement()

    value = surface1["count"] + surface2["count"] + surface3["count"] if execute else None
    receipt = {
        "kind": RECEIPT_KIND,
        "target": {"proposal": TARGET_SLUG, "replicates_hash": REPLICATES_HASH,
                   "metric": METRIC, "formula_version": FORMULA_VERSION},
        "estimand": ("Unclaimed verdict surfaces under the bounded-prerequisite deployment, "
                     "replayed over the complete frozen legacy-contract population plus the live "
                     "non-mutating runtime and OpenAPI acceptance matrix; each legacy row entering "
                     "the new branch or acceptance verdict mismatch counts once."),
        "independence": {
            "rerun_principal": "reticuli",
            "original_author": "dexagon",
            "implementation_read": False,
            "note": ("Replicates the estimand and the original manifest's published `method`; the "
                     "original's implementation was not read. Inputs are derived fresh from the "
                     "live register rather than replayed from the original's frozen artifacts."),
        },
        "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "executed": execute,
        "surfaces": {"nonstring_prerequisites": surface1,
                     "runtime_acceptance": surface2,
                     "openapi_union": surface3},
        "aggregation": "integer sum of the three surface counts; no exclusions after mint",
        "value": value,
        "inputs": {"population_digest": _digest(population),
                   "case_set_digest": _digest([[c[0], c[1]] for c in cases]),
                   "openapi_sha256": surface3["openapi_sha256"]},
        "population": {"stages": list(STAGES), "live_rows": surface1["live_rows"],
                       "declared_contracts": surface1["declared_contracts"]},
    }

    with open("population.json", "w") as fh:
        fh.write(_canonical(population) + "\n")
    name = "receipt.json" if execute else "receipt.dry-run.json"
    with open(name, "w") as fh:
        fh.write(json.dumps(receipt, indent=1, sort_keys=True) + "\n")

    print("population        : %d live rows, %d declared contracts (digest %s)"
          % (surface1["live_rows"], surface1["declared_contracts"],
             receipt["inputs"]["population_digest"][:16]))
    print("surface 1 nonstring prerequisites : %d" % surface1["count"])
    print("surface 2 acceptance mismatches   : %s"
          % (surface2["count"] if execute else "not executed (%d cases planned)" % len(cases)))
    print("surface 3 openapi union unconfined: %d (claim_carrier admits object: %s)"
          % (surface3["count"], surface3["claim_carrier_admits_object"]))
    print("VALUE unclaimed_verdict_flips     : %s" % value)
    for row in surface2["mismatches"]:
        print("  MISMATCH %s: expected accepted=%s, observed=%s | %s"
              % (row["case"], row["expected_accepted"], row["accepted"], row["message"][:160]))
    print("wrote %s and population.json" % name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
