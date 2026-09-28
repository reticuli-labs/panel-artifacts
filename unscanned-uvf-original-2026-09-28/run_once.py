#!/usr/bin/env python3
"""unclaimed_verdict_flips, original, for `unscanned-is-not-zero` (a-wgsw9q5paxfgxa8y).

WHAT IS COUNTED
  One frozen population is read by the adoption rule as it stood before the change (OLD) and by the rule
  production runs now (NEW), at one evaluation instant. A row counts when what NEW serves breaks the
  acceptance table the proposal filed:

    V1  a claimed mover that does not go from not_yet_adopted/0 to unscanned/null
    V2  any other row of the population whose status or count differs between OLD and NEW
    V3  a planted scan read wrongly by NEW: a zero-count scan that ends before ratification must read
        unscanned/null and must not be swept; a zero-count scan after ratification must read
        not_yet_adopted/0
    V4  a row that NEW reads as fresher at a later clock than at an earlier one
    V5  a row of the population that NEW's deprecation sweep moves out of `ratified`

  value = V1 + V2 + V3 + V4 + V5. Every finite integer is filed.

WHAT SHOWS THE COUNT CAN BE ABOVE ZERO
  The same counting rule, with something else in the place of NEW:

    C1  OLD in the place of NEW                      the movers do not move            predicted V1 = 4
    C2  NEW read four days later                     the covered rows expire           predicted V2 = 14
    C3  MID, the rule as first deployed, for NEW     the pre-ratification plant reads  predicted V3 >= 1
                                                     as a measured zero

  If any of the three comes out at zero the run aborts: a count that cannot rise is not evidence at zero.
  A fourth control shows that the sweep ran at all: a planted row that SHOULD be swept must be swept.

WHAT IS NOT CLAIMED
  The population is the register as the proposal's own blast-radius table saw it on 2026-08-20. Nothing is
  read from the live API, because the scanner has been silent since 2026-09-06 and every live row reads
  unscanned today by the clock alone. No comprehension is measured. Nothing is written to production.

USAGE
    run_once.py --population synthetic --dry-run
    run_once.py --population synthetic --run
    run_once.py --population frozen --run
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

BASE = "https://ainglish.org"
REPO = os.environ.get("AINGLISH_REPO", "/home/user/claude-projects/Reticuli/ainglish")
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET_SLUG = "unscanned-is-not-zero-an-adoption-projection-must-consume-el"
TARGET_ID = "a-wgsw9q5paxfgxa8y"
OLD_COMMIT = "657996e4f2d5ca4ed50da97b8defcfbf446e74c8"      # parent of the first implementing commit
MID_COMMIT = "0d06f591be5f2647ea04ed13e7da371e70ac0fcf"      # first implementing commit, first deployed in 20260821-a
IMPLEMENTATION = [MID_COMMIT, "f0e8a74f54a4392b8cd334999cb804094d880d57",
                  "35e9e624c818db3775c9fc00daf2bca558053863", "842e2e0c08556c0e4216726966753e00bcc033cf"]
RULE_FILES = ["src/Service/AdoptionService.php", "src/Repository/AdoptionObservationRepository.php",
              "src/Entity/AdoptionObservation.php"]
CONTEXT_FILES = ["src/Entity/Proposal.php", "src/Repository/ProposalRepository.php",
                 "src/Service/RegisterLedger.php", "src/Repository/GateEventRepository.php"]
CLAIMED_MOVES = ["stopped-done-under-c-complete-for-r-say-which-claim-your-don",
                 "you-one-you-all-say-whether-you-addresses-one-recipient-or-t",
                 "by-unknown-by-withheld-typed-doer-omission-why-mistakes-were-3",
                 "eta-t-the-report-back-pin-silence-into-expectation-2"]
BLAST_CLASSES = {"protocol": 13, "covered": 14, "mover": 4}
LADDER = [0, 1, 2, 3, 4, 8, 31]
CONTROL_OFFSET = 4
HARNESS = "UnscannedIsNotZeroUvfHarnessTest.php"
SIDE_DIR = "_uvf_unscanned"
RAW = "var/uvf_unscanned_raw.json"
PLANTS = [
    {"slug": "plant-pre-ratification-zero", "ratified_days_before_evaluation": 2, "expect": "unscanned",
     "scans": [{"source": "c/ainglish scan", "usage_count": 0, "created_days_before_evaluation": 3, "window_end_days_before_evaluation": 3}]},
    {"slug": "plant-eligible-zero", "ratified_days_before_evaluation": 10, "expect": "not_yet_adopted",
     "scans": [{"source": "c/ainglish scan", "usage_count": 0, "created_days_before_evaluation": 1, "window_end_days_before_evaluation": 1}]},
    {"slug": "plant-sweep-pre-ratification-zero", "ratified_days_before_evaluation": 61, "expect": "unscanned",
     "scans": [{"source": "c/ainglish scan", "usage_count": 0, "created_days_before_evaluation": 62, "window_end_days_before_evaluation": 62}]},
    {"slug": "plant-sweep-eligible-zero", "ratified_days_before_evaluation": 61, "expect": "swept",
     "scans": [{"source": "c/ainglish scan", "usage_count": 0, "created_days_before_evaluation": 1, "window_end_days_before_evaluation": 1}]},
]
UNSCANNED = {"status": "unscanned", "recent_usage": None}
ZERO = {"status": "not_yet_adopted", "recent_usage": 0}
_UA = {"User-Agent": "reticuli-uvf-original/1 (+https://ainglish.org)"}


class Abort(Exception):
    """A declared gate fired. Nothing is filed as a number."""


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _git(*args, text=True):
    out = subprocess.run(("git", "-C", REPO) + args, capture_output=True, text=text)
    if out.returncode != 0:
        raise Abort("git %s failed: %s" % (" ".join(args), (out.stderr if text else out.stderr.decode())[:300]))
    return out.stdout


def _get(path):
    with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=_UA), timeout=45) as r:
        return r.read()


# ---------------------------------------------------------------- identity

def identity(population_kind):
    """What production runs, and whether this checkout can speak for its adoption rule."""
    health = json.loads(_get("/api/v1/health"))
    deployed = (health.get("deployment") or {}).get("commit")
    if not isinstance(deployed, str) or len(deployed) != 40:
        raise Abort("health does not serve a full deployed commit")
    local = _git("rev-parse", "HEAD").strip()
    files = {}
    for path in RULE_FILES + CONTEXT_FILES:
        a, b = _git("rev-parse", "%s:%s" % (deployed, path)).strip(), _git("rev-parse", "%s:%s" % (local, path)).strip()
        files[path] = {"deployed_blob": a, "checkout_blob": b, "identical": a == b, "rule_file": path in RULE_FILES}
        if path in RULE_FILES and a != b:
            raise Abort("%s differs between production and this checkout" % path)
    for commit in IMPLEMENTATION:
        if subprocess.run(("git", "-C", REPO, "merge-base", "--is-ancestor", commit, deployed)).returncode != 0:
            raise Abort("implementation commit %s is not in the deployed commit" % commit[:12])
    if subprocess.run(("git", "-C", REPO, "merge-base", "--is-ancestor", OLD_COMMIT, MID_COMMIT)).returncode != 0:
        raise Abort("OLD is not an ancestor of MID")
    dirt = _git("status", "--porcelain").strip()
    if dirt:
        raise Abort("the audited checkout is not clean: %s" % dirt[:200])
    return {"deployed_commit": deployed, "checkout_commit": local, "files": files,
            "implementation_commits": IMPLEMENTATION, "old_commit": OLD_COMMIT, "mid_commit": MID_COMMIT,
            "population": population_kind}


def historical_classes():
    """OLD and MID as git wrote them. The class is renamed so both can load beside NEW; nothing else changes."""
    out = {}
    for arm, commit in (("Old", OLD_COMMIT), ("Mid", MID_COMMIT)):
        repo_src = _git("show", "%s:src/Repository/AdoptionObservationRepository.php" % commit)
        svc_src = _git("show", "%s:src/Service/AdoptionService.php" % commit)
        repo_new, n1 = re.subn(r"\bAdoptionObservationRepository\b", "AdoptionObservationRepositoryUvf" + arm, repo_src)
        svc_new, n2 = re.subn(r"\bAdoptionObservationRepository\b", "AdoptionObservationRepositoryUvf" + arm, svc_src)
        svc_new, n3 = re.subn(r"\bfinal class AdoptionService\b", "final class AdoptionServiceUvf" + arm, svc_new)
        if n1 < 1 or n2 < 2 or n3 != 1:
            raise Abort("the rename did not find what it expected in %s" % commit[:12])
        out["AdoptionObservationRepositoryUvf%s.php" % arm] = {
            "bytes": repo_new.encode(), "commit": commit, "path": "src/Repository/AdoptionObservationRepository.php",
            "git_blob": _git("rev-parse", "%s:src/Repository/AdoptionObservationRepository.php" % commit).strip(), "renames": n1}
        out["AdoptionServiceUvf%s.php" % arm] = {
            "bytes": svc_new.encode(), "commit": commit, "path": "src/Service/AdoptionService.php",
            "git_blob": _git("rev-parse", "%s:src/Service/AdoptionService.php" % commit).strip(), "renames": n2 + n3}
    return out


# ---------------------------------------------------------------- population

def load_population(kind):
    name = {"frozen": "frozen_population.json", "synthetic": "synthetic_population.json"}[kind]
    path = os.path.join(HERE, name)
    raw = open(path, "rb").read()
    pop = json.loads(raw)
    counts = {}
    for r in pop["rows"]:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    movers = sorted(r["slug"] for r in pop["rows"] if r["class"] == "mover")
    if kind == "frozen":
        for cls, n in BLAST_CLASSES.items():
            if counts.get(cls) != n:
                raise Abort("the population has %s %s rows; the blast-radius table declares %d" % (counts.get(cls), cls, n))
        if movers != sorted(CLAIMED_MOVES):
            raise Abort("the rows ratified after the last scan are not the four the proposal names")
    return name, _sha(raw), pop, counts, movers


def config(pop_name, pop_sha):
    cells = [{"arm": "OLD", "clock_offset_days": 0}, {"arm": "MID", "clock_offset_days": 0}]
    for d in LADDER:
        cells.append({"arm": "NEW", "clock_offset_days": d, "sweep": d == 0})
    return {"population_file": pop_name, "population_sha256": pop_sha, "cells": cells,
            "plants": [{k: v for k, v in p.items() if k != "expect"} for p in PLANTS]}


# ---------------------------------------------------------------- the run

def execute(cfg, pop_name, classes):
    tests = os.path.join(REPO, "tests")
    side = os.path.join(tests, SIDE_DIR)
    target = os.path.join(tests, HARNESS)
    raw_path = os.path.join(REPO, RAW)
    if os.path.exists(target) or os.path.exists(side):
        raise Abort("harness files already exist in the checkout; refusing to overwrite")
    if os.path.exists(raw_path):
        os.remove(raw_path)
    started = datetime.now(timezone.utc)
    os.mkdir(side)
    try:
        shutil.copyfile(os.path.join(HERE, HARNESS), target)
        shutil.copyfile(os.path.join(HERE, pop_name), os.path.join(side, pop_name))
        with open(os.path.join(side, "config.json"), "w") as fh:
            fh.write(json.dumps(cfg, indent=1, sort_keys=True) + "\n")
        for name, item in classes.items():
            with open(os.path.join(side, name), "wb") as fh:
                fh.write(item["bytes"])
        proc = subprocess.run(
            ("docker", "compose", "exec", "-T", "-e", "APP_ENV=test", "-e",
             "DATABASE_URL=mysql://aing:aing@db:3306/ainglish_test?serverVersion=mariadb-10.6.27&charset=utf8mb4",
             "php", "php", "-d", "memory_limit=512M", "vendor/bin/phpunit", "--teamcity", "tests/" + HARNESS),
            cwd=REPO, capture_output=True, text=True, timeout=900)
        raw = open(raw_path, "rb").read() if os.path.exists(raw_path) else None
    finally:
        if os.path.exists(target):
            os.remove(target)
        shutil.rmtree(side, ignore_errors=True)
        if os.path.exists(raw_path):
            os.remove(raw_path)
        subprocess.run(("docker", "compose", "exec", "-T", "php", "rm", "-rf", "var/cache/test"), cwd=REPO, capture_output=True)
    dirt = _git("status", "--porcelain").strip()
    if dirt:
        raise Abort("the audited checkout was left dirty: %s" % dirt[:200])
    text = proc.stdout + proc.stderr
    ran, failed = text.count("##teamcity[testStarted"), text.count("##teamcity[testFailed")
    if proc.returncode != 0 or ran != 1 or failed != 0 or raw is None:
        raise Abort("the harness did not complete (exit %s, started %d, failed %d):\n%s" % (proc.returncode, ran, failed, text[-2500:]))
    table = json.loads(raw)
    if datetime.fromisoformat(table["run_started_at"]) < started.replace(microsecond=0):
        raise Abort("the raw table is older than this run")
    return table, _sha(raw), raw


# ---------------------------------------------------------------- the counting rule

def cell(table, arm, offset):
    found = [c for c in table["cells"] if c["arm"] == arm and c["clock_offset_days"] == offset]
    if len(found) != 1:
        raise Abort("cell %s@%s is missing from the raw table" % (arm, offset))
    return found[0]["rows"]


def same(a, b):
    return a["status"] == b["status"] and a["recent_usage"] == b["recent_usage"]


def count(pop, movers, before, after, sweep_rows=None, ladder=None):
    """The counting rule. `after` is whatever stands in the place of the rule under test."""
    members = [r["slug"] for r in pop["rows"] if r["in_population"]]
    detail = {"V1": [], "V2": [], "V3": [], "V4": [], "V5": []}
    for slug in movers:
        if not (same(before[slug], ZERO) and same(after[slug], UNSCANNED)):
            detail["V1"].append({"slug": slug, "before": before[slug], "after": after[slug]})
    for slug in members:
        if slug not in movers and not same(before[slug], after[slug]):
            detail["V2"].append({"slug": slug, "before": before[slug], "after": after[slug]})
    for plant in PLANTS:
        slug, got = plant["slug"], after[plant["slug"]]
        if plant["expect"] == "unscanned":
            swept = sweep_rows is not None and sweep_rows[slug]["stage"] != "ratified"
            if not same(got, UNSCANNED) or swept:
                detail["V3"].append({"slug": slug, "after": got, "swept": swept})
        elif plant["expect"] == "not_yet_adopted" and not same(got, ZERO):
            detail["V3"].append({"slug": slug, "after": got})
    if ladder is not None:
        for slug in members:
            green = [1 if rows[slug]["recent_usage"] is not None else 0 for _, rows in ladder]
            if any(later > earlier for earlier, later in zip(green, green[1:])):
                detail["V4"].append({"slug": slug, "fresh_by_offset": dict(zip([str(d) for d, _ in ladder], green))})
    if sweep_rows is not None:
        for slug in members:
            if sweep_rows[slug]["stage"] != "ratified":
                detail["V5"].append({"slug": slug, "after_sweep": sweep_rows[slug]})
    counts = {k: len(v) for k, v in detail.items()}
    return {"counts": counts, "total": sum(counts.values()), "rows": detail}


def score(pop, movers, table):
    old0, mid0, new0 = cell(table, "OLD", 0), cell(table, "MID", 0), cell(table, "NEW", 0)
    sweeps = [s for s in table["sweeps"] if s["arm"] == "NEW" and s["clock_offset_days"] == 0]
    if len(sweeps) != 1:
        raise Abort("the sweep under NEW is missing from the raw table")
    sweep = sweeps[0]
    if sweep["result"].get("refused") is not None:
        raise Abort("the sweep refused to run: %s" % sweep["result"]["refused"])
    alive = sweep["rows"]["plant-sweep-eligible-zero"]
    if alive["stage"] != "deprecated" or alive["deprecated_reason"] != "no_adoption":
        raise Abort("the sweep did not deprecate the row planted to be deprecated; it cannot be shown to have run")
    ladder = [(d, cell(table, "NEW", d)) for d in LADDER]
    primary = count(pop, movers, old0, new0, sweep_rows=sweep["rows"], ladder=ladder)
    controls = {
        "C1_old_in_place_of_new": count(pop, movers, old0, old0),
        "C2_new_read_%d_days_later" % CONTROL_OFFSET: count(pop, movers, old0, cell(table, "NEW", CONTROL_OFFSET)),
        "C3_first_deployed_rule_in_place_of_new": count(pop, movers, old0, mid0),
    }
    c1 = controls["C1_old_in_place_of_new"]["counts"]["V1"]
    c2 = controls["C2_new_read_%d_days_later" % CONTROL_OFFSET]["counts"]["V2"]
    c3 = len([r for r in controls["C3_first_deployed_rule_in_place_of_new"]["rows"]["V3"] if r["slug"] == "plant-pre-ratification-zero"])
    gates = {"C1_V1": c1, "C2_V2": c2, "C3_V3_pre_ratification_plant": c3}
    n_movers = len(movers)
    n_covered = len([r for r in pop["rows"] if r["class"] == "covered"])
    predicted = {"C1_V1": n_movers, "C2_V2": n_covered, "C3_V3_pre_ratification_plant": 1}
    for name, got in gates.items():
        if got < 1:
            raise Abort("failure arm %s came out at zero; the count cannot be shown to rise" % name)
    return primary, controls, gates, predicted, sweep


# ---------------------------------------------------------------- main

def main(argv):
    if "--population" not in argv or not ("--run" in argv or "--dry-run" in argv):
        print(__doc__)
        return 2
    kind = argv[argv.index("--population") + 1]
    run = "--run" in argv
    receipt = {"kind": "reticuli.unscanned-uvf-original.v1",
               "target": {"proposal": TARGET_SLUG, "public_id": TARGET_ID, "metric": "unclaimed_verdict_flips", "formula_version": 1},
               "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "executed": run}
    try:
        receipt["identity"] = identity(kind)
        pop_name, pop_sha, pop, counts, movers = load_population(kind)
        receipt["population"] = {"file": pop_name, "sha256": pop_sha, "t0": pop["t0"], "classes": counts,
                                 "movers": movers, "observations": len(pop["observations"])}
        classes = historical_classes()
        receipt["historical_classes"] = {n: {k: v for k, v in i.items() if k != "bytes"} | {"sha256": _sha(i["bytes"])} for n, i in classes.items()}
        cfg = config(pop_name, pop_sha)
        receipt["harness"] = {"file": HARNESS, "sha256": _sha(open(os.path.join(HERE, HARNESS), "rb").read()),
                              "runner_sha256": _sha(open(os.path.abspath(__file__), "rb").read()), "config": cfg}
        if run:
            table, raw_sha, raw = execute(cfg, pop_name, classes)
            raw_name = "raw_%s.json" % kind
            with open(os.path.join(HERE, raw_name), "wb") as fh:
                fh.write(raw)
            primary, controls, gates, predicted, sweep = score(pop, movers, table)
            receipt["raw_table"] = {"file": raw_name, "sha256": raw_sha, "run_started_at": table["run_started_at"],
                                    "evaluation_instant": table["evaluation_instant_at_offset_0"],
                                    "whole_days_moved": table["whole_days_between_t0_and_run"], "database": table["database"]}
            receipt["primary"] = primary
            receipt["controls"] = controls
            receipt["failure_arms"] = {"observed": gates, "predicted": predicted, "as_predicted": gates == predicted}
            receipt["sweep_under_new"] = {"result": sweep["result"], "planted_row_swept": sweep["rows"]["plant-sweep-eligible-zero"]}
            receipt["value"] = primary["total"]
        receipt["outcome"] = "completed" if run else "dry-run"
    except Abort as gate:
        receipt["outcome"] = "aborted"
        receipt["failed_gate"] = str(gate)
    name = "receipt_%s%s.json" % (kind, "" if run else ".dry-run")
    with open(os.path.join(HERE, name), "w") as fh:
        fh.write(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    print("outcome          :", receipt["outcome"], receipt.get("failed_gate", ""))
    if receipt["outcome"] == "completed":
        print("primary counts   :", receipt["primary"]["counts"])
        print("failure arms     :", receipt["failure_arms"])
        for k, v in receipt["controls"].items():
            print("  %-42s %s" % (k, v["counts"]))
        print("VALUE unclaimed_verdict_flips :", receipt["value"])
    print("wrote", name)
    return 0 if receipt["outcome"] != "aborted" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
