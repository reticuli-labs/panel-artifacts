#!/usr/bin/env python3
"""Score the eight frozen targets of plan.md from this directory's run/ files. Reads only paths inside this directory.

Per-reader × per-state accuracies come from the real-cells file (states by item-id suffix, readers by model prefix),
exactly as the cold-arm table of 2026-10-02 was read. Stratum deltas (T6–T8) are legend-arm minus English-arm accuracy
per stratum, computed from the same cells and cross-checked against the filed measurement payload. Writes results.json
and prints the table. A target outside its range is a miss, as the plan says.
"""
import glob, json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fs = [f for f in glob.glob(str(ROOT / 'run' / '*attempt-*cells.json')) if 'calibration' not in f]
assert len(fs) == 1, fs
cells = json.load(open(fs[0]))['rows']
assert len(cells) == 240, len(cells)
cal = json.load(open(fs[0].replace('.cells.json', '.calibration.cells.json')))['rows']
meas_files = glob.glob(str(ROOT / 'run' / '*attempt-*measurement.json')); assert len(meas_files) == 1
meas = json.load(open(meas_files[0]))

def form(r):
    m = re.match(r'inr-(idempotent|no-retry)-(\d)-(.+)$', r['item_id']); return (m.group(1), m.group(3)) if m else None
def rd(r): return '12B' if r['reader'].startswith('gemma3') else '24B'
T = {}
for reader in ('12B', '24B'):
    for arm in ('ainglish', 'english'):
        acc = collections.defaultdict(lambda: [0, 0])
        for r in cells:
            f = form(r)
            if f and f[0] == 'idempotent' and r['arm'] == arm and rd(r) == reader:
                acc[f[1]][0] += 1; acc[f[1]][1] += int(r['correct'])
        T[(reader, arm)] = {k: list(v) for k, v in acc.items()}
CUE = ('failed-mid', 'timeout-late'); CLEAN = ('confirmed-again', 'timeout')
def agg(reader, arm, states):
    n = sum(T[(reader, arm)].get(s, [0, 0])[0] for s in states); k = sum(T[(reader, arm)].get(s, [0, 0])[1] for s in states); return k, n
def acc_of(k, n): return (k / n) if n else None

strata = {}
for s in ('idempotent', 'no-retry', 'transfer'):
    by = {}
    for arm in ('ainglish', 'english'):
        rows = [r for r in cells if re.match(r'inr-(idempotent|no-retry|transfer)-', r['item_id']).group(1) == s and r['arm'] == arm]
        by[arm] = (sum(int(r['correct']) for r in rows), len(rows))
    strata[s] = {'legend': by['ainglish'], 'english': by['english'],
                 'delta_pp': round(100 * (acc_of(*by['ainglish']) - acc_of(*by['english'])), 2)}

C12, C24 = agg('12B', 'ainglish', CUE), agg('24B', 'ainglish', CUE)
K12, K24 = agg('12B', 'ainglish', CLEAN), agg('24B', 'ainglish', CLEAN)
V12, V24 = agg('12B', 'ainglish', ('verified-none',)), agg('24B', 'ainglish', ('verified-none',))
targets = [
    ('T1', '12B reader, cue states, legend arm', f'{C12[0]} of {C12[1]}', acc_of(*C12), 'ge', 0.75),
    ('T2', '24B reader, cue states, legend arm', f'{C24[0]} of {C24[1]}', acc_of(*C24), 'ge', 0.67),
    ('T3a', '12B reader, clean states, legend arm', f'{K12[0]} of {K12[1]}', acc_of(*K12), 'ge', 0.75),
    ('T3b', '24B reader, clean states, legend arm', f'{K24[0]} of {K24[1]}', acc_of(*K24), 'ge', 0.75),
    ('T4', '24B reader, verified-none, legend arm', f'{V24[0]} of {V24[1]}', acc_of(*V24), 'le', 0.67),
    ('T5', '12B reader, verified-none, legend arm', f'{V12[0]} of {V12[1]}', acc_of(*V12), 'le', 0.75),
    ('T6', 'idempotent stratum delta (legend - English), pp', str(strata['idempotent']['delta_pp']), strata['idempotent']['delta_pp'], 'in', (-10, 5)),
    ('T7', 'no-retry stratum delta, pp', str(strata['no-retry']['delta_pp']), strata['no-retry']['delta_pp'], 'in', (-10, 5)),
    ('T8', 'transfer stratum delta, pp', str(strata['transfer']['delta_pp']), strata['transfer']['delta_pp'], 'in', (-15, 0)),
]
def held(v, op, bound):
    if v is None: return None
    if op == 'ge': return v >= bound
    if op == 'le': return v <= bound
    lo, hi = bound; return lo <= v <= hi
rows = []
for tid, what, raw, v, op, bound in targets:
    h = held(v, op, bound); rows.append({'target': tid, 'what': what, 'observed': raw, 'value': v, 'rule': f'{op} {bound}', 'held': h})
out = {'kind': 'reticuli.legend-window.score.v1', 'attempt': meas.get('attempt_id') or meas.get('attempt'), 'cells': len(cells), 'calibration_cells': len(cal),
       'per_reader_arm_state_idempotent': {f'{k[0]}-{k[1]}': v for k, v in T.items()}, 'strata': strata, 'targets': rows,
       'held': sum(1 for r in rows if r['held'] is True), 'missed': sum(1 for r in rows if r['held'] is False), 'untestable': sum(1 for r in rows if r['held'] is None),
       'served_value': meas.get('value'), 'served_strata': meas.get('stratum_results')}
for sr in meas.get('stratum_results') or []:
    assert abs(sr['value'] - strata[sr['id']]['delta_pp']) < 0.02, (sr['id'], sr['value'], strata[sr['id']]['delta_pp'])
json.dump(out, open(ROOT / 'results.json', 'w'), indent=1)
print(f"cells {len(cells)} | calibration {len(cal)} | served value {meas.get('value')}")
for k, v in sorted(T.items()): print(f"  {k[0]} {k[1]:9} idempotent per state: {dict(sorted(v.items()))}")
for s, v in strata.items(): print(f"  stratum {s:11} legend {v['legend'][0]}/{v['legend'][1]} english {v['english'][0]}/{v['english'][1]} delta {v['delta_pp']:+.2f} pp")
for r in rows: print(f"  {r['target']:3} {r['what']:48} {r['observed']:>8}  {r['rule']:18} {'HELD' if r['held'] else ('MISS' if r['held'] is False else 'untestable')}")
print(f"held {out['held']} missed {out['missed']} untestable {out['untestable']}")
