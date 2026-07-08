# -*- coding: utf-8 -*-
"""Этап 14 (§BK): морфотактика биморфов — сеть сочетаемости элементов.

Для 34 биморфов (§BI): в каких длинных словах они соседствуют друг с другом
и с калиброванными маркерами (A-, -JA, PI-); матрица «элемент слева ×
элемент справа»; примеры трёх-компонентных разборов слов.
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
WORDS = set(lex)

# биморфы из §BI (пересчёт тем же критерием)
two = [w for w in WORDS if len(w) == 2]
BIM = []
for x in two:
    pre = sum(1 for w in WORDS if len(w) > 2 and w[:2] == x)
    suf = sum(1 for w in WORDS if len(w) > 2 and w[-2:] == x)
    if pre + suf >= 2: BIM.append(x)
BIMset = set(BIM)
print(f'биморфов: {len(BIM)}')

# сочетаемость: слово длины >=4 содержит два биморфа встык или через маркер
MARK = {'A', 'JA', 'PI', 'I'}
pairs = Counter(); examples = defaultdict(list)
for w in WORDS:
    if len(w) < 4: continue
    for i in range(len(w) - 1):
        left = w[i:i + 2]
        if left not in BIMset: continue
        # встык
        if i + 4 <= len(w) and w[i + 2:i + 4] in BIMset:
            key = (left, w[i + 2:i + 4], 'встык')
            pairs[key] += 1; examples[key].append(w)
        # через один знак-маркер
        if i + 5 <= len(w) and w[i + 2] in MARK and w[i + 3:i + 5] in BIMset:
            key = (left, w[i + 3:i + 5], f'через {w[i + 2]}')
            pairs[key] += 1; examples[key].append(w)
print('\n=== пары биморфов внутри слов ===')
for (a, b, mode), n in pairs.most_common(20):
    ex = ', '.join('-'.join(x) for x in examples[(a, b, mode)][:2])
    print(f'   {"-".join(a)} + {"-".join(b)} ({mode}): ×{n} [{ex}]')

# биморф + калиброванный маркер на краях
print('\n=== биморфы с краевыми маркерами ===')
edge = Counter(); edge_ex = defaultdict(list)
for w in WORDS:
    if len(w) < 3: continue
    if w[0] in MARK and w[1:3] in BIMset:
        edge[(w[0] + '-', tuple(w[1:3]))] += 1
        edge_ex[(w[0] + '-', tuple(w[1:3]))].append(w)
    if w[-1] == 'JA' and w[-3:-1] in BIMset:
        edge[(tuple(w[-3:-1]), '-JA')] += 1
        edge_ex[(tuple(w[-3:-1]), '-JA')].append(w)
for key, n in edge.most_common(15):
    a, b = key
    lab = (a if isinstance(a, str) else '-'.join(a)) + ' ⊕ ' + \
          (b if isinstance(b, str) else '-'.join(b))
    ex = ', '.join('-'.join(x) for x in edge_ex[key][:2])
    print(f'   {lab}: ×{n} [{ex}]')
