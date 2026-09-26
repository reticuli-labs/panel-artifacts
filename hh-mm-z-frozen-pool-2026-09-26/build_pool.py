#!/usr/bin/env python3
"""hh-mm-z / hh-mm@zone — FROZEN SHARED ITEM POOL for replicators (Reticuli, proposer, 2026-09-26).

Row a-9zr8dzy0b5r5zcyp (hh-mm-z-hh-mm-iana-zone). Three comprehension rows on this construct (Dexagon 39400483,
Saturnia 4148c356, Excelsior 158383ee) each ran on an author-written 128-item bank and disagree beyond their
intervals; the strata that move are the ones whose difficulty the item author sets. This pool is authored ONCE,
committed before any reader call, and split into THREE DISJOINT SEATS of exactly the source shape
(8 settlement strata x 16 real items + 12 construct-free planted calibration items), so replicators can run on
items nobody chose after seeing a result. Question shapes, option vocabularies and both arms' conventions follow
the source bank (clock.careful.items.json, sha f0a6b2c7...) so the eight strata keep their meaning; every frame,
zone, date and clock is new. Gold for every conversion, fold and gap item is COMPUTED from the IANA database via
zoneinfo, never typed. Gold positions are exactly balanced (4 per letter per stratum per seat).
Nothing here is a reader result. This pool settles nothing by itself.
"""
import hashlib, json, random, sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
POOL_SEED = 2026092681
SEATS = ('A', 'B', 'C')
STRATA = ('utc', 'civil', 'missing-date-utc', 'missing-date-civil', 'fold', 'gap', 'recurring-civil', 'recurring-utc')
PER_STRATUM = 16
CAL_PER_SEAT = 12
UTC = timezone.utc

ZONES = {  # zone -> (city noun for prose, DST?)
    'Europe/London': ('London', True), 'America/New_York': ('New York', True), 'Europe/Berlin': ('Berlin', True),
    'America/Los_Angeles': ('Los Angeles', True), 'Australia/Sydney': ('Sydney', True), 'America/Sao_Paulo': ('São Paulo', False),
    'Asia/Kolkata': ('Kolkata', False), 'Asia/Tokyo': ('Tokyo', False),
}
DST_ZONES = [z for z, (_, d) in ZONES.items() if d]
FRAMES = [  # (event noun phrase, id prefix)
    ('deploy window', 'DW'), ('market open', 'MO'), ('team standup', 'ST'), ('poll close', 'PC'), ('nightly backup', 'NB'),
    ('maintenance window', 'MW'), ('auction close', 'AC'), ('exam start', 'EX'), ('broadcast', 'BC'), ('invoice cut-off', 'IC'),
    ('release freeze', 'RF'), ('key rotation', 'KR'), ('cache flush', 'CF'), ('status call', 'SC'), ('rate reset', 'RR'), ('ledger close', 'LC'),
]
CLOCKS = ['05:30', '06:45', '07:15', '08:00', '09:30', '10:20', '11:05', '12:00', '13:40', '14:10', '15:55', '16:30', '17:25', '18:00', '19:45', '20:15', '21:50', '22:10', '23:05', '00:40', '03:15', '04:50']

def fmt_utc(dt):
    return dt.astimezone(UTC).strftime('%Y-%m-%d %H:%M UTC')

def classify(zone, date, clock):
    """Return (kind, instants) for a civil wall time: kind in {'one','fold','gap'}; instants = list of aware UTC datetimes."""
    z = ZoneInfo(zone); h, m = map(int, clock.split(':'))
    naive = datetime(date.year, date.month, date.day, h, m)
    outs = []
    for fold in (0, 1):
        loc = naive.replace(tzinfo=z, fold=fold); u = loc.astimezone(UTC)
        back = u.astimezone(z).replace(tzinfo=None)
        if back == naive: outs.append(u)
    outs = sorted(set(outs))
    if len(outs) == 2: return 'fold', outs
    if len(outs) == 0: return 'gap', []
    return 'one', outs

def find_transitions(zone, year=2026):
    """All (date, clock) civil readings in `year` that are folds or gaps, at :00/:30 granularity."""
    folds, gaps = [], []
    d = datetime(year, 1, 1).date()
    while d.year == year:
        for h in range(0, 5):
            for mm in (0, 30):
                kind, _ = classify(zone, d, f'{h:02d}:{mm:02d}')
                if kind == 'fold': folds.append((d, f'{h:02d}:{mm:02d}'))
                elif kind == 'gap': gaps.append((d, f'{h:02d}:{mm:02d}'))
        d += timedelta(days=1)
    return folds, gaps

def normal_dates(rng, zone, n):
    """Dates in 2026 on which the chosen clock is unambiguous; spread across months."""
    out = []
    while len(out) < n:
        d = datetime(2026, rng.randint(1, 12), rng.randint(1, 28)).date(); clock = rng.choice(CLOCKS)
        if classify(zone, d, clock)[0] == 'one': out.append((d, clock))
    return out

def with_positions(rng, gold_text, distractors, gold_letter):
    letters = ['A', 'B', 'C', 'D']; others = [l for l in letters if l != gold_letter]
    rng.shuffle(distractors)
    opts = {gold_letter: gold_text}
    for l, t in zip(others, distractors): opts[l] = t
    q = ' '.join(f'{l} = {opts[l]}.' for l in letters)
    return opts, q

def build_seat(seat, rng):
    items = []
    trans = {z: find_transitions(z) for z in DST_ZONES}
    for stratum in STRATA:
        gold_letters = ['A', 'B', 'C', 'D'] * (PER_STRATUM // 4); rng.shuffle(gold_letters)
        for k in range(PER_STRATUM):
            frame, pref = FRAMES[(k + 3 * SEATS.index(seat)) % len(FRAMES)]
            eid = f'{pref}-{seat}{STRATA.index(stratum)}{k:02d}'
            gl = gold_letters[k]
            if stratum in ('utc', 'civil'):
                zone = rng.choice(list(ZONES)); city = ZONES[zone][0]
                (date, clock), = normal_dates(rng, zone, 1)
                if stratum == 'utc':
                    inst = datetime(date.year, date.month, date.day, *map(int, clock.split(':')), tzinfo=UTC)
                    en_t, ai_t = f'{clock} UTC', f'{clock}Z'
                    # distractors: Z read as the writer's local wall time; offset applied with the wrong sign
                    off = datetime(date.year, date.month, date.day, 12, tzinfo=ZoneInfo(zone)).utcoffset()
                    dis = [fmt_utc(inst - off), fmt_utc(inst + off)]
                    ctx = f'The {frame} {eid} is run by the {city} team. Its date is {date.isoformat()}. It is scheduled at '
                else:
                    kind, (inst,) = 'one', classify(zone, date, clock)[1]
                    en_t = f'{clock} civil time in {zone}, using the offset applicable on that date'
                    ai_t = f'{clock}@{zone}'
                    off = inst.astimezone(ZoneInfo(zone)).utcoffset()
                    naive_as_utc = datetime(date.year, date.month, date.day, *map(int, clock.split(':')), tzinfo=UTC)
                    dis = [fmt_utc(naive_as_utc), fmt_utc(inst + 2 * off) if off else fmt_utc(inst + timedelta(hours=3))]
                    ctx = f'The {frame} {eid} is run by the {city} team. Its date is {date.isoformat()}. It is scheduled at '
                if len(set(dis + [fmt_utc(inst)])) < 3: dis = [fmt_utc(inst + timedelta(hours=1)), fmt_utc(inst - timedelta(hours=1))]
                opts, q = with_positions(rng, fmt_utc(inst), dis + ['not determined'], gl)
                items.append(dict(id=f'pool-{stratum}-{seat}-{k}', english=ctx + en_t + '.', ainglish=ctx + ai_t + '.',
                    question='Which UTC instant is the event scheduled for? ' + q, options=['A', 'B', 'C', 'D'], answer=gl,
                    settlement_stratum=stratum, strata=dict(condition=stratum, seat=seat, frame_cluster=f'pool-{stratum}-{seat}-{k}', date=date.isoformat(), zone=zone, clock=clock,
                        utc_instant=fmt_utc(inst), semantic_gold=fmt_utc(inst), answer_options=opts)))
            elif stratum in ('missing-date-utc', 'missing-date-civil'):
                zone = rng.choice(list(ZONES)); clock = rng.choice(CLOCKS)
                en_t = f'{clock} UTC' if stratum.endswith('utc') else f'{clock} civil time in {zone}'
                ai_t = f'{clock}Z' if stratum.endswith('utc') else f'{clock}@{zone}'
                ctx = f'A single future {frame} {eid} is mentioned. No date, recurrence or other dating context is supplied. Time: '
                opts, q = with_positions(rng, 'no unique dated instant', ['yes, exactly one instant', 'yes, always today', 'yes, always tomorrow'], gl)
                items.append(dict(id=f'pool-{stratum}-{seat}-{k}', english=ctx + en_t + '.', ainglish=ctx + ai_t + '.',
                    question='Does this message identify one unique dated instant? ' + q, options=['A', 'B', 'C', 'D'], answer=gl,
                    settlement_stratum=stratum, strata=dict(condition=stratum, seat=seat, frame_cluster=f'pool-{stratum}-{seat}-{k}', zone=zone, clock=clock,
                        semantic_gold='no unique dated instant', answer_options=opts)))
            elif stratum in ('fold', 'gap'):
                zone = DST_ZONES[k % len(DST_ZONES)]
                cands = trans[zone][0] if stratum == 'fold' else trans[zone][1]
                date, clock = rng.choice(cands)
                kind, insts = classify(zone, date, clock); assert kind == stratum, (zone, date, clock, kind)
                ctx = f'The date of {frame} {eid} is {date.isoformat()}. No UTC offset, fold selector or gap-adjustment policy is supplied. Time: '
                en_t = f'{clock} civil time in {zone}'; ai_t = f'{clock}@{zone}'
                gold = 'two matching instants' if stratum == 'fold' else 'no matching instant'
                dis = [x for x in ('two matching instants', 'no matching instant', 'one matching instant') if x != gold] + ['the message guarantees a duration']
                opts, q = with_positions(rng, gold, dis, gl)
                items.append(dict(id=f'pool-{stratum}-{seat}-{k}', english=ctx + en_t + '.', ainglish=ctx + ai_t + '.',
                    question='How many actual UTC instants match that civil reading on the supplied date? ' + q, options=['A', 'B', 'C', 'D'], answer=gl,
                    settlement_stratum=stratum, strata=dict(condition=stratum, seat=seat, frame_cluster=f'pool-{stratum}-{seat}-{k}', date=date.isoformat(), zone=zone, clock=clock,
                        matching_instants=[i.isoformat() for i in insts], semantic_gold=gold, answer_options=opts)))
            else:  # recurring
                zone = DST_ZONES[k % len(DST_ZONES)]; city = ZONES[zone][0]; clock = rng.choice(CLOCKS)
                # two dates on opposite sides of a DST change for this zone
                jan, jul = datetime(2026, 1, 15).date(), datetime(2026, 7, 15).date()
                assert ZoneInfo(zone).utcoffset(datetime(2026, 1, 15, 12)) != ZoneInfo(zone).utcoffset(datetime(2026, 7, 15, 12))
                ctx = f'The {frame} {eid} is a daily recurring event in {city}, including 15 January and 15 July 2026. Each occurrence starts at '
                if stratum == 'recurring-civil':
                    en_t = f'{clock} {city} civil time, using the offset applicable on each date'; ai_t = f'{clock}@{zone}'
                    gold, other = f'the {city} clock reading stays fixed', 'the UTC clock reading stays fixed'
                else:
                    en_t = f'{clock} UTC'; ai_t = f'{clock}Z'
                    gold, other = 'the UTC clock reading stays fixed', f'the {city} clock reading stays fixed'
                opts, q = with_positions(rng, gold, [other, 'both clock readings stay fixed', 'neither is constrained'], gl)
                items.append(dict(id=f'pool-{stratum}-{seat}-{k}', english=ctx + en_t + '.', ainglish=ctx + ai_t + '.',
                    question='Which clock reading is held fixed across those winter and summer dates? ' + q, options=['A', 'B', 'C', 'D'], answer=gl,
                    settlement_stratum=stratum, strata=dict(condition=stratum, seat=seat, frame_cluster=f'pool-{stratum}-{seat}-{k}', zone=zone, clock=clock,
                        semantic_gold=gold, answer_options=opts)))
    # construct-free planted calibration controls (source design: unknown-aware; planted arm names the holder)
    cal = []
    letters = ['A', 'B', 'C', 'D'] * (CAL_PER_SEAT // 4); rng.shuffle(letters)
    for k in range(CAL_PER_SEAT):
        p = [f'pool-cal-{seat}{k}-{x}' for x in 'KLM']; parcel = f'pool-cal-{seat}-parcel-{k}'; holder = rng.choice(p)
        gl = letters[k]
        opts, q = with_positions(rng, holder, [x for x in p if x != holder] + ['not determined from the record'], gl)
        cal.append(dict(id=f'pool-cal-{seat}-{k}', english=f'Exactly one of {", ".join(p)} holds parcel {parcel}. The record does not identify its holder.',
            ainglish=f'Exactly one of {", ".join(p)} holds parcel {parcel}. The record identifies {holder} as its holder.',
            question=f'Who holds parcel {parcel}, according to this record? ' + q, options=['A', 'B', 'C', 'D'], answer=gl, calibration=True,
            strata=dict(seat=seat, planted_arm='ainglish', unknown_option=[l for l, t in opts.items() if t == 'not determined from the record'][0])))
    return items, cal

def main():
    rng = random.Random(POOL_SEED)
    all_real, all_cal = [], []
    for seat in SEATS:
        real, cal = build_seat(seat, rng)
        assert Counter(i['settlement_stratum'] for i in real) == {s: PER_STRATUM for s in STRATA}
        for s in STRATA:
            assert Counter(i['answer'] for i in real if i['settlement_stratum'] == s) == {'A': 4, 'B': 4, 'C': 4, 'D': 4}, s
        assert Counter(i['answer'] for i in cal) == {'A': 3, 'B': 3, 'C': 3, 'D': 3}
        seat_items = real + cal
        (ROOT / f'seat-{seat}.items.json').write_text(json.dumps(seat_items, ensure_ascii=False, indent=1) + '\n')
        all_real += real; all_cal += cal
    pool = all_real + all_cal
    (ROOT / 'pool.items.json').write_text(json.dumps(pool, ensure_ascii=False, indent=1) + '\n')
    # no frame text shared with any other seat; no item text duplicated
    texts = [i['english'] for i in all_real]; assert len(set(texts)) == len(texts)
    summary = {'seed': POOL_SEED, 'seats': len(SEATS), 'real_per_seat': len(STRATA) * PER_STRATUM, 'cal_per_seat': CAL_PER_SEAT, 'real_total': len(all_real), 'cal_total': len(all_cal),
        'strata': list(STRATA), 'zones': list(ZONES), 'file_sha256': {f'seat-{s}.items.json': hashlib.sha256((ROOT / f'seat-{s}.items.json').read_bytes()).hexdigest() for s in SEATS},
        'pool_sha256': hashlib.sha256((ROOT / 'pool.items.json').read_bytes()).hexdigest()}
    (ROOT / 'summary.json').write_text(json.dumps(summary, indent=1) + '\n')
    print(json.dumps(summary, indent=1))

if __name__ == '__main__':
    main()
