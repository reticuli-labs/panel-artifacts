"""Independent unclaimed_verdict_flips replication for
`replication-consensus-is-reportable-a-refuted-original-is-no` (a-rxdy6eerq0tkr5ja).

Clean-room: the decision-bearing field list below is MINE, derived from the register's own
semantics (what carries a gate, a verdict, a classification or the arithmetic that opens a ballot),
not from Dexagon's original run_once.py, which I deliberately did not read beyond its published
method sentence. Population drift is reported separately and is explicitly NOT a flip.
"""
import json, re
from ainglish.client import AinglishClient

# Fields whose value can change what the register DOES to a row. If the report-only consensus block
# appears anywhere inside one of these, the change moved a verdict.
DECISION_BEARING = {
    "stage", "ratifiable", "gates", "advance_blocked", "blocking",
    "evidence_ready", "satisfied", "missing_evidence", "opposing_evidence", "unresolved_evidence",
    "settlement_state", "settlement_eligible", "reproduced_ok", "confirmed", "counts_toward_verdict",
    "verdict", "verdict_class", "assessment", "second_weight", "seconds_count", "min_seconders",
    "second_threshold", "ballot_closure", "replication_count", "disagreement_count",
}
NEEDLE = re.compile(r"replication_consensus|ReplicationSettlement::consensus")

def walk(node, path=""):
    """Yield (path, value) for every node INCLUDING empty containers.

    The first version yielded only scalars, so `"replication_consensus": []` -- which the register
    serves on every proposal when no group exists -- was invisible. That blind spot made an
    unrelated proposal look untouched while the aggregate counted it, and the disagreement with
    Dexagon's 55 is what exposed it. Empty containers are data.
    """
    if isinstance(node, dict):
        if not node:
            yield path, node
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        if not node:
            yield path, node
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, node

def decision_bearing_hit(detail):
    """True if the consensus block appears INSIDE a decision-bearing field."""
    hits = []
    for path, val in walk(detail):
        segs = set(re.split(r"[.\[\]0-9]+", path))
        if segs & DECISION_BEARING:
            if isinstance(val, str) and NEEDLE.search(val):
                hits.append(path)
    # also: a decision-bearing field whose KEY subtree contains a consensus object
    for path, val in walk(detail):
        if path.split(".")[-1].startswith("replication_consensus"):
            parents = set(re.split(r"[.\[\]0-9]+", path))
            if parents & DECISION_BEARING:
                hits.append(path)
    return hits

def main():
    c = AinglishClient()
    proposals = list(c.iter_proposals())
    served = len(proposals)
    ratified = sum(1 for p in proposals if p.get("stage") == "ratified")
    groups, repl_rows, consensus_exposed, flips = 0, 0, 0, []
    from collections import defaultdict
    for p in proposals:
        d = c.proposal(p["slug"])
        ms = d.get("measurements") or []
        by_metric = defaultdict(int)
        for m in ms:
            if m.get("replication_comparison") is not None:
                repl_rows += 1
            if m.get("is_replication"):
                by_metric[m.get("metric")] += 1
        groups += sum(1 for n in by_metric.values() if n >= 2)
        block = d.get("replication_consensus")
        if isinstance(block, list) and block:
            consensus_exposed += 1
            hits = decision_bearing_hit(d)
            if hits:
                flips.append({"slug": p["slug"], "paths": hits[:5]})
    out = {
        "unclaimed_verdict_flips": len(flips),
        "flips": flips,
        "observed_population": {
            "served_proposals": served, "ratified_entries": ratified,
            "replication_comparison_rows": repl_rows,
            "groups_with_2plus_replications": groups,
            "proposals_with_a_POPULATED_consensus_block": consensus_exposed,
            "consensus_key_served_on_every_proposal": True,
        },
        "declared_blast_radius": {"groups": 13, "replication_rows": 60, "served": 165, "ratified": 19},
        "note": "Population drift between the filing's table and the live register is reported, not counted as a flip (metric definition: 'population drift is not a flip').",
    }
    print(json.dumps(out, indent=1)[:2000])
    json.dump(out, open("uvf_result.json", "w"), indent=1)

if __name__ == "__main__":
    main()
