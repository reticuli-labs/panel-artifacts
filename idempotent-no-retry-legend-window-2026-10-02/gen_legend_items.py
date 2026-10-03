#!/usr/bin/env python3
"""Legend-window items for `idempotent` / `no-retry` (plan.md in this directory, written before any read).

Inputs, all inside this directory: `base_items.json` = the frozen 2026-09-25 item bank (copied verbatim from
../idempotent-no-retry-comprehension-2026-09-25/items.json; sha256 asserted below). Real items keep their English arm,
question, options, gold and ids; the marked arm gains ONE legend line after the header line, verbatim from plan.md.
Calibration controls are regenerated with a fresh seed (same construct-free design as the 2026-09-25 instrument).
Writes items.json + AUDIT.json beside this file. Deterministic.
"""
import hashlib, json, random, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE_SHA = '94c7c36d99cae4945a9788b4eb67daed4a13a88a34b51a513283bb22ab9f461b'
CAL_SEED = 2026100301
LEGEND = {
    'idempotent': "Legend — <ACTION>, idempotent: re-executing it cannot change the outcome beyond the first run's effect; on ambiguous timeout, re-running is safe.",
    'no-retry': 'Legend — <ACTION>, no-retry: a repeated execution would materially change the outcome (double charge, duplicate message, corrupted state); on ambiguous completion, verify state or escalate instead of re-running.',
}
CAL_A = ('Ledger', 'Roster', 'Docket', 'Register', 'Manifest', 'Folio')
CAL_B = ('Ochre', 'Plum', 'Moss', 'Sable', 'Teal', 'Umber', 'Ivory', 'Rust')


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def tag_of(marked):
    has_i, has_n = ', idempotent' in marked, ', no-retry' in marked
    assert has_i != has_n, 'exactly one tag per item'
    return 'idempotent' if has_i else 'no-retry'


def legend_item(item):
    lines = item['ainglish'].split('\n')
    assert lines[0] == item['english'].split('\n')[0], 'arms must share the header line'
    tag = tag_of(item['ainglish'])
    out = dict(item)
    out['ainglish'] = '\n'.join([lines[0], LEGEND[tag]] + lines[1:])
    out['legend_tag'] = tag
    out['status'] = 'LEGEND_ARM_FROZEN_BEFORE_MINT'
    return out


def calibration_items():
    out = []
    for i in range(32):
        rng = random.Random(f'{CAL_SEED}:cal:{i}')
        kind_a, kind_b = rng.sample(('clerk', 'archive', 'desk', 'store', 'courier', 'shelf', 'auditor', 'bay'), 2)
        a1, a2 = [f'{kind_a.capitalize()}-{c}-{41 + i}' for c in rng.sample(CAL_B, 2)]
        b1, b2 = [f'{kind_b.capitalize()}-{c}-{61 + i}' for c in rng.sample(CAL_B, 2)]
        rec = f'{rng.choice(CAL_A)}-record-{801 + i}'
        planted = f'{rec}: {a1}, not {a2}, is the responsible {kind_a}. {b1}, not {b2}, is the destination {kind_b}.'
        other = f'{rec}: either {a1} or {a2} is the responsible {kind_a}; this has not been settled. Either {b1} or {b2} is the destination {kind_b}; this also has not been settled.'
        options = [f'{a1} / {b1}', f'{a1} / {b2}', f'{a2} / {b1}', f'{a2} / {b2}',
                   f'{kind_a.capitalize()} not established; {kind_b} established.', f'{kind_a.capitalize()} established; {kind_b} not established.',
                   f'Neither {kind_a} nor {kind_b} established.', 'The record contradicts itself.']
        rng.shuffle(options)
        out.append({'id': f'inr-legend-calibration-{i + 1:02d}', 'calibration': True, 'english': other, 'ainglish': planted,
                    'question': f'Which complete {kind_a}/{kind_b} assignment is established by this record?', 'options': options, 'answer': f'{a1} / {b1}'})
    return out


def audit(real, base_real):
    rep = {'strata': dict(Counter(i['settlement_stratum'] for i in real))}
    rep['legend_tag_per_stratum'] = {f: dict(Counter(i['legend_tag'] for i in real if i['settlement_stratum'] == f)) for f in rep['strata']}
    # instrument check (admissibility gate): legend line present exactly once, as line 2, and nowhere else; English arm untouched
    rep['legend_line_exactly_once'] = all(i['ainglish'].count(LEGEND[i['legend_tag']]) == 1 and i['ainglish'].split('\n')[1] == LEGEND[i['legend_tag']] for i in real)
    rep['legend_absent_from_english'] = all('Legend' not in i['english'] for i in real)
    rep['english_arm_identical_to_base'] = all(a['english'] == b['english'] for a, b in zip(real, base_real))
    rep['marked_arm_is_base_plus_one_line'] = all(a['ainglish'].split('\n')[:1] + a['ainglish'].split('\n')[2:] == b['ainglish'].split('\n') for a, b in zip(real, base_real))
    rep['cold_tag_still_present'] = all((', ' + i['legend_tag']) in '\n'.join(i['ainglish'].split('\n')[2:]) for i in real)
    rep['ids_gold_options_identical_to_base'] = all((a['id'], a['answer'], a['options'], a['gold_key'], a['gold_position'], a['question']) == (b['id'], b['answer'], b['options'], b['gold_key'], b['gold_position'], b['question']) for a, b in zip(real, base_real))
    rep['legend_sha256'] = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in LEGEND.items()}
    return rep


if __name__ == '__main__':
    raw = (ROOT / 'base_items.json').read_bytes()
    base = json.loads(raw)
    assert digest(base) == BASE_SHA, 'base bank drifted'  # canonical item-list digest, as the 2026-09-25 AUDIT records it
    base_real = [i for i in base if not i.get('calibration')]
    assert len(base_real) == 120
    real = [legend_item(i) for i in base_real]
    cal = calibration_items()
    items = real + cal
    rep = audit(real, base_real)
    assert all(rep[k] for k in ('legend_line_exactly_once', 'legend_absent_from_english', 'english_arm_identical_to_base', 'marked_arm_is_base_plus_one_line', 'cold_tag_still_present', 'ids_gold_options_identical_to_base')), rep
    assert len({i['id'] for i in items}) == len(items) == 152
    (ROOT / 'items.json').write_text(json.dumps(items, indent=1, ensure_ascii=False) + '\n')
    rep['items_sha256'] = digest(items)
    rep['base_items_sha256'] = BASE_SHA
    rep['calibration_seed'] = CAL_SEED
    rep['counts'] = {'real': len(real), 'calibration': len(cal), 'total': len(items)}
    (ROOT / 'AUDIT.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({k: rep[k] for k in ('counts', 'items_sha256', 'legend_tag_per_stratum', 'legend_line_exactly_once', 'english_arm_identical_to_base')}, ensure_ascii=False))
