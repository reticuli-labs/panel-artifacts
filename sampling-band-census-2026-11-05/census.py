"""The sampling band (SamplingBand.php, z=2, refuse-only), re-derived from committed bytes over every standing token_delta disagreement
on the register: recount both rows' per-pair deltas with tiktoken, take exact moments on each row's headline encoding (and per declared
stratum with committed shares), and classify each comparison as the server would if it held the moments. Pure: reads dl/, writes dl/census.json."""
import json, os, math, tiktoken
# dl/measurements_slim.json carries every field the census reads, from iter_measurements() at read_at; the full rows are public at /api/v1/measurements
from collections import Counter, defaultdict
os.chdir(os.path.dirname(os.path.abspath(__file__)))
Z = 2.0; MIN_PAIRS = 2; MIN_AGREEMENTS = 1; ABS_TOL = 0.02; REL_TOL = 0.10
M = json.load(open('dl/measurements_slim.json')); byhash = {m['manifest_hash']: m for m in M}
def active(m): return not m.get('retraction') and not m.get('voided_at') and m.get('evidence_state') in (None, 'valid')
dis = [m for m in M if m['metric'] == 'token_delta' and m.get('is_replication') and m.get('reproduced_ok') is False and m.get('settlement_eligible') is True and active(m)]
assert len(dis) == 210
ENC = {}
AVAIL = set(tiktoken.list_encoding_names())
def canon(m):
    base = m.split('@')[0]
    if base.startswith('tiktoken/'): base = base[len('tiktoken/'):]
    return base if base in AVAIL else None
def enc(m):
    b = canon(m)
    if b is None: raise KeyError(m)
    if b not in ENC: ENC[b] = tiktoken.get_encoding(b)
    return ENC[b]
RC = {}
def recount(h):
    if h in RC: return RC[h]
    p = f'dl/manifests/{h}.json'
    if not os.path.exists(p): RC[h] = None; return None
    d = json.load(open(p)); man = d['manifest']; models = man['models']; ts = man['test_set']
    per = {}
    if not isinstance(ts, list): RC[h] = {'error': 'test_set is not a list of pairs'}; return RC[h]
    if any(canon(m) is None for m in models): RC[h] = {'error': 'tokenizer not available locally: ' + ','.join(m for m in models if canon(m) is None)}; return RC[h]
    models = [canon(m) for m in models]
    for m in models:
        e = enc(m)
        def arms(x):  # dict rows carry english/ainglish (the server reads exactly those keys); legacy list rows are [english, ainglish] per measure.py
            if isinstance(x, dict): return x.get('english', x.get('baseline')), x.get('ainglish', x.get('marked'))
            if isinstance(x, list) and len(x) == 2: return x[0], x[1]
            raise ValueError('unknown pair shape')
        try: pairs = [arms(x) for x in ts]
        except ValueError: RC[h] = {'error': 'unknown pair shape'}; return RC[h]
        if any(not isinstance(a, str) or not isinstance(b, str) for a, b in pairs): RC[h] = {'error': 'non-string arm'}; return RC[h]
        deltas = [len(e.encode(b)) - len(e.encode(a)) for a, b in pairs]
        per[m] = {'n': len(deltas), 'sum': sum(deltas), 'sum_squares': sum(v * v for v in deltas), 'mean': sum(deltas) / len(deltas), 'deltas': deltas}
    means = [per[m]['mean'] for m in models]; head = models[means.index(max(means))]
    # a stratified headline is sum(share * cell mean) over committed strata, not the pooled mean
    strata = man.get('settlement_strata'); shares = None; cells = None
    if strata:
        tot = sum(float(s['weight']) for s in strata); shares = {s['id']: float(s['weight']) / tot for s in strata}
        cells = {m: {} for m in models}
        for m in models:
            for sid in shares:
                ds = [per[m]['deltas'][i] for i, x in enumerate(ts) if isinstance(x, dict) and x.get('stratum') == sid]
                cells[m][sid] = {'n': len(ds), 'sum': sum(ds), 'sum_squares': sum(v * v for v in ds), 'mean': (sum(ds) / len(ds)) if ds else None}
        smeans = [sum(shares[sid] * cells[m][sid]['mean'] for sid in shares) if all(cells[m][sid]['n'] for sid in shares) else None for m in models]
        if all(v is not None for v in smeans): head = models[smeans.index(max(smeans))]; headline_value = max(smeans)
        else: headline_value = None
    else: headline_value = max(means)
    RC[h] = {'hash': h, 'models': models, 'per': per, 'headline_model': head, 'headline_value': headline_value, 'filed': d['value'], 'shares': shares, 'cells': cells, 'pairs': len(ts)}
    return RC[h]
def variance(cell):
    n = cell['n']
    if n < MIN_PAIRS: return None
    return max(0.0, (cell['sum_squares'] - cell['sum'] * cell['sum'] / n) / (n - 1))
def status(a, d):
    a = max(0, a); d = max(0, d)
    if a >= MIN_AGREEMENTS and 1 + a > d: return 'confirmed_contested' if d > 0 else 'confirmed'
    return 'disputed' if d > 0 else 'awaiting'
rows = []
for r in dis:
    o = byhash.get(r['replicates_hash']); rc = r.get('replication_comparison') or {}
    tol = (rc.get('tolerance') or {}).get('effective'); tol = tol if tol is not None else (max(ABS_TOL, REL_TOL * abs(float(o['value']))) if o else None)
    out = {'rep': r['manifest_hash'][:8], 'orig': r['replicates_hash'][:8], 'proposal': (r.get('report_target') or {}).get('proposal') or '', 'rep_value': r['value'], 'orig_value': o['value'] if o else None,
           'diff': rc.get('absolute_difference'), 'tolerance': tol, 'tolerance_from_receipt': (rc.get('tolerance') or {}).get('effective') is not None, 'stratified': bool(rc.get('strata')), 'at': r['at'][:10], 'outcome': None, 'reason': None}
    R = recount(r['manifest_hash']); O = recount(r['replicates_hash']) if o else None
    def na(reason): out['outcome'] = 'not_applicable'; out['reason'] = reason; rows.append(out)
    if o is None: na('original row missing from the measurement list'); continue
    if R is None or O is None: na('inline manifest unavailable on one row'); continue
    if 'error' in R or 'error' in O: na('not derivable: ' + ((R.get('error') if 'error' in R else O.get('error')).split(':')[0])); continue
    if R['headline_value'] is None or O['headline_value'] is None: na('stratified headline not derivable'); continue
    def reproduces(X, row):
        if abs(X['headline_value'] - float(row['value'])) > 5e-4: return False
        pm = {x['model']: float(x['value']) for x in (row.get('per_member') or []) if isinstance(x, dict) and 'model' in x}
        for m, v in pm.items():
            b = canon(m)
            if b is None or b not in X['per'] or abs(X['per'][b]['mean'] - v) > 5e-4: return False
        return True
    if not (reproduces(R, r) and reproduces(O, o)):
        out['recount'] = {'rep': R['headline_value'], 'orig': O['headline_value']}; na('filed value not reproduced from the manifest (the filed-vs-derived class)'); continue
    out['exact'] = abs(R['headline_value'] - float(r['value'])) <= 1e-9 and abs(O['headline_value'] - float(o['value'])) <= 1e-9
    hO, hR = O['headline_model'], R['headline_model']; vO = variance(O['per'][hO]); vR = variance(R['per'][hR])
    if vO is None or vR is None: na('fewer than 2 pairs on a headline encoding'); continue
    nO, nR = O['per'][hO]['n'], R['per'][hR]['n']; diff = abs(float(r['value']) - float(o['value']))
    strata_out = None; all_within = True; agg_var = None
    if rc.get('strata'):
        sh = None
        if O['shares'] and R['shares'] and set(O['shares']) == set(R['shares']) == {s['id'] for s in rc['strata']} and all(abs(O['shares'][k] - R['shares'][k]) <= 1e-9 for k in O['shares']) and abs(sum(O['shares'].values()) - 1) <= 1e-9: sh = O['shares']
        if sh is None: na('aggregate variance not derivable: committed stratum shares missing or disagree'); out['aggregate_declined'] = True; continue
        strata_out = []; agg_var = 0.0; bad = None
        for srow in rc['strata']:
            sid = srow['id']; cO = O['cells'][hO][sid]; cR = R['cells'][hR][sid]; svO = variance(cO); svR = variance(cR)
            if svO is None or svR is None: bad = 'fewer than 2 pairs in a declared stratum'; break
            cv = svO / cO['n'] + svR / cR['n']; sb = Z * math.sqrt(cv); w = float(srow['absolute_difference']) <= sb; all_within = all_within and w
            agg_var += sh[sid] * sh[sid] * cv; strata_out.append({'id': sid, 'difference': float(srow['absolute_difference']), 'band': sb, 'within': w})
        if bad: na(bad); continue
    se = math.sqrt(vO / nO + vR / nR) if agg_var is None else math.sqrt(agg_var); band = Z * se; within = diff <= band
    out.update({'outcome': 'unconfirmable' if (within and all_within) else 'disagreement_stands', 'se': se, 'band': band, 'within_aggregate': within, 'strata': strata_out, 'n': [nO, nR], 'variance': [vO, vR], 'tolerance_below_band': (out['tolerance'] is not None and out['tolerance'] < band), 'headline': [hO, hR]})
    rows.append(out)
assert len(rows) == 210
C = Counter(x['outcome'] for x in rows); print('OUTCOMES over 210 standing token disagreements:', dict(C))
print('not_applicable reasons:', Counter(x['reason'] for x in rows if x['outcome'] == 'not_applicable'))
der = [x for x in rows if x['outcome'] != 'not_applicable']
print('derivable', len(der), '| exact', sum(1 for x in der if x.get('exact')), '| within filing rounding', sum(1 for x in der if not x.get('exact')), '| stratified among derivable', sum(x['stratified'] for x in der), '| tolerance below band', sum(x['tolerance_below_band'] for x in der))
ratios = sorted(x['tolerance'] / x['band'] for x in der if x['band'] > 0); print('tolerance/band quartiles', [round(ratios[int(len(ratios) * q)], 3) for q in (0.25, 0.5, 0.75)], 'max', round(ratios[-1], 3))
# per original
per_o = defaultdict(lambda: {'eligible': 0, 'unconfirmable': 0, 'standing': 0, 'not_derivable': 0})
for x in rows:
    g = per_o[x['orig']]; g['eligible'] += 1; g[{'unconfirmable': 'unconfirmable', 'disagreement_stands': 'standing', 'not_applicable': 'not_derivable'}[x['outcome']]] += 1
origs = {r['replicates_hash'][:8]: byhash[r['replicates_hash']] for r in dis}
cf = Counter(); moves = []
for h8, g in per_o.items():
    o = origs[h8]; a = o.get('replication_count') or 0; d = o.get('disagreement_count') or 0
    now = status(a, d); after = status(a, max(0, d - g['unconfirmable'])); g['agreements'] = a; g['disagreements'] = d; g['status_now'] = now; g['status_if_band'] = after; g['served_state'] = o.get('settlement_state')
    g['all_unconfirmable'] = g['eligible'] > 0 and g['unconfirmable'] == g['eligible']
    cf[(now, after)] += 1
    if now != after: moves.append((h8, a, d, g['unconfirmable'], now, after))
print('originals', len(per_o), '| all_unconfirmable', sum(g['all_unconfirmable'] for g in per_o.values()), '| any unconfirmable', sum(g['unconfirmable'] > 0 for g in per_o.values()), '| fully derivable', sum(g['not_derivable'] == 0 for g in per_o.values()))
print('status now -> if the band were applied to stored counters:', dict(cf))
print('served_state agreement with status(a,d):', Counter((g['served_state'], g['status_now']) for g in per_o.values()))
# cross-check with the queue's shadow where the register could derive anything
shadow = {h: v['sampling_band'] for h, v in json.load(open('dl/queue_shadow.json'))['originals'].items()}  # the authenticated queue read of 12:39Z, extracted
print('queue shadow token originals', len(shadow), '| derivable by the register', sum(1 for s in shadow.values() if s['not_derivable'] < s['eligible_disagreements']), '| register unconfirmable total', sum(s['unconfirmable'] for s in shadow.values()))
cmp = [(h8, shadow[h8]['eligible_disagreements'], per_o[h8]['eligible'], shadow[h8]['unconfirmable'], per_o[h8]['unconfirmable'], shadow[h8]['not_derivable'], per_o[h8]['not_derivable']) for h8 in shadow if h8 in per_o]
print('overlap originals', len(cmp), '| eligible counts equal', sum(1 for t in cmp if t[1] == t[2]), '| register derivable rows', sum(t[1] - t[5] for t in cmp), '| mine derivable', sum(t[2] - t[6] for t in cmp))
for t in cmp:
    if t[1] - t[5] > 0: print('  register could derive:', t)
json.dump({'read_at': open('dl/read_at.txt').read().strip(), 'z': Z, 'rows': rows, 'per_original': per_o, 'status_counterfactual': {f'{k[0]}->{k[1]}': v for k, v in cf.items()}, 'moves': moves, 'queue_shadow': shadow}, open('dl/census.json', 'w'), indent=1, default=str)
print('MOVES (orig, agreements, disagreements, unconfirmable, now, after):'); [print('  ', m) for m in moves[:60]]
