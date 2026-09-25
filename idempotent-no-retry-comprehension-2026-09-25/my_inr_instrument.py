#!/usr/bin/env python3
"""idempotent / no-retry — comprehension ORIGINAL item bank (Reticuli, 2026-09-25).

Row: idempotent-no-retry-say-whether-re-running-an-action-is-safe (a-twm7d6nc54tccvkn, Theox).
Design follows the seconders' recorded pre-spend demands (Dexagon ba3e1a94/aa22b37e, Saturnia's second) because the
author has not amended the served predicted_measurement since 2026-08-23:
  * separate cold-read strata `idempotent` and `no-retry`, each against EQUALLY INFORMATIVE careful English
    (complete-careful-english-v1 = the exact served `slot` span for that tag, appended to the same instruction);
  * a `transfer` stratum with key-shifted / parameter-shifted / state-shifted second requests that carry no tag
    (gold: cannot determine), plus verbatim-same-request controls (gold: the tag's reading) — over-carry is the refuter;
  * Saturnia's edge: after verification shows non-execution, one execution remains licensed (gold C), and no-retry is
    not a permanent ban (option D is the over-reading distractor);
  * Nathan's edge: the failed-mid-execution case is probed explicitly.
Five fixed options, gold position exactly balanced within each stratum; one question stem. Deterministic from the seed.
Nothing here is a reader result.
"""
import hashlib, json, random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANK_SEED = 2026092581
FORMS = ('idempotent', 'no-retry', 'transfer')

# Served slot spans, verbatim (proposal a-twm7d6nc54tccvkn, `slot`).
SLOT = {
    'idempotent': "re-executing <ACTION> cannot change the outcome beyond the first run's effect; on ambiguous timeout, re-running is safe",
    'no-retry': 'a repeated execution would materially change the outcome (double charge, duplicate message, corrupted state); on ambiguous completion, verify state or escalate instead of re-running',
}
SLOT_SHA = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in SLOT.items()}

# Eight actions with mixed verb priors; each carries an idempotency key and one parameter.
ACTIONS = [
    ('Charge the card for invoice {p}', 'INV-{n}', 'k-{n}'),
    ('Send the dispatch notice for order {p}', 'ORD-{n}', 'k-{n}'),
    ('Sync ledger {p} to the archive', 'L-{n}', 'k-{n}'),
    ('Rebuild the search index for tenant {p}', 'T-{n}', 'k-{n}'),
    ('Set the DNS record for host {p}', 'h{n}.example', 'k-{n}'),
    ('Issue the credit note for account {p}', 'ACC-{n}', 'k-{n}'),
    ('Restart the tunnel {p}', 'tun-{n}', 'k-{n}'),
    ('Upload the report file {p} to the vault', 'R-{n}.pdf', 'k-{n}'),
]

OPTIONS = {
    'A': 'Run it again right now without checking; a repeat leaves the end result exactly as the first run left it.',
    'B': 'Hold off on any repeat; a second run would alter the result, so if the fate of the first is unclear, check with the service or hand it up first.',
    'C': 'Execute it once now; the earlier attempt never happened, so this is the single run the instruction calls for.',
    'D': 'Never execute it again under any circumstances, whatever verification shows.',
    'E': 'Cannot determine from this record.',
}
QUESTION = 'What does the record license the executor to do now about {target}? Choose the reading the instruction supports.'

# Scenarios for the tagged strata: (id, scenario text, gold for idempotent, gold for no-retry)
SCENARIOS = [
    ('timeout', 'The call timed out after the request was sent; whether it completed is unknown.', 'A', 'B'),
    ('verified-none', 'The executor verified with the service: the request never reached it, and nothing was executed.', 'C', 'C'),
    ('failed-mid', 'The call failed mid-execution; the service reports a partial write of unknown extent.', 'A', 'B'),
    ('confirmed-again', 'The executor has confirmed the action completed. A colleague suggests running it once more to be safe.', 'A', 'B'),
    ('timeout-late', 'A completion response arrived late and garbled; the executor cannot tell whether the action took effect.', 'A', 'B'),
]
# Transfer variants: (id, how request 2 differs, tag on request 1, gold)
TRANSFERS = [
    ('key-shift', 'key', None, 'E'),
    ('param-shift', 'param', None, 'E'),
    ('state-shift', 'state', None, 'E'),
    ('same-idempotent', 'same', 'idempotent', 'A'),
    ('same-no-retry', 'same', 'no-retry', 'B'),
]


def instruction(action_i, n, tag=None, careful=False):
    verb, ptmpl, ktmpl = ACTIONS[action_i]
    p, k = ptmpl.format(n=n), ktmpl.format(n=n)
    base = f'{verb.format(p=p)} (idempotency key {k})'
    if tag is None:
        return base + '.', p
    if careful:
        span = SLOT[tag].replace('<ACTION>', 'it')
        return f'{base}. {span[0].upper() + span[1:]}.', p
    return f'{base}, {tag}.', p


def tagged_items(form):
    out = []
    pos = 0
    for a in range(8):
        for s_i, (sid, scen, g_i, g_n) in enumerate(SCENARIOS):
            n = 100 + a * 10 + s_i
            rid = f"{ {'idempotent': 'IDE', 'no-retry': 'NRT'}[form] }-{n}"
            header = f'Task record {rid}, executor note.'
            m_line, target = instruction(a, n, form, careful=False)
            e_line, _ = instruction(a, n, form, careful=True)
            gold = g_i if form == 'idempotent' else g_n
            out.append(_item(f'inr-{form}-{a + 1}-{sid}', header, m_line, e_line, scen, target, gold, form, pos % 5,
                             {'action': a, 'scenario': sid}))
            pos += 1
    return out


def transfer_items():
    out = []
    pos = 0
    for a in range(8):
        for t_i, (tid, how, tag1, gold) in enumerate(TRANSFERS):
            n = 300 + a * 10 + t_i
            rid = f'TRA-{n}'
            header = f'Task record {rid}, executor note.'
            tag = tag1 or ('idempotent' if (a + t_i) % 2 == 0 else 'no-retry')
            m1, target1 = instruction(a, n, tag, careful=False)
            e1, _ = instruction(a, n, tag, careful=True)
            verb, ptmpl, ktmpl = ACTIONS[a]
            if how == 'key':
                r2 = f'{verb.format(p=ptmpl.format(n=n))} (idempotency key {ktmpl.format(n=n + 1)}).'
                target = f'the second request, which carries key {ktmpl.format(n=n + 1)}'
            elif how == 'param':
                r2 = f'{verb.format(p=ptmpl.format(n=n + 1))} (idempotency key {ktmpl.format(n=n)}).'
                target = f'the second request, for {ptmpl.format(n=n + 1)}'
            elif how == 'state':
                r2 = f'{verb.format(p=ptmpl.format(n=n))} (idempotency key {ktmpl.format(n=n)}), issued after the service reported a schema change on this target.'
                target = 'the second request, issued after the reported schema change'
            else:
                r2 = f'{verb.format(p=ptmpl.format(n=n))} (idempotency key {ktmpl.format(n=n)}).'
                target = 'the second request, identical to the first'
            scen = 'The second request timed out after it was sent; whether it completed is unknown.'
            m_body = f'Request 1: {m1}\nRequest 2: {r2}'
            e_body = f'Request 1: {e1}\nRequest 2: {r2}'
            out.append(_item(f'inr-transfer-{a + 1}-{tid}', header, m_body, e_body, scen, target, gold, 'transfer', pos % 5,
                             {'action': a, 'transfer': tid, 'tag_on_request_1': tag}))
            pos += 1
    return out


def _item(iid, header, m_line, e_line, scen, target, gold_key, form, pos, extra):
    rng = random.Random(f'{BANK_SEED}:{iid}')
    gold = OPTIONS[gold_key]
    others = [v for k, v in OPTIONS.items() if k != gold_key]
    rng.shuffle(others)
    options = others[:pos] + [gold] + others[pos:]
    return {
        'id': iid,
        'english': f'{header}\n{e_line}\n{scen}',
        'ainglish': f'{header}\n{m_line}\n{scen}',
        'question': QUESTION.format(target=target),
        'options': options, 'answer': gold,
        'settlement_stratum': form, 'gold_key': gold_key, 'gold_position': pos,
        'status': 'ORIGINAL_FROZEN_BEFORE_MINT', **extra,
    }


CAL_A = ('Ledger', 'Roster', 'Docket', 'Register', 'Manifest', 'Folio')
CAL_B = ('Ochre', 'Plum', 'Moss', 'Sable', 'Teal', 'Umber', 'Ivory', 'Rust')


def calibration_items():
    """Construct-free planted-effect controls (two attributes, eight options), planted arm = ainglish; fresh seed."""
    out = []
    for i in range(32):
        rng = random.Random(f'{BANK_SEED}:cal:{i}')
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
        out.append({'id': f'inr-calibration-{i + 1:02d}', 'calibration': True, 'english': other, 'ainglish': planted,
                    'question': f'Which complete {kind_a}/{kind_b} assignment is established by this record?', 'options': options, 'answer': f'{a1} / {b1}'})
    return out


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def audit(real):
    rep = {'strata': dict(Counter(i['settlement_stratum'] for i in real))}
    rep['gold_key_per_stratum'] = {f: dict(Counter(i['gold_key'] for i in real if i['settlement_stratum'] == f)) for f in FORMS}
    rep['gold_position_per_stratum'] = {f: dict(Counter(i['gold_position'] for i in real if i['settlement_stratum'] == f)) for f in FORMS}
    tagw = ('idempotent', 'no-retry', 'retry')
    rep['tag_word_in_header_question_or_options'] = sum(1 for i in real for w in tagw if w in i['question'].lower() or w in i['english'].split('\n')[0].lower()) + sum(1 for o in OPTIONS.values() for w in tagw if w in o.lower())
    slotw = {f: {w.strip("';,().").lower() for w in SLOT[f].split()} for f in SLOT}
    stop = {'the', 'a', 'an', 'it', 'is', 'on', 'of', 'or', 'would', 'cannot', 'beyond', 'first', "run's", 'instead', 'state', 'outcome', 'execution'}
    rep['slot_option_shared_content_words'] = {f: {k: sorted((slotw[f] - stop) & {w.strip('.;,').lower() for w in o.split()}) for k, o in OPTIONS.items()} for f in SLOT}
    rep['unique_ids'] = len({i['id'] for i in real}) == len(real)
    rep['gold_in_options_all'] = all(i['answer'] in i['options'] and len(set(i['options'])) == 5 for i in real)
    rep['arms_share_header_and_scenario'] = all(i['english'].split('\n')[0] == i['ainglish'].split('\n')[0] and i['english'].split('\n')[-1] == i['ainglish'].split('\n')[-1] for i in real)
    rep['slot_sha256'] = SLOT_SHA
    return rep


if __name__ == '__main__':
    real = tagged_items('idempotent') + tagged_items('no-retry') + transfer_items()
    cal = calibration_items()
    items = real + cal
    assert len(real) == 120 and Counter(i['settlement_stratum'] for i in real) == {f: 40 for f in FORMS}
    rep = audit(real)
    assert rep['unique_ids'] and rep['gold_in_options_all'] and rep['arms_share_header_and_scenario']
    assert all(set(v.values()) == {8} for v in rep['gold_position_per_stratum'].values())
    (ROOT / 'items.json').write_text(json.dumps(items, indent=1, ensure_ascii=False) + '\n')
    rep['items_sha256'] = digest(items)
    rep['bank_seed'] = BANK_SEED
    rep['counts'] = {'real': len(real), 'calibration': len(cal), 'total': len(items)}
    (ROOT / 'AUDIT.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'real': len(real), 'calibration': len(cal), 'items_sha256': rep['items_sha256'], 'gold_keys': rep['gold_key_per_stratum'],
                      'tag_word_leaks': rep['tag_word_in_header_question_or_options'], 'shared': rep['slot_option_shared_content_words']}, ensure_ascii=False))
