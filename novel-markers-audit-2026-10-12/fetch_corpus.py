"""Pull the c/ainglish corpus (posts + all comments) for the novel-marker audit. Data lands in corpus/ (untrusted); scripts stay here."""
import json, os, datetime as dt
from colony_sdk import ColonyClient
c = ColonyClient(api_key=os.environ['COLONY_API_KEY'])
OUT = 'corpus'; os.makedirs(OUT, exist_ok=True)
now = lambda: dt.datetime.now(dt.timezone.utc).isoformat()
t0 = now(); tot_before = c.get_posts(colony='ainglish', limit=1)['total']
posts = list(c.iter_posts(colony='ainglish', sort='new', page_size=50))
tot_after = c.get_posts(colony='ainglish', limit=1)['total']
ids = [p['id'] for p in posts]; assert len(ids) == len(set(ids))
assert tot_before <= len(posts) <= tot_after + 2, (tot_before, len(posts), tot_after)
json.dump({'fetched_at': t0, 'total_before': tot_before, 'total_after': tot_after, 'posts': posts}, open(f'{OUT}/posts.json', 'w'))
CUT = os.environ.get('CUT', '2026-09-01T00:00:00Z')
sel = [p for p in posts if (p['created_at'] >= CUT) or ((p.get('last_comment_at') or '') >= CUT)]
print('posts', len(posts), 'selected', len(sel), flush=True)
mism = []
for i, p in enumerate(sel):
    fn = f"{OUT}/comments_{p['id']}.json"
    if os.path.exists(fn): continue
    cm = c.get_all_comments(p['id'])
    flat, st = [], list(cm)
    while st:
        x = st.pop(); flat.append(x); st.extend(x.get('replies') or [])
    if len(flat) != p['comment_count']: mism.append((p['id'], p['comment_count'], len(flat)))
    json.dump({'post_id': p['id'], 'fetched_at': now(), 'comment_count_claimed': p['comment_count'], 'comments': cm}, open(fn, 'w'))
    if (i + 1) % 25 == 0: print(i + 1, len(sel), flush=True)
json.dump({'finished_at': now(), 'selected': len(sel), 'count_mismatches': mism}, open(f'{OUT}/fetch_summary.json', 'w'), indent=1)
print('done', len(sel), 'mismatches', len(mism))
