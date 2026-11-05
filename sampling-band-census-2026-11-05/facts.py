"""Bind every number for the census post to dl/census.json (and the manifests for the single-pair rows). Pure; writes dl/facts.json."""
import json, os, time, statistics
from collections import Counter
os.chdir(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open('dl/census.json')); rows = C['rows']; per_o = C['per_original']; M = json.load(open('dl/measurements_slim.json'))
F = {'facts_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'read_at': C['read_at'], 'z': C['z']}
assert len(rows) == 210 and len(per_o) == 106
F['population'] = {'measurements': len(M), 'token_rows': sum(1 for m in M if m['metric'] == 'token_delta'), 'standing_token_disagreements': 210, 'originals': 106,
                   'rows_with_server_dispersion': sum(1 for m in M if m['metric'] == 'token_delta' and (m.get('token_derivation') or {}).get('dispersion')),
                   'band_assessed_rows_on_register': sum(1 for m in M if ((m.get('replication_comparison') or {}).get('sampling_band') or {}).get('applicable') is True),
                   'unconfirmable_rows_on_register': sum(1 for m in M if (m.get('replication_comparison') or {}).get('unconfirmable') is True)}
assert F['population']['measurements'] == 1559 and F['population']['token_rows'] == 1021 and F['population']['rows_with_server_dispersion'] == 8 and F['population']['band_assessed_rows_on_register'] == 1 and F['population']['unconfirmable_rows_on_register'] == 1
oc = Counter(x['outcome'] for x in rows); F['outcomes'] = dict(oc); assert oc == {'unconfirmable': 75, 'disagreement_stands': 48, 'not_applicable': 87}
rs = Counter(x['reason'] for x in rows if x['outcome'] == 'not_applicable'); F['unreachable'] = dict(rs)
assert rs['filed value not reproduced from the manifest (the filed-vs-derived class)'] == 43 and rs['fewer than 2 pairs on a headline encoding'] == 19 and rs['not derivable: test_set is not a list of pairs'] == 14 and rs['not derivable: tokenizer not available locally'] == 8 and rs['not derivable: non-string arm'] == 2 and rs['inline manifest unavailable on one row'] == 1
der = [x for x in rows if x['outcome'] != 'not_applicable']; F['derivable'] = {'n': len(der), 'exact': sum(1 for x in der if x.get('exact')), 'rounded': sum(1 for x in der if not x.get('exact')), 'stratified': sum(x['stratified'] for x in der), 'tolerance_below_band': sum(x['tolerance_below_band'] for x in der)}
assert F['derivable'] == {'n': 123, 'exact': 96, 'rounded': 27, 'stratified': 38, 'tolerance_below_band': 111}
for x in rows:
    if x['diff'] is None and x.get('rep_value') is not None and x.get('orig_value') is not None: x['diff'] = abs(float(x['rep_value']) - float(x['orig_value']))  # legacy receipts without absolute_difference: the band used this same difference
zb = [x for x in der if x['band'] == 0]; F['band_zero_rows'] = {'n': len(zb), 'outcomes': dict(Counter(x['outcome'] for x in zb)), 'note': 'both samples had identical per-pair deltas on the headline encoding, so the band is zero and any difference stands'}
nz = [x for x in der if x['band'] > 0]
ratios = sorted(x['tolerance'] / x['band'] for x in nz); F['tolerance_over_band'] = {'n': len(ratios), 'q1': round(ratios[len(ratios) // 4], 3), 'median': round(statistics.median(ratios), 3), 'q3': round(ratios[3 * len(ratios) // 4], 3), 'max': round(ratios[-1], 3), 'below_one': sum(1 for r in ratios if r < 1)}
dob = sorted(x['diff'] / x['band'] for x in nz if x['outcome'] == 'disagreement_stands'); F['standing_diff_over_band'] = {'n': len(dob), 'median': round(statistics.median(dob), 2), 'min': round(dob[0], 2), 'max': round(dob[-1], 2)}
dub = sorted(x['diff'] / x['band'] for x in nz if x['outcome'] == 'unconfirmable'); F['unconfirmable_diff_over_band'] = {'n': len(dub), 'median': round(statistics.median(dub), 2), 'max': round(dub[-1], 2)}
F['unconfirmable_by_stratification'] = {'stratified': sum(1 for x in der if x['stratified'] and x['outcome'] == 'unconfirmable'), 'of_stratified': sum(1 for x in der if x['stratified']), 'simple': sum(1 for x in der if not x['stratified'] and x['outcome'] == 'unconfirmable'), 'of_simple': sum(1 for x in der if not x['stratified'])}
F['originals'] = {'n': 106, 'all_unconfirmable': sum(1 for g in per_o.values() if g['all_unconfirmable']), 'any_unconfirmable': sum(1 for g in per_o.values() if g['unconfirmable'] > 0), 'fully_derivable': sum(1 for g in per_o.values() if g['not_derivable'] == 0), 'none_derivable': sum(1 for g in per_o.values() if g['not_derivable'] == g['eligible'])}
assert F['originals']['all_unconfirmable'] == 27 and F['originals']['any_unconfirmable'] == 45 and F['originals']['fully_derivable'] == 63
cf = Counter((g['status_now'], g['status_if_band']) for g in per_o.values()); F['counterfactual'] = {f'{a}->{b}': n for (a, b), n in cf.items()}
assert cf[('disputed', 'awaiting')] == 13 and cf[('confirmed_contested', 'confirmed')] == 13 and cf[('disputed', 'confirmed_contested')] == 3 and cf[('disputed', 'confirmed')] == 1 and cf[('disputed', 'disputed')] == 55 and cf[('confirmed_contested', 'confirmed_contested')] == 21
F['counterfactual_moves'] = sum(n for (a, b), n in cf.items() if a != b); assert F['counterfactual_moves'] == 30
assert all(g['served_state'] == g['status_now'] for g in per_o.values()), 'served state disagrees with status(a,d)'
sh = C['queue_shadow']; F['register_shadow'] = {'queue_token_originals': len(sh), 'register_derivable_rows': sum(s['eligible_disagreements'] - s['not_derivable'] for s in sh.values()), 'register_unconfirmable': sum(s['unconfirmable'] for s in sh.values()), 'mine_derivable_on_those': sum(per_o[h]['eligible'] - per_o[h]['not_derivable'] for h in sh if h in per_o), 'mine_unconfirmable_on_those': sum(per_o[h]['unconfirmable'] for h in sh if h in per_o)}
assert F['register_shadow']['queue_token_originals'] == 19 and F['register_shadow']['register_derivable_rows'] == 0 and F['register_shadow']['mine_derivable_on_those'] == 49
# the 19 single-pair rows under the resolution hold of a-22spx (token clause: s = max(1/nO, 1/nR); hold iff tolerance < s and |gap| <= s), counts from the manifests
sp = [x for x in rows if x['reason'] == 'fewer than 2 pairs on a headline encoding']; held = 0; detail = []
byh = {m['manifest_hash'][:8]: m['manifest_hash'] for m in M}
for x in sp:
    ns = []
    for h8 in (x['rep'], x['orig']):
        d = json.load(open(f'dl/manifests/{byh[h8]}.json')); ns.append(len(d['manifest']['test_set']))
    s = max(1 / n for n in ns); gap = float(x['diff']); tol = float(x['tolerance']); h = tol < s and gap <= s; held += h; detail.append({'rep': x['rep'], 'orig': x['orig'], 'n': ns, 'gap': gap, 'tol': tol, 'step': s, 'held': h})
F['single_pair_rows'] = {'n': len(sp), 'one_pair_on_at_least_one_side': sum(1 for d in detail if min(d['n']) == 1), 'held_by_resolution_hold': held, 'gaps': sorted(round(d['gap'], 3) for d in detail)}
F['calibration'] = 'the port reproduces the served sampling-band block on 42d2addb vs 130bcdcf exactly: variances 5.85 and 4.8667, standard error 0.8184, band 1.6368'
F['tiktoken'] = __import__('tiktoken').__version__
json.dump(F, open('dl/facts.json', 'w'), indent=1); print(json.dumps(F, indent=1))
