#!/usr/bin/env python3
"""File-only audits of the replica bank. No inference, no network."""
import json, re, sys, hashlib
from collections import Counter
from fractions import Fraction
from pathlib import Path
ROOT = Path(__file__).resolve().parent
items = json.load(open(ROOT / 'items.json')); real = [i for i in items if not i.get('calibration')]
dex = json.load(open(ROOT.parent / 'items.json')); sat = json.load(open(ROOT.parent / 'sat_items.json'))
sat = sat.get('items', sat) if isinstance(sat, dict) else sat
report = {}
# 1. options-only shortcut: an options-only rule needs the form; check both forms' 4 records are present in every menu
def shapes(item):
    recs = item['probe_contract']['option_records']; gold = item['probe_contract']['gold']
    forms_present = {'choose-any': 0, 'draw-uniform': 0}
    for r in recs.values():
        forms_present['draw-uniform' if len(r['policies']) <= 2 else 'choose-any'] += 1
    return forms_present
bad = [i['id'] for i in real if set(shapes(i).values()) != {4}]
# form-agnostic best heuristic: always pick the record with max policies+min guarantees (choose-any-shaped gold) => accuracy
def heuristic(item):
    recs = item['probe_contract']['option_records']
    pick = max(recs.items(), key=lambda kv: (len(kv[1]['policies']), -len(kv[1]['guarantees'])))[0]
    return pick == item['answer']
acc = sum(heuristic(i) for i in real) / len(real)
report['options_only'] = {'menus_with_4_records_per_form': len(real) - len(bad), 'irregular_menus': bad, 'form_agnostic_heuristic_accuracy': acc}
# 2. request-removed cue: shared context must not contain form words
cues = re.compile(r'choose-any|draw-uniform|uniform|random|any member|equal', re.I)
leak = [i['id'] for i in real if cues.search(i['english'].split('\nRequest:')[0])]
report['request_removed_form_cue'] = {'contexts_with_cue': leak}
# 3. overlap with existing banks: identities, set refs, outsiders, world ids; and word 8-grams
def idents(bank):
    s = set()
    for i in bank:
        sw = i.get('semantic_world') or {}
        s |= set(sw.get('members', [])); s.add(sw.get('set_ref')); s.add(sw.get('outsider'))
        for m in re.findall(r'\b[A-Z][a-z]+-[0-9a-f]{5}\b', i.get('english', '')): s.add(m)
        for m in re.findall(r'\b[a-zA-Z]+-\d{3}-[A-Z]\b|\bSERV-SET-\d+-v\d\b|[A-Z]+-SET-\d+-v\d', i.get('english', '')): s.add(m)
    s.discard(None); return s
mine, dexi, sati = idents(items), idents(dex), idents(sat)
def grams(text, n=8):
    w = re.findall(r"[A-Za-z0-9'@:/.-]+", text.lower()); return {' '.join(w[k:k + n]) for k in range(len(w) - n + 1)}
def bank_grams(bank, field):
    g = set()
    for i in bank: g |= grams(i.get(field, ''))
    return g
ctx_mine = set(); [ctx_mine.update(grams(i['english'].split('\nRequest:')[0])) for i in real]
ctx_dex = set(); [ctx_dex.update(grams(i['english'].split('\nRequest:')[0])) for i in dex if not i.get('calibration')]
ctx_sat = set(); [ctx_sat.update(grams(i['english'].split('Request')[0])) for i in sat if not i.get('calibration')]
q_mine = bank_grams(real, 'question'); q_dex = bank_grams([i for i in dex if not i.get('calibration')], 'question')
report['overlap'] = {'identity_overlap_dexagon': sorted(mine & dexi)[:10], 'identity_overlap_saturnia': sorted(mine & sati)[:10],
                     'context_8gram_overlap_dexagon': len(ctx_mine & ctx_dex), 'context_8gram_overlap_saturnia': len(ctx_mine & ctx_sat),
                     'context_8grams_mine': len(ctx_mine),
                     'question_8gram_overlap_dexagon': len(q_mine & q_dex), 'question_8grams_mine': len(q_mine),
                     'shared_context_8grams_examples': sorted(ctx_mine & ctx_dex)[:5]}
# 4. semantic derivation from visible words (adapted to my phrasing)
errors = []
for it in real:
    w = it['semantic_world']; ctx = it['english'].split('\nRequest:')[0]
    m = re.search(r'identities, in recorded order: ([^.]+)\.', ctx); assert m and m[1].split(', ') == w['members'], it['id']
    s = re.search(r'scores, in the same order: ([^.]+)\.', ctx); assert s and list(map(int, s[1].split(', '))) == w['scores'], it['id']
    assert f'{w["outsider"]} is not in it.' in ctx and f'The reference {w["set_ref"]} resolves uniquely' in ctx and ctx.endswith('Each distinct identity is one member; repeated appearances do not create another member.'), it['id']
    meta = {p['label']: p for p in it['probe_contract']['policies']}
    for label, text in re.findall(r'^(P\d+): (.+)$', it['question'], flags=re.M):
        c = re.fullmatch(r'Returns (\S+) on every execution, with probability one\.', text)
        k = re.fullmatch(r'Returns (\S+), which has the unique lowest (.+) score, with probability one\.', text)
        u = re.fullmatch(r'Assigns probability (\d+/\d+) to each distinct listed identity before drawing and returning exactly one\.', text)
        g = re.fullmatch(r'Assigns probability (\d+/\d+) to (\S+) and (\d+/\d+) to each other listed identity, then returns one draw from that distribution\.', text)
        if c: dist = {c[1]: Fraction(1)}
        elif k: assert k[2] == w['criterion'] and k[1] == w['members'][w['scores'].index(min(w['scores']))]; dist = {k[1]: Fraction(1)}
        elif u: dist = {mm: Fraction(u[1]) for mm in w['members']}
        elif g: dist = {mm: Fraction(g[1] if mm == g[2] else g[3]) for mm in w['members']}
        else: raise AssertionError(text)
        assert dist == {mm: Fraction(v) for mm, v in meta[label]['distribution'].items()} and sum(dist.values()) == 1
        sat_ = set(dist).issubset(set(w['members']))
        if it['settlement_stratum'] == 'draw-uniform': sat_ = sat_ and all(dist.get(mm, 0) == Fraction(1, w['n']) for mm in w['members'])
        if sat_ != (label in it['probe_contract']['gold']['policies']): errors.append((it['id'], label))
    # guarantees gold
    gl = {gg['label']: gg['key'] for gg in it['probe_contract']['guarantees']}
    truth = {'one-eligible'} | ({'equal-odds'} if it['settlement_stratum'] == 'draw-uniform' else set())
    if {gl[x] for x in it['probe_contract']['gold']['guarantees']} != truth: errors.append((it['id'], 'guarantees'))
    assert it['answer'] in it['options'] and it['options'].count(it['answer']) == 1 and len(set(it['options'])) == 8
report['semantic_audit'] = {'items_checked': len(real), 'errors': errors}
# 5. answer position balance per form; member counts; frames
pos = {f: Counter(i['options'].index(i['answer']) for i in real if i['settlement_stratum'] == f) for f in ('choose-any', 'draw-uniform')}
report['answer_position_by_form'] = {f: dict(sorted(c.items())) for f, c in pos.items()}
report['member_count'] = dict(sorted(Counter(i['member_count'] for i in real).items()))
report['frames'] = len(set(i['frame_family'] for i in real))
cal = [i for i in items if i.get('calibration')]
report['calibration'] = {'n': len(cal), 'answer_in_options': all(i['answer'] in i['options'] for i in cal), 'planted_arm_states_answer': all(i['answer'].split(' / ')[0] in i['ainglish'] and i['answer'].split(' / ')[0] not in i['english'].replace('either '+i['answer'].split(' / ')[0], '') for i in cal), 'no_selection_vocab': not any(cues.search(i['english'] + i['ainglish']) for i in cal)}
report['items_sha256'] = hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
json.dump(report, open(ROOT / 'AUDIT.json', 'w'), indent=1)
print(json.dumps(report, indent=1)[:3000])
