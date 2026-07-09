# -*- coding: utf-8 -*-
"""Этап 23 (§CQ-б): решётка v3 — основы с приставочной И финальной
вариацией (кандидаты полных парадигм).

Ядро = слово без первого и последнего знака (len>=4, ядро >=2 знаков).
Ядро «двумерно», если засвидетельствовано (а) с >=2 разными первыми
знаками при какой-либо фиксированной финали ИЛИ по объединению, и
(б) с >=2 разными финалями. Считаем двумерные ядра против Null-B.
Это стык §L/§W (приставки), §CK (финали): у скольких основ вариация
живёт с ОБЕИХ сторон одновременно.
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

def dims(word_list):
    cores = defaultdict(lambda: (set(), set()))
    for w in word_list:
        if len(w) >= 4:
            pre, fin = cores[w[1:-1]]
            pre.add(w[0])
            fin.add(w[-1])
    two = {c: (p, f) for c, (p, f) in cores.items()
           if len(p) >= 2 and len(f) >= 2}
    return two

obs = dims(words)
print(f'двумерных ядер (>=2 первых И >=2 финалей): {len(obs)}')
for c, (p, f) in sorted(obs.items()):
    ws = ['-'.join(w) for w in words
          if len(w) >= 4 and w[1:-1] == c]
    print(f'   [{"-".join(c)}]: первые {sorted(p)} × финали {sorted(f)}')
    print(f'      слова: {ws}')

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
    sims.append(len(dims(gen_B())))
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
p = sum(1 for x in sims if x >= len(obs)) / R
print(f'нуль: {mu:.2f}±{sd:.2f}, p={p:.4f}')
print('''
Чтение: p разведочное; двумерное ядро = кандидат ПОЛНОЙ парадигмы
([приставка]+ядро+[финаль], ср. морфотактику §BK). Список мал — ценность
в конкретных ядрах для точечного разбора.''')
