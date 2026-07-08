# -*- coding: utf-8 -*-
"""Этап 21 (§CK): решётка Кобер v2 — классы финальных знаков по общим
основам (чистая комбинаторика, без чтений).

Строки решётки — основы (первые len-1 знаков слова, len>=3, основа >=2);
столбцы — финальные знаки. Основа «многофинальна», если засвидетельствована
с >=2 разными финалями. Статистика: (1) число многофинальных основ против
Null-B; (2) граф со-встречаемости финалей (ребро = >=1 общая основа; вес =
число общих основ); пары с весом >=2 и компоненты по ним — кандидаты
«класса окончаний» LA (аналог падежных колонок Кобер в LB).
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words = sorted(lex)
lengths = [len(w) for w in words]

def grid(word_list):
    stems = defaultdict(set)
    for w in word_list:
        if len(w) >= 3:
            stems[w[:-1]].add(w[-1])
    multi = {s: f for s, f in stems.items() if len(f) >= 2}
    return multi

obs = grid(words)
print(f'многофинальных основ: {len(obs)}')
for s, fs in sorted(obs.items(), key=lambda kv: -len(kv[1])):
    print(f'   {"-".join(s):<16} + {{{", ".join(sorted(fs))}}}')

# нуль
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
    sims.append(len(grid(gen_B())))
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
p = sum(1 for x in sims if x >= len(obs)) / R
print(f'нуль: {mu:.1f}±{sd:.1f}, p={p:.4f}')

# граф со-встречаемости финалей
edge = Counter()
for s, fs in obs.items():
    fs = sorted(fs)
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            edge[(fs[i], fs[j])] += 1
print('\nпары финалей с общими основами (вес >=1):')
for (a, b), c in edge.most_common():
    stems_ab = [s for s, fs in obs.items() if a in fs and b in fs]
    ex = '; '.join('-'.join(s) for s in stems_ab[:3])
    print(f'   {a:<5}~ {b:<5} вес {c}  [{ex}]')

# компоненты по рёбрам веса >=2
strong = [(a, b) for (a, b), c in edge.items() if c >= 2]
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
for a, b in strong:
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb
comp = defaultdict(set)
for a, b in strong:
    comp[find(a)].update([a, b])
print('\nкомпоненты финалей (рёбра веса >=2) — кандидаты класса окончаний:')
for r, mem in comp.items():
    print(f'   {{{", ".join(sorted(mem))}}}')
if not comp:
    print('   нет (все рёбра единичные)')
print('''
Чтение: p разведочное; «класс окончаний» здесь — строго комбинаторный
объект (финали, систематически делящие основы), связь с падежами/родами —
лишь возможная интерпретация при подтверждении на большем корпусе.
Сопоставить с §C (чередования делят согласную) и §CE (гласные пары).''')
