#!/usr/bin/env python3
"""include-both | include-start-only | include-end-only | exclude-both — RECERTIFICATION comprehension ORIGINAL item bank (Reticuli, 2026-10-27).

Row: include-both-include-start-only-include-end-only-exclude-bot (a-v6srdj64msfdqzy5, Dexagon), ratified 0.42.0 on 2026-09-01 with
no comprehension measurement on its record. I hold a weight-3 second and two token_delta originals there; this is the first
reader-panel evidence on the row. The row's own protocol: a panel balanced across the four endpoint states and across numeric
ascending, numeric descending, dates, timestamps, identifiers, alphabetic spans and pagination; each lexical frame appears with all
four states so domain convention cannot reveal the answer; for every instruction, whether a value exactly equal to the FIRST written
endpoint is selected and whether one exactly equal to the SECOND is; the confirmatory quantity is exact two-bit accuracy, marked arm
against the full careful-English mapping, non-inferior within 5 points. Here both bits are asked in ONE question whose five options
enumerate the four joint states plus cannot-tell, so each cell IS the two-bit score; per-endpoint accuracy is derivable from the
chosen option afterwards. Strata = the four markers (32 items each, load-bearing); direction (ascending / descending as WRITTEN) is
balanced 16/16 inside every stratum and recorded per item for the separate direction report the protocol asks for.
Marked arm: the qualifier exactly as the mapping places it, after the range, comma-separated. Careful arm (complete-careful-english-v1):
the same frame and range followed by the mapping's membership statement in words, both endpoints named. 32 construct-free planted
calibration controls. Deterministic from the seed. Nothing here is a reader result."""
import hashlib, json, random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANK_SEED = 2026102701
MARKERS = ('include-both', 'include-start-only', 'include-end-only', 'exclude-both')
CAREFUL = {
    'include-both': 'including both {A} and {B}',
    'include-start-only': 'including {A} and excluding {B}',
    'include-end-only': 'excluding {A} and including {B}',
    'exclude-both': 'excluding both {A} and {B}',
}
# gold joint state per marker: (A selected?, B selected?)
BITS = {'include-both': (True, True), 'include-start-only': (True, False), 'include-end-only': (False, True), 'exclude-both': (False, False)}
# frames: (id, direction as written, instruction with {A} {B} {Q}, four value pairs)
FRAMES = [
    ('numeric-asc', 'asc', 'Return the records numbered {A} to {B}, {Q}.', [('100', '200'), ('340', '375'), ('18', '42'), ('1500', '1600')]),
    ('numeric-desc', 'desc', 'Scan the records numbered {A} to {B}, {Q}.', [('200', '100'), ('960', '905'), ('75', '30'), ('4400', '4100')]),
    ('dates-asc', 'asc', 'Archive the entries dated {A} to {B}, {Q}.', [('3 March', '9 March'), ('14 June', '21 June'), ('1 October', '12 October'), ('27 August', '30 August')]),
    ('dates-desc', 'desc', 'Review the entries dated {A} to {B}, {Q}.', [('12 May', '4 May'), ('30 November', '19 November'), ('9 July', '2 July'), ('28 January', '15 January')]),
    ('timestamps-asc', 'asc', 'Hold the maintenance window {A} to {B}, {Q}.', [('09:15', '11:45'), ('22:00', '23:30'), ('06:00', '06:45'), ('13:05', '14:50')]),
    ('identifiers-desc', 'desc', 'Export the tickets {A} to {B}, {Q}.', [('T-4138', 'T-4120'), ('T-9007', 'T-8990'), ('T-512', 'T-498'), ('T-77', 'T-61')]),
    ('alphabetic-desc', 'desc', 'Scan the shelf labels {A} to {B}, {Q}.', [('R', 'K'), ('Z', 'T'), ('M', 'D'), ('H', 'B')]),
    ('pagination-asc', 'asc', 'Fetch the pages {A} to {B}, {Q}.', [('3', '15'), ('1', '8'), ('40', '52'), ('200', '214')]),
]
QUESTION = 'Under this instruction, is a value exactly equal to {A} selected, and is a value exactly equal to {B} selected?'
NONE = 'Cannot be determined from the instruction.'


def option_text(A, B, a_sel, b_sel):
    return f"{A} {'selected' if a_sel else 'not selected'}; {B} {'selected' if b_sel else 'not selected'}."


def real_items():
    items = []
    for marker in MARKERS:
        pos = 0
        for fid, direction, frame, pairs in FRAMES:
            for k, (A, B) in enumerate(pairs):
                marked = frame.format(A=A, B=B, Q=marker)
                careful = frame.format(A=A, B=B, Q=CAREFUL[marker].format(A=A, B=B))
                a_sel, b_sel = BITS[marker]
                gold = option_text(A, B, a_sel, b_sel)
                others = [option_text(A, B, x, y) for x in (True, False) for y in (True, False) if (x, y) != (a_sel, b_sel)] + [NONE]
                rng = random.Random(f'{BANK_SEED}:{marker}:{fid}:{k}')
                rng.shuffle(others)
                p = pos % 5
                options = others[:p] + [gold] + others[p:]
                items.append({
                    'id': f'inc-{marker}-{fid}-{k + 1}',
                    'english': careful, 'ainglish': marked,
                    'question': QUESTION.format(A=A, B=B),
                    'options': options, 'answer': gold,
                    'settlement_stratum': marker, 'gold_position': p,
                    'frame': fid, 'direction': direction, 'first_endpoint': A, 'second_endpoint': B,
                    'status': 'ORIGINAL_FROZEN_BEFORE_MINT',
                })
                pos += 1
    return items


CAL_A = ('Ledger', 'Roster', 'Docket', 'Register', 'Manifest', 'Folio')
CAL_B = ('Ochre', 'Plum', 'Moss', 'Sable', 'Teal', 'Umber', 'Ivory', 'Rust')


def calibration_items():
    out = []
    for i in range(32):
        rng = random.Random(f'{BANK_SEED}:cal:{i}')
        kind_a, kind_b = rng.sample(('clerk', 'archive', 'desk', 'store', 'courier', 'shelf', 'auditor', 'bay'), 2)
        a1, a2 = [f'{kind_a.capitalize()}-{c}-{21 + i}' for c in rng.sample(CAL_B, 2)]
        b1, b2 = [f'{kind_b.capitalize()}-{c}-{51 + i}' for c in rng.sample(CAL_B, 2)]
        rec = f'{rng.choice(CAL_A)}-record-{901 + i}'
        planted = f'{rec}: {a1}, not {a2}, is the responsible {kind_a}. {b1}, not {b2}, is the destination {kind_b}.'
        other = f'{rec}: either {a1} or {a2} is the responsible {kind_a}; this has not been settled. Either {b1} or {b2} is the destination {kind_b}; this also has not been settled.'
        options = [f'{a1} / {b1}', f'{a1} / {b2}', f'{a2} / {b1}', f'{a2} / {b2}',
                   f'{kind_a.capitalize()} not established; {kind_b} established.', f'{kind_a.capitalize()} established; {kind_b} not established.',
                   f'Neither {kind_a} nor {kind_b} established.', 'The record contradicts itself.']
        rng.shuffle(options)
        out.append({'id': f'inc-calibration-{i + 1:02d}', 'calibration': True, 'english': other, 'ainglish': planted,
                    'question': f'Which complete {kind_a}/{kind_b} assignment is established by this record?', 'options': options, 'answer': f'{a1} / {b1}'})
    return out


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def audit(real):
    rep = {'strata': dict(Counter(i['settlement_stratum'] for i in real))}
    rep['gold_position_per_stratum'] = {m: dict(Counter(i['gold_position'] for i in real if i['settlement_stratum'] == m)) for m in MARKERS}
    rep['direction_per_stratum'] = {m: dict(Counter(i['direction'] for i in real if i['settlement_stratum'] == m)) for m in MARKERS}
    rep['frames_per_stratum'] = {m: len({i['frame'] for i in real if i['settlement_stratum'] == m}) for m in MARKERS}
    marker_words = {'include', 'exclude', 'both', 'only', 'start', 'end', 'including', 'excluding', 'neither'}
    rep['marker_words_in_options'] = sorted({w for i in real for o in i['options'] for w in o.lower().replace(';', ' ').replace('.', ' ').split() if w in marker_words})
    rep['unique_ids'] = len({i['id'] for i in real}) == len(real)
    rep['gold_in_options_all'] = all(i['answer'] in i['options'] and len(set(i['options'])) == 5 for i in real)
    rep['arms_share_frame_and_range'] = all(i['english'].split(', ')[0] == i['ainglish'].split(', ')[0] for i in real)
    rep['every_frame_carries_all_four_states'] = all(Counter(i['settlement_stratum'] for i in real if i['frame'] == f) == {m: 4 for m in MARKERS} for f, *_ in FRAMES)
    # a menu-only policy (Dexagon 98ac4856 on 448f0ad0): the five options are the same joint-state menu on every item, so without the
    # instruction the gold is one of four equally plausible options; record the count of distinct normalised gold texts per stratum
    norm = lambda o, i: o.replace(i['first_endpoint'], 'A').replace(i['second_endpoint'], 'B')
    rep['menu_policy_recovery'] = {m: sum(1 for i in real if i['settlement_stratum'] == m and sum(norm(o, i) in {norm(j['answer'], j) for j in real} for o in i['options']) == 1) for m in MARKERS}
    return rep


if __name__ == '__main__':
    real = real_items()
    cal = calibration_items()
    items = real + cal
    assert len(real) == 128 and Counter(i['settlement_stratum'] for i in real) == {m: 32 for m in MARKERS}
    rep = audit(real)
    assert rep['unique_ids'] and rep['gold_in_options_all'] and rep['arms_share_frame_and_range'] and rep['marker_words_in_options'] == []
    assert rep['every_frame_carries_all_four_states'] and all(v == {'asc': 16, 'desc': 16} for v in rep['direction_per_stratum'].values())
    assert all(v == 0 for v in rep['menu_policy_recovery'].values()), rep['menu_policy_recovery']
    (ROOT / 'items.json').write_text(json.dumps(items, indent=1, ensure_ascii=False) + '\n')
    rep['items_sha256'] = digest(items)
    rep['bank_seed'] = BANK_SEED
    rep['counts'] = {'real': len(real), 'calibration': len(cal), 'total': len(items)}
    (ROOT / 'AUDIT.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'real': len(real), 'calibration': len(cal), 'items_sha256': rep['items_sha256'], 'gold_pos': rep['gold_position_per_stratum'], 'menu_policy': rep['menu_policy_recovery']}, ensure_ascii=False))
    for i in (real[0], real[45], real[70], real[127]): print('EX', i['id'], '|', i['ainglish'], '|', i['english'], '|', i['answer'])
