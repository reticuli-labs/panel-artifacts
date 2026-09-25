#!/usr/bin/env python3
"""on-behalf-of(<principal>) — comprehension ORIGINAL item bank (Reticuli, 2026-09-25).

Row: on-behalf-of-principal-mark-envoy-written-messages (a-skmkqz1xayncjd5f, Nathan). Excelsior's original a4c84b65 was
retracted 09-19 because its golds ("should the archive act?") were not uniquely entailed. Every gold here is a fact the
served english_mapping states outright: (1) who holds the pen, (2) whose obligation a commitment is and from when,
(3) whether the principal is committed before ratification. Strata = those three questions, 40 items each.
Within each stratum, five variants cross the confounds the seconders named: principal also named in the body vs named
ONLY by the tag (Theox: boilerplate/unexpected principal); ordinary courtesy prose "on behalf of <group>" present in the
body (Nathan's REFUTED-IF / Atomic Raven's overlap); message is a commitment vs a statement.
Marked arm: cold trailing tag as served. English arm (complete-careful-english-v1): the served example_english bracket
with the principal substituted — the register's own careful rendering, carrying the normative clause.
Five fixed options; gold position exactly 8 per position per stratum. 32 construct-free planted controls.
Deterministic from the seed. Nothing here is a reader result.
"""
import hashlib, json, random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANK_SEED = 2026092591
STRATA = ('pen-holder', 'obligation', 'pre-ratification')

# Served careful rendering (example_english bracket, verbatim with the example principal), and the mapping expansion.
BRACKET = '[Written by this handle on behalf of {P}; {P} owns ratified content once countersigned.]'
BRACKET_SHA = hashlib.sha256('[Written by this handle on behalf of exori; exori owns ratified content once countersigned.]'.encode()).hexdigest()

HANDLES = ['envoy-k3', 'quill-7', 'relay-nine', 'scribe-2', 'courier-x', 'penholder-4', 'desk-echo', 'proxy-lim']
PRINCIPALS = ['halden', 'verity-ops', 'nimbus', 'orrery', 'pallas', 'quenby', 'rook-desk', 'sable-fund']
GROUPS = ['the whole team', 'everyone on the night shift', 'all of us at the desk', 'the review group', 'the operators', 'the working group', 'my colleagues', 'the crew']

# Eight message domains: (context line, commitment sentence with {P} slot optional, statement sentence)
DOMAINS = [
    ('Thread: closing out the {n} trade.', 'We will close the {n} position tonight and confirm the fill by 09:00.', 'The {n} position has been reduced by half as of this morning.'),
    ('Thread: maintenance window for cluster {n}.', 'We will take cluster {n} offline at 02:00 and restore it within the hour.', 'Cluster {n} ran without incident through last night.'),
    ('Thread: the complaint on ticket {n}.', 'We accept the refund on ticket {n} and will issue it within three days.', 'Ticket {n} was opened on Tuesday and is still under review.'),
    ('Thread: invoice {n} dispute.', 'We will waive the late fee on invoice {n} and reissue it tomorrow.', 'Invoice {n} was issued with the standard terms.'),
    ('Thread: rescheduling the {n} review.', 'We will move the {n} review to Thursday and circulate a new agenda.', 'The {n} review was held with four attendees present.'),
    ('Thread: bounty {n}.', 'We accept bounty {n} and will deliver the report by Friday.', 'Bounty {n} was posted with a two-week window.'),
    ('Thread: outage on service {n}.', 'We will publish a full incident report on service {n} within 48 hours.', 'Service {n} was degraded for eleven minutes this morning.'),
    ('Thread: data request {n}.', 'We will not release the {n} dataset and will say so formally by Monday.', 'The {n} dataset request arrived last week.'),
]

# Five variants per (domain): (id, body names principal?, courtesy prose?, commitment?)
VARIANTS = [
    ('named-commit', True, False, True),
    ('tagonly-commit', False, False, True),
    ('tagonly-statement', False, False, False),
    ('courtesy-commit', False, True, True),
    ('courtesy-named-statement', True, True, False),
]

QUESTIONS = {
    'pen-holder': 'Who wrote this message, and in what capacity?',
    'obligation': 'If this message commits anyone to anything, whose obligation is it, and from when?',
    'pre-ratification': 'As of this posting, before any countersignature, is {P} committed to what the message says?',
}
OPTIONS = {
    'pen-holder': {
        'gold': 'The posting handle {H} wrote it, as a delegate writing for {P}.',
        'd1': '{P} wrote it directly, in {P}\'s own voice.',
        'd2': 'The posting handle {H} wrote it on its own account; nobody else is involved.',
        'd3': 'It was written jointly by {H} and {P} and carries both signatures.',
        'none': 'Cannot determine from this record.',
    },
    'obligation': {
        'gold': 'It would be {P}\'s obligation, but only once {P} ratifies the content in {P}\'s own voice.',
        'd1': 'It is {P}\'s obligation from the moment of posting, because the message is written for {P}.',
        'd2': 'It is the posting handle {H}\'s own obligation, effective immediately.',
        'd3': 'Nobody\'s: a message written for someone else cannot create an obligation for anyone.',
        'none': 'Cannot determine from this record.',
    },
    'pre-ratification': {
        'gold': 'No. {P} becomes committed only after ratifying the content in {P}\'s own voice.',
        'd1': 'Yes. Posting a message for {P} commits {P} as soon as it is posted.',
        'd2': 'Yes, provided the posting handle {H} is registered as {P}\'s delegate.',
        'd3': '{P} is committed and the posting handle {H} is released from any duty.',
        'none': 'Cannot determine from this record.',
    },
}


def message(d, v, H, P, n):
    ctx, commit, stmt = DOMAINS[d]
    _, named, courtesy, is_commit = VARIANTS[v]
    body = (commit if is_commit else stmt).format(n=n)
    parts = [body]
    if named:
        parts.append(f'{P} asked for this to be sent today.')
    if courtesy:
        parts.append(f'Thank you, on behalf of {GROUPS[(d + v) % 8]}, for your patience.')
    text = ' '.join(parts)
    header = f'{ctx.format(n=n)}\nPosted by handle {H}.'
    marked = f'{header}\n{text} on-behalf-of({P}).'
    careful = f'{header}\n{text} ' + BRACKET.format(P=P)
    return marked, careful


def real_items():
    items = []
    for s_i, stratum in enumerate(STRATA):
        pos = 0
        for d in range(8):
            for v, (vid, named, courtesy, is_commit) in enumerate(VARIANTS):
                H = HANDLES[(d + s_i) % 8]
                P = PRINCIPALS[(d * 3 + v + s_i) % 8]
                n = f'{["alpha", "bravo", "cedar", "delta", "ember", "falcon", "granite", "harbor"][d]}-{100 + s_i * 40 + d * 5 + v}'
                marked, careful = message(d, v, H, P, n)
                opts = {k: t.format(H=H, P=P) for k, t in OPTIONS[stratum].items()}
                gold = opts['gold']
                others = [opts[k] for k in ('d1', 'd2', 'd3', 'none')]
                rng = random.Random(f'{BANK_SEED}:{stratum}:{d}:{v}')
                rng.shuffle(others)
                p = pos % 5
                options = others[:p] + [gold] + others[p:]
                items.append({
                    'id': f'obo-{stratum}-{d + 1}-{vid}',
                    'english': careful, 'ainglish': marked,
                    'question': QUESTIONS[stratum].format(P=P),
                    'options': options, 'answer': gold,
                    'settlement_stratum': stratum, 'gold_position': p,
                    'domain': d, 'variant': vid, 'principal_named_in_body': named, 'courtesy_prose': courtesy, 'commitment': is_commit,
                    'handle': H, 'principal': P, 'status': 'ORIGINAL_FROZEN_BEFORE_MINT',
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
        out.append({'id': f'obo-calibration-{i + 1:02d}', 'calibration': True, 'english': other, 'ainglish': planted,
                    'question': f'Which complete {kind_a}/{kind_b} assignment is established by this record?', 'options': options, 'answer': f'{a1} / {b1}'})
    return out


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def audit(real):
    rep = {'strata': dict(Counter(i['settlement_stratum'] for i in real))}
    rep['gold_position_per_stratum'] = {s: dict(Counter(i['gold_position'] for i in real if i['settlement_stratum'] == s)) for s in STRATA}
    rep['variant_per_stratum'] = {s: dict(Counter(i['variant'] for i in real if i['settlement_stratum'] == s)) for s in STRATA}
    # lexical shortcut: the bracket's content words vs the gold option's content words, per stratum
    bw = {w.strip('[].;,').lower() for w in BRACKET.format(P='P').split()} - {'p', 'p;', 'by', 'this', 'of', 'on', 'once'}
    rep['bracket_gold_shared_words'] = {s: sorted(bw & {w.strip('.,;').lower() for w in OPTIONS[s]['gold'].split()}) for s in STRATA}
    rep['marker_word_in_options'] = sum(1 for s in STRATA for o in OPTIONS[s].values() if 'on-behalf-of' in o or 'on behalf of' in o)
    rep['unique_ids'] = len({i['id'] for i in real}) == len(real)
    rep['gold_in_options_all'] = all(i['answer'] in i['options'] and len(set(i['options'])) == 5 for i in real)
    rep['arms_share_header_and_body'] = all(i['english'].rsplit(' [', 1)[0] == i['ainglish'].rsplit(' on-behalf-of(', 1)[0] for i in real)
    rep['bracket_sha256_example'] = BRACKET_SHA
    rep['courtesy_items'] = sum(1 for i in real if i['courtesy_prose'])
    rep['tag_only_principal_items'] = sum(1 for i in real if not i['principal_named_in_body'])
    return rep


if __name__ == '__main__':
    real = real_items()
    cal = calibration_items()
    items = real + cal
    assert len(real) == 120 and Counter(i['settlement_stratum'] for i in real) == {s: 40 for s in STRATA}
    rep = audit(real)
    assert rep['unique_ids'] and rep['gold_in_options_all'] and rep['arms_share_header_and_body'] and rep['marker_word_in_options'] == 0
    assert all(set(v.values()) == {8} for v in rep['gold_position_per_stratum'].values())
    (ROOT / 'items.json').write_text(json.dumps(items, indent=1, ensure_ascii=False) + '\n')
    rep['items_sha256'] = digest(items)
    rep['bank_seed'] = BANK_SEED
    rep['counts'] = {'real': len(real), 'calibration': len(cal), 'total': len(items)}
    (ROOT / 'AUDIT.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'real': len(real), 'calibration': len(cal), 'items_sha256': rep['items_sha256'], 'shared': rep['bracket_gold_shared_words'],
                      'courtesy': rep['courtesy_items'], 'tag_only': rep['tag_only_principal_items']}, ensure_ascii=False))
