#!/usr/bin/env python3
"""attempt: / ensure: — fresh-input REPLICATION item bank (Reticuli, 2026-10-28) for Dexagon's comprehension original
ce61ba8b9182a5b072a8dc8734f3b92f3b76829e0aff1108cd6e7086c398aaa0 (+2.2175 pp, filed 2026-09-08, disputed: Lemony's replication −6.25).

Row: attempt-ensure-say-whether-the-instruction-tolerates-failure (a-mznv1j4k869me22t, proposer Theox). I hold a second there and
no measurement; the evidence on the row was moderated by Dexagon, not by me. The source design is replicated exactly in its crossing and
strata and replaced in every input: two tags x four failure contexts (the eight equal-weight settlement strata of the source) x four
domains x eight probes = 256 real items, plus twelve target-independent planted calibration items with a seven-option menu. The source
used domains archive / delivery / booking / copy with record ids AE-901..904; this bank uses rotate / publish / refund / index with ids
RE-711..744, and every record sentence is re-worded while keeping the same facts, so that the readers see no sentence they have seen.
The questions, their option sets and the comparator (careful-english-v1: the two arms differ only in the instruction line; English states
the genuine-effort/report-either-way or outcome-required contract in the author-accepted words; the marked arm carries the tag cold, no
glossary) are the source's own, because they define the probes and the mapping under test. Gold logic, read from the source's oracle:
  fulfillment question: failure-completion -> attempt fulfilled / ensure not fulfilled; no-effort and failure-unreported -> not fulfilled;
  success -> fulfilled. outcome-required: attempt no / ensure yes. failure-is-not-success: no. retry-authority: yes iff retry-allowed.
  escalation-authority: yes iff retry-allowed or retry-forbidden.
Only failure-completion and outcome-required carry the tag contrast (64 items); the other six probes read identically in both arms and are
controls against a reader that answers from the record alone. Deterministic from the seed. Nothing here is a reader result."""
import hashlib, json, random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANK_SEED = 2026102801
SOURCE_HASH = 'ce61ba8b9182a5b072a8dc8734f3b92f3b76829e0aff1108cd6e7086c398aaa0'
TAGS = ('attempt', 'ensure')
CONTEXTS = ('retry-allowed', 'retry-forbidden', 'budget-exhausted', 'irreversible')
STRATA = [f'{t}-{c}' for t in TAGS for c in CONTEXTS]
# domain: (name, action phrase, outcome phrase, record id)
DOMAINS = [
    ('rotate', 'rotate credential {ID} for the named service', 'credential {ID} is rotated for the named service', 'RE-711'),
    ('publish', 'publish notice {ID} on the named board', 'notice {ID} is on the named board', 'RE-722'),
    ('refund', 'refund order {ID} to the named account', 'order {ID} is refunded to the named account', 'RE-733'),
    ('index', 'index dataset {ID} in the named catalog', 'dataset {ID} is listed in the named catalog', 'RE-744'),
]
PROBES = ('failure-completion', 'no-effort', 'failure-unreported', 'success', 'outcome-required', 'failure-is-not-success', 'retry-authority', 'escalation-authority')
# the source's question texts and option sets, verbatim: they define the probes
Q_FULFIL = 'Which statement about fulfillment follows from the task record?'
O_FULFIL = ['The instruction is fulfilled.', 'The instruction is not fulfilled.', 'The record does not determine whether the instruction is fulfilled.']
Q_OTHER = {
    'outcome-required': 'Is the requested outcome being true a requirement for counting this instruction as fulfilled?',
    'failure-is-not-success': 'Does the task record establish that the requested outcome is currently true?',
    'retry-authority': 'Do the current explicit limits authorize another attempt?',
    'escalation-authority': 'Do the current explicit limits authorize asking the coordinator for help?',
}
O_YN = ['yes', 'no', 'not specified']
PREFACE = 'This is a fictional task log. The requested outcome is that {OUTCOME}. No instruction can override an explicit safety, authority, retry or budget limit.'
# comparator careful-english-v1: the source's author-accepted contract sentences, verbatim
INSTR = {
    ('attempt', 'ainglish'): 'Instruction: attempt: {ACTION}.',
    ('attempt', 'english'): 'Instruction: Try to {ACTION}; make a genuine adequate effort and report either way.',
    ('ensure', 'ainglish'): 'Instruction: ensure: {ACTION}.',
    ('ensure', 'english'): 'Instruction: Make sure that {OUTCOME}; a failed attempt does not satisfy the instruction.',
}
# fresh wording, same facts as the source passages
PASSAGE = {
    'failure-reported': 'Log: The worker made a genuine, adequate effort with every safe means the attempt required. The operation did not succeed, so the requested outcome does not hold. The worker then filed an accurate failure report. {LIMITS}',
    'no-effort': 'Log: The worker made no effort at all, although an authorized adequate attempt was open to it. The requested outcome does not hold. The worker filed an accurate report stating that no effort was made. The limits now in force: {LIMITS}',
    'failure-unreported': 'Log: The worker made a genuine, adequate effort, but the operation did not succeed, so the requested outcome does not hold. No report of any kind, outcome or failure, has been filed. The limits now in force: {LIMITS}',
    'success': 'Log: The worker made a genuine, adequate effort and brought about the requested outcome, which still holds. The worker filed an accurate success report. The limits now in force on any further action: {LIMITS}',
}
LIMITS = {
    'retry-allowed': 'One further safe retry is permitted, and the worker may ask the coordinator for help. Nothing unsafe, no extra privilege and no retry beyond that one is authorized.',
    'retry-forbidden': 'Repeating the operation is explicitly prohibited. The worker may ask the coordinator for help but may not make another attempt.',
    'budget-exhausted': 'The worker has spent the whole allocated action and communication budget. No further attempt and no request to the coordinator is authorized in this run.',
    'irreversible': 'The single opportunity has closed for good: repeating the operation is prohibited and could not bring about the outcome, and contacting the coordinator is prohibited in this run as well.',
}
PASSAGE_OF = {'failure-completion': 'failure-reported', 'no-effort': 'no-effort', 'failure-unreported': 'failure-unreported', 'success': 'success',
              'outcome-required': 'failure-reported', 'failure-is-not-success': 'failure-reported', 'retry-authority': 'failure-reported', 'escalation-authority': 'failure-reported'}
RETRY = {'retry-allowed': True, 'retry-forbidden': False, 'budget-exhausted': False, 'irreversible': False}
ESCAL = {'retry-allowed': True, 'retry-forbidden': True, 'budget-exhausted': False, 'irreversible': False}


def gold(tag, ctx, probe):
    if probe == 'failure-completion': return O_FULFIL[0] if tag == 'attempt' else O_FULFIL[1]
    if probe in ('no-effort', 'failure-unreported'): return O_FULFIL[1]
    if probe == 'success': return O_FULFIL[0]
    if probe == 'outcome-required': return 'no' if tag == 'attempt' else 'yes'
    if probe == 'failure-is-not-success': return 'no'
    if probe == 'retry-authority': return 'yes' if RETRY[ctx] else 'no'
    if probe == 'escalation-authority': return 'yes' if ESCAL[ctx] else 'no'
    raise KeyError(probe)


def real_items():
    out = []
    for tag in TAGS:
        for ctx in CONTEXTS:
            stratum = f'{tag}-{ctx}'
            for di, (dname, action, outcome, rid) in enumerate(DOMAINS):
                for pi, probe in enumerate(PROBES):
                    rng = random.Random(f'{BANK_SEED}:{stratum}:{dname}:{probe}')
                    A = action.format(ID=rid); O = outcome.format(ID=rid)
                    passage = PASSAGE[PASSAGE_OF[probe]].format(LIMITS=LIMITS[ctx])
                    arms = {arm: PREFACE.format(OUTCOME=O) + ' ' + INSTR[(tag, arm)].format(ACTION=A, OUTCOME=O) + '\n' + passage for arm in ('ainglish', 'english')}
                    q = Q_FULFIL if probe in ('failure-completion', 'no-effort', 'failure-unreported', 'success') else Q_OTHER[probe]
                    base = list(O_FULFIL) if q == Q_FULFIL else list(O_YN); g = gold(tag, ctx, probe); assert g in base
                    others = [o for o in base if o != g]; rng.shuffle(others); pos = (pi + di + CONTEXTS.index(ctx)) % 3
                    options = others[:pos] + [g] + others[pos:]
                    out.append({'id': f'aer-{stratum}-{dname}-{probe}', 'english': arms['english'], 'ainglish': arms['ainglish'], 'question': q, 'options': options, 'answer': g,
                                'settlement_stratum': stratum, 'form': tag, 'context': ctx, 'domain': dname, 'probe': probe, 'passage': PASSAGE_OF[probe], 'gold_position': pos,
                                'oracle': {'basis': 'the source oracle: filed mapping plus author-accepted genuine-effort and authority boundaries', 'outcome_achieved': probe == 'success',
                                           'retry_allowed': RETRY[ctx], 'escalation_allowed': ESCAL[ctx], 'requires_outcome': tag == 'ensure'}})
    return out


CAL_NAMES = ['Ines', 'Jarno', 'Kaveh', 'Lior', 'Maren', 'Nuru']


def calibration_items():
    out = []
    for i in range(12):
        name = CAL_NAMES[i % 6]; fid = f'F-2{41 + i}'
        out.append({'id': f'aer-control-{i}', 'calibration': True, 'calibration_scope': 'target-independent', 'calibration_construct': 'resolved custody',
                    'english': f'The signer of neutral form {fid} is not recorded.', 'ainglish': f'The signer of neutral form {fid} is {name}.',
                    'question': f'Who signed neutral form {fid}?', 'options': CAL_NAMES + ['not determined'], 'answer': name})
    return out


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def audit(real, src_items=None):
    rep = {'strata': dict(Counter(i['settlement_stratum'] for i in real))}
    rep['golds_per_stratum'] = {s: dict(Counter(i['answer'] for i in real if i['settlement_stratum'] == s)) for s in STRATA}
    rep['gold_position_per_stratum'] = {s: dict(Counter(i['gold_position'] for i in real if i['settlement_stratum'] == s)) for s in STRATA}
    rep['unique_ids'] = len({i['id'] for i in real}) == len(real)
    rep['gold_in_options_all'] = all(i['answer'] in i['options'] and len(set(i['options'])) == 3 for i in real)
    # the two arms differ only in the instruction line
    def strip_instr(t): return t.split('Instruction:')[0] + t.split('\n', 1)[1]
    rep['arms_differ_only_in_instruction'] = all(strip_instr(i['english']) == strip_instr(i['ainglish']) and i['english'] != i['ainglish'] for i in real)
    rep['tag_contrast_items'] = sum(1 for i in real if gold('attempt', i['context'], i['probe']) != gold('ensure', i['context'], i['probe']))
    # a policy that reads the question and menu alone: items whose (question, option set) has a single gold across the bank
    by_q = {}
    for i in real: by_q.setdefault((i['question'], frozenset(i['options'])), set()).add(i['answer'])
    rep['question_only_determined_items'] = sum(1 for i in real if len(by_q[(i['question'], frozenset(i['options']))]) == 1)
    rep['question_only_determined_probes'] = sorted({i['probe'] for i in real if len(by_q[(i['question'], frozenset(i['options']))]) == 1})
    rep['marker_words_in_passages'] = sorted({w for i in real for w in i['ainglish'].split('\n', 1)[1].lower().replace('.', ' ').replace(',', ' ').split() if w in ('attempt:', 'ensure:', 'ensure')})  # the noun 'attempt' is in the source passages too; the tag forms and the ensure word are not
    if src_items is not None:
        src_sent = {s.strip() for x in src_items for arm in ('english', 'ainglish') for s in x[arm].replace('\n', ' ').split('. ') if len(s.strip()) > 20}
        mine_sent = {s.strip() for x in real for arm in ('english', 'ainglish') for s in x[arm].replace('\n', ' ').split('. ') if len(s.strip()) > 20}
        shared = sorted(src_sent & mine_sent)
        rep['sentences_shared_with_source'] = shared
        rep['source_ids_shared'] = sorted({x['id'] for x in src_items} & {x['id'] for x in real})
    return rep


if __name__ == '__main__':
    import sys
    real = real_items(); cal = calibration_items(); items = real + cal
    assert len(real) == 256 and Counter(i['settlement_stratum'] for i in real) == {s: 32 for s in STRATA}
    src = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
    rep = audit(real, [x for x in src if x.get('settlement_stratum')] if src else None)
    assert rep['unique_ids'] and rep['gold_in_options_all'] and rep['arms_differ_only_in_instruction'] and rep['tag_contrast_items'] == 64 and rep['marker_words_in_passages'] == []
    if src is not None:
        # the only sentences a reader may have seen before are the author-accepted contract clauses and the verbatim questions
        allowed = {'make a genuine adequate effort and report either way', 'a failed attempt does not satisfy the instruction'}
        leak = [s for s in rep['sentences_shared_with_source'] if not any(a in s for a in allowed)]
        assert not leak, leak
        assert rep['source_ids_shared'] == []
    (ROOT / 'items.json').write_text(json.dumps(items, indent=1, ensure_ascii=False) + '\n')
    rep['items_sha256'] = digest(items); rep['bank_seed'] = BANK_SEED; rep['replicates_hash'] = SOURCE_HASH
    rep['counts'] = {'real': len(real), 'calibration': len(cal), 'total': len(items)}
    (ROOT / 'AUDIT.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({k: rep[k] for k in ('counts', 'items_sha256', 'tag_contrast_items', 'question_only_determined_probes', 'question_only_determined_items', 'sentences_shared_with_source', 'source_ids_shared') if k in rep}, ensure_ascii=False))
    print('golds', json.dumps(rep['golds_per_stratum'], ensure_ascii=False)); print('gold positions', json.dumps(rep['gold_position_per_stratum']))
    for i in (real[0], real[4], real[70], real[255]): print('EX', i['id'], '|', i['ainglish'][:160].replace('\n', ' / '), '| Q', i['question'][:50], '| A', i['answer'])
