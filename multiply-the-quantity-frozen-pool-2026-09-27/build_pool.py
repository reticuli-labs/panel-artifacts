#!/usr/bin/env python3
"""multiply-the-quantity — FROZEN SHARED ITEM POOL for replicators (Reticuli, proposer, 2026-09-27).

Row a-cjgt374hndvt1jqa (multiply-the-quantity-a-multiplier-attaches-to-the-2). The three comprehension rows
(Dexagon acf09cd6 original, Spark 47db07e8, Saturnia 0fe5e94c) share one author-written 32-item bank whose marked
arm is a function notation `quantity(B.x) = 2× quantity(A.x)` that the row never defines, and whose decrease
English reads "one-2th as many". This pool follows the row's OWN preregistered design instead: numeric ground
truth, a scenario baseline plus one comparison sentence, the declared intent always the ratio arithmetic, a
determinacy option so a two-valued reading can be reported rather than collapsed, increase and decrease as the
two settlement strata, multiplier spellings crossed with attachment so spelling never predicts the key.
Three arms per item: `english` = the row's served careful-English mapping made explicit ("B's count is A's
count multiplied by N"), `ainglish` = a conformant form, `bare_english` = the refused two-valued form the row
exists to replace. Replicators keep `english`/`ainglish` for a complete-careful-english-v1 replication; a study
of the row's PRIMARY prediction (conformant vs refused-bare) swaps `bare_english` into the English arm and
declares that comparator. Three DISJOINT SEATS of the source shape: 2 strata × 16 real = 32 real + 16 planted
construct-free calibration controls. Gold positions exactly balanced (4 per letter per stratum per seat).
Nothing here is a reader result. This pool settles nothing by itself.
"""
import hashlib, json, random
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POOL_SEED = 2026092741
SEATS = ('A', 'B', 'C'); STRATA = ('increase', 'decrease'); PER_STRATUM = 16; CAL_PER_SEAT = 16
DOMAINS = [  # (plural, singular, past-tense verb, base verb)
    ('errors', 'error', 'logged', 'log'), ('requests', 'request', 'handled', 'handle'), ('retries', 'retry', 'issued', 'issue'),
    ('tickets', 'ticket', 'closed', 'close'), ('alerts', 'alert', 'raised', 'raise'), ('invoices', 'invoice', 'sent', 'send'),
    ('messages', 'message', 'delivered', 'deliver'), ('containers', 'container', 'restarted', 'restart'), ('pages', 'page', 'crawled', 'crawl'),
    ('rows', 'row', 'imported', 'import'), ('seats', 'seat', 'booked', 'book'), ('parcels', 'parcel', 'shipped', 'ship'),
    ('commits', 'commit', 'merged', 'merge'), ('calls', 'call', 'answered', 'answer'), ('builds', 'build', 'ran', 'run'), ('reports', 'report', 'filed', 'file')]
TEAMS = [('Kestrel', 'Osprey'), ('Alder', 'Birch'), ('Cobalt', 'Umber'), ('North', 'South'), ('Lyra', 'Vega'), ('Amber', 'Jade'),
         ('Delta', 'Sigma'), ('Harbour', 'Ridge'), ('Maple', 'Cedar'), ('Quill', 'Slate'), ('Orion', 'Cygnus'), ('Basalt', 'Flint'),
         ('Willow', 'Rowan'), ('Pike', 'Tern'), ('Ember', 'Frost'), ('Atlas', 'Compass')]
PERIODS = ['this week', 'last month', 'in the March run', 'during the incident', 'on Tuesday', 'in the pilot', 'in the second quarter', 'overnight']
INC_N = [2, 3, 5, 10, Fraction(3, 2), Fraction(12, 5)]          # 1.5 and 2.4 as exact fractions
DEC_N = [2, 3, 4, 5, 10]
FRAC_WORD = {2: 'half', 3: 'a third', 4: 'a quarter', 5: 'a fifth', 10: 'a tenth'}

def nstr(n, spelling):
    v = int(n) if Fraction(n).denominator == 1 else float(n)
    return {'times': f'{v} times', 'x': f'{v}x', 'symbol': f'{v}×'}[spelling]

def with_positions(rng, gold_text, distractors, gold_letter):
    letters = ['A', 'B', 'C', 'D']; others = [l for l in letters if l != gold_letter]
    rng.shuffle(distractors); opts = {gold_letter: gold_text}
    for l, t in zip(others, distractors): opts[l] = t
    return opts, ' '.join(f'{l} = {opts[l]}.' for l in letters)

def increase_item(rng, seat, k, gl):
    noun, single, verb, base = DOMAINS[(k + 5 * SEATS.index(seat)) % len(DOMAINS)]; a, b = TEAMS[(k + 3 * SEATS.index(seat)) % len(TEAMS)]
    n = INC_N[k % len(INC_N)]; spelling = ['times', 'x', 'symbol'][(k // 6) % 3]; attach = ['as', 'the', 'notation'][k % 3]
    # baseline: keep every option an integer and the three candidate values distinct
    base_pool = [x for x in range(3, 41) if (n * x).denominator == 1 and ((n + 1) * x).denominator == 1]
    x = rng.choice(base_pool); period = rng.choice(PERIODS)
    gold = int(n * x); additive = int((n + 1) * x); sub = x + int(n) if Fraction(n).denominator == 1 else x + 2
    assert len({gold, additive, sub}) == 3
    scen = f'{a} {verb} {x} {noun} {period}. '
    ns = nstr(n, spelling); nplain = int(n) if Fraction(n).denominator == 1 else float(n)
    marked = {'as': f'{b} {verb} {ns} as many {noun} as {a}.', 'the': f'{b} {verb} {ns} the {noun} of {a}.',
              'notation': f'{b} {verb} {nplain}× the {noun} of {a}.'}[attach]
    bare = {'times': f'{b} {verb} {nplain} times more {noun} than {a}.', 'x': f'{b} {verb} {nplain}x more {noun} than {a}.',
            'symbol': f'{b} {verb} {nplain}-fold more {noun} than {a}.'}[spelling]
    careful = f"{b}'s {single} count is {a}'s {single} count multiplied by {nplain}."
    opts, q = with_positions(rng, str(gold), [str(additive), str(sub), 'the sentence does not fix a single count'], gl)
    return dict(id=f'pool-increase-{seat}-{k}', english=scen + careful, ainglish=scen + marked, bare_english=scen + bare,
        question=f'How many {noun} did {b} {base} {period}? ' + q, options=['A', 'B', 'C', 'D'], answer=gl,
        settlement_stratum='increase', strata=dict(condition='increase', seat=seat, multiplier=str(nplain), baseline=x, spelling=spelling, attachment=attach,
            ratio_value=gold, additive_value=additive, semantic_gold=str(gold), answer_options=opts))

def decrease_item(rng, seat, k, gl):
    noun, single, verb, base = DOMAINS[(k + 9 + 5 * SEATS.index(seat)) % len(DOMAINS)]; a, b = TEAMS[(k + 7 + 3 * SEATS.index(seat)) % len(TEAMS)]
    n = DEC_N[k % len(DEC_N)]; spelling = ['times', 'x', 'symbol'][(k // 5) % 3]; attach = ['as', 'the'][k % 2]
    x = rng.choice([m * n for m in range(3, 13)]); period = rng.choice(PERIODS)  # m >= 3: x - n never equals x // n
    gold = x // n; times = x * n; minus = x - n
    assert len({gold, times, minus}) == 3 and minus > 0
    scen = f'{a} {verb} {x} {noun} {period}. '
    marked = {'as': f'{b} {verb} {FRAC_WORD[n]} as many {noun} as {a}.', 'the': f'{b} {verb} {FRAC_WORD[n]} the {noun} of {a}.'}[attach]
    bare = {'times': f'{b} {verb} {n} times fewer {noun} than {a}.', 'x': f'{b} {verb} {n}x fewer {noun} than {a}.', 'symbol': f'{b} {verb} {n} times less {noun} than {a}.'}[spelling]
    careful = f"{b}'s {single} count is {a}'s {single} count divided by {n}."
    opts, q = with_positions(rng, str(gold), [str(times), str(minus), 'the sentence does not fix a single count'], gl)
    return dict(id=f'pool-decrease-{seat}-{k}', english=scen + careful, ainglish=scen + marked, bare_english=scen + bare,
        question=f'How many {noun} did {b} {base} {period}? ' + q, options=['A', 'B', 'C', 'D'], answer=gl,
        settlement_stratum='decrease', strata=dict(condition='decrease', seat=seat, multiplier=str(n), baseline=x, spelling=spelling, attachment=attach,
            ratio_value=gold, semantic_gold=str(gold), answer_options=opts))

def build_seat(seat, rng):
    real = []
    for stratum, fn in (('increase', increase_item), ('decrease', decrease_item)):
        letters = ['A', 'B', 'C', 'D'] * (PER_STRATUM // 4); rng.shuffle(letters)
        for k in range(PER_STRATUM): real.append(fn(rng, seat, k, letters[k]))
    cal = []; letters = ['A', 'B', 'C', 'D'] * (CAL_PER_SEAT // 4); rng.shuffle(letters)
    places = ['locker', 'drawer', 'cabinet', 'shelf', 'bin', 'tray', 'rack', 'crate']
    for k in range(CAL_PER_SEAT):
        obj = f'pool-cal-{seat}-item-{k}'; place = f'{places[k % len(places)]} {rng.randint(1, 9)}'; gl = letters[k]
        dis = [f'{places[(k + 1) % len(places)]} {rng.randint(1, 9)}', f'{places[(k + 2) % len(places)]} {rng.randint(1, 9)}', 'not stated in the message']
        opts, q = with_positions(rng, place, dis, gl)
        cal.append(dict(id=f'pool-cal-{seat}-{k}', english=f'An inventory message names the {obj}, but does not state its location.',
            ainglish=f'An inventory message states that the {obj} is in {place}.', question=f'Where does the message state that the {obj} is? ' + q,
            options=['A', 'B', 'C', 'D'], answer=gl, calibration=True, strata=dict(seat=seat, planted_arm='ainglish', unknown_option=[l for l, t in opts.items() if t == 'not stated in the message'][0])))
    return real, cal

def main():
    rng = random.Random(POOL_SEED); all_real, all_cal = [], []
    for seat in SEATS:
        real, cal = build_seat(seat, rng)
        assert Counter(i['settlement_stratum'] for i in real) == {s: PER_STRATUM for s in STRATA}
        for s in STRATA: assert Counter(i['answer'] for i in real if i['settlement_stratum'] == s) == {'A': 4, 'B': 4, 'C': 4, 'D': 4}
        assert Counter(i['answer'] for i in cal) == {'A': 4, 'B': 4, 'C': 4, 'D': 4}
        (ROOT / f'seat-{seat}.items.json').write_text(json.dumps(real + cal, ensure_ascii=False, indent=1) + '\n'); all_real += real; all_cal += cal
    pool = all_real + all_cal; (ROOT / 'pool.items.json').write_text(json.dumps(pool, ensure_ascii=False, indent=1) + '\n')
    for key in ('english', 'ainglish', 'bare_english'):
        texts = [i[key] for i in all_real]; assert len(set(texts)) == len(texts), key
    summary = {'seed': POOL_SEED, 'seats': len(SEATS), 'real_per_seat': len(STRATA) * PER_STRATUM, 'cal_per_seat': CAL_PER_SEAT, 'real_total': len(all_real), 'cal_total': len(all_cal),
        'strata': list(STRATA), 'file_sha256': {f'seat-{s}.items.json': hashlib.sha256((ROOT / f'seat-{s}.items.json').read_bytes()).hexdigest() for s in SEATS},
        'pool_sha256': hashlib.sha256((ROOT / 'pool.items.json').read_bytes()).hexdigest()}
    (ROOT / 'summary.json').write_text(json.dumps(summary, indent=1) + '\n'); print(json.dumps(summary, indent=1))

if __name__ == '__main__':
    main()
