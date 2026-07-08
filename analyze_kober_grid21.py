# -*- coding: utf-8 -*-
"""Этап 22 (§CO): решётка Кобер v2.1 — двузнаковые окончания.

§CK: классы ОДНОзнаковых финалей не кристаллизуются (рёбра единичные).
Здесь колонки ищутся на ДВУзнаковых окончаниях: для слов len>=4 ядро =
w[:-2], окончание = w[-2:]; ядра с >=2 разными окончаниями; пары
окончаний, делящие >=2 ядра, и их компоненты — прямой аналог триплетов
Кобер (у неё столбцы были как раз многознаковыми хвостами). Нуль gen_B
для числа многоокончательных ядер, R=10000, seed=42.
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
    cores = defaultdict(set)
    for w in word_list:
        if len(w) >= 4:
            cores[w[:-2]].add(w[-2:])
    return {c: e for c, e in cores.items() if len(e) >= 2}

obs = grid(words)
print(f'ядер (len>=2) с >=2 двузнаковыми окончаниями: {len(obs)}')
for c, es in sorted(obs.items(), key=lambda kv: -len(kv[1])):
    print(f'   {"-".join(c):<14} + {{{", ".join("-".join(e) for e in sorted(es))}}}')

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

edge = Counter()
for c, es in obs.items():
    es = sorted(es)
    for i in range(len(es)):
        for j in range(i + 1, len(es)):
            edge[(es[i], es[j])] += 1
strong = [(a, b, c) for (a, b), c in edge.items() if c >= 2]
print(f'\nпар окончаний с >=2 общими ядрами: {len(strong)}')
for a, b, c in sorted(strong, key=lambda t: -t[2]):
    cores_ab = ['-'.join(x) for x, es in obs.items() if a in es and b in es]
    print(f'   {"-".join(a)} ~ {"-".join(b)} (ядер {c}): {cores_ab}')
if not strong:
    print('   нет — колонки не кристаллизуются и на двузнаковых окончаниях')
print('''
Чтение: p разведочное. Появление пар окончаний с >=2 ядрами = первые
«колонки» решётки (аналог триплетов Кобер); их отсутствие = честная
граница нынешнего корпуса.''')
