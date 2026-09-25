#!/usr/bin/env python3
"""counted / estimated / quoted / placeholder — comprehension ORIGINAL item bank (Reticuli, 2026-09-25).

Row: counted-n-estimated-n-quoted-n-source-placeholder-n-2 (a-0nqvf9999wvtvnxm). Comparator class
complete-careful-english-v1: the English arm is the exact per-form span of the SERVED english_mapping with <N> and
<source> substituted (and, for counted, "the source I name" replaced by the named source). The marked arm is the
cold marker as served in `slot`/`form` (quoted carries its source inside the marker), no teaching. One target
number per item. Question: how must the receiver treat that figure; five fixed options (the four provenance
readings, paraphrased so neither arm gets a string match, plus "Cannot determine from this record").
Strata = the four forms, 40 items each; zero-valued figures 8 per stratum so the digit cannot identify the form;
gold position cycles over the five positions within each stratum (exactly 8 per position per stratum). 32 construct-free planted calibration controls.
Deterministic from the seeds below; nothing here is a reader result.
"""
import hashlib, json, random, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANK_SEED = 2026092571
FORMS = ('counted', 'estimated', 'quoted', 'placeholder')

# Served mapping spans (proposal a-0nqvf9999wvtvnxm, english_mapping, verbatim per form).
SPANS = {
    'counted': 'N; I counted it, and the count is reproducible from the source I name.',
    'estimated': 'about N; nobody counted it — this is an inference with an unstated margin.',
    'quoted': 'N, as <source> states it; I did not verify it.',
    'placeholder': 'N is standing where a real number is not yet known; do not compute with it.',
}
SPAN_SHA = {f: hashlib.sha256(s.encode()).hexdigest() for f, s in SPANS.items()}

# Eight domains x four (label, source) variants. Headers carry no provenance vocabulary.
DOMAINS = {
    'marketplace-board': {
        'header': 'Board scan {rid}, marketplace listings, read at 09:{mm} UTC.',
        'targets': [('Open listings', 'the board API'), ('Supply-side listings', 'the category filter'),
                    ('Listings with escrow', 'the escrow index'), ('Listings closed today', 'the closure log'), ('Listings flagged for review', 'the flag queue')],
        'values': [63, 340, 41, 12, 7, 155, 28, 91],
    },
    'job-board': {
        'header': 'Job-board pass {rid}, contract roles, page set complete.',
        'targets': [('Roles matching the filter', 'the search export'), ('Roles posted this week', 'the posting dates'),
                    ('Roles paying hourly', 'the rate field'), ('Roles with a named client', 'the client column'), ('Roles marked remote', 'the location field')],
        'values': [17, 200, 9, 58, 3, 120, 44, 26],
    },
    'inventory': {
        'header': 'Stock record {rid}, warehouse bay C, end of shift.',
        'targets': [('Units on the shelf', 'the shelf tally sheet'), ('Units reserved', 'the reservation ledger'),
                    ('Units damaged', 'the damage form'), ('Units in transit', 'the carrier manifest'), ('Units awaiting inspection', 'the inspection queue')],
        'values': [480, 36, 5, 1200, 72, 14, 250, 8],
    },
    'incident': {
        'header': 'Incident note {rid}, checkout service, written during the response.',
        'targets': [('Affected requests', 'the gateway log'), ('Affected accounts', 'the session table'),
                    ('Retries observed', 'the retry counter'), ('Minutes of degradation', 'the alert timeline'), ('Alerts raised', 'the pager history')],
        'values': [4400, 310, 19, 45, 87, 1500, 6, 230],
    },
    'budget': {
        'header': 'Budget sheet {rid}, quarter three, line items under review.',
        'targets': [('Sats allocated', 'the treasury ledger'), ('Sats spent', 'the payment log'),
                    ('Invoices outstanding', 'the invoice tracker'), ('Vendors paid', 'the payout list'), ('Sats held in escrow', 'the escrow statement')],
        'values': [155000, 40000, 11, 9, 2500, 72000, 4, 300],
    },
    'poll': {
        'header': 'Poll summary {rid}, member survey, responses closed.',
        'targets': [('Responses received', 'the form export'), ('Members in favour', 'the tally column'),
                    ('Members abstaining', 'the abstention field'), ('Responses discarded', 'the moderation log'), ('Members opposed', 'the opposition column')],
        'values': [212, 130, 15, 6, 98, 47, 3, 510],
    },
    'shipping': {
        'header': 'Dispatch record {rid}, outbound dock, morning run.',
        'targets': [('Parcels dispatched', 'the dock scanner'), ('Parcels returned', 'the returns bin count'),
                    ('Pallets loaded', 'the loading sheet'), ('Parcels missing a label', 'the exception list'), ('Parcels held at customs', 'the customs notice')],
        'values': [96, 7, 12, 3, 640, 21, 150, 33],
    },
    'test-suite': {
        'header': 'Suite report {rid}, nightly run, main branch.',
        'targets': [('Tests executed', 'the runner output'), ('Tests failing', 'the failure list'),
                    ('Tests skipped', 'the skip markers'), ('Assertions counted', 'the assertion counter'), ('Tests newly added', 'the diff summary')],
        'values': [1743, 2, 31, 31679, 512, 9, 88, 4000],
    },
}

OPTIONS = {
    'counted': 'As an exact tally the writer made; a reader can reproduce it from the source the line names.',
    'estimated': 'As a rough figure that was never tallied; usable only if its imprecision is flagged.',
    'quoted': 'As a figure carried over from the named source, unchecked by the writer; usable only with attribution.',
    'placeholder': 'As a value holding the field open until the true figure arrives; it must not be used as if it were actual.',
    'none': 'Cannot determine from this record.',
}
QUESTION = 'The receiver must decide how to treat the figure {N} in the second line of this record. Which reading is correct?'


def marked(form, label, n, source):
    if form == 'counted':
        return f'{label}: counted({n}), per {source}.'
    if form == 'estimated':
        return f'{label}: estimated({n}).'
    if form == 'quoted':
        return f'{label}: quoted({n}|{source}).'
    return f'{label}: placeholder({n}).'


def careful(form, label, n, source):
    span = SPANS[form]
    if form == 'counted':
        body = span.replace('N', str(n), 1).replace('the source I name', source)
    elif form == 'quoted':
        body = span.replace('N', str(n), 1).replace('<source>', source)
    else:
        body = span.replace('N', str(n), 1)
    return f'{label}: {body}'


def real_items():
    rng = random.Random(f'{BANK_SEED}:bank')
    items = []
    domains = list(DOMAINS)
    # 160 = 8 domains x 4 forms x 5 variants; each (domain, form) gets all five target variants (5 gold positions -> exact balance).
    # Zero-valued: 8 per form, spread one per domain (variant chosen by seed).
    zero_variant = {}
    for form in FORMS:
        for d in domains:
            zero_variant[(form, d)] = rng.randrange(5)
    gold_pos = {form: 0 for form in FORMS}
    k = 0
    for d in domains:
        spec = DOMAINS[d]
        for form in FORMS:
            for v in range(5):
                label, source = spec['targets'][v]
                n = 0 if zero_variant[(form, d)] == v else spec['values'][(v * 2 + FORMS.index(form)) % len(spec['values'])]
                rid = f'{d[:3].upper()}-{1000 + k}'
                header = spec['header'].format(rid=rid, mm=f'{(k * 7) % 60:02d}')
                eng = f'{header}\n{careful(form, label, n, source)}'
                ain = f'{header}\n{marked(form, label, n, source)}'
                gold = OPTIONS[form]
                others = [OPTIONS[f] for f in FORMS if f != form] + [OPTIONS['none']]
                rng.shuffle(others)
                pos = gold_pos[form] % 5
                gold_pos[form] += 1
                options = others[:pos] + [gold] + others[pos:]
                items.append({
                    'id': f'cn-{form}-{d}-{v + 1}', 'english': eng, 'ainglish': ain,
                    'question': QUESTION.format(N=n), 'options': options, 'answer': gold,
                    'settlement_stratum': form, 'domain': d, 'target_label': label, 'source': source,
                    'value': n, 'zero_valued': n == 0, 'gold_position': pos,
                    'status': 'ORIGINAL_FROZEN_BEFORE_MINT',
                })
                k += 1
    return items


CAL_A = ('Ledger', 'Roster', 'Docket', 'Register', 'Manifest', 'Folio')
CAL_B = ('Ochre', 'Plum', 'Moss', 'Sable', 'Teal', 'Umber', 'Ivory', 'Rust')


def calibration_items():
    """Construct-free planted-effect controls: planted arm = ainglish (facts resolved), english leaves both unresolved.
    Same shape as my 09-25 replica controls (two attributes, eight options); fresh seed and record ids; no number
    or provenance vocabulary."""
    out = []
    for i in range(32):
        rng = random.Random(f'{BANK_SEED}:cal:{i}')
        kind_a, kind_b = rng.sample(('clerk', 'archive', 'desk', 'store', 'courier', 'shelf', 'auditor', 'bay'), 2)
        a1, a2 = [f'{kind_a.capitalize()}-{c}-{71 + i}' for c in rng.sample(CAL_B, 2)]
        b1, b2 = [f'{kind_b.capitalize()}-{c}-{91 + i}' for c in rng.sample(CAL_B, 2)]
        rec = f'{rng.choice(CAL_A)}-record-{701 + i}'
        planted = f'{rec}: {a1}, not {a2}, is the responsible {kind_a}. {b1}, not {b2}, is the destination {kind_b}.'
        other = f'{rec}: either {a1} or {a2} is the responsible {kind_a}; this has not been settled. Either {b1} or {b2} is the destination {kind_b}; this also has not been settled.'
        options = [f'{a1} / {b1}', f'{a1} / {b2}', f'{a2} / {b1}', f'{a2} / {b2}',
                   f'{kind_a.capitalize()} not established; {kind_b} established.', f'{kind_a.capitalize()} established; {kind_b} not established.',
                   f'Neither {kind_a} nor {kind_b} established.', 'The record contradicts itself.']
        rng.shuffle(options)
        out.append({'id': f'cn-calibration-{i + 1:02d}', 'calibration': True, 'english': other, 'ainglish': planted,
                    'question': f'Which complete {kind_a}/{kind_b} assignment is established by this record?', 'options': options, 'answer': f'{a1} / {b1}'})
    return out


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def audit(real):
    rep = {}
    rep['strata'] = dict(Counter(i['settlement_stratum'] for i in real))
    rep['zero_valued_per_stratum'] = dict(Counter(i['settlement_stratum'] for i in real if i['zero_valued']))
    rep['gold_position_per_stratum'] = {f: dict(Counter(i['gold_position'] for i in real if i['settlement_stratum'] == f)) for f in FORMS}
    rep['domain_x_stratum'] = dict(Counter(f"{i['domain']}|{i['settlement_stratum']}" for i in real))
    form_words = ('counted', 'estimated', 'quoted', 'placeholder')
    rep['form_word_in_header_or_question'] = sum(1 for i in real for w in form_words if w in i['english'].split('\n')[0].lower() or w in i['question'].lower())
    rep['form_word_in_options'] = sum(1 for o in OPTIONS.values() for w in form_words if w in o.lower())
    # marker-surface shortcut: does the gold option share a content word with the marker name? (declared, by construction none)
    rep['marker_name_in_gold_option'] = sum(1 for f in FORMS if f in OPTIONS[f].lower())
    # english-arm span shortcut: content words shared between the served span and the gold option
    shared = {}
    for f in FORMS:
        sw = {w.strip('.;,—').lower() for w in SPANS[f].split()} - {'n', 'i', 'it', 'the', 'is', 'a', 'and', 'with', 'not', 'do', 'from', 'this', 'an', 'as', 'did'}
        ow = {w.strip('.;,').lower() for w in OPTIONS[f].split()}
        shared[f] = sorted(sw & ow)
    rep['span_option_shared_content_words'] = shared
    rep['unique_ids'] = len({i['id'] for i in real}) == len(real)
    rep['gold_in_options_all'] = all(i['answer'] in i['options'] and len(set(i['options'])) == 5 for i in real)
    rep['arms_differ_only_in_second_line'] = all(i['english'].split('\n')[0] == i['ainglish'].split('\n')[0] for i in real)
    rep['span_sha256'] = SPAN_SHA
    return rep


if __name__ == '__main__':
    real = real_items()
    cal = calibration_items()
    items = real + cal
    assert len(real) == 160 and Counter(i['settlement_stratum'] for i in real) == {f: 40 for f in FORMS}
    assert Counter(i['settlement_stratum'] for i in real if i['zero_valued']) == {f: 8 for f in FORMS}
    rep = audit(real)
    assert rep['form_word_in_header_or_question'] == 0 and rep['form_word_in_options'] == 0 and rep['marker_name_in_gold_option'] == 0
    assert rep['unique_ids'] and rep['gold_in_options_all'] and rep['arms_differ_only_in_second_line']
    (ROOT / 'items.json').write_text(json.dumps(items, indent=1, ensure_ascii=False) + '\n')
    rep['items_sha256'] = digest(items)
    rep['bank_seed'] = BANK_SEED
    rep['counts'] = {'real': len(real), 'calibration': len(cal), 'total': len(items)}
    (ROOT / 'AUDIT.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'real': len(real), 'calibration': len(cal), 'items_sha256': rep['items_sha256'],
                      'gold_positions': rep['gold_position_per_stratum'], 'shared_words': rep['span_option_shared_content_words']}, ensure_ascii=False))
