"""Every figure for the ballot report, computed from ballots_all.json (pulled from the register's public API). Writes facts.json."""
import json, collections
B = json.load(open("ballots_all.json")); rows = B["rows"]; ME = "040b6f79-a867-46d4-8069-fd6143bd9e20"
def carriers(r):
    cc = (r.get("evidence_contract") or {}).get("claim_carrier") or []; return [x if isinstance(x, str) else x.get("metric") for x in cc]
def stances(r): return (r.get("verdict") or {}).get("metric_stances") or {}
def cstate(r):
    cc = carriers(r); st = stances(r)
    if not cc: return "none declared"
    s = [x for m in cc for x in (st.get(m) or ["absent"])]
    return "supports" if "supports" in s else "opposes" if "opposes" in s else "/".join(sorted(set(s)))
def last(r): return ((r.get("stage_history") or {}).get("transitions") or [{}])[-1]
lang = lambda r: r["kind"] != "protocol"
RAT = [r for r in rows.values() if r["stage"] == "ratified" and (r.get("ratified_at") or "") >= "2026-09-01"]
FAIL = [r for r in rows.values() if r["stage"] == "vote_failed"]
M = [r for r in rows.values() if r["stage"] in ("measured", "voted")]
legacy = [r for r in FAIL if "transition tracking began" in (last(r).get("detail") or "")]
clock = [r for r in FAIL if "no_supermajority" in (last(r).get("detail") or "")]
assert len(legacy) + len(clock) == len(FAIL)
helps = lambda rs: sum((r.get("verdict") or {}).get("assessment") == "helps" for r in rs)
token_only = lambda rs: sum((r.get("verdict") or {}).get("assessment") == "helps" and not any("supports" in (stances(r).get(m) or []) for m in stances(r) if m != "token_delta") for r in rs)
Mc = [r for r in M if carriers(r) == ["comprehension_accuracy_delta"]]
cs = collections.Counter(cstate(r) for r in Mc)
absent = [r for r in Mc if cstate(r) == "absent"]
cls = collections.Counter(); sett = collections.Counter()
for r in absent:
    ms = [m for m in r.get("measurements") or [] if m["metric"] == "comprehension_accuracy_delta" and not m.get("retraction") and m.get("evidence_state", "valid") == "valid"]
    o = [m for m in ms if not m.get("is_replication")]; rp = [m for m in ms if m.get("is_replication")]
    cls["no original" if not o else "original, no replication" if not rp else "replicated, none confirmed"] += 1
    for m in o: sett[m.get("settlement_state")] += 1
openb = sorted(({"id": r["public_id"], "slug": r["slug"], "closes": r["ballot_closure"]["closes_at"], "yes": r["ratification"]["tally"]["yes"], "no": r["ratification"]["tally"]["no"], "mine": r["proposer"]["sub"] == ME}
                for r in M if (r.get("ballot_closure") or {}).get("closes_at")), key=lambda x: x["closes"])
votes = collections.Counter(len((r.get("ratification") or {}).get("votes") or []) for r in M)
F = {"read_at": B["at"], "ratified_since_0901": len(RAT), "ratified_language": sum(lang(r) for r in RAT), "ratified_protocol": sum(not lang(r) for r in RAT),
     "ratified_language_by_0904": sum(lang(r) and r["ratified_at"] < "2026-09-05" for r in RAT), "ratified_language_after_0904": sorted(r["ratified_at"][:10] for r in RAT if lang(r) and r["ratified_at"] >= "2026-09-05"),
     "failed": len(FAIL), "failed_before_tracking": len(legacy), "failed_by_clock": len(clock), "failed_by_clock_first": min(last(r)["occurred_at"] for r in clock)[:10], "failed_by_clock_last": max(last(r)["occurred_at"] for r in clock)[:10],
     "helps_on_ratified_language": helps([r for r in RAT if lang(r)]), "helps_on_failed": helps(FAIL), "helps_token_only_on_failed": token_only(FAIL), "helps_token_only_on_ratified_language": token_only([r for r in RAT if lang(r)]),
     "failed_with_carrier_declared": sum(bool(carriers(r)) for r in FAIL), "failed_helps_with_carrier_not_supporting": sum((r.get("verdict") or {}).get("assessment") == "helps" and bool(carriers(r)) and cstate(r) != "supports" for r in FAIL),
     "ratified_language_with_carrier_declared": sum(bool(carriers(r)) for r in RAT if lang(r)), "ratified_language_with_carrier_supporting": sum(cstate(r) == "supports" for r in RAT if lang(r)),
     "waiting": len(M), "waiting_comprehension_carrier": len(Mc), "waiting_carrier_states": dict(cs), "waiting_absent_classes": dict(cls), "waiting_absent_original_states": dict(sett),
     "waiting_helps": helps(M), "waiting_votes_distribution": dict(sorted(votes.items())), "waiting_without_quorum": sum(1 for r in M if not (r.get("ballot_closure") or {}).get("closes_at")),
     "open_ballots": openb, "mine_failed": sum(r["proposer"]["sub"] == ME for r in FAIL), "mine_waiting": sum(r["proposer"]["sub"] == ME for r in M),
     "failed_helps_ids": sorted(r["public_id"] for r in FAIL if (r.get("verdict") or {}).get("assessment") == "helps")}
json.dump(F, open("facts.json", "w"), indent=1); print(json.dumps(F, indent=1))
