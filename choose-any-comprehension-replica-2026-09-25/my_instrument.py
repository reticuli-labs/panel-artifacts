#!/usr/bin/env python3
"""Fresh-input replica bank for Dexagon's choose-any / draw-uniform comprehension original 04eb391d.
DESIGN IDENTICAL to dexagon-ai/ainglish-evidence choose-any-completion-2026-09-14/fresh-bank-v2/instrument.py
+ choose-any-final-package-2026-09-15/build.py (144 worlds, 72 per form, 12 per form/domain, member counts 2-8,
five policy kinds, four guarantee claims, common-eight-record menus, English arm = exact mapping SPAN with S->set_ref,
shared dedup sentence in both arms). INPUTS FRESH: new world/assignment seeds, disjoint identity names, new set-ref
scheme, new outsider label, new frames, new task families, reworded shared-context sentences. Probe vocabulary
(policy/claim sentences, question stem, option records) is kept verbatim: it is the probe, not the input.
No inference, no network."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib, json, random, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
WORLD_SEED = 2026092561
ASSIGNMENT_SEED = 2026092562
FORMS = ('choose-any', 'draw-uniform')
POLICIES = ('constant-first', 'criterion-based', 'unequal-weight', 'equal-probability', 'out-of-set')
GUARANTEES = ('one-eligible', 'equal-odds', 'crypto-unpredictable', 'cross-draw-independent')
DOMAINS = (
    ('service-routing', 'service endpoint', 'latency', (
        'a receipt-rendering call', 'a postcode lookup', 'a map-tile fetch', 'a session-refresh call', 'a price-quote request', 'a font-subset request')),
    ('reviewer-assignment', 'reviewer', 'queue length', (
        'a grant renewal', 'a code-audit report', 'a survey instrument', 'a preprint revision', 'a thesis chapter', 'a benchmark submission')),
    ('evaluation-item-selection', 'evaluation item', 'preparation cost', (
        'a summarisation evaluation slot', 'a tool-use evaluation slot', 'a calibration evaluation slot', 'a coding evaluation slot', 'a citation evaluation slot', 'a dialogue evaluation slot')),
    ('failover', 'standby node', 'activation cost', (
        'a stalled queue consumer', 'an unreachable metrics store', 'a crashed scheduler', 'a paused webhook relay', 'a degraded search shard', 'a halted backup agent')),
    ('content-choice', 'content item', 'retrieval cost', (
        'a landing-page banner slot', 'a newsletter header slot', 'a help-centre example slot', 'a release-note screenshot slot', 'a podcast intro slot', 'a museum label slot')),
    ('resource-allocation', 'worker', 'current load', (
        'a thumbnail-generation job', 'a ledger-reconciliation job', 'a spell-check job', 'a geocoding job', 'a log-rotation job', 'a dependency-scan job')),
)
FRAMES = (
    'A routing note about {task} is under review before it is acted on.',
    'Two operators are reading the same request concerning {task} and must agree what it asks.',
    'A change request has arrived for {task}; the on-call engineer is checking what it permits.',
    'A checklist item asks what the selection wording for {task} actually commits to.',
    'Before running anything, a planner writes down what the request about {task} requires.',
    'The runbook entry for {task} contains a selection instruction that needs interpreting.',
    'A reviewer is asked which procedures would comply with the request for {task}.',
    'A ticket about {task} is being triaged; the wording of its selection line matters.',
    'A compliance note distinguishes what the request for {task} permits from what it promises.',
    'A junior engineer asks a senior one what the instruction about {task} rules in and out.',
    'The dispatch log will record the interpretation of the request for {task}; nothing has run yet.',
    'An incident retrospective re-reads the original selection request for {task}.',
)
NAMES = ('Amber', 'Basalt', 'Cobalt', 'Dune', 'Elm', 'Flint', 'Gale', 'Heron',
         'Iris', 'Juniper', 'Kestrel', 'Lumen', 'Marsh', 'Nettle', 'Onyx', 'Pike')
DEDUP = ' Each distinct identity is one member; repeated appearances do not create another member.'
SPANS = json.loads((ROOT.parent / 'pkg' / 'rendering-contract.json').read_text())['spans']
SPAN_SHA = {'choose-any': 'adc546414cd979a5690b76505dfd7bea0004d651437fce4d1f3ac1d3fbae361b',
            'draw-uniform': '2571329e64a77bb4767b0951aa41068bdec0faf777b5c450158bc036ea317045'}
for f, s in SPANS.items(): assert hashlib.sha256(s.encode()).hexdigest() == SPAN_SHA[f], f

def canonical(v): return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
def digest(v): return hashlib.sha256(canonical(v)).hexdigest()

def permitted(form, world, distribution):
    p = {k: Fraction(v) for k, v in distribution.items()}
    assert sum(p.values()) == 1 and all(v >= 0 for v in p.values())
    if not {k for k, v in p.items() if v > 0}.issubset(set(world['members'])): return False
    if form == 'choose-any': return True
    return all(p.get(m, 0) == Fraction(1, world['n']) for m in world['members'])

def neutral_world(domain_index, local_index):
    domain, member_type, criterion, tasks = DOMAINS[domain_index]
    wid = f'rt1-world-{domain_index + 1:02d}-{local_index + 1:02d}'
    rng = random.Random(f'{WORLD_SEED}:{wid}')
    n = 2 + (local_index + 3 * domain_index) % 7
    suffix = hashlib.sha256(wid.encode()).hexdigest()[:5]
    members = [f'{name}-{suffix}' for name in rng.sample(NAMES, n)]
    outsider = 'Excluded-' + suffix
    scores = rng.sample(range(2, 97), n)
    if scores.index(min(scores)) == 0: scores[0], scores[-1] = scores[-1], scores[0]
    high_weight = 2 + local_index % 3
    weighted_index = rng.randrange(n)
    denominator = n - 1 + high_weight
    ref = 'roster-' + suffix + '@snapshot-1'
    task = tasks[local_index % len(tasks)]
    frame = local_index % len(FRAMES)
    common = (FRAMES[frame].format(task=task) + '\n'
              f'The frozen roster lists these eligible {member_type} identities, in recorded order: {", ".join(members)}. '
              f'Recorded {criterion} scores, in the same order: {", ".join(map(str, scores))}. '
              f'The reference {ref} resolves uniquely to this finite, nonempty snapshot of distinct identities. '
              f'The snapshot was fixed before any selection, and {outsider} is not in it. '
              'Nothing else has been required of the selection, and no outcome has been observed yet.')
    world = {'id': wid, 'domain': domain, 'frame_family': f'rt1-frame-{frame:02d}', 'task_family': task, 'n': n,
             'members': members, 'outsider': outsider, 'scores': scores, 'criterion': criterion, 'set_ref': ref,
             'context': common, 'weighted_index': weighted_index, 'high_weight': high_weight}
    minimum = members[scores.index(min(scores))]
    policies = [
        {'kind': 'constant-first', 'text': f'Returns {members[0]} on every execution, with probability one.', 'distribution': {members[0]: '1'}},
        {'kind': 'criterion-based', 'text': f'Returns {minimum}, which has the unique lowest {criterion} score, with probability one.', 'distribution': {minimum: '1'}},
        {'kind': 'unequal-weight', 'text': f'Assigns probability {high_weight}/{denominator} to {members[weighted_index]} and 1/{denominator} to each other listed identity, then returns one draw from that distribution.',
         'distribution': {x: str(Fraction(high_weight if j == weighted_index else 1, denominator)) for j, x in enumerate(members)}},
        {'kind': 'equal-probability', 'text': f'Assigns probability 1/{n} to each distinct listed identity before drawing and returning exactly one.', 'distribution': {x: str(Fraction(1, n)) for x in members}},
        {'kind': 'out-of-set', 'text': f'Returns {outsider} on every execution, with probability one.', 'distribution': {outsider: '1'}},
    ]
    guarantees = [
        {'key': 'one-eligible', 'text': 'Exactly one identity is returned, and it belongs to the frozen eligible set.'},
        {'key': 'equal-odds', 'text': 'Before this selection, every distinct eligible identity has the same probability of being returned.'},
        {'key': 'crypto-unpredictable', 'text': 'A well-informed adversary cannot predict the result better than chance.'},
        {'key': 'cross-draw-independent', 'text': 'Learning this result leaves the probability distribution of a later selection unchanged.'},
    ]
    rng.shuffle(policies); rng.shuffle(guarantees)
    for i, p in enumerate(policies, 1): p['label'] = 'P' + str(i)
    for i, g in enumerate(guarantees, 1): g['label'] = 'G' + str(i)
    policy_contrast = POLICIES[(local_index + domain_index) % 5]
    guarantee_contrasts = {form: GUARANTEES[(local_index + domain_index + j) % 4] for j, form in enumerate(FORMS)}
    gold, profiles = {}, []
    for form in FORMS:
        allowed = {p['label'] for p in policies if permitted(form, world, p['distribution'])}
        true_keys = {'one-eligible'} | ({'equal-odds'} if form == 'draw-uniform' else set())
        established = {g['label'] for g in guarantees if g['key'] in true_keys}
        gold[form] = {'policies': sorted(allowed), 'guarantees': sorted(established)}
        toggle_p = next(p['label'] for p in policies if p['kind'] == policy_contrast)
        toggle_g = next(g['label'] for g in guarantees if g['key'] == guarantee_contrasts[form])
        for pset in (allowed, allowed ^ {toggle_p}):
            for gset in (established, established ^ {toggle_g}):
                profiles.append({'policies': sorted(pset), 'guarantees': sorted(gset)})
    rng.shuffle(profiles)
    label = lambda r: 'Implementations: ' + (', '.join(r['policies']) or 'none') + '; claims: ' + (', '.join(r['guarantees']) or 'none') + '.'
    options = [label(r) for r in profiles]; assert len(set(options)) == 8
    question = ('Evaluate two complete lists: implementations that satisfy the request, and claims that follow from the request itself. '
                'Select the answer record containing BOTH complete lists. A permitted procedure may have extra properties that the request does not guarantee.\n\n'
                'Candidate implementations (each returns exactly once):\n' + '\n'.join(p['label'] + ': ' + p['text'] for p in policies) +
                '\n\nClaims an auditor might make:\n' + '\n'.join(g['label'] + ': ' + g['text'] for g in guarantees))
    world.update(question=question, options=options, option_records=dict(zip(options, profiles)), policies=policies,
                 guarantees=guarantees, gold_by_form=gold, policy_contrast=policy_contrast, guarantee_contrasts=guarantee_contrasts)
    return world

def neutral_bank(): return [neutral_world(d, i) for i in range(24) for d in range(6)]

def assign(worlds):
    """12/12 per domain AND, as in the original's balanced assignment, every (domain, member_count) cell split
    1-2 per form with each member count 10-11 per form globally. Per-domain rejection sampling from ONE seeded
    stream (accept a domain's split when its cell rule holds), then the global rule; if the global rule fails,
    all domains are redrawn. Draw counts are recorded. No reader ever saw any assignment, so nothing here is
    outcome-based selection."""
    by_domain = {d: sorted(w['id'] for w in worlds if w['domain'] == d) for d, *_ in DOMAINS}
    n_of = {w['id']: w['n'] for w in worlds}
    rng = random.Random(f'{ASSIGNMENT_SEED}:balanced')
    draws = {'rounds': 0, 'per_domain': {}}
    for _round in range(1, 1000):
        draws['rounds'] = _round
        mapping = {}
        for d, ids in by_domain.items():
            for k in range(1, 100000):
                ids2 = list(ids); rng.shuffle(ids2)
                m = {wid: FORMS[i // 12] for i, wid in enumerate(ids2)}
                cells = Counter((n_of[w], f) for w, f in m.items())
                if all(1 <= cells.get((n, f), 0) <= 2 for n in range(2, 9) for f in FORMS if any(n_of[w] == n for w in ids)):
                    mapping.update(m); draws['per_domain'][d] = draws['per_domain'].get(d, 0) + k; break
            else:
                raise RuntimeError('domain ' + d + ' infeasible')
        glob = Counter((n_of[w], f) for w, f in mapping.items())
        if all(10 <= glob.get((n, f), 0) <= 11 for n in range(2, 9) for f in FORMS):
            mapping['_draws'] = draws
            return mapping
    raise RuntimeError('no balanced assignment found')

def render(world, form):
    gold = world['gold_by_form'][form]
    answer, = [l for l, r in world['option_records'].items() if r == gold]
    context = world['context'] + DEDUP
    expansion = re.sub(r'\bS\b', lambda _: world['set_ref'], SPANS[form])
    return {'id': world['id'], 'english': context + '\nRequest: ' + expansion,
            'ainglish': context + f'\nRequest: {form}({world["set_ref"]}).',
            'question': world['question'], 'options': deepcopy(world['options']), 'answer': answer,
            'settlement_stratum': form, 'domain': world['domain'], 'frame_family': world['frame_family'],
            'member_count': world['n'], 'world_id': world['id'],
            'semantic_world': {k: deepcopy(world[k]) for k in ('n', 'members', 'outsider', 'scores', 'criterion', 'set_ref')},
            'probe_contract': {'kind': 'common-eight-record-complete-lists-v2', 'option_records': deepcopy(world['option_records']),
                               'policies': deepcopy(world['policies']), 'guarantees': deepcopy(world['guarantees']), 'gold': deepcopy(gold)},
            'status': 'REPLICA_FRESH_INPUT_FROZEN_BEFORE_MINT'}

CAL_A = ('Ledger', 'Vault', 'Docket', 'Manifest', 'Roster', 'Charter', 'Registry', 'Folio')
CAL_B = ('Teal', 'Umber', 'Slate', 'Ochre', 'Sable', 'Rust', 'Moss', 'Plum', 'Lilac', 'Fawn', 'Jade', 'Coral')
def calibration_items():
    """Construct-free planted-effect controls, planted arm = ainglish (facts resolved), english arm leaves both unresolved.
    Same shape as the original's controls (two attributes, eight options); fresh names; no selection vocabulary."""
    out = []
    for i in range(32):
        rng = random.Random(f'{WORLD_SEED}:cal:{i}')
        kind_a, kind_b = rng.sample(('clerk', 'archive', 'desk', 'store', 'courier', 'shelf', 'auditor', 'bay'), 2)
        a1, a2 = [f'{kind_a.capitalize()}-{c}-{61 + i}' for c in rng.sample(CAL_B, 2)]
        b1, b2 = [f'{kind_b.capitalize()}-{c}-{81 + i}' for c in rng.sample(CAL_B, 2)]
        rec = f'{rng.choice(CAL_A)}-record-{501 + i}'
        planted = f'{rec}: {a1}, not {a2}, is the responsible {kind_a}. {b1}, not {b2}, is the destination {kind_b}.'
        other = f'{rec}: either {a1} or {a2} is the responsible {kind_a}; this has not been settled. Either {b1} or {b2} is the destination {kind_b}; this also has not been settled.'
        options = [f'{a1} / {b1}', f'{a1} / {b2}', f'{a2} / {b1}', f'{a2} / {b2}',
                   f'{kind_a.capitalize()} not established; {kind_b} established.', f'{kind_a.capitalize()} established; {kind_b} not established.',
                   f'Neither {kind_a} nor {kind_b} established.', 'The record contradicts itself.']
        rng.shuffle(options)
        out.append({'id': f'rt1-calibration-{i + 1:02d}', 'calibration': True, 'english': other, 'ainglish': planted,
                    'question': f'Which complete {kind_a}/{kind_b} assignment is established by this record?', 'options': options, 'answer': f'{a1} / {b1}'})
    return out

if __name__ == '__main__':
    worlds = neutral_bank(); mapping = assign(worlds); draw_index = mapping.pop('_draws')
    items = [render(w, mapping[w['id']]) for w in worlds] + calibration_items()
    real = [i for i in items if not i.get('calibration')]
    assert len(real) == 144 and Counter(i['settlement_stratum'] for i in real) == {'choose-any': 72, 'draw-uniform': 72}
    assert all(v == 12 for v in Counter((i['domain'], i['settlement_stratum']) for i in real).values())
    (ROOT / 'items.json').write_text(json.dumps(items, indent=1, ensure_ascii=False) + '\n')
    (ROOT / 'neutral-worlds.json').write_text(json.dumps({'world_seed': WORLD_SEED, 'assignment_seed': ASSIGNMENT_SEED, 'assignment_draw_index': draw_index, 'assignment_rule': 'first seeded draw with 12/12 per domain, 1-2 per form per (domain, member_count) cell, 10-11 per form per member_count globally', 'worlds_sha256': digest(worlds), 'mapping': mapping}, indent=1) + '\n')
    print(json.dumps({'items': len(items), 'real': len(real), 'calibration': len(items) - len(real), 'items_sha256': digest(items), 'worlds_sha256': digest(worlds)}))
