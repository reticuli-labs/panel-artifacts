#!/usr/bin/env python3
"""Re-derive the token_delta reproducibility census from the live register.

Sweeps EVERY proposal -- deliberately no pre-filter. An earlier version of this selected proposals
whose `evidence_readiness` mentioned token_delta, which silently dropped 60% of the population
(rows on proposals with a null evidence_contract, including the two that prompted the study).
"""
import collections, json, time
from ainglish.client import AinglishClient

ORIGINAL_STATES = ("confirmed", "disputed", "confirmed_contested", "awaiting", "voided_by_submitter")
RERUN_STATES = ("confirmed", "disputed", "confirmed_contested")

def sweep():
    c = AinglishClient()
    out = {}
    for p in c.iter_proposals():
        for attempt in range(4):
            try:
                full = c.proposal(p["slug"])
                ms = [m for m in (full.get("measurements") or [])
                      if m.get("metric") == "token_delta" and m.get("value") is not None]
                if ms:
                    out[p["slug"]] = [{"value": m["value"], "hash": m.get("manifest_hash"),
                                       "models": m.get("panel_models"), "settle": m.get("settlement_state"),
                                       "disagree": m.get("disagreement_count")} for m in ms]
                break
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    time.sleep(6); continue
                break
    return out

def report(d):
    rows = [m for v in d.values() for m in v]
    st = collections.Counter((m.get("settle") or "replication") for m in rows)
    rerun = [m for m in rows if m.get("settle") in RERUN_STATES]
    with_dis = [m for m in rerun if (m.get("disagree") or 0) >= 1]
    # Two independent routes to the same set; if they diverge the tally is wrong.
    assert len(with_dis) == st["disputed"] + st["confirmed_contested"]
    print(f"rows {len(rows)} | originals {sum(st[k] for k in ORIGINAL_STATES)} | replications {st['replication']}")
    print(f"re-run originals {len(rerun)}: >=1 disagreement {len(with_dis)} "
          f"({100*len(with_dis)/len(rerun):.0f}%), deadlocked {st['disputed']} "
          f"({100*st['disputed']/len(rerun):.0f}%), clean {st['confirmed']}")

if __name__ == "__main__":
    report(sweep())
