"""Register-wide census: how many proposal rows carry their title as their problem statement,
and how many AMENDED rows had a distinct problem on the predecessor that the successor lost.
Public API only (no credentials needed for reads). Run: python census.py > census.out"""
import json, collections, datetime
from ainglish.client import AinglishClient
c = AinglishClient()
rows = {}
for p in c.iter_proposals(page_size=200):
    slug = p.get('slug')
    if not slug: continue
    full = c.proposal(slug)  # list rows omit long text fields; fetch each
    rows[slug] = {k: full.get(k) for k in ('slug','public_id','title','problem','stage','supersedes','superseded_by','created_at','kind','proposer')}
print('proposals fetched:', len(rows))
def eq(r): return (r.get('problem') or '').strip() == (r.get('title') or '').strip()
roots = [r for r in rows.values() if not r.get('supersedes')]
succ = [r for r in rows.values() if r.get('supersedes')]
print('roots:', len(roots), 'problem==title:', sum(map(eq, roots)))
print('successors:', len(succ), 'problem==title:', sum(map(eq, succ)))
damaged, preserved, written, uninformative, missing_pred = [], [], [], [], []
for r in succ:
    pred = rows.get(r['supersedes'] if isinstance(r['supersedes'], str) else (r['supersedes'] or {}).get('slug'))
    if not pred: missing_pred.append(r['slug']); continue
    if not eq(pred) and eq(r): damaged.append((r['slug'], pred['slug'], r.get('stage'), (r.get('proposer') or {}).get('name'), r.get('created_at'), len((pred.get('problem') or '')), len((r.get('problem') or ''))))
    elif not eq(pred) and not eq(r): preserved.append(r['slug'])
    elif eq(pred) and not eq(r): written.append(r['slug'])
    else: uninformative.append(r['slug'])
print('\nsuccessors with an informative predecessor (predecessor problem != title):', len(damaged) + len(preserved))
print('  DAMAGED (predecessor distinct problem -> successor problem == title):', len(damaged))
print('  preserved (both distinct):', len(preserved))
print('written on amendment (pred title-shaped -> successor distinct):', len(written))
print('uninformative (both title-shaped):', len(uninformative), '| predecessor not found:', len(missing_pred))
by_prop = collections.Counter(d[3] for d in damaged); print('damaged by proposer:', dict(by_prop))
by_month = collections.Counter((d[4] or '')[:7] for d in damaged); print('damaged by month:', dict(sorted(by_month.items())))
print('\nDAMAGED ROWS:')
for d in sorted(damaged, key=lambda x: x[4] or ''): print('  ', d)
json.dump({'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'counts': {'proposals': len(rows), 'roots': len(roots), 'roots_problem_eq_title': sum(map(eq, roots)), 'successors': len(succ), 'successors_problem_eq_title': sum(map(eq, succ)), 'damaged': len(damaged), 'preserved': len(preserved), 'written_on_amendment': len(written), 'uninformative': len(uninformative), 'missing_pred': len(missing_pred)}, 'damaged': damaged, 'preserved': preserved, 'written': written, 'rows': rows}, open('census.json', 'w'), indent=1, ensure_ascii=False, default=str)
