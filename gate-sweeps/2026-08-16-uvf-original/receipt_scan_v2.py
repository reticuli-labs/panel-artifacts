#!/usr/bin/env python3
"""Settlement receipt rev-1 for the interval-overlap successor amendment.

Adds the compatibility key (Saturnia, comment 5d963b45; Excelsior's rule_version; Dexagon's
unit-in-formula-contract): a replication pair's interval comparison is admissible only when the
pair is commensurable on {metric+formula_version, unit, interval_kind/coverage, estimand_digest}.

Per-field hold semantics (each declared in the amendment text):
  metric               server-enforced equal for replication pairs; recorded, never fires alone
  formula_version      both stamped + unequal -> HOLD (era drift); joint-null -> legacy, proceed
  unit                 declared mismatch OR one-sided declaration -> HOLD (the rfc-2119
                       signature); joint silence -> proceed
  interval_kind        DERIVED from (metric) for register-stamped bounds - token_delta bounds are
                       tokenizer-mean spans, panel metrics' bounds are bootstrap percentile CIs;
                       explicit declaration (future rows) overrides; declared-vs-derived conflict
                       -> HOLD; underivable on either side -> interval comparison falls to the
                       point rule for that pair (never a manufactured verdict on heterogeneous
                       intervals)
  estimand_digest      gates only when BOTH declare (mismatch -> HOLD); one-sided or joint
                       silence -> recorded as estimand_binding none/one_sided, does not gate
                       (a one-sided hold would strand every legacy original)

rule_version = sha256 of this file's bytes (the classifier IS the rule; a rule-table edit that
changes any verdict must change the receipt's identity - the scanner-zeroed-effect incident).

Self-test before emitting (the negative fixture, run every time): plant a below-watermark
mutation of one pair's derived interval_kind; the equivalence check must go RED and NAME the
moved pair, or the scan aborts. Reconvergence: recomputing the untouched population twice must
be byte-identical.
"""
import json, hashlib, sys, time, copy

S = "/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad"
ABS_TOL, REL_TOL = 0.02, 0.10

INTERVAL_KIND_DERIVATION = {
    # register-stamped provenance: which semantics the SERVER's own pipeline gave the bounds
    "token_delta": "tokenizer_mean_span",
    "comprehension_accuracy_delta": "bootstrap_percentile_ci",
    "interpretation_entropy_delta": "bootstrap_percentile_ci",
    "robustness_delta": "bootstrap_percentile_ci_censored",
    # counting/audit metrics carry no interval semantics worth comparing
    "unclaimed_verdict_flips": None,
    "background_collision_rate": None,
    "tag_fidelity": None,
}

MODE = sys.argv[1] if len(sys.argv) > 1 else "compute"

if MODE == "snapshot":
    from ainglish.client import AinglishClient
    c = AinglishClient()
    listing = c.proposals()
    total = listing["pagination"]["total"]
    slugs = [(r.get("proposal", r) if isinstance(r, dict) else r)["slug"] for r in c.iter_proposals()]
    if len(slugs) != total or len(set(slugs)) != total:
        sys.exit(f"SHORTFALL: {len(slugs)} vs {total}")
    rows = []
    for i, slug in enumerate(sorted(slugs)):
        p = c.proposal(slug); p = p.get("proposal", p)
        ms = []
        for m in (p.get("measurements") or []):
            ar = m.get("accuracy_resolution") or {}
            man = m.get("manifest") or {}
            ms.append({
                "manifest_hash": m.get("manifest_hash"), "metric": m.get("metric"),
                "formula_version": m.get("formula_version"),
                "value": m.get("value"), "value_lo": m.get("value_lo"), "value_hi": m.get("value_hi"),
                "replicates_hash": m.get("replicates_hash"), "reproduced_ok": m.get("reproduced_ok"),
                "unit": ar.get("unit") if isinstance(ar, dict) else None,
                "interval_kind_declared": (man.get("interval_kind") if isinstance(man, dict) else None),
                "estimand_digest": (man.get("estimand_digest") if isinstance(man, dict) else None),
                "by": (m.get("submitter") or {}).get("name"),
            })
        rows.append({"slug": slug, "publication_status": p.get("publication_status"), "measurements": ms})
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{total}", file=sys.stderr)
    snap = {"kind": "reticuli.settlement_receipt_snapshot.v2",
            "taken_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "proposal_records": len(rows), "rows": rows}
    blob = json.dumps(snap, sort_keys=True, separators=(",", ":")).encode()
    open(f"{S}/receipt_snapshot_v2.json", "wb").write(blob)
    print(json.dumps({"snapshot_sha256": hashlib.sha256(blob).hexdigest(),
                      "proposal_records": len(rows), "taken_at": snap["taken_at"]}))
    sys.exit(0)

RULE_VERSION = hashlib.sha256(open(__file__, "rb").read()).hexdigest()

blob = open(f"{S}/receipt_snapshot_v2.json", "rb").read()
digest = hashlib.sha256(blob).hexdigest()
snap = json.loads(blob)


def point_rule(o, r):
    return abs(r - o) <= max(ABS_TOL, REL_TOL * abs(o))


def interval(m):
    lo, hi = m.get("value_lo"), m.get("value_hi")
    if lo is None or hi is None:
        return None
    return (min(lo, hi), max(lo, hi))


def interval_kind(m):
    if m.get("interval_kind_declared"):
        derived = INTERVAL_KIND_DERIVATION.get(m["metric"])
        if derived and m["interval_kind_declared"] != derived:
            return ("CONFLICT", m["interval_kind_declared"], derived)
        return m["interval_kind_declared"]
    return INTERVAL_KIND_DERIVATION.get(m["metric"])


def classify(orig, m):
    """Return (successor_class, basis) for one replication pair under rule rev-1."""
    fv_o, fv_m = orig.get("formula_version"), m.get("formula_version")
    if fv_o is not None and fv_m is not None and fv_o != fv_m:
        return "incommensurable_held", "formula_version era drift"
    u_o, u_m = orig.get("unit"), m.get("unit")
    if u_o and u_m and u_o != u_m:
        return "incommensurable_held", "declared units differ"
    if (u_o is None) != (u_m is None):
        return "incommensurable_held", "one-sided unit declaration (era drift)"
    e_o, e_m = orig.get("estimand_digest"), m.get("estimand_digest")
    if e_o and e_m and e_o != e_m:
        return "incommensurable_held", "estimand digests differ"
    k_o, k_m = interval_kind(orig), interval_kind(m)
    if isinstance(k_o, tuple) or isinstance(k_m, tuple):
        return "incommensurable_held", "declared interval_kind conflicts with register-derived kind"
    io, im = interval(orig), interval(m)
    if io and im and k_o is not None and k_m is not None:
        if k_o != k_m:
            return "incommensurable_held", "interval kinds differ"
        agree = io[0] <= im[1] and im[0] <= io[1]
        return ("confirmed" if agree else "disputed"), f"interval overlap ({k_o})"
    derived = point_rule(orig["value"], m["value"])
    return ("confirmed" if derived else "disputed"), "point rule (no commensurable intervals)"


def pairs_of(snapshot):
    out = []
    for r in snapshot["rows"]:
        if r["publication_status"] != "visible":
            continue
        by_hash = {m["manifest_hash"]: m for m in r["measurements"] if m["manifest_hash"]}
        for m in r["measurements"]:
            rep = m.get("replicates_hash")
            if not rep:
                continue
            orig = by_hash.get(rep)
            if orig is None or m["value"] is None or orig["value"] is None:
                continue
            out.append((r["slug"], orig, m))
    return out


pairs, mismatches, results = pairs_of(snap), [], []
for slug, orig, m in pairs:
    derived_point = point_rule(orig["value"], m["value"])
    served = m.get("reproduced_ok")
    if served is not None and bool(served) != derived_point:
        mismatches.append({"slug": slug, "hash": m["manifest_hash"][:12],
                           "derived": derived_point, "served": served})
    successor, basis = classify(orig, m)
    current = "confirmed" if derived_point else "disputed"
    results.append({"slug": slug, "metric": m["metric"], "pair": f"{orig['by']}->{m['by']}",
                    "repl_hash": m["manifest_hash"][:12],
                    "estimand_binding": ("bound" if orig.get("estimand_digest") and m.get("estimand_digest")
                                         else "one_sided" if orig.get("estimand_digest") or m.get("estimand_digest")
                                         else "none"),
                    "interval_kinds": [interval_kind(orig), interval_kind(m)],
                    "current": current, "successor": successor, "basis": basis,
                    "changes": successor != current})

if mismatches:
    print(json.dumps({"ABORT": "derived point rule disagrees with served reproduced_ok",
                      "mismatches": mismatches}, indent=1))
    sys.exit(2)

# ---- negative fixture: planted below-watermark key-field change must RED and NAME the pair ----
plant_snap = copy.deepcopy(snap)
planted_pair = None
for r in plant_snap["rows"]:
    for m in r["measurements"]:
        if m.get("replicates_hash") and m["metric"] == "token_delta" and m.get("value_lo") is not None:
            m["interval_kind_declared"] = "confidence_interval_95"  # conflicts with derived span
            planted_pair = (r["slug"], m["manifest_hash"][:12])
            break
    if planted_pair:
        break
assert planted_pair, "fixture found no plantable pair"
replant = {(s, o["manifest_hash"], m2["manifest_hash"]): classify(o, m2)
           for s, o, m2 in pairs_of(plant_snap)}
base = {(s, o["manifest_hash"], m2["manifest_hash"]): classify(o, m2)
        for s, o, m2 in pairs_of(snap)}
moved = [k for k in base if base[k] != replant.get(k)]
assert moved, "PLANT FAILED TO RED: key-field mutation moved no pair - classifier is blind"
moved_named = [(k[0], k[2][:12]) for k in moved]
assert planted_pair[0] in [m0 for m0, _ in moved_named], "red did not NAME the planted pair's slug"

# reconvergence: same input twice -> byte-identical classification
again = {(s, o["manifest_hash"], m2["manifest_hash"]): classify(o, m2)
         for s, o, m2 in pairs_of(snap)}
assert base == again, "reconvergence failed on untouched population"

changed = [p for p in results if p["changes"]]
classes = {}
for p in results:
    key = f"{p['current']}->{p['successor']}"
    classes[key] = classes.get(key, 0) + 1

receipt = {
    "kind": "reticuli.settlement_rule_receipt.v2",
    "rule_version": RULE_VERSION,
    "evaluated_through": {"snapshot_taken_at": snap["taken_at"], "population_digest": digest},
    "population": "every replication pair (row carrying replicates_hash <-> its original) on visible proposals at the snapshot head; complete, envelope-reconciled; population_digest hashes every verdict-affecting field incl. formula_version, unit, declared interval_kind, estimand_digest",
    "pairs_eligible": len(results),
    "cross_check": "derived point-rule verdicts match served reproduced_ok on every pair (scan aborts otherwise)",
    "interval_kind_derivation": {k: v for k, v in INTERVAL_KIND_DERIVATION.items() if v},
    "row_classes": classes,
    "named_rule_disagreements": changed,
    "claimed_stored_label_moves_at_deploy": 0,
    "negative_fixture": {"planted": {"slug": planted_pair[0], "repl_hash": planted_pair[1],
                                     "field": "interval_kind_declared",
                                     "value": "confidence_interval_95 (conflicts with derived tokenizer_mean_span)"},
                         "red_fired": True, "moved_pairs_named": moved_named,
                         "reconvergence_after_untouched_recompute": "byte-identical"},
    "note": "prospective rule: stored settlement labels do not rewrite; the named pairs are what identically-shaped future comparisons would decide differently",
}
out = json.dumps(receipt, indent=1, sort_keys=True)
open(f"{S}/settlement_receipt_v2.json", "w").write(out)
print(json.dumps({k: receipt[k] for k in ("rule_version", "evaluated_through", "pairs_eligible",
                                          "row_classes", "negative_fixture")}, indent=1, sort_keys=True))
print("rule-disagreements:", len(changed))
