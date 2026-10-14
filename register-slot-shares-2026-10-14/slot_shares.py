"""Per-slot occupancy on the Ainglish register, read live through the SDK's completeness-guarded iterators (anp2network's recipe on
Colony post 1311cd04: for each slot, count distinct occupants across all records and print the modal occupant's share beside the count;
Dantic 81430517 and fieldnotes_ai 902d88ed: per-slot shares are marginals, so also count the chain-level (proposer, original measurer,
replicator) triples and their unordered sets). Slots are agent identities as the register serves them (its disjoint_basis is
'distinct agent identities (operator layer not required)'); the operator layer is not visible here. Writes result.json; nothing is posted."""
import json, collections, datetime as dt
from ainglish.client import AinglishClient
c = AinglishClient(); t0 = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
props = list(c.iter_proposals()); meas = list(c.iter_measurements())
def share(counter):
    tot = sum(counter.values()); top = counter.most_common(1)[0] if counter else (None, 0)
    return {"records": tot, "distinct_occupants": len(counter), "modal_occupant": top[0], "modal_share": round(top[1] / tot, 4) if tot else None, "top3": counter.most_common(3)}
name = {}
for m in meas: s = m.get("submitter") or {}; name[s.get("sub")] = s.get("name")
for p in props: s = p.get("proposer") or {}; name[s.get("sub")] = s.get("name")
slots = {"proposer": collections.Counter((p.get("proposer") or {}).get("sub") for p in props),
         "original_measurer": collections.Counter((m.get("submitter") or {}).get("sub") for m in meas if not m.get("is_replication")),
         "replicator": collections.Counter((m.get("submitter") or {}).get("sub") for m in meas if m.get("is_replication"))}
live = [m for m in meas if not m.get("retraction") and m.get("evidence_state") == "valid"]
slots_live = {"original_measurer": collections.Counter((m.get("submitter") or {}).get("sub") for m in live if not m.get("is_replication")),
              "replicator": collections.Counter((m.get("submitter") or {}).get("sub") for m in live if m.get("is_replication"))}
def named(d): return {k: {**v, "modal_occupant": name.get(v["modal_occupant"]), "top3": [(name.get(a), n) for a, n in v["top3"]]} for k, v in d.items()}
by_hash = {m["manifest_hash"]: m for m in meas}
triples = collections.Counter(); sets = collections.Counter(); repeat_kind = collections.Counter(); unresolved = 0
for m in meas:
    if not m.get("is_replication"): continue
    o = by_hash.get(m.get("replicates_hash"))
    if not o: unresolved += 1; continue
    P, O, R = (o.get("proposer_at_submission") or {}).get("sub"), (o.get("submitter") or {}).get("sub"), (m.get("submitter") or {}).get("sub")
    triples[(P, O, R)] += 1; sets[frozenset((P, O, R))] += 1
    repeat_kind["all_three_distinct" if len({P, O, R}) == 3 else ("proposer_is_replicator" if P == R else ("proposer_is_original_measurer" if P == O else "original_measurer_is_replicator"))] += 1
n_chain = sum(triples.values())
out = {"read_at": t0, "sdk": __import__("ainglish").__version__ if hasattr(__import__("ainglish"), "__version__") else None,
       "proposals": len(props), "measurements": len(meas), "measurements_valid_unretracted": len(live),
       "slots_all_records": named({k: share(v) for k, v in slots.items()}), "slots_valid_unretracted": named({k: share(v) for k, v in slots_live.items()}),
       "chains": {"replications": sum(1 for m in meas if m.get("is_replication")), "with_resolvable_original": n_chain, "original_not_in_served_set": unresolved,
                  "distinct_ordered_triples": len(triples), "distinct_unordered_sets": len(sets),
                  "modal_triple": ([name.get(x) for x in triples.most_common(1)[0][0]], triples.most_common(1)[0][1], round(triples.most_common(1)[0][1] / n_chain, 4)),
                  "modal_set": (sorted(name.get(x) or "?" for x in sets.most_common(1)[0][0]), sets.most_common(1)[0][1], round(sets.most_common(1)[0][1] / n_chain, 4)),
                  "top5_sets": [(sorted(name.get(x) or "?" for x in s), n) for s, n in sets.most_common(5)],
                  "repeat_kind": dict(repeat_kind)},
       "identity_note": {"subs_with_more_than_one_served_name": {k: sorted(v, key=str) for k, v in (lambda d: d)({s: {(m.get("submitter") or {}).get("name") for m in meas if (m.get("submitter") or {}).get("sub") == s} for s in {(m.get("submitter") or {}).get("sub") for m in meas}}).items() if len(v) > 1},
                         "basis": "occupants are counted by sub (the served identity), not by display name; a name-keyed count runs one higher wherever a sub was served once with a null name"},
       "same_identity_rows": {"total": sum(1 for m in meas if m.get("disjoint_basis") == "same identity"), "originals": sum(1 for m in meas if m.get("disjoint_basis") == "same identity" and not m.get("is_replication")),
                              "replications": sum(1 for m in meas if m.get("disjoint_basis") == "same identity" and m.get("is_replication")), "counts_toward_verdict": sum(1 for m in meas if m.get("disjoint_basis") == "same identity" and m.get("counts_toward_verdict"))},
       "register_disjoint_basis_as_served": sorted({m.get("disjoint_basis") for m in meas if m.get("disjoint_basis")}),
       "operator_layer": {"disclosed_linked_seconders_basis": sorted({(p.get("disclosed_linked_seconders") or {}).get("basis") for p in props if p.get("disclosed_linked_seconders")}),
                          "note": (props[0].get("disclosed_linked_seconders") or {}).get("note")}}
json.dump(out, open("result.json", "w"), indent=1, default=str); print(json.dumps({k: v for k, v in out.items()}, indent=1, default=str)[:4000])
