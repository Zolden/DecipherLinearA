# -*- coding: utf-8 -*-
"""Этап 13, п.4 (§BG): вариативность слота 1 (открытие формулы возлияний).

Инвентарь всех слов, начинающихся с (J)A-TA-I-*301 / TA-I-*301, по сайтам и
носителям; разложение варианта на ось приставки (A-/JA-) и ось хвоста
(-WA-JA / -WA-E / -DE-KA / -U-JA); точный тест сайт-зависимости хвоста
(перестановка сайтов, R=10000, seed=42) — формализация наблюдения §K/§P.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))

occ = []
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and 'TA-I-*301' in v['norm']:
            n = v['norm']
            pre = 'JA-' if n.startswith('JA-') else ('A-' if n.startswith('A-') else '∅')
            tail = n.split('TA-I-*301-')[-1] if 'TA-I-*301-' in n else '∅'
            occ.append({'doc': d['id'], 'site': d['site'], 'sup': d['support'],
                        'norm': n, 'pre': pre, 'tail': tail,
                        'damaged': not v['complete']})
print('=== все вхождения открытия формулы ===')
for o in sorted(occ, key=lambda x: (x['site'], x['doc'])):
    print(f'   {o["norm"]:<26} {o["doc"]:<10} {o["site"]:<4} {o["sup"]:<14} '
          f'{"повр." if o["damaged"] else ""}')

cln = [o for o in occ if not o['damaged']]
print(f'\nцелых: {len(cln)}; приставки: {Counter(o["pre"] for o in cln)}; '
      f'хвосты: {Counter(o["tail"] for o in cln)}')
tab = defaultdict(Counter)
for o in cln: tab[o['site']][o['tail']] += 1
print('сайт × хвост:')
for s, c in sorted(tab.items()): print(f'   {s}: {dict(c)}')

# перестановочный тест: связан ли хвост с сайтом
def stat(pairs_):
    bysite = defaultdict(Counter)
    for s, t in pairs_: bysite[s][t] += 1
    # доля пар документов одного сайта с одинаковым хвостом
    same = diff = same_hit = diff_hit = 0
    items = pairs_
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i][0] == items[j][0]:
                same += 1; same_hit += items[i][1] == items[j][1]
            else:
                diff += 1; diff_hit += items[i][1] == items[j][1]
    if not same or not diff: return None
    return same_hit / same - diff_hit / diff

pairs = [(o['site'], o['tail']) for o in cln]
obs = stat(pairs)
sites = [s for s, _ in pairs]; tails = [t for _, t in pairs]
ge = 0
for _ in range(R):
    random.shuffle(sites)
    d2 = stat(list(zip(sites, tails)))
    if d2 is not None and d2 >= obs - 1e-12: ge += 1
print(f'\nΔ(одинаковый хвост | один сайт − разные сайты) = {obs:+.3f}, '
      f'p={ge / R:.4f} (перестановка сайтов, R={R}, seed=42)')
