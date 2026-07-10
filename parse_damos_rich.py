# -*- coding: utf-8 -*-
"""Этап 30 (§DM): контекстный слой DĀMOS — damos_context.tsv.

НЕ меняет замороженные правила §DH; дополнительный слой для будущих
тестов: слово → сайты, серии, число документов, доля повреждённых
контекстов (токены с ][ рядом). Вне стресс-ростера (кэш .damos_cache/).
"""
import sys, json, os, re
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')

info = defaultdict(lambda: {'docs': set(), 'sites': Counter(),
                            'series': Counter(), 'dmg': 0, 'n': 0})
n_items = 0
for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    n_items += 1
    head = (item.get('heading_short') or '').strip()
    m = re.match(r'^([A-Z]{2})', head)
    site = m.group(1) if m else '?'
    ser = ((item.get('series') or '') + (item.get('subseries') or '')).strip()
    content = item.get('content') or ''
    for raw_line in content.split('\n'):
        toks = raw_line.replace(',', ' ').split()
        for j, rt in enumerate(toks):
            t = rt.strip('][')
            if not t or not WORD_RE.match(t):
                continue
            k = tuple(t.split('-'))
            e = info[k]
            e['docs'].add(head or fn)
            e['sites'][site] += 1
            e['series'][ser or '?'] += 1
            e['n'] += 1
            near_dmg = ('[' in rt or ']' in rt or
                        (j > 0 and (']' in toks[j-1] or '[' in toks[j-1])) or
                        (j + 1 < len(toks) and
                         ('[' in toks[j+1] or ']' in toks[j+1])))
            if near_dmg:
                e['dmg'] += 1

print(f'документов: {n_items}; слов с контекстом: {len(info)}')
with open('damos_context.tsv', 'w', encoding='utf-8') as f:
    f.write('word\tn_tokens\tn_docs\tsites\ttop_series\tdamaged_share\n')
    for w in sorted(info, key=lambda x: -info[x]['n']):
        e = info[w]
        f.write('\t'.join([
            '-'.join(w), str(e['n']), str(len(e['docs'])),
            ','.join(f'{s}:{c}' for s, c in e['sites'].most_common(4)),
            ','.join(f'{s}:{c}' for s, c in e['series'].most_common(3)),
            f'{e["dmg"] / e["n"]:.2f}']) + '\n')
print('damos_context.tsv записан')
