#!/usr/bin/env python3
"""Re-derive every token_delta receipt whose filed per-member values are all exactly 2.

Public data only: the register's measurement API and the SDK's own token_delta harness.
Usage:  pip install "ainglish>=0.2.57" tiktoken ; python3 recount_constant_rows.py
Writes token_rows.json (all token_delta rows), all2_recount.json (the constant rows recounted)
and per_submitter.json (modal-share table). No credentials, no writes to the register.
"""
import collections, json, statistics, sys
import tiktoken
from ainglish.client import AinglishClient
from ainglish import measure

c = AinglishClient()
rows = list(c.iter_measurements(metric='token_delta'))
json.dump(rows, open('token_rows.json', 'w'))
pm = lambda r: [m.get('value') for m in (r.get('per_member') or [])]
def sub(r):
    s = r.get('submitter'); return (s.get('name') or s.get('sub', '?')[:8]) if isinstance(s, dict) else str(s)
constant = [r for r in rows if pm(r) and all(v == 2 for v in pm(r))]
out = []
for r in constant:
    full = c.measurement(r['manifest_hash']); man = full.get('manifest') or {}
    pairs = man.get('test_set') or man.get('pairs') or []; models = man.get('models') or ['cl100k_base', 'o200k_base', 'p50k_base']
    norm = [{'english': p['english'], 'ainglish': p['ainglish']} if isinstance(p, dict) else {'english': p[0], 'ainglish': p[1]} for p in pairs]
    res = measure.token_delta(norm, models)
    out.append({'hash': r['manifest_hash'], 'at': full.get('at'), 'proposal': (full.get('proposal') or {}).get('slug'),
                'role': 'replication' if full.get('is_replication') else 'original', 'evidence_state': full.get('evidence_state'),
                'pairs': len(norm), 'declared_tiktoken': (full.get('tokenizer_provenance') or {}).get('version'), 'recount_tiktoken': tiktoken.__version__,
                'filed_per_member': pm(r), 'derived_per_member': {k: v['mean'] for k, v in res['by_tokenizer'].items()}, 'derived_headline': res['floor'],
                'derives_to_filed': all(abs(v['mean'] - 2) < 1e-9 for v in res['by_tokenizer'].values())})
json.dump(out, open('all2_recount.json', 'w'), indent=1)
by = collections.defaultdict(list)
for r in rows:
    if r.get('value') is not None: by[sub(r)].append(float(r['value']))
table = []
for s, vals in by.items():
    if len(vals) >= 5:
        mode, cnt = collections.Counter(vals).most_common(1)[0]
        table.append({'submitter': s, 'n': len(vals), 'distinct': len(set(vals)), 'mode': mode, 'share_at_mode': cnt / len(vals), 'stdev': statistics.pstdev(vals)})
json.dump(sorted(table, key=lambda t: -t['n']), open('per_submitter.json', 'w'), indent=1)
print(f"token rows {len(rows)}; constant-2 rows {len(constant)}; derive to filed {sum(o['derives_to_filed'] for o in out)}")
