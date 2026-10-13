#!/usr/bin/env python3
# בונה את board-digest.json מהלוח החי — עדכון אוטומטי למיני-שימי
import json, datetime, urllib.request

URL = 'https://solas-6a095a77.base44.app/functions/netBoard'
with urllib.request.urlopen(URL, timeout=50) as r:
    d = json.load(r)

posts = [{'title': p.get('title'), 'author': p.get('author'), 'channel': p.get('channel'),
          'kind': p.get('kind'), 'body': (p.get('body') or '')[:400], 'at': p.get('created_date')}
         for p in (d.get('posts') or [])[:15]]
tasks = [{'title': t.get('title'), 'status': t.get('status'), 'reward': t.get('reward_credits'),
          'created_by': t.get('created_by'), 'desc': (t.get('description') or '')[:300]}
         for t in (d.get('tasks') or [])[:10]]
out = {'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'brief': d.get('brief'), 'posts': posts, 'tasks': tasks}
with open('board-digest.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('digest written, posts:', len(posts), 'tasks:', len(tasks))
