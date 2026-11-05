"""Why 130 of 210 standing token disagreements could not be re-derived: encodings, pair shapes, and filed values my recount does not reproduce."""
import json, os, tiktoken
# dl/measurements_slim.json carries every field this reads, from iter_measurements() at read_at
from collections import Counter
os.chdir(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open('dl/measurements_slim.json')); byhash = {m['manifest_hash']: m for m in M}
def active(m): return not m.get('retraction') and not m.get('voided_at') and m.get('evidence_state') in (None, 'valid')
dis = [m for m in M if m['metric'] == 'token_delta' and m.get('is_replication') and m.get('reproduced_ok') is False and m.get('settlement_eligible') is True and active(m)]
def load(h):
    p = f'dl/manifests/{h}.json'; return json.load(open(p)) if os.path.exists(p) else None
avail = set(tiktoken.list_encoding_names()); unavail = Counter(); shapes = Counter(); mism = []; ENC = {}
def enc(m):
    if m not in ENC: ENC[m] = tiktoken.get_encoding(m)
    return ENC[m]
def arms(x):
    if isinstance(x, dict):
        a, b = x.get('english', x.get('baseline')), x.get('ainglish', x.get('marked'))
        return (a, b) if isinstance(a, str) and isinstance(b, str) else None
    if isinstance(x, list) and len(x) == 2 and all(isinstance(v, str) for v in x): return x[0], x[1]
    return None
seen = set()
for r in dis:
    for h in (r['manifest_hash'], r['replicates_hash']):
        if h in seen: continue
        seen.add(h); d = load(h)
        if not d: shapes['no manifest'] += 1; continue
        man = d['manifest']; models = man['models']; bad = [m for m in models if m not in avail]
        if bad: unavail[tuple(bad)] += 1; continue
        ts = man['test_set']; pairs = [arms(x) for x in ts]
        if any(p is None for p in pairs):
            x = next(x for x, p in zip(ts, pairs) if p is None); shapes[type(x).__name__ + ':' + (json.dumps(x)[:90] if not isinstance(x, dict) else ','.join(sorted(x.keys())))] += 1; continue
        shapes['ok'] += 1
        means = {}
        for m in models:
            e = enc(m); ds = [len(e.encode(b)) - len(e.encode(a)) for a, b in pairs]; means[m] = sum(ds) / len(ds)
        head = max(means.values()); filed = d['value']
        if abs(head - filed) > 1e-9:
            pm = {x['model']: x['value'] for x in (d.get('per_member') or [])}
            alt = {'mean_of_members': sum(means.values()) / len(means), 'min': min(means.values())}
            alt['stripped_max'] = max(sum(len(enc(m).encode(b.strip())) - len(enc(m).encode(a.strip())) for a, b in pairs) / len(pairs) for m in models)
            if any(isinstance(x, list) for x in ts): alt['swapped_max'] = max(sum(len(enc(m).encode(a)) - len(enc(m).encode(b)) for a, b in pairs) / len(pairs) for m in models)
            pm_match = all(abs(pm.get(m, 1e9) - means[m]) < 1e-9 for m in models) if pm else None
            mism.append({'hash': h[:8], 'filed': filed, 'my_max': round(head, 4), 'my_means': {k: round(v, 4) for k, v in means.items()}, 'per_member': pm, 'pm_matches_mine': pm_match, 'fv': byhash[h].get('formula_version'), 'n': len(pairs), 'list': any(isinstance(x, list) for x in ts), 'alt_match': [k for k, v in alt.items() if abs(v - filed) < 1e-9], 'verified': byhash[h].get('derivation_verified'), 'is_rep': byhash[h].get('is_replication'), 'at': byhash[h]['at'][:10], 'strata': bool(man.get('settlement_strata'))})
print('distinct manifests in the population', len(seen))
print('UNAVAILABLE encodings:', unavail.most_common())
print('PAIR SHAPES:', shapes.most_common(8))
print('\nMISMATCHES distinct manifests', len(mism))
print(' alt match', Counter(tuple(x['alt_match']) for x in mism)); print(' per_member matches my means', Counter(x['pm_matches_mine'] for x in mism)); print(' formula_version', Counter(x['fv'] for x in mism)); print(' derivation_verified', Counter(x['verified'] for x in mism)); print(' month', Counter(x['at'][:7] for x in mism)); print(' strata', Counter(x['strata'] for x in mism))
for x in mism[:16]: print(' ', json.dumps(x)[:360])
json.dump({'unavailable': [list(k) + [v] for k, v in unavail.items()], 'shapes': dict(shapes), 'mismatches': mism}, open('dl/diag.json', 'w'), indent=1)
