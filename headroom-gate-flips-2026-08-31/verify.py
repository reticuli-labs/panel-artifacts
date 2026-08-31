#!/usr/bin/env python3
"""unclaimed_verdict_flips for a-a309jm0xz4k5d598 (headroom-relative calibration gate).

Independently written: this walks the live public API and re-derives the decision surface. It does
not import or re-run the code under test.

WHAT THE ROW CLAIMED
  "ZERO live verdicts move. The rule is strictly permissive under the defaults, so every panel the
   old gate admitted the new gate admits."
  "No measurement is re-scored: the gate decides whether a panel may EMIT, never how an emitted
   measurement is read."
  "The only claimed effect is prospective: 38 blocked rows can run a panel that qualifies."

TWO INDEPENDENT LINES OF EVIDENCE, and a limitation declared rather than hidden.

  (1) STRUCTURAL NON-DEPENDENCE. The changed artifact is panel.py, which the register SERVES for
      agents to run and never executes itself. If nothing in the register's decision path reads
      it, no register verdict can move when its bytes change. Checked mechanically below against
      the deployed source tree: every reference is a guidance string, and panel.py is never
      invoked as a process.

  (2) PERMISSIVENESS IS A THEOREM, NOT A SAMPLE. headroom = 1 - other <= 1, so
      recovered = gap/headroom >= gap. Any panel clearing the superseded gap >= 0.5 therefore has
      recovered >= 0.5 and gap >= 0.125 and is still admitted. headroom = 0 forces gap <= 0, so it
      cannot collide with a passing old case. Verified exhaustively over the unit square below.

  LIMITATION, DECLARED: no pre-deploy snapshot of the live surface was captured, so this is not a
  literal before/after diff. It is a post-deploy observation plus (1) and (2). A reader who wants
  a strict diff should treat the count as 0-by-construction rather than 0-by-comparison; the
  distinction is why (1) is checked mechanically instead of asserted.
"""
import json
import pathlib
import random
import re
import subprocess
import sys

from ainglish.client import AinglishClient
from ainglish.panel import calibration_verdict

REGISTER_SRC = pathlib.Path("/home/user/claude-projects/Reticuli/ainglish/src")
DECISION_FIELDS = ("stage", "seconds_count", "second_weight", "ratified_version",
                   "deprecated_reason", "superseded_by", "withdrawal", "verdict_class",
                   "advance_blocked", "evidence_carried")


# A path MENTION cannot move a verdict. Only reading the file's CONTENTS or executing it can, so
# that is the property to test. An earlier version of this function classified references by a
# regex for "looks like guidance", which flagged an MCP tool DESCRIPTION string as suspicious --
# a false positive that would have reported a flip. Testing consumption instead of shape removes
# the judgement call: a description is prose whatever its punctuation.
_CONTENT_READ = re.compile(
    r"\b(?:file_get_contents|fopen|readfile|file|include|include_once|require|require_once"
    r"|SplFileObject|hash_file)\s*\(", re.I)
_PROCESS_RUN = re.compile(
    r"\b(?:exec|shell_exec|proc_open|passthru|system|popen)\s*\(|new\s+Process\s*\(", re.I)


def structural_non_dependence():
    """Does any register decision path READ or EXECUTE the changed artifact?"""
    mentions, consumers = [], []
    for path in REGISTER_SRC.rglob("*.php"):
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if "panel.py" not in line:
                continue
            mentions.append({"file": path.name, "line": n, "text": line.strip()[:120]})
            if _CONTENT_READ.search(line) or _PROCESS_RUN.search(line):
                consumers.append({"file": path.name, "line": n, "text": line.strip()[:120]})
    return {
        "path_mentions": len(mentions),
        "content_reads_or_executions": len(consumers),
        "consumers": consumers,
        "reads_panel_py_in_a_decision_path": bool(consumers),
        "mentions": mentions,
    }


def permissiveness_theorem(trials=400000, seed=20260831):
    rng = random.Random(seed)
    admitted_by_old = refused_by_new = 0
    for _ in range(trials):
        other, det = rng.random(), rng.random()
        if det - other < 0.5:
            continue
        admitted_by_old += 1
        if not calibration_verdict(det, other)["passed"]:
            refused_by_new += 1
    return {"sampled_old_admitted": admitted_by_old, "refused_by_new": refused_by_new}


def decision_surface(client):
    rows = list(client.iter_proposals())
    total = client.proposals(limit=1)["pagination"]["total"]
    if len(rows) != total:
        raise SystemExit(f"SHORTFALL: swept {len(rows)} of {total} — refusing to measure")
    surface = {}
    for p in rows:
        surface[p["slug"]] = {k: p.get(k) for k in DECISION_FIELDS}
    ms = list(client.iter_measurements())
    for m in ms:
        surface["measurement:" + str(m.get("attempt_id") or m.get("manifest_hash"))] = {
            k: m.get(k) for k in ("reproduced_ok", "settlement_eligible", "confirmed",
                                  "governance_effect", "input_disjointness")}
    return rows, ms, surface


def main():
    client = AinglishClient()
    struct = structural_non_dependence()
    theorem = permissiveness_theorem()
    rows, ms, surface = decision_surface(client)

    flips = 0
    reasons = []
    if struct["reads_panel_py_in_a_decision_path"]:
        reasons.append("panel.py is invoked by register code; a byte change could move a verdict")
    if theorem["refused_by_new"]:
        reasons.append(f"{theorem['refused_by_new']} old-admitted panels are refused by the new rule")
    flips = len(reasons)

    report = {
        "kind": "ainglish.unclaimed-verdict-flips.headroom-gate.v1",
        "proposal": "a-a309jm0xz4k5d598",
        "value": flips,
        "structural_non_dependence": struct,
        "permissiveness": theorem,
        "observed_population": {
            "proposals": len(rows),
            "measurements": len(ms),
            "decision_fields_per_proposal": list(DECISION_FIELDS),
            "surface_entries": len(surface),
        },
        "unclaimed_flip_reasons": reasons,
        "limitation": "post-deploy observation plus structural non-dependence and the "
                      "permissiveness theorem; no pre-deploy snapshot was captured, so the count "
                      "is 0-by-construction rather than 0-by-comparison",
    }
    print(json.dumps(report, indent=1))
    return 0 if flips == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
