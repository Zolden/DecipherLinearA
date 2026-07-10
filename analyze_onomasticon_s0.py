# -*- coding: utf-8 -*-
"""Этап 29 (§DH-а): чистая ДОАДАПТИВНАЯ фигура ономастикона (S0).

По аудиту (INPUT_FROM_SOL §1): слоты N6/N7 добавлены адаптивно, поэтому
честная discovery-фигура должна считаться на S0 = {N1, N1b, N2, N3, N4,
N5} — правилах, заявленных до диагностики пропусков. Здесь S0-версия
v8-теста: union двух транскрипций, мишень = слот-имена, чьи слот-метки
пересекают S0; Null-B, R=10000, seed=42. Для реестра hypotheses.tsv.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000
S0 = {'N1', 'N1b', 'N2', 'N3', 'N4', 'N5'}

NS = set()
n_total = n_s0 = 0
for fn in ('lb_name_slots.tsv', 'lb2_name_slots.tsv'):
    for line in open(fn, encoding='utf-8'):
        if line.startswith('word\t'):
            continue
        parts = line.rstrip('\n').split('\t')
        slots = set(parts[1].split(','))
        n_total += 1
        if slots & S0:
            NS.add(tuple(parts[0].split('-')))
            n_s0 += 1
print(f'слот-имена S0 (union): {len(NS)} типов '
      f'({n_s0}/{n_total} строк с S0-меткой)')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words = sorted(lex)
lengths = [len(w) for w in words]

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s:
            return None
        out.append(s.lower())
    return tuple(out)

obs_hits = [w for w in words if len(w) >= 3 and read_lb(w) in NS]
print('S0-слот-подтверждённые >=3:',
      [('-'.join(w)) for w in obs_hits])

pos_pools = {0: [], 1: [], 2: []}
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)

def gen_B():
    for p in pos_pools.values():
        random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = []
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.append(tuple(w))
    return out

sims = []
for _ in range(R):
    wl = gen_B()
    n = sum(1 for w in wl if len(w) >= 3 and read_lb(w) in NS)
    sims.append(n)
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
obs = len(obs_hits)
p = (sum(1 for x in sims if x >= obs) + 1) / (R + 1)
print(f'S0: наблюдаемо {obs}, нуль {mu:.2f}±{sd:.2f}, p={p:.4f} '
      f'((b+1)/(R+1))')
print('''
Чтение: S0 — доадаптивные правила; эта фигура + подтверждающий прогон на
DĀMOS (предрегистрация, hypotheses.tsv) заменяют post-selected v8 в
качестве опорных чисел ономастикона.''')
