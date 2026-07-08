# -*- coding: utf-8 -*-
"""Этап 17 (§BR): синтаксис записи — полный позиционный профиль операторов.

Продолжение §BO (нач/фин): теперь позиции {вторая, предпоследняя} в
документах >=3 слов. Мотив: §BO показал, что TE не начален — гипотеза
«TE метит слово, за которым стоит» предсказывает избыток ВТОРОЙ позиции
(заголовок + TE). Симметрично: у финальных операторов проверяем
предпоследнюю позицию (слово перед итогом).

Нуль: позиция вхождения равновероятна в своём документе (R=10000,
seed=42); семейный контроль Westfall–Young min-p (семейство = операторы ×
{вторая, предпоследняя}). p разведочные.
"""
import sys, pickle
import numpy as np
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
OPERATORS = ['KU-RO', 'PO-TO-KU-RO', 'KI-RO', 'TE', 'A-DU', 'I-DA',
             'SI-RU-TE', 'SA-RA2', 'KI', 'A-TA-I-*301-WA-JA']

docs_words = []
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) >= 3:
        docs_words.append(ws)
print(f'документов с >=3 словами: {len(docs_words)}')

occ = defaultdict(list)
for ws in docs_words:
    L = len(ws)
    for i, w in enumerate(ws):
        if w in OPERATORS:
            occ[w].append((i, L))

tests = []
for name in OPERATORS:
    o = occ.get(name, [])
    if len(o) < 5:
        continue
    n = len(o)
    sec = sum(1 for i, L in o if i == 1)
    pen = sum(1 for i, L in o if i == L - 2)
    tests.append((name, 'вторая', sec, n, o))
    tests.append((name, 'предпосл', pen, n, o))

rng = np.random.default_rng(42)
sims = np.zeros((R, len(tests)), dtype=np.int32)
for j, (name, side, obs, n, o) in enumerate(tests):
    Ls = np.array([L for _, L in o])
    u = rng.random((R, len(o)))
    if side == 'вторая':
        sims[:, j] = ((u >= 1.0 / Ls) & (u < 2.0 / Ls)).sum(axis=1)
    else:
        sims[:, j] = ((u >= (Ls - 2.0) / Ls) & (u < (Ls - 1.0) / Ls)).sum(axis=1)
obs_arr = np.array([t[2] for t in tests])
p_raw = ((sims >= obs_arr).sum(axis=0) + 1) / (R + 1)
p_sim = np.zeros_like(sims, dtype=np.float64)
for j in range(len(tests)):
    order = np.sort(sims[:, j])
    idx = np.searchsorted(order, sims[:, j], side='left')
    p_sim[:, j] = (R - idx + 1) / (R + 1)
minp = p_sim.min(axis=1)
p_adj = np.array([((minp <= p).sum() + 1) / (R + 1) for p in p_raw])

print(f'\n{"оператор":<20}{"n":>4}{"вт%":>6}{"пп%":>6}'
      f'{"p(вт)":>9}{"p(пп)":>9}{"p̃сем(вт)":>10}{"p̃сем(пп)":>10}')
by = {}
for j, (name, side, obs, n, o) in enumerate(tests):
    by.setdefault(name, {})[side] = (obs, n, p_raw[j], p_adj[j])
for name in OPERATORS:
    if name not in by:
        continue
    s2, n, p2, pa2 = by[name]['вторая']
    pp, _, p3, pa3 = by[name]['предпосл']
    print(f'{name:<20}{n:>4}{s2 / n:>6.0%}{pp / n:>6.0%}'
          f'{p2:>9.4f}{p3:>9.4f}{pa2:>10.4f}{pa3:>10.4f}')

# контекст: полные профили позиций (наблюдаемо, без теста)
print('\nполные профили (доли позиций: 1-я/2-я/середина/предпосл/посл):')
for name in OPERATORS:
    o = occ.get(name, [])
    if len(o) < 5:
        continue
    n = len(o)
    c = [0] * 5
    for i, L in o:
        if i == 0:
            c[0] += 1
        elif i == 1:
            c[1] += 1
        if i == L - 1:
            c[4] += 1
        elif i == L - 2:
            c[3] += 1
        if 1 < i < L - 2:
            c[2] += 1
    print(f'  {name:<20} n={n:<3} ' + '/'.join(f'{x / n:.0%}' for x in c))
print('''
Чтение: «вторая» и «предпоследняя» могут пересекаться с «первой»/«последней»
только в документах из 3 слов (там 2-я = предпоследняя); категории
маргинальные, каждая против своего равномерного нуля. p разведочные;
нач/фин уже протестированы в §BO и здесь не перетестируются.''')
