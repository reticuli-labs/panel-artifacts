"""Kavi c3e39114 on 024ca2b6 (2026-10-27): the fixture is a test only if it fails when the predicates stop differing, and only if each expected
verdict names the predicate that produced it. This re-runs BOTH predicates over every candidate row of negative_branch_fixtures.json and exits 1
on any row whose recomputed verdicts or point class differ from the recorded columns. The two arms are both present by construction: rows
where the right answer is "a PDA" (not decompressible; both predicates agree) and rows where it is "not a PDA" (decompressible), the latter split
into the prime-subgroup class (both agree) and the off-subgroup class (the arm where libsodium parts from Solana, the 2026-10-18 defect).
A replacement predicate that overcorrects, refusing points it should accept, fails the prime-subgroup rows; one that under-rejects fails the
off-subgroup rows; one that breaks decompression fails the PDA rows. Usage: python3 fixture_test.py negative_branch_fixtures.json [--mutate]
(--mutate flips one recorded verdict in memory to show the test fails on a disagreement; it never writes)."""
import json, sys
from negative_fixtures import classify, sodium_valid  # defs only; the writer is behind __main__
fx = json.load(open(sys.argv[1])); rows = [(x, r) for x in fx['records'] + fx['artifacts'] for r in x['candidates']]
if '--mutate' in sys.argv:
    rows[0][1]['libsodium_valid_point'] = not rows[0][1]['libsodium_valid_point']; print('MUTATED one recorded verdict in memory')
fails = []; arms = {'pda': 0, 'prime_subgroup': 0, 'off_subgroup': 0}
for x, r in rows:
    h = bytes.fromhex(r['candidate_hex']); c = classify(h)
    got = {'solana_is_pda': c.startswith('not_decompressible'), 'libsodium_valid_point': bool(sodium_valid(h)), 'point_class': c}
    exp = {k: r[k] for k in got}
    if got != exp: fails.append({'record': x.get('record') or x.get('artifact'), 'bump': r['bump'], 'expected': exp, 'got': got})
    arms['pda' if got['solana_is_pda'] else ('prime_subgroup' if c == 'prime_subgroup' else 'off_subgroup')] += 1
print(json.dumps({'rows': len(rows), 'arms': arms, 'disagreeing_arm_rows': sum(1 for _, r in rows if r['solana_is_pda'] != (not r['libsodium_valid_point']) and not r['solana_is_pda'] and r['point_class'] == 'off_subgroup_large_order'), 'fails': fails}, indent=1))
sys.exit(1 if fails else 0)
