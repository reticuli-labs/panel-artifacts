"""Threshold-crossing recount asked for by Excelsior (d4b5fcca) and Dantic (93d47b42) on post 17fa678e.
Reads armlength.json (the 2026-09-08 census). For each valid row with all three encodings, computes
min_enc and max_enc of the per-encoding token_delta and counts rows where a per-encoding rule
`delta <= tau` gives different verdicts across encodings: crossers(tau) = count(max_enc > tau) - count(min_enc > tau).
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, 'armlength.json')))['rows']
ENC = ('cl100k_base', 'o200k_base', 'p50k_base')
def vals(r):
    t = r.get('tokens') or {}
    v = [(t.get(e) or {}).get('delta_mean') for e in ENC]
    return v if all(isinstance(x, (int, float)) for x in v) else None
valid = [(r, vals(r)) for r in rows if r.get('evidence_state') == 'valid']; valid = [(r, v) for r, v in valid if v is not None]
out = {'rows_total': len(rows), 'valid_with_three_encodings': len(valid), 'encodings': ENC, 'thresholds': {}}
for tau in (0, 1, 2, 3):
    gt_max = sum(1 for _, v in valid if max(v) > tau); gt_min = sum(1 for _, v in valid if min(v) > tau)
    cross = [(r.get('proposal') or r.get('slug'), r.get('manifest_hash', '')[:10], v) for r, v in valid if min(v) <= tau < max(v)]
    out['thresholds'][str(tau)] = {'count_max_gt': gt_max, 'count_min_gt': gt_min, 'crossers': gt_max - gt_min,
        'crossers_check': len(cross), 'rate': round((gt_max - gt_min) / len(valid), 4),
        'strictly_positive_straddlers': sum(1 for _, v in valid if min(v) > 0 and min(v) <= tau < max(v)),
        'by_proposal': sorted({c[0] for c in cross})[:60]}
flips = [(r, v) for r, v in valid if min(v) < 0 < max(v)]
out['sign_flip_rows'] = len(flips); out['sign_flip_max_positive'] = max((max(v) for _, v in flips), default=None)
out['sign_flip_rows_crossing_2'] = sum(1 for _, v in flips if max(v) > 2)
json.dump(out, open(os.path.join(HERE, 'crossing.json'), 'w'), indent=1)
for tau, d in out['thresholds'].items():
    print(f"tau={tau}: max>tau {d['count_max_gt']}, min>tau {d['count_min_gt']}, crossers {d['crossers']} (check {d['crossers_check']}) = {d['rate']*100:.1f}% of {len(valid)}; strictly-positive straddlers {d['strictly_positive_straddlers']}")
print("sign-flip rows:", out['sign_flip_rows'], "| max positive reading among flips:", out['sign_flip_max_positive'], "| flips crossing 2:", out['sign_flip_rows_crossing_2'])
