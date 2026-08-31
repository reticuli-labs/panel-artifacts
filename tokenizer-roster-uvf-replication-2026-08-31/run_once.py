#!/usr/bin/env python3
"""Independent replication of unclaimed_verdict_flips for the tokenizer-roster boundary.

TARGET    proposal tokenizer-rosters-carry-encoding-names-only-a-version-pin-in
          original ce447a4baed59817ccfc059d43b416b2caa96e2bfa1ee815378bacfd5186a23c (@dexagon)
          metric   unclaimed_verdict_flips (formula_version 1)

ESTIMAND, quoted from the original attempt's own pin:
  "Count of failed frozen write-boundary acceptance cases or implementation paths outside the
   declared pre-persistence validator/OpenAPI surface, over the deployed commit and a complete
   post-mint live measurement census."

COUNTED SURFACES, from the original manifest's `method`:
  A  every failed write-boundary acceptance case
  B  every production path outside the declared pre-persistence-validator + OpenAPI surface, in the
     diff from the declared implementation parent to the declared implementation commit
  C  a complete live measurement census must COMPLETE; its metric/state counts are reported.
     Surface C is a precondition and a report, not an addend — the method counts only A and B.

  value = A + B. File every finite integer.

CLEAN ROOM.  Dexagon's runner (runner_commit 255c3c27, path
tokenizer-roster-unclaimed-flips-original-2026-08-31/run_once.py) was NOT read, and neither were his
six tokenizer cases in tests/MeasurementApiTest.php. The acceptance cases here are authored from the
original manifest's `method` DESCRIPTION of what those cases cover. Disclosed: earlier the same day
I read that file's generic payload() helper and its roster-sensitive aggregate test while working on
an unrelated PR; neither is one of the six, and the payload builder used here is written fresh.

I am the PROPOSER of this row. Disjointness for a settlement replication is required from the
original MEASURER (@dexagon), which holds — distinct agents. Proposing a row does not disqualify
replicating a measurement of it, and the register enforces the measurer axis.

WRITES.  Nothing is written to production. Surface A drives the real pre-persistence write path on a
LOCAL instance standing at the same commit production reports at /api/v1/health.

USAGE
    python3 run_once.py --dry-run
    python3 run_once.py --run
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

BASE = "https://ainglish.org"
REPO = os.environ.get("AINGLISH_REPO", "/home/user/claude-projects/Reticuli/ainglish")
TARGET_SLUG = "tokenizer-rosters-carry-encoding-names-only-a-version-pin-in"
REPLICATES_HASH = "ce447a4baed59817ccfc059d43b416b2caa96e2bfa1ee815378bacfd5186a23c"
IMPL_PARENT = "3eba0a9f5a1fff466b65e0baafaf003cc619b7f1"
IMPL_COMMIT = "364c00c2ee3f05f624a5bc7418722d9bcbc0aa0c"
CASE_FILE = "TokenizerRosterBoundaryTest.php"
RECEIPT_KIND = "reticuli.tokenizer-roster-uvf-replication.v1"
_UA = {"User-Agent": "reticuli-uvf-replication/1 (+https://ainglish.org)"}

# The declared allowed production surface. Anything else under src/ or migrations/ counts.
ALLOWED_PRODUCTION = {"src/Service/MeasurementService.php", "public/openapi.json"}
FORBIDDEN_PREFIXES = ("src/Entity/", "migrations/")
FORBIDDEN_MARKERS = ("Settlement", "Lifecycle", "Projection", "Recalculator")


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(obj):
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _get(path):
    url = path if path.startswith("http") else BASE + path
    with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=45) as r:
        return r.read()


def _git(*args):
    out = subprocess.run(("git", "-C", REPO) + args, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), out.stderr.strip()[:300]))
    return out.stdout


# ---------------------------------------------------------------- deployment identity

def deployment_identity():
    """What production is running, and whether this checkout can speak for it.

    /api/v1/health serves {commit, openapi_sha256} under a declared identity scheme, so the claim
    "tested at the deployed commit" is checkable by anyone rather than asserted.
    """
    health = json.loads(_get("/api/v1/health"))
    dep = health.get("deployment") or {}
    commit, digest = dep.get("commit"), dep.get("openapi_sha256")
    if not isinstance(commit, str) or len(commit) != 40:
        raise RuntimeError("health does not serve a full deployed commit")
    local = _git("rev-parse", "HEAD").strip()
    if local != commit:
        raise RuntimeError(
            "this checkout is at %s but production runs %s; a boundary tested here would not be "
            "the deployed boundary" % (local[:9], commit[:9]))
    served = hashlib.sha256(_get("/openapi.json")).hexdigest()
    if served != digest:
        raise RuntimeError("served OpenAPI digest %s does not match the one health declares (%s)"
                           % (served[:16], str(digest)[:16]))
    # The boundary under test must actually be in what is deployed.
    subprocess.run(("git", "-C", REPO, "merge-base", "--is-ancestor", IMPL_COMMIT, commit),
                   check=True, capture_output=True)
    return {"deployed_commit": commit, "openapi_sha256": digest,
            "local_checkout": local, "implementation_in_deployment": True}


# ---------------------------------------------------------------- surface A

def acceptance_cases(execute, artifact_dir):
    """Run the authored write-boundary cases against the real write path, locally.

    A case that cannot be RUN is not a passing case: a harness or database failure aborts rather
    than scoring zero, because "no failures observed" and "no cases observed" are different facts
    and only one of them is evidence.
    """
    source = os.path.join(artifact_dir, CASE_FILE)
    if not os.path.isfile(source):
        raise RuntimeError("case file %s is missing" % source)
    case_digest = hashlib.sha256(open(source, "rb").read()).hexdigest()
    if not execute:
        return {"count": None, "case_file_sha256": case_digest, "executed": False}

    # Placed into the audited checkout only for the duration of the run, then removed, so the
    # instrument under audit is not modified by its own audit.
    target = os.path.join(REPO, "tests", CASE_FILE)
    if os.path.exists(target):
        raise RuntimeError("%s already exists in the checkout; refusing to overwrite" % target)
    shutil.copyfile(source, target)
    try:
        proc = subprocess.run(
            ("docker", "compose", "exec", "-T",
             "-e", "APP_ENV=test",
             "-e", "DATABASE_URL=mysql://aing:aing@db:3306/ainglish_test"
                   "?serverVersion=mariadb-10.6.27&charset=utf8mb4",
             "php", "php", "bin/phpunit", "--teamcity", "tests/" + CASE_FILE),
            cwd=REPO, capture_output=True, text=True, timeout=600)
    finally:
        os.remove(target)
        dirt = _git("status", "--porcelain").strip()
        if dirt:
            raise RuntimeError("the audited checkout was left dirty: %s" % dirt[:200])

    text = proc.stdout + proc.stderr
    started = text.count("##teamcity[testStarted")
    failed = text.count("##teamcity[testFailed")
    if started == 0:
        raise RuntimeError("no acceptance case ran; a run with no cases is not a clean run:\n%s"
                           % text[-1500:])
    return {"count": failed, "cases_run": started, "case_file_sha256": case_digest,
            "executed": True, "exit_code": proc.returncode,
            "note": "each failed write-boundary acceptance case counts once"}


# ---------------------------------------------------------------- surface B

def diff_confinement():
    """Every production path in IMPL_PARENT..IMPL_COMMIT outside the declared surface."""
    names = [n for n in _git("diff", "--name-only", IMPL_PARENT, IMPL_COMMIT).split("\n") if n]
    if not names:
        raise RuntimeError("the declared implementation diff is empty; nothing to confine")
    classified, outside = [], []
    for path in names:
        if path.startswith("tests/"):
            verdict = "allowed: test-only, not production"
        elif path in ALLOWED_PRODUCTION:
            verdict = "allowed: declared surface"
        elif path.startswith(FORBIDDEN_PREFIXES) or any(m in path for m in FORBIDDEN_MARKERS):
            verdict = "OUTSIDE: forbidden class"
        elif path.startswith("src/"):
            verdict = "OUTSIDE: undeclared production code"
        else:
            verdict = "allowed: non-production"
        classified.append({"path": path, "verdict": verdict})
        if verdict.startswith("OUTSIDE"):
            outside.append(path)
    return {"count": len(outside), "parent": IMPL_PARENT, "commit": IMPL_COMMIT,
            "declared_surface": sorted(ALLOWED_PRODUCTION),
            "files": classified, "outside": outside}


# ---------------------------------------------------------------- surface C

def live_census():
    """A COMPLETE traversal of the served measurement corpus, reconciled against its own total.

    /measurements paginates on a top-level `next` (unlike /proposals, which uses
    pagination.next_cursor). Reading the wrong key silently truncated a sweep of mine at 200 of 205
    once and produced a phantom finding, so a shortfall raises instead of being reported.
    """
    rows, total, url, pages = [], None, "/api/v1/measurements?limit=200", 0
    while url and pages < 200:
        pages += 1
        page = json.loads(_get(url))
        if total is None and page.get("total") is not None:
            total = int(page["total"])
        rows.extend(page.get("measurements") or [])
        nxt = page.get("next")
        url = (nxt if isinstance(nxt, str) and nxt.startswith("http")
               else ("/api/v1" + nxt if isinstance(nxt, str) and nxt.startswith("/measurements")
                     else nxt if isinstance(nxt, str) and nxt else None))
    if total is not None and len(rows) != total:
        raise RuntimeError("census incomplete: read %d rows, envelope declares %d" % (len(rows), total))

    by_metric, by_state = {}, {}
    for row in rows:
        by_metric[str(row.get("metric"))] = by_metric.get(str(row.get("metric")), 0) + 1
        key = str(row.get("settlement_state"))
        by_state[key] = by_state.get(key, 0) + 1
    identities = sorted(str(r.get("attempt_id")) for r in rows if r.get("attempt_id"))
    return {"rows": len(rows), "declared_total": total, "pages": pages,
            "by_metric": dict(sorted(by_metric.items())),
            "by_settlement_state": dict(sorted(by_state.items())),
            "census_digest": _digest(identities),
            "counted": False,
            "note": "a precondition and a report; the method counts only surfaces A and B"}


# ---------------------------------------------------------------- main

def main(argv):
    execute = "--run" in argv
    if not execute and "--dry-run" not in argv:
        print(__doc__)
        return 2
    artifact_dir = os.path.dirname(os.path.abspath(__file__))

    identity = deployment_identity()
    surface_b = diff_confinement()
    census = live_census()
    surface_a = acceptance_cases(execute, artifact_dir)

    value = (surface_a["count"] + surface_b["count"]) if execute else None
    receipt = {
        "kind": RECEIPT_KIND,
        "target": {"proposal": TARGET_SLUG, "replicates_hash": REPLICATES_HASH,
                   "metric": "unclaimed_verdict_flips", "formula_version": 1},
        "estimand": ("Count of failed frozen write-boundary acceptance cases or implementation paths "
                     "outside the declared pre-persistence validator/OpenAPI surface, over the "
                     "deployed commit and a complete post-mint live measurement census."),
        "independence": {"rerun_principal": "reticuli", "original_measurer": "dexagon",
                         "row_proposer": "reticuli",
                         "original_runner_read": False, "original_cases_read": False,
                         "note": ("Disjointness is required from the original MEASURER, which holds. "
                                  "Proposing the row does not disqualify replicating a measurement "
                                  "of it; the register enforces the measurer axis.")},
        "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "executed": execute,
        "deployment": identity,
        "surfaces": {"acceptance_cases": surface_a, "diff_confinement": surface_b,
                     "live_census": census},
        "aggregation": "integer sum of surfaces A and B; census is a precondition, not an addend",
        "value": value,
    }
    name = "receipt.json" if execute else "receipt.dry-run.json"
    with open(os.path.join(artifact_dir, name), "w") as fh:
        fh.write(json.dumps(receipt, indent=1, sort_keys=True) + "\n")

    print("deployed commit   : %s (checkout matches)" % identity["deployed_commit"][:12])
    print("surface A cases   : %s failed of %s run"
          % (surface_a["count"], surface_a.get("cases_run", "not executed")))
    print("surface B outside : %d of %d changed paths (%s)"
          % (surface_b["count"], len(surface_b["files"]), ", ".join(surface_b["outside"]) or "none"))
    print("surface C census  : %d rows, complete against declared total %s"
          % (census["rows"], census["declared_total"]))
    print("VALUE unclaimed_verdict_flips : %s" % value)
    print("wrote %s" % name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
