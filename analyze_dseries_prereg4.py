# -*- coding: utf-8 -*-
"""Этап 37 (§DW): ПРЕДРЕГИСТРАЦИЯ №4 (коммит b797e9c, до этого файла).

Замороженный эндпойнт: в KN D-документах DĀMOS (>=2 чистых слов)
междокументная повторяемость токенов слота 2 выше, чем слота 1
(Δ = rep2 − rep1 > 0); нуль — обмен позиций внутри документа (p=1/2),
R=10000, seed=42, односторонний. Один прогон. Вне ростера (кэш DĀMOS).
"""
import sys, json, os, re, random
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')

pairs = []
for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    head = (item.get('heading_short') or '')
    if not re.match(r'^KN D[a-z]?\b', head):
        continue
    ws = []
    for raw_line in (item.get('content') or '').split('\n'):
        for rt in raw_line.replace(',', ' ').split():
            if '[' in rt or ']' in rt or '?' in rt:
                continue
            if WORD_RE.match(rt):
                ws.append(rt)
    if len(ws) >= 2:
        pairs.append((head, ws[0], ws[1]))

print(f'KN D-документов: {len(pairs)}')

def rep_shares(prs):
    d1 = defaultdict(set); d2 = defaultdict(set)
    for h, a, b in prs:
        d1[a].add(h); d2[b].add(h)
    r1 = sum(1 for h, a, b in prs if len(d1[a]) >= 2) / len(prs)
    r2 = sum(1 for h, a, b in prs if len(d2[b]) >= 2) / len(prs)
    return r1, r2

r1, r2 = rep_shares(pairs)
d_obs = r2 - r1
print(f'повторяемость слот-1 (пастух): {r1:.3f}; слот-2 '
      f'(коллектор/топоним): {r2:.3f}; Δ={d_obs:+.3f}')
sims = []
for _ in range(R):
    sw = [(h, b, a) if random.random() < 0.5 else (h, a, b)
          for h, a, b in pairs]
    s1, s2 = rep_shares(sw)
    sims.append(s2 - s1)
p = (sum(1 for x in sims if x >= d_obs) + 1) / (R + 1)
print(f'нуль обмена: p={p:.4f} (односторонний)')
print(f'ПРЕДРЕГИСТРАЦИЯ №4: {"ПОДТВЕРЖДЕНА" if p < 0.05 else "НЕ ПОДТВЕРЖДЕНА"}')
print('''
Чтение: пастухи по одному на табличку (уникальны), коллекторы/топонимы
повторяются между табличками — зеркало логики печатей (№3). Один прогон,
результат как вышел.''')
