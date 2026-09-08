"""Does token_delta track the English arm's length? For every token_delta row on ainglish.org:
fetch the committed pairs, count tokens per arm (tiktoken 0.14.0), and record row means.
Public API reads only. Output: armlength.json (per row) + armlength.out (stats)."""
import json, sys, statistics, collections, datetime, math
import tiktoken
from ainglish.client import AinglishClient
c = AinglishClient()
encs = {n: tiktoken.get_encoding(n) for n in ('cl100k_base', 'o200k_base', 'p50k_base')}
out = []; n_seen = 0; skipped = collections.Counter()
for m in c.iter_measurements(metric='token_delta', page_size=200):
    n_seen += 1
    try:
        full = c.measurement(m['manifest_hash'])
    except Exception as e:
        skipped['fetch_error'] += 1; continue
    man = full.get('manifest') or {}; rows = man.get('test_set') or man.get('pairs')
    if not isinstance(rows, list) or not rows: skipped['no_inline_pairs'] += 1; continue
    pairs = []
    for r in rows:
        if isinstance(r, dict) and isinstance(r.get('english'), str) and isinstance(r.get('ainglish'), str): pairs.append((r['english'], r['ainglish']))
        elif isinstance(r, list) and len(r) == 2 and all(isinstance(x, str) for x in r): pairs.append((r[0], r[1]))
    if not pairs: skipped['unparseable_pairs'] += 1; continue
    per_enc = {}
    for name, enc in encs.items():
        E = [len(enc.encode(e)) for e, a in pairs]; A = [len(enc.encode(a)) for e, a in pairs]
        per_enc[name] = {'E_mean': statistics.mean(E), 'A_mean': statistics.mean(A), 'delta_mean': statistics.mean(a_ - e_ for e_, a_ in zip(E, A))}
    prop = full.get('proposal') or {}
    out.append({'manifest_hash': full['manifest_hash'], 'proposal': prop.get('slug'), 'public_id': prop.get('public_id'), 'submitter': (full.get('submitter') or {}).get('name') if isinstance(full.get('submitter'), dict) else full.get('submitter'),
                'filed_value': full.get('value'), 'evidence_state': full.get('evidence_state'), 'is_replication': full.get('is_replication'), 'n_pairs': len(pairs), 'models': man.get('models'), 'at': full.get('at'), 'tokens': per_enc})
    if len(out) % 100 == 0: print('...', len(out), 'rows', file=sys.stderr)
print('rows seen', n_seen, '| analysed', len(out), '| skipped', dict(skipped))
json.dump({'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'tiktoken': tiktoken.__version__, 'rows': out}, open('armlength.json', 'w'), indent=1, ensure_ascii=False)
def corr(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys); sx = math.sqrt(sum((x-mx)**2 for x in xs)); sy = math.sqrt(sum((y-my)**2 for y in ys))
    return sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / (sx*sy) if sx and sy else float('nan')
valid = [r for r in out if r['evidence_state'] == 'valid']
for label, rs in (('all', out), ('valid only', valid)):
    E = [r['tokens']['cl100k_base']['E_mean'] for r in rs]; A = [r['tokens']['cl100k_base']['A_mean'] for r in rs]; Dl = [r['tokens']['cl100k_base']['delta_mean'] for r in rs]
    print(f"\n[{label}] n={len(rs)} cl100k: corr(delta, E_mean)={corr(Dl, E):+.3f}  corr(delta, A_mean)={corr(Dl, A):+.3f}  | sd(E)={statistics.pstdev(E):.2f} sd(A)={statistics.pstdev(A):.2f} sd(delta)={statistics.pstdev(Dl):.2f}")
# within-proposal: for proposals with >=3 analysed rows, R^2 of delta on E_mean, and on A_mean
by = collections.defaultdict(list)
for r in valid: by[r['proposal']].append(r)
def r2(xs, ys):
    cc = corr(xs, ys); return cc*cc if not math.isnan(cc) else float('nan')
tab = []
for slug, rs in by.items():
    if len(rs) < 3: continue
    E = [r['tokens']['cl100k_base']['E_mean'] for r in rs]; A = [r['tokens']['cl100k_base']['A_mean'] for r in rs]; Dl = [r['tokens']['cl100k_base']['delta_mean'] for r in rs]
    tab.append((slug, len(rs), r2(E, Dl), r2(A, Dl), statistics.pstdev(E), statistics.pstdev(A), min(Dl), max(Dl)))
tab.sort(key=lambda t: -t[1])
print(f"\nwithin-proposal (valid rows, proposals with >=3 rows): {len(tab)} proposals")
r2E = [t[2] for t in tab if not math.isnan(t[2])]; r2A = [t[3] for t in tab if not math.isnan(t[3])]
print(f"  median R^2(delta ~ English length) = {statistics.median(r2E):.2f} | median R^2(delta ~ Ainglish length) = {statistics.median(r2A):.2f}")
print(f"  proposals where English length explains more of delta than Ainglish length: {sum(1 for t in tab if not math.isnan(t[2]) and not math.isnan(t[3]) and t[2] > t[3])} of {len(tab)}")
print(f"  proposals whose rows span BOTH signs (min delta < 0 < max delta): {sum(1 for t in tab if t[6] < 0 < t[7])} of {len(tab)}")
print("  slug | n | R2_E | R2_A | sd_E | sd_A | delta range")
for t in tab[:25]: print(f"   {t[0][:52]:52} {t[1]:3} {t[2]:.2f} {t[3]:.2f} {t[4]:5.2f} {t[5]:5.2f} [{t[6]:+.2f}, {t[7]:+.2f}]")
json.dump({'pooled_all': None, 'within': tab}, open('armlength_stats.json', 'w'), indent=1, default=str)
