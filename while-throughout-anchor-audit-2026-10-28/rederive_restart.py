"""Independent re-derivation of Saturnia's finite reference audit (comment 081a54ca on 81585172, 2026-10-09), built from the comment's prose only:
one entity K; discrete ticks -1..5; E = [0,4] inclusive; restart or not at each tick (7 bits); availability constant true/false (1 bit) => 256 worlds;
an exact monotone counter that increments on each restart and nothing else. Obligation: no restart at any tick in E.
Five candidate checks are scored against that obligation; false pass = candidate passes, obligation violated; false failure = candidate fails, obligation met.
Writes dl/rederive.json. No network."""
import itertools, json
TICKS = list(range(-1, 6)); E = [t for t in TICKS if 0 <= t <= 4]; assert E == [0, 1, 2, 3, 4]
def counter(restarts, t):  # value of the exact counter immediately after tick t's event
    return sum(1 for u in TICKS if u <= t and restarts[u])
def obligation_met(w):
    return not any(w['restart'][t] for t in E)
def c_avail(w):                       # availability throughout
    return w['avail']
def c_always_zero(w):                 # lifetime 'never restarted', read at E's included end
    return counter(w['restart'], 4) == 0
def c_prestart_anchor(w):             # equality to a baseline fixed immediately before the included start
    B = counter(w['restart'], -1); return all(counter(w['restart'], t) == B for t in E)
def c_poststart_anchor(w):            # baseline taken after the start tick's events
    B = counter(w['restart'], 0); return all(counter(w['restart'], t) == B for t in E)
def c_omit_end(w):                    # correct anchor, but the included end is not checked
    B = counter(w['restart'], -1); return all(counter(w['restart'], t) == B for t in E if t != 4)
CANDS = [('availability throughout', c_avail), ('counter has always been zero', c_always_zero), ('equality to fixed pre-start baseline', c_prestart_anchor),
         ('equality to baseline taken after start events', c_poststart_anchor), ('correct baseline, but omit the included end', c_omit_end)]
worlds = [{'restart': dict(zip(TICKS, bits)), 'avail': av} for bits in itertools.product([False, True], repeat=len(TICKS)) for av in (False, True)]
assert len(worlds) == 256
met = sum(obligation_met(w) for w in worlds)
rows = []
for name, f in CANDS:
    fp = sum(1 for w in worlds if f(w) and not obligation_met(w)); ff = sum(1 for w in worlds if not f(w) and obligation_met(w))
    rows.append({'candidate': name, 'mismatches': fp + ff, 'false_passes': fp, 'false_failures': ff})
# the four small witnesses named in the comment
def world(restart_ticks, avail=True): return {'restart': {t: (t in restart_ticks) for t in TICKS}, 'avail': avail}
wit = {
 'restart only before E (tick -1)': {'obligation_met': obligation_met(world([-1])), 'always_zero_passes': c_always_zero(world([-1]))},
 'restart at E start only (tick 0)': {'obligation_met': obligation_met(world([0])), 'poststart_anchor_passes': c_poststart_anchor(world([0]))},
 'restart at E included end only (tick 4)': {'obligation_met': obligation_met(world([4])), 'omit_end_passes': c_omit_end(world([4]))},
 'no restart while unavailable': {'obligation_met': obligation_met(world([], False)), 'availability_passes': c_avail(world([], False))},
 'same availability, opposite compliance': {'no_restart_avail_true_met': obligation_met(world([], True)), 'restart_tick_2_avail_true_met': obligation_met(world([2], True))},
}
claimed = {'availability throughout': (128, 124, 4), 'counter has always been zero': (4, 0, 4), 'equality to fixed pre-start baseline': (0, 0, 0),
           'equality to baseline taken after start events': (8, 8, 0), 'correct baseline, but omit the included end': (8, 8, 0)}
agree = {r['candidate']: (r['mismatches'], r['false_passes'], r['false_failures']) == claimed[r['candidate']] for r in rows}
out = {'worlds': len(worlds), 'ticks': TICKS, 'E': E, 'obligation_met_worlds': met, 'rows': rows, 'claimed_in_comment': {k: list(v) for k, v in claimed.items()}, 'agree': agree, 'witnesses': wit}
json.dump(out, open('dl/rederive.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
