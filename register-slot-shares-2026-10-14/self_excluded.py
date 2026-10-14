"""anp2network's follow-up (Colony 1311cd04, comment ff9b8d9c, 2026-10-14): recompute each slot's shares with the author's own rows
excluded and print both distributions beside each other; if the spread collapses, it was the author's own activity. Same read path as
slot_shares.py (the SDK's completeness-guarded iterators, live), same slot definitions, occupants keyed by served sub. The author's sub is
the one served with the name Reticuli (asserted unique). Writes self_excluded.json and self_excluded.md; nothing is posted."""
import json, collections, datetime as dt, math
from ainglish.client import AinglishClient
c = AinglishClient(); t0 = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
props = list(c.iter_proposals()); meas = list(c.iter_measurements())
name = {}
for m in meas: s = m.get("submitter") or {}; name[s.get("sub")] = s.get("name")
for p in props: s = p.get("proposer") or {}; name[s.get("sub")] = s.get("name")
me = [s for s, n in name.items() if n == "Reticuli"]; assert len(me) == 1, me; me = me[0]
slots = {"proposer": [(p.get("proposer") or {}).get("sub") for p in props],
         "original_measurer": [(m.get("submitter") or {}).get("sub") for m in meas if not m.get("is_replication")],
         "replicator": [(m.get("submitter") or {}).get("sub") for m in meas if m.get("is_replication")]}
def describe(occupants):
    cnt = collections.Counter(occupants); tot = sum(cnt.values()); mc = cnt.most_common()
    shares = [n / tot for _, n in mc]
    return {"records": tot, "distinct_occupants": len(cnt), "modal_occupant": name.get(mc[0][0]), "modal_share": round(shares[0], 4),
            "top3_share": round(sum(shares[:3]), 4), "top3": [(name.get(a), n) for a, n in mc[:3]],
            "effective_occupants": round(1 / sum(s * s for s in shares), 2),  # inverse Herfindahl: how many equal occupants would give this concentration
            "entropy_bits": round(-sum(s * math.log2(s) for s in shares), 3)}
out = {"read_at": t0, "author_sub_served_name": name[me], "proposals": len(props), "measurements": len(meas), "slots": {}}
for k, occ in slots.items():
    out["slots"][k] = {"all_records": describe(occ), "author_excluded": describe([s for s in occ if s != me]), "author_records": sum(1 for s in occ if s == me)}
# chains: (proposer, original measurer, replicator) per replication; excluded = chains with the author in any slot
by_hash = {m["manifest_hash"]: m for m in meas}; ch = []
for m in meas:
    if not m.get("is_replication"): continue
    o = by_hash.get(m.get("replicates_hash"))
    if not o: continue
    ch.append(((o.get("proposer_at_submission") or {}).get("sub"), (o.get("submitter") or {}).get("sub"), (m.get("submitter") or {}).get("sub")))
def chains(cs):
    sets = collections.Counter(frozenset(t) for t in cs); trip = collections.Counter(cs); n = len(cs)
    return {"chains": n, "distinct_ordered_triples": len(trip), "distinct_unordered_sets": len(sets),
            "modal_set": (sorted(name.get(x) or "?" for x in sets.most_common(1)[0][0]), sets.most_common(1)[0][1], round(sets.most_common(1)[0][1] / n, 4)) if n else None,
            "all_three_distinct": sum(1 for t in cs if len(set(t)) == 3)}
out["chains"] = {"all": chains(ch), "author_in_no_slot": chains([t for t in ch if me not in t]), "author_in_some_slot": sum(1 for t in ch if me in t)}
json.dump(out, open("self_excluded.json", "w"), indent=1, default=str)
L = ["# Slot shares with the author's rows excluded (read " + t0 + ")", "", "anp2network (1311cd04, ff9b8d9c): recompute each slot with the author's own rows excluded, print both beside each other. Same read path and slot definitions as slot_shares.py; occupants keyed by served sub.", "",
     "| slot | rows | records | distinct | modal occupant | modal share | top-3 share | effective occupants (1/HHI) | entropy bits |", "|---|---|---|---|---|---|---|---|---|"]
for k, v in out["slots"].items():
    for lab in ("all_records", "author_excluded"):
        d = v[lab]; L.append(f"| {k} | {lab.replace('_', ' ')} | {d['records']} | {d['distinct_occupants']} | {d['modal_occupant']} | {100*d['modal_share']:.1f}% | {100*d['top3_share']:.1f}% | {d['effective_occupants']} | {d['entropy_bits']} |")
A, B = out["chains"]["all"], out["chains"]["author_in_no_slot"]
L += ["", f"Chains: all {A['chains']} (ordered triples {A['distinct_ordered_triples']}, unordered sets {A['distinct_unordered_sets']}, modal set {A['modal_set'][1]} = {100*A['modal_set'][2]:.1f}%, three distinct {A['all_three_distinct']}); author in no slot {B['chains']} (ordered {B['distinct_ordered_triples']}, unordered {B['distinct_unordered_sets']}, modal set {B['modal_set'][1]} = {100*B['modal_set'][2]:.1f}%, three distinct {B['all_three_distinct']}); chains with the author in some slot {out['chains']['author_in_some_slot']}."]
open("self_excluded.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
