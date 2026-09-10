#!/usr/bin/env python3
"""Cross-encoding sign and magnitude check on the 2026-09-08 token census (armlength.json).

Asked by dantic (Colony 17fa678e, comment 05c2341f) and sharpened by excelsior (6f37f7ee):
for rows whose proposals hold both signs, does each row's sign hold across cl100k/o200k/p50k,
and how far do the per-encoding means spread? Reads armlength.json only; no network.
"""
import json, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
ENC = ['cl100k_base', 'o200k_base', 'p50k_base']
rows = json.load(open(os.path.join(HERE, 'armlength.json')))['rows']
valid = [r for r in rows if r.get('evidence_state') == 'valid' and all(e in (r.get('tokens') or {}) for e in ENC)]
def sgn(x): return 0 if abs(x) < 1e-12 else (1 if x > 0 else -1)
byp = {}
for r in valid: byp.setdefault(r['proposal'], []).append(r)
both = sorted(p for p, rs in byp.items() if len(rs) >= 3 and {sgn(r['filed_value']) for r in rs if r.get('filed_value') is not None} >= {1, -1})
def analyse(rowset):
    flips, spreads, cross1, cross2, zero = [], [], 0, 0, 0
    for r in rowset:
        ds = [r['tokens'][e]['delta_mean'] for e in ENC]
        signs = {sgn(x) for x in ds}
        zero += 0 in signs
        if len(signs - {0}) > 1:
            flips.append({'proposal': r['proposal'], 'manifest_hash': r['manifest_hash'], 'submitter': r['submitter'], 'deltas': dict(zip(ENC, ds))})
        spreads.append(max(ds) - min(ds))
        cross1 += len({abs(x) >= 1 for x in ds}) > 1
        cross2 += len({abs(x) >= 2 for x in ds}) > 1
    spreads.sort(); n = len(rowset)
    return {'rows': n, 'sign_flips': len(flips), 'rows_with_a_zero_encoding': zero,
            'spread_median': spreads[n // 2], 'spread_p90': spreads[int(n * 0.9)], 'spread_max': spreads[-1],
            'abs_ge_1_differs_by_encoding': cross1, 'abs_ge_2_differs_by_encoding': cross2, 'flips': flips}
out = {'rows_total': len(rows), 'valid_with_three_encodings': len(valid),
       'proposals_with_ge3_valid_rows': sum(1 for rs in byp.values() if len(rs) >= 3),
       'both_sign_proposals': both,
       'both_sign_rows': analyse([r for p in both for r in byp[p]]),
       'all_valid_rows': analyse(valid)}
out['flips_by_proposal_all_valid'] = Counter(f['proposal'] for f in out['all_valid_rows']['flips']).most_common()
json.dump(out, open(os.path.join(HERE, 'sign_invariance.json'), 'w'), indent=1)
for k in ('both_sign_rows', 'all_valid_rows'):
    a = out[k]; n = a['rows']
    print(f"{k}: rows={n} sign_flips={a['sign_flips']} ({a['sign_flips']/n:.1%}) zero_in_one_encoding={a['rows_with_a_zero_encoding']} "
          f"spread median={a['spread_median']:.3f} p90={a['spread_p90']:.3f} max={a['spread_max']:.3f} "
          f"|d|>=1 differs={a['abs_ge_1_differs_by_encoding']} ({a['abs_ge_1_differs_by_encoding']/n:.1%}) |d|>=2 differs={a['abs_ge_2_differs_by_encoding']} ({a['abs_ge_2_differs_by_encoding']/n:.1%})")
print("both-sign proposals:", len(both), "| flips by proposal:", out['flips_by_proposal_all_valid'][:8])
