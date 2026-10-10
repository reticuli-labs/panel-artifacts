#!/usr/bin/env python3
"""rate-cap / stock-cap consequence bank (plan.md in this directory, committed first). Deterministic.

Writes: items_filed.json (128 room items + 32 calibration), items_bare.json (same scenarios, bare arm, entailment key),
items_permission.json (128 permission items + calibration), items_undisclosed.json (16 + calibration), keys.json, AUDIT.json,
MANIFEST.sha256. Every assertion below is a rule from plan.md; a failed assertion means the generator disagrees with the plan.
"""
import hashlib, json, random, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 2026101001
MAPPING = (ROOT / 'mapping_verbatim.txt').read_text(encoding='utf-8')
assert hashlib.sha256(MAPPING.encode()).hexdigest().startswith('f156627d90c46635'), 'mapping drifted from plan.md'
CD = 'Cannot determine from the statement and the facts'
NUM = {0: 'no', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
       12: 'twelve', 15: 'fifteen', 16: 'sixteen', 20: 'twenty', 24: 'twenty-four', 30: 'thirty', 40: 'forty', 50: 'fifty', 60: 'sixty'}
MIN = {'hour': 60, 'day': 1440, 'minute': 1, 'week': 10080}
AGE = {'hour': ('minutes', 60), 'day': ('hours', 24), 'minute': ('seconds', 60), 'week': ('days', 7)}
SG = {'requests': 'request', 'snapshots': 'snapshot', 'activations': 'activation', 'connections': 'connection', 'messages': 'message', 'permits': 'permit', 'retries': 'retry', 'reservations': 'reservation', 'seats': 'seat', 'vehicles': 'vehicle'}
BOUNDARY = {'hour': 'the top of the hour', 'day': 'midnight', 'minute': 'the top of the minute', 'week': 'the start of Monday'}
TIME = {'hour': 'The current time is 10:40.', 'day': 'The current time is 14:00 on Wednesday.', 'minute': 'The current time is 10:40:30.', 'week': 'Today is Wednesday.'}


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


# ---------------------------------------------------------------- domains
DOMAINS = [
    dict(key='api', header='Service note, API budget.', actor='this client', other='another client',
         rate=dict(noun='requests', window='hour', act='make a request', past='made'),
         stock=dict(noun='requests', set='in-flight requests by this client', member='in-flight request', members='in-flight requests', scope='per-identity', act='start a request')),
    dict(key='storage', header='Storage policy note.', actor='the backup agent', other='the archive agent',
         rate=dict(noun='snapshots', window='day', act='take a snapshot', past='took'),
         stock=dict(noun='snapshots', set='retained snapshots of volume V', member='retained snapshot of volume V', members='retained snapshots of volume V', scope='global', act='retain a snapshot')),
    dict(key='seats', header='Licensing note.', actor='team T', other='team U',
         rate=dict(noun='activations', window='day', act='activate a licence', past='performed'),
         stock=dict(noun='seats', set='active seats held by team T', member='active seat held by team T', members='active seats held by team T', scope='per-identity', act='claim a seat')),
    dict(key='connections', header='Connection pool note.', actor='worker A', other='worker B',
         rate=dict(noun='connections', window='minute', act='open a connection', past='opened'),
         stock=dict(noun='connections', set='open connections owned by worker A', member='open connection owned by worker A', members='open connections owned by worker A', scope='per-identity', act='open a connection')),
    dict(key='messages', header='Messaging note.', actor='this sender', other='another sender',
         rate=dict(noun='messages', window='day', act='send a message', past='sent'),
         stock=dict(noun='messages', set='queued messages in mailbox M', member='queued message in mailbox M', members='queued messages in mailbox M', scope='global', act='queue a message')),
    dict(key='permits', header='Parking office note.', actor='this permit holder', other='another permit holder',
         rate=dict(noun='permits', window='week', act='issue a permit', past='issued'),
         stock=dict(noun='vehicles', set='vehicles parked in bay set B', member='vehicle parked in bay set B', members='vehicles parked in bay set B', scope='global', act='park a vehicle')),
    dict(key='retries', header='Retry policy note.', actor='job J', other='job K',
         rate=dict(noun='retries', window='hour', act='schedule a retry', past='scheduled'),
         stock=dict(noun='retries', set='pending retries for job J', member='pending retry for job J', members='pending retries for job J', scope='per-identity', act='schedule a retry')),
    dict(key='memory', header='Memory reservation note.', actor='service S', other='service U',
         rate=dict(noun='reservations', window='minute', act='take a reservation', past='took'),
         stock=dict(noun='reservations', set='held reservations in pool R', member='held reservation in pool R', members='held reservations in pool R', scope='global', act='take a reservation')),
]
ALIGN_CYCLE = ['per-clock', 'per-any', 'none']


def plural(member, n):
    raise RuntimeError('use mem()')


def mem(d, n):
    return d['stock']['member'] if n == 1 else d['stock']['members']


def room_phrase(r, N):
    if r == 0:
        return 'No room for another'
    if r == N:
        return f'Room for the full allowance of {NUM[N]}'
    return f'Room for {NUM[r]} more'


def room_options(gold, N, rng):
    """Five options: four room sentences including the gold when numeric, plus the unknown option."""
    cands = []
    for r in (0, 1, 2, 3, N - 1, N, gold if isinstance(gold, int) else None):
        if r is None or r < 0 or r > N:
            continue
        p = room_phrase(r, N)
        if p not in cands:
            cands.append(p)
    if isinstance(gold, int):
        g = room_phrase(gold, N)
        others = [c for c in cands if c != g]
        rng.shuffle(others)
        chosen = [g] + others[:3]
    else:
        rng.shuffle(cands)
        chosen = cands[:4]
    rng.shuffle(chosen)
    opts = chosen + [CD]
    assert len(set(o.casefold() for o in opts)) == 5, opts
    return opts


BOUNDARY_OPTS = ['Yes, both bursts can be legal', 'No, at most one of the two bursts can be legal',
                 'Only the burst before the boundary can be legal', 'Only the burst after the boundary can be legal', CD]
EXIST_OPTS = lambda N: [f'Exactly {NUM[N]} exist now', f'Fewer than {NUM[N]} exist now', f'More than {NUM[N]} exist now', 'None exist now', CD]


def perm_options(actor, act):
    return [f'Yes, {actor} is authorised to {act}', f'No, {actor} is not authorised to {act}',
            f'Only while room remains under the cap', f'Only once the window has passed', CD]


# ---------------------------------------------------------------- statements
def reg_rate(d, N, align):
    s = f"{d['rate']['noun']} rate-cap({N}; {d['rate']['window']})."
    if align != 'none':
        s += f" {align}({d['rate']['window']})."
    return s


def reg_stock(d, N):
    return f"{d['stock']['noun']} stock-cap({N}; {d['stock']['set']})."


def en_rate(d, N, align):
    w = d['rate']['window']
    tail = {'none': f'whether the {w} is clock-aligned or sliding is not stated.',
            'per-clock': f'the count restarts at each clock {w} boundary.',
            'per-any': f'the window slides, so any span of one {w} counts.'}[align]
    return f"At most {N} {d['rate']['noun']} in each {w}; capacity returns as the {w} passes; {tail}"


def en_stock(d, N):
    return (f"At most {N} {d['stock']['set']} may exist at one time; room returns only when one of them leaves that set "
            f"by closing, release, deletion, consumption or expiry, however long one waits.")


def bare_rate(d, N):
    return f"A limit of {N} {d['rate']['noun']} per {d['rate']['window']}."


def bare_stock(d, N):
    return f"A limit of {N} {d['stock']['set']}."


def scope_line(d, kind):
    if kind == 'rate':
        return f"Budget for {d['actor']} only." if d['stock']['scope'] == 'per-identity' else f"Budget shared by every actor on this service."
    return ''


def arms(d, statement_reg, statement_en, statement_bare, facts, scope):
    head = d['header'] + (' ' + scope if scope else '')
    facts = [re.sub(r'(^|\. )([a-z])', lambda m: m.group(1) + m.group(2).upper(), f) for f in facts]
    fact_block = 'Counts below are as of now, before any further action.\n' + '\n'.join(facts)
    return {
        'ainglish': f"{head}\n{statement_reg}\n{fact_block}",
        'english': f"{head}\nRegister definition: {MAPPING}\n{statement_en}\n{fact_block}",
        'bare': f"{head}\n{statement_bare}\n{fact_block}",
    }


# ---------------------------------------------------------------- scenarios
def rate_scenarios(d, di, rng):
    r = d['rate']; w = r['window']; m = MIN[w]; noun = r['noun']; actor = d['actor']; out = []
    N = [4, 5, 6, 8, 3, 10, 5, 6][di]
    scope = 'per-identity' if di % 2 == 0 else 'global'
    scope_txt = f"Budget for {actor} only." if scope == 'per-identity' else "Budget shared by every actor on this service."
    U = AGE[w][1]; unit = AGE[w][0]
    def ages(ks):
        parts = [f'{k} {unit if k != 1 else unit[:-1]}' for k in ks]
        return parts[0] if len(parts) == 1 else ', '.join(parts[:-1]) + ' and ' + parts[-1]
    # r1 wait, exhausted, alignment none, permission granted
    f = [f"In the preceding {w}, {actor} {r['past']} {NUM[N]} {noun}.", f"{actor} holds an authorisation to {r['act']} that runs until the end of today."]
    out.append(dict(idx=1, probe='wait', align='none', N=N, facts=f, gold=N, classes=['waiting-returns-rate'], permission='granted',
                    q=f"If {actor} waits one full {w} from now and does nothing else, how much room is there under this cap then?"))
    # r2 wait, exhausted, per-clock
    f = [f"In the current clock {w}, {actor} {r['past']} {NUM[N]} {noun}."]
    out.append(dict(idx=2, probe='wait', align='per-clock', N=N, facts=f, gold=N, classes=['waiting-returns-rate', 'boundary-known'], permission='none',
                    q=f"If {actor} waits one full {w} from now and does nothing else, how much room is there under this cap then?"))
    # r3 release, per-any, k within window; closing an item returns nothing
    k = max(1, N - 2); a = [max(1, U // 6) + i * max(1, U // 12) for i in range(k)]
    f = [f"In the preceding {w}, {actor} {r['past']} {NUM[k]} {noun}, aged {ages(a)}.", f"Just now, {actor} closed one of those {noun}; nothing else changed."]
    out.append(dict(idx=3, probe='release', align='per-any', N=N, facts=f, gold=N - k, classes=['release-useless-for-rate', 'boundary-known'], permission='none',
                    q=f"How much room is there under this cap now, immediately after that closure?"))
    # r4 delete, alignment none, ages well inside the window either way, permission denied
    k = min(N - 1, 2); a = [max(1, U // 10), max(2, U // 6)][:k]
    f = [f"In the preceding {w}, {actor} {r['past']} {NUM[k]} {noun}, aged {ages(a)}.", TIME[w],
         f"Just now, {actor} deleted an older {SG[noun]} that it {r['past']} last week; nothing else changed.", f"{actor}'s authorisation to {r['act']} was revoked this morning and has not been restored."]
    out.append(dict(idx=4, probe='delete', align='none', N=N, facts=f, gold=N - k, classes=['delete-useless-for-rate'], permission='denied',
                    q=f"How much room is there under this cap now, immediately after that deletion?"))
    # r5 count determinate with scope test, per-any: some aged out, some inside; another actor's usage
    inside = min(N - 1, 2); aged = 2; a_in = [max(1, U // 10), max(2, U // 5)][:inside]; a_out = [U + U // 2, 2 * U]
    other_k = 3
    f = [f"{actor} {r['past']} {NUM[inside + aged]} {noun}: {NUM[inside]} of them {ages(a_in)} ago, and {NUM[aged]} of them {ages(a_out)} ago.",
         f"{d['other']} {r['past']} {NUM[other_k]} {noun} in the preceding {w}."]
    gold = N - inside if scope == 'per-identity' else max(0, N - inside - other_k)
    out.append(dict(idx=5, probe='count', align='per-any', N=N, facts=f, gold=gold, classes=['scope-' + scope, 'boundary-known'], permission='none',
                    q=f"How much room is there under this cap for {actor} now?"))
    # r6 ceiling-not-count: how many exist
    f = [f"Only this cap is stated. No count of {noun} is given."]
    out.append(dict(idx=6, probe='count', align='none', N=N, facts=f, gold=CD, classes=['ceiling-not-count'], permission='none',
                    q=f"How many {noun} exist now?", opts=EXIST_OPTS(N)))
    # r7 boundary: alignment cycles
    align = ALIGN_CYCLE[di % 3]
    f = [f"The {w} boundary falls at {BOUNDARY[w]}. {actor} plans {NUM[N]} {noun} just before the boundary and {NUM[N]} more just after it, with nothing else {r['past']} in the surrounding span."]
    gold = {'per-clock': BOUNDARY_OPTS[0], 'per-any': BOUNDARY_OPTS[1], 'none': CD}[align]
    out.append(dict(idx=7, probe='boundary', align=align, N=N, facts=f, gold=gold, classes=['boundary-known' if align != 'none' else 'boundary-unknown'], permission='none',
                    q=f"Can both planned bursts be legal under this cap?", opts=BOUNDARY_OPTS))
    # r8 mixed, rate decides: rate exhausted inside the window, stock has room
    N2 = 5; held = N2 - 2; k = N; a = [max(1, U // 6) + i * max(1, U // 20) for i in range(k)]
    f = [f"In the preceding {w}, {actor} {r['past']} {NUM[k]} {noun}, aged {ages(a)}.", f"{NUM[held].capitalize()} {mem(d, held)} exist now."]
    out.append(dict(idx=8, probe='count', align='per-any', N=N, N2=N2, facts=f, gold=0, classes=['mixed-rate-decides', 'boundary-known'], permission='none', mixed=True,
                    q=f"How much room is there now for one additional {SG[noun]} under both constraints together?"))
    return out, scope_txt


def stock_scenarios(d, di, rng):
    s = d['stock']; noun = s['noun']; actor = d['actor']; member = s['member']; out = []
    N = [3, 4, 5, 3, 6, 4, 5, 8][di]
    # s1 wait, held = N, no membership change: room 0
    f = [f"{NUM[N].capitalize()} {mem(d, N)} exist now.", f"{actor} waits twenty minutes and does nothing else; no membership of the named set changes in that time."]
    out.append(dict(idx=1, probe='wait', N=N, facts=f, gold=0, classes=['waiting-useless-for-stock'], permission='none',
                    q=f"How much room is there under this cap after those twenty minutes?"))
    # s2 wait with expiry: one member leaves by expiry
    f = [f"{NUM[N].capitalize()} {mem(d, N)} exist now.", f"Exactly one of them is scheduled to expire and leave the named set in twenty minutes. {actor} waits twenty minutes and does nothing else; nothing else changes."]
    out.append(dict(idx=2, probe='wait', N=N, facts=f, gold=1, classes=['expiry-member-leaves'], permission='none',
                    q=f"How much room is there under this cap after those twenty minutes?"))
    # s3 release: held k, one released; permission granted
    k = N - 1
    f = [f"{NUM[k].capitalize()} {mem(d, k)} exist now.", f"Just now, {actor} released one of them; nothing else changed.", f"{actor} holds an authorisation to {s['act']} that runs until the end of today."]
    out.append(dict(idx=3, probe='release', N=N, facts=f, gold=N - k + 1, classes=['release-returns-stock'], permission='granted',
                    q=f"How much room is there under this cap now, immediately after that release?"))
    # s4 delete a member
    f = [f"{NUM[N].capitalize()} {mem(d, N)} exist now, and {NUM[6]} archived {noun} exist that are not in the named set.", f"Just now, {actor} deleted one of the {mem(d, N)}; nothing else changed."]
    out.append(dict(idx=4, probe='delete', N=N, facts=f, gold=1, classes=['deleted-member'], permission='none',
                    q=f"How much room is there under this cap now, immediately after that deletion?"))
    # s5 delete a nonmember; permission denied
    f = [f"{NUM[N].capitalize()} {mem(d, N)} exist now, and {NUM[6]} archived {noun} exist that are not in the named set.", f"Just now, {actor} deleted one of the archived {noun}; no member of the named set changed.", f"{actor}'s authorisation to {s['act']} was revoked this morning and has not been restored."]
    out.append(dict(idx=5, probe='delete', N=N, facts=f, gold=0, classes=['deleted-nonmember'], permission='denied',
                    q=f"How much room is there under this cap now, immediately after that deletion?"))
    # s6 count with scope test
    own = 1; other_k = 2
    f = ([f"{actor} has {NUM[own]} {SG[noun]} in the named set now; {d['other']} has {NUM[other_k]} {noun} of the same kind, which belong to {d['other']} and not to {actor}. No membership changes."] if s['scope'] == 'per-identity' else [f"{actor} has {NUM[own]} {SG[noun]} in the named set now; {d['other']} has {NUM[other_k]} {noun} in the same named set. No membership changes."])
    gold = N - own if s['scope'] == 'per-identity' else max(0, N - own - other_k)
    out.append(dict(idx=6, probe='count', N=N, facts=f, gold=gold, classes=['scope-' + s['scope']], permission='none',
                    q=f"How much room is there under this cap for {actor} now?"))
    # s7 ceiling-not-count
    f = [f"Only this cap is stated. The number of {mem(d, 2)} is not given."]
    out.append(dict(idx=7, probe='count', N=N, facts=f, gold=CD, classes=['ceiling-not-count'], permission='none',
                    q=f"Exactly how many {mem(d, 2)} exist now?", opts=EXIST_OPTS(N)))
    # s8 mixed, stock decides: rate allowance renewed, every slot occupied
    r = d['rate']; w = r['window']; m = MIN[w]; N1 = 4
    f = [f"In the span from two {w}s ago to one {w} ago, {actor} {r['past']} {NUM[N1]} {r['noun']}; none since.", f"{NUM[N].capitalize()} {mem(d, N)} exist now and none is scheduled to leave."]
    out.append(dict(idx=8, probe='count', N=N, N1=N1, align='per-any', facts=f, gold=0, classes=['mixed-stock-decides', 'boundary-known'], permission='none', mixed=True,
                    q=f"How much room is there now for one additional {SG[noun]} under both constraints together?"))
    return out


def build():
    rng = random.Random(SEED)
    filed, bare, perm, keys = [], [], [], {}
    for di, d in enumerate(DOMAINS):
        rs, scope_txt = rate_scenarios(d, di, rng)
        for sc in rs:
            N = sc['N']; align = sc['align']
            if sc.get('mixed'):
                reg = reg_rate(d, N, align) + ' ' + reg_stock(d, sc['N2']); en = en_rate(d, N, align) + ' ' + en_stock(d, sc['N2']); br = bare_rate(d, N) + ' ' + bare_stock(d, sc['N2'])
            else:
                reg, en, br = reg_rate(d, N, align), en_rate(d, N, align), bare_rate(d, N)
            A = arms(d, reg, en, br, sc['facts'], scope_txt)
            sid = f"rc-{d['key']}-rate-{sc['idx']:02d}-{sc['probe']}"
            opts = sc.get('opts') or room_options(sc['gold'], N, rng)
            gold = sc['gold'] if isinstance(sc['gold'], str) else room_phrase(sc['gold'], N)
            entail = CD if sc['probe'] in ('wait', 'release', 'delete', 'boundary') or sc['gold'] == CD else gold
            frame = f"rate-{sc['idx']:02d}-{sc['probe']}"
            filed.append(dict(id=sid, english=A['english'], ainglish=A['ainglish'], question=sc['q'], options=opts, answer=gold, settlement_stratum='rate', probe=sc['probe'], domain=d['key'], semantic_frame=frame))
            bare.append(dict(id=sid + '-bare', english=A['bare'], ainglish=A['ainglish'], question=sc['q'], options=opts, answer=entail, author_intent_answer=gold, settlement_stratum='rate', probe=sc['probe'], domain=d['key'], semantic_frame=frame))
            po = perm_options(d['actor'], d['rate']['act']); pg = {'granted': po[0], 'denied': po[1], 'none': CD}[sc['permission']]
            perm.append(dict(id=sid + '-permission', english=A['english'], ainglish=A['ainglish'], question=f"Independently of any room under the cap, is {d['actor']} authorised to {d['rate']['act']} at all?", options=po, answer=pg, settlement_stratum='permission', probe='permission', domain=d['key'], semantic_frame=frame + '-permission'))
            keys[sid] = dict(cap_kind='mixed' if sc.get('mixed') else 'rate', renewal='both' if sc.get('mixed') else 'time', stratum='rate', scope=('per-identity' if di % 2 == 0 else 'global'), alignment=align,
                             permission_fact=sc['permission'], domain=d['key'], probe=sc['probe'], classes=sc['classes'] + (['headroom-not-permission'] if sc['permission'] != 'none' else []), mixed=bool(sc.get('mixed')),
                             gold=gold, bare_text_entailment=entail, bare_author_intent=gold, permission_gold=pg, N=N, N2=sc.get('N2'))
        for sc in stock_scenarios(d, di, rng):
            N = sc['N']
            if sc.get('mixed'):
                reg = reg_rate(d, sc['N1'], 'per-any') + ' ' + reg_stock(d, N); en = en_rate(d, sc['N1'], 'per-any') + ' ' + en_stock(d, N); br = bare_rate(d, sc['N1']) + ' ' + bare_stock(d, N)
            else:
                reg, en, br = reg_stock(d, N), en_stock(d, N), bare_stock(d, N)
            A = arms(d, reg, en, br, sc['facts'], '')
            sid = f"rc-{d['key']}-stock-{sc['idx']:02d}-{sc['probe']}"
            opts = sc.get('opts') or room_options(sc['gold'], N, rng)
            gold = sc['gold'] if isinstance(sc['gold'], str) else room_phrase(sc['gold'], N)
            entail = CD if sc['probe'] in ('wait', 'release', 'delete') or sc['gold'] == CD else gold
            frame = f"stock-{sc['idx']:02d}-{sc['probe']}"
            filed.append(dict(id=sid, english=A['english'], ainglish=A['ainglish'], question=sc['q'], options=opts, answer=gold, settlement_stratum='stock', probe=sc['probe'], domain=d['key'], semantic_frame=frame))
            bare.append(dict(id=sid + '-bare', english=A['bare'], ainglish=A['ainglish'], question=sc['q'], options=opts, answer=entail, author_intent_answer=gold, settlement_stratum='stock', probe=sc['probe'], domain=d['key'], semantic_frame=frame))
            po = perm_options(d['actor'], d['stock']['act']); pg = {'granted': po[0], 'denied': po[1], 'none': CD}[sc['permission']]
            perm.append(dict(id=sid + '-permission', english=A['english'], ainglish=A['ainglish'], question=f"Independently of any room under the cap, is {d['actor']} authorised to {d['stock']['act']} at all?", options=po, answer=pg, settlement_stratum='permission', probe='permission', domain=d['key'], semantic_frame=frame + '-permission'))
            keys[sid] = dict(cap_kind='mixed' if sc.get('mixed') else 'stock', renewal='both' if sc.get('mixed') else 'release', stratum='stock', scope=d['stock']['scope'], alignment=sc.get('align', 'n/a'),
                             permission_fact=sc['permission'], domain=d['key'], probe=sc['probe'], classes=sc['classes'] + (['headroom-not-permission'] if sc['permission'] != 'none' else []), mixed=bool(sc.get('mixed')),
                             gold=gold, bare_text_entailment=entail, bare_author_intent=gold, permission_gold=pg, N=N, N1=sc.get('N1'))
    # undisclosed-renewal stratum: 16 scenarios, bare statement in every arm, wait question keyed unknown everywhere
    undis = []
    for di, d in enumerate(DOMAINS):
        for kind in ('rate', 'stock'):
            N = 5 if kind == 'rate' else 3
            st = f"A limit of {N} {d['rate']['noun']}." if kind == 'rate' else f"A limit of {N} {d['stock']['noun']}."
            facts = [f"{NUM[N].capitalize()} {d['rate']['noun'] if kind == 'rate' else d['stock']['noun']} are counted against the limit now. The source that stated the limit says nothing about whether, or when, room comes back.",
                     f"{d['actor']} waits one hour and does nothing else."]
            A = arms(d, st, st, st, facts, '')
            sid = f"rc-{d['key']}-undisclosed-{kind}"
            opts = room_options(CD, N, rng)
            undis.append(dict(id=sid, english=A['english'], ainglish=A['ainglish'], question=f"How much room is there under this limit after that hour?", options=opts, answer=CD, settlement_stratum='undisclosed', probe='wait', domain=d['key'], semantic_frame=f'undisclosed-{kind}'))
            keys[sid] = dict(cap_kind='undisclosed', intended_kind=kind, renewal='undisclosed', stratum='undisclosed', domain=d['key'], probe='wait', classes=['undisclosed-renewal'], gold=CD, bare_text_entailment=CD, bare_author_intent=CD, N=N)
    # calibration: planted contrast carried by the ainglish arm only (harness convention)
    CAL_ROLE = ['Auditor', 'Keeper', 'Clerk', 'Marshal', 'Warden', 'Steward']; CAL_COL = ['Teal', 'Moss', 'Rust', 'Ochre', 'Plum', 'Sable', 'Umber', 'Ivory']; CAL_PLACE = ['Shelf', 'Bay', 'Rack', 'Vault', 'Dock', 'Loft']
    crng = random.Random(SEED + 7); cal = []
    for i in range(1, 33):
        role = crng.choice(CAL_ROLE); place = crng.choice(CAL_PLACE); c1, c2, c3, c4 = crng.sample(CAL_COL, 4); n1, n2 = crng.randint(10, 99), crng.randint(10, 99)
        rid = f"{place}-record-{crng.randint(100, 999)}"
        en = f"{rid}: either {role}-{c1}-{n1} or {role}-{c2}-{n1} is the responsible {role.lower()}; this has not been settled. Either {place}-{c3}-{n2} or {place}-{c4}-{n2} is the destination {place.lower()}; this also has not been settled."
        ai = f"{rid}: {role}-{c1}-{n1}, not {role}-{c2}-{n1}, is the responsible {role.lower()}. {place}-{c3}-{n2}, not {place}-{c4}-{n2}, is the destination {place.lower()}."
        gold = f"{role}-{c1}-{n1} / {place}-{c3}-{n2}"
        opts = [gold, f"{role}-{c2}-{n1} / {place}-{c3}-{n2}", f"{role}-{c1}-{n1} / {place}-{c4}-{n2}", f"{role}-{c2}-{n1} / {place}-{c4}-{n2}",
                f"{role} established; {place.lower()} not established.", f"{role} not established; {place.lower()} established.", "Neither is established.", "The record contradicts itself."]
        crng.shuffle(opts)
        cal.append(dict(id=f"rc-calibration-{i:02d}", calibration=True, english=en, ainglish=ai, question=f"Which complete {role.lower()}/{place.lower()} assignment is established by this record?", options=opts, answer=gold, settlement_stratum='calibration', semantic_frame='calibration-planted-pair'))
    return filed, bare, perm, undis, cal, keys


def guards(filed, bare, perm, undis, cal, keys):
    def basic(items, label):
        ids = [i['id'] for i in items]; assert len(ids) == len(set(ids)), label
        for it in items:
            opts = it['options']; assert len(set(o.strip().casefold() for o in opts)) == len(opts) and 2 <= len(opts) <= 8, (label, it['id'])
            assert it['answer'] in opts, (label, it['id'])
            assert it['english'] != it['ainglish'], (label, it['id'])
            if not it.get('calibration'):
                for arm in ('english', 'ainglish'):
                    assert it['answer'].casefold() not in it[arm].casefold(), ('answer vocabulary in arm', label, it['id'])
                    assert 'renew' not in it['ainglish'].casefold(), ('renew leaked into registered arm', it['id'])
    basic(filed, 'filed'); basic(bare, 'bare'); basic(perm, 'permission'); basic(undis, 'undisclosed'); basic(cal, 'calibration')
    strata = Counter(i['settlement_stratum'] for i in filed); assert strata == Counter(rate=64, stock=64), strata
    mixed = sum(1 for k in keys.values() if k.get('mixed')); assert mixed == 16, mixed
    for s in ('rate', 'stock'):
        probes = {i['probe'] for i in filed if i['settlement_stratum'] == s}; assert probes >= {'wait', 'release', 'delete', 'count'}, (s, probes)
    assert {i['probe'] for i in filed if i['settlement_stratum'] == 'rate'} >= {'boundary'}
    pf = Counter(k['permission_fact'] for k in keys.values() if 'permission_fact' in k); assert pf == Counter(none=96, granted=16, denied=16), pf
    assert len(undis) == 16 and len(cal) == 32 and len(perm) == 128 and len(bare) == 128
    for it in bare:
        assert 'rate-cap(' not in it['english'] and 'stock-cap(' not in it['english'] and 'per-clock' not in it['english'] and 'per-any' not in it['english'], ('marker in bare arm', it['id'])
    for it in filed + undis:
        assert MAPPING in it['english'] and MAPPING not in it['ainglish'], ('definition placement', it['id'])


def main():
    filed, bare, perm, undis, cal, keys = build()
    guards(filed, bare, perm, undis, cal, keys)
    files = {'items_filed.json': filed + cal, 'items_bare.json': bare + cal, 'items_permission.json': perm + cal, 'items_undisclosed.json': undis + cal, 'keys.json': keys}
    digests = {}
    for name, obj in files.items():
        (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8'); digests[name] = digest(obj)
    classes = Counter(c for k in keys.values() for c in k['classes'])
    cross = Counter((i['settlement_stratum'], i['probe']) for i in filed)
    audit = {'kind': 'reticuli.rate-cap-bank.audit.v1', 'seed': SEED, 'mapping_sha256': hashlib.sha256(MAPPING.encode()).hexdigest(), 'counts': {'filed_room_items': len(filed), 'calibration': len(cal), 'bare': len(bare), 'permission': len(perm), 'undisclosed': len(undis)},
             'strata': dict(Counter(i['settlement_stratum'] for i in filed)), 'mixed': sum(1 for k in keys.values() if k.get('mixed')), 'probe_by_stratum': {f'{s}/{p}': n for (s, p), n in sorted(cross.items())},
             'classes': dict(sorted(classes.items())), 'permission_facts': dict(Counter(k['permission_fact'] for k in keys.values() if 'permission_fact' in k)), 'alignment': dict(Counter(k.get('alignment') for k in keys.values() if k.get('stratum') == 'rate')),
             'bare_entailment_unknown': sum(1 for k in keys.values() if k.get('bare_text_entailment') == CD and k.get('stratum') in ('rate', 'stock')),
             'canonical_digests': digests, 'settlement_strata_filed': [{'id': 'rate', 'weight': 1}, {'id': 'stock', 'weight': 1}]}
    (ROOT / 'AUDIT.json').write_text(json.dumps(audit, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (ROOT / 'MANIFEST.sha256').write_text(''.join(f"{d}  {n}\n" for n, d in digests.items()), encoding='utf-8')
    print(json.dumps({k: v for k, v in audit.items() if k != 'canonical_digests'}, indent=1)); print({n: d[:16] for n, d in digests.items()})


if __name__ == '__main__':
    main()
