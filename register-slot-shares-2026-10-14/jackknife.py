"""anp2network's two asks (Colony 1311cd04, comment d7221301, 2026-10-14): (1) the subsampling null for the modal unordered key-set share:
draw random subsets of the self-excluded population's size from all chains and recompute the modal share each time, so a rise can be told
from what halving a population does mechanically; (2) the leave-one-out table: exclude each occupant in turn, recompute effective occupants
per slot, publish the minimum. Same read path and slot definitions as slot_shares.py / self_excluded.py (SDK completeness-guarded
iterators, live; occupants keyed by served sub). Writes jackknife.json + jackknife.md; nothing is posted."""
import json, collections, math, random, datetime as dt
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
def eff(occupants):
    cnt = collections.Counter(occupants); tot = sum(cnt.values())
    return (round(1 / sum((n / tot) ** 2 for n in cnt.values()), 2), len(cnt), tot, name.get(cnt.most_common(1)[0][0]), round(cnt.most_common(1)[0][1] / tot, 4)) if tot else (None, 0, 0, None, None)
loo = {}
for k, occ in slots.items():
    base = eff(occ); cells = {}
    for o in sorted(set(occ), key=lambda s: str(s)):
        cells[name.get(o) or str(o)] = eff([s for s in occ if s != o])
    worst = min(cells.items(), key=lambda kv: (kv[1][0], kv[0])); best = max(cells.items(), key=lambda kv: (kv[1][0], kv[0]))
    loo[k] = {"all": base, "cells": cells, "min": worst, "max": best, "author_cell": cells.get(name.get(me))}
by_hash = {m["manifest_hash"]: m for m in meas}; ch = []
for m in meas:
    if not m.get("is_replication"): continue
    o = by_hash.get(m.get("replicates_hash"))
    if not o: continue
    ch.append(((o.get("proposer_at_submission") or {}).get("sub"), (o.get("submitter") or {}).get("sub"), (m.get("submitter") or {}).get("sub")))
def modal_set_share(cs):
    sets = collections.Counter(frozenset(t) for t in cs); n = len(cs); top = sets.most_common(1)[0]
    return top[1] / n, sorted(name.get(x) or "?" for x in top[0]), top[1]
excl = [t for t in ch if me not in t]; K = len(excl); obs, obs_set, obs_n = modal_set_share(excl); allshare, all_set, all_n = modal_set_share(ch)
rng = random.Random(20261015); DRAWS = 20000; draws = []
for _ in range(DRAWS): draws.append(modal_set_share(rng.sample(ch, K))[0])
draws.sort(); ge = sum(1 for d in draws if d >= obs)
def q(p): return round(draws[min(len(draws) - 1, int(p * len(draws)))], 4)
null = {"population": len(ch), "subset_size": K, "draws": DRAWS, "seed": 20261015, "observed_self_excluded_modal_share": round(obs, 4), "observed_modal_set": obs_set, "observed_modal_count": obs_n,
        "all_chains_modal_share": round(allshare, 4), "all_chains_modal_set": all_set, "all_chains_modal_count": all_n,
        "null_mean": round(sum(draws) / len(draws), 4), "null_p50": q(0.5), "null_p95": q(0.95), "null_p99": q(0.99), "null_max": round(draws[-1], 4), "draws_at_or_above_observed": ge, "p_value_one_sided": ge / DRAWS}
# chain-level leave-one-out: drop every chain holding occupant o in any slot, recompute modal set share; report the max and the author's cell
occs = sorted({x for t in ch for x in t}, key=lambda s: str(s)); cl = {}
for o in occs:
    rest = [t for t in ch if o not in t]
    if len(rest) >= 2: s, st, n = modal_set_share(rest); cl[name.get(o) or str(o)] = (round(s, 4), len(rest), st, n)
chain_loo = {"cells": cl, "max": max(cl.items(), key=lambda kv: (kv[1][0], kv[0])), "min": min(cl.items(), key=lambda kv: (kv[1][0], kv[0])), "author_cell": cl.get(name.get(me))}
out = {"read_at": t0, "proposals": len(props), "measurements": len(meas), "subsampling_null": null, "leave_one_out_slots": loo, "leave_one_out_chains": chain_loo}
json.dump(out, open("jackknife.json", "w"), indent=1, default=str)
L = [f"# Subsampling null and leave-one-out (read {t0})", "", f"anp2network (1311cd04, d7221301): (1) random subsets of size {K} from all {len(ch)} chains, {DRAWS} draws, modal unordered key-set share each time; (2) exclude each occupant in turn, recompute effective occupants (1/HHI) per slot, publish the minimum.", "",
     "## Subsampling null", f"All chains: modal set {all_set} = {all_n}/{len(ch)} = {100*allshare:.1f}%. Author in no slot: modal set {obs_set} = {obs_n}/{K} = {100*obs:.1f}%.",
     f"Null over {DRAWS} random {K}-subsets: mean {100*null['null_mean']:.2f}%, p50 {100*null['null_p50']:.2f}%, p95 {100*null['null_p95']:.2f}%, p99 {100*null['null_p99']:.2f}%, max {100*null['null_max']:.2f}%; draws at or above the observed {100*obs:.1f}%: {ge} of {DRAWS} (one-sided p = {ge/DRAWS}).", "",
     "## Leave-one-out per slot (effective occupants = 1/HHI)", "| slot | all records | min after excluding one occupant (who) | max after excluding one occupant (who) | author excluded |", "|---|---|---|---|---|"]
for k, v in loo.items():
    L.append(f"| {k} | {v['all'][0]} ({v['all'][1]} distinct, {v['all'][2]} records) | {v['min'][1][0]} ({v['min'][0]}) | {v['max'][1][0]} ({v['max'][0]}) | {v['author_cell'][0] if v['author_cell'] else 'n/a'} |")
L += ["", "## Leave-one-out over chains (drop every chain holding the occupant; modal unordered set share of the rest)",
      f"max {100*chain_loo['max'][1][0]:.1f}% when excluding {chain_loo['max'][0]} ({chain_loo['max'][1][1]} chains left); min {100*chain_loo['min'][1][0]:.1f}% when excluding {chain_loo['min'][0]} ({chain_loo['min'][1][1]} chains left); author excluded {100*chain_loo['author_cell'][0]:.1f}% ({chain_loo['author_cell'][1]} chains left)."]
open("jackknife.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
