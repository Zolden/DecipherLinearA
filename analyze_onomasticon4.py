# -*- coding: utf-8 -*-
"""Этап 9.1 (§AH, часть 2): ономастикон v4 — слот-имена вместо серий.

NAME_SLOT = слова из lb_name_slots.tsv (потабличные именные слоты N1–N4).
Тесты (Null-B, R=10000, seed=42):
  V4-a: длинные (>=3 знаков) совпадения LA с NAME_SLOT;
  V4-b: топ-30 поведенческих кандидатов LA (§AC) против NAME_SLOT — попадания;
  V4-c: полный список совпадений LA×NAME_SLOT с профилями обеих сторон.
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

name_slot = {}
for line in open('lb_name_slots.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    w, sl, n, ser = (line.rstrip('\n').split('\t') + [''])[:4]
    name_slot[w] = (sl, int(n), ser)
NS = set(name_slot)
print(f'NAME_SLOT: {len(NS)} слов')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); lex_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1; lex_docs[w].add(d['id'])
words = sorted(lex)

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s: return None
        out.append(s.lower())
    return '-'.join(out)

hits = [(w, read_lb(w)) for w in words
        if read_lb(w) in NS]
long_hits = [(w, r) for w, r in hits if len(w) >= 3]
print(f'\nсовпадений LA×NAME_SLOT: {len(hits)} (длинных >=3: {len(long_hits)})')
for w, r in sorted(hits, key=lambda x: -len(x[0])):
    sl, n, ser = name_slot[r]
    print(f'   {r:<16} len={len(w)} LA×{lex[w]} {sorted(lex_docs[w])[:3]} | '
          f'слоты {sl}, табличек {n} [{ser[:40]}]')

# нуль
lengths = [len(w) for w in words]
pos_pools = {0: [], 1: [], 2: []}
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)
def gen_B():
    for p in pos_pools.values(): random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = []
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.append(tuple(w))
    return out
c_all = []; c_long = []
for _ in range(R):
    wl = gen_B()
    a = l = 0
    for w in wl:
        r = read_lb(w)
        if r and r in NS:
            a += 1
            if len(w) >= 3: l += 1
    c_all.append(a); c_long.append(l)
for label, obs, cs in [('все', len(hits), c_all), ('длинные >=3', len(long_hits), c_long)]:
    m = sum(cs) / R
    sd = (sum((x - m) ** 2 for x in cs) / R) ** 0.5
    p = sum(1 for x in cs if x >= obs) / R
    print(f'{label}: наблюдаемо {obs}, нуль {m:.2f}±{sd:.2f}, p={p:.4f}')

# топ-30 поведенческих кандидатов из §AC — есть ли слот-совпадения
TOP30 = ['JA-MI-DA-RE', 'KE-KI-RU', 'KI-KI-NA', 'KU-RA-MU', 'RI-MI-SI',
         'TU-JU-MA', 'A-RI-SU', 'DA-TA-RE', 'KA-RO-NA', 'U-DE-ZA', 'U-DI-MI',
         'NA-DA-RE', 'TE-JA-RE', 'I-DU-NE-SI', 'RI-RU-MA', 'MI-RU-TA-RA-RE',
         'KU-PA3-PA3', 'KU-ZU-NI', 'PA-DA-SU-TI', 'SA-MA-RO', 'MA-I-MI',
         'DE-DI', 'TU-MA', '*86-KA', 'QE-PU', 'MA-ZU', 'PI-SA', 'TE-KE',
         'JA-*345', 'MA-RU']
print('\nтоп-30 поведенческих кандидатов против NAME_SLOT:')
n30 = 0
for nm in TOP30:
    r = '-'.join(s.lower() for s in nm.split('-'))
    if '*' in r: continue
    if r in NS:
        n30 += 1
        print(f'   {nm} == {r} [{name_slot[r][0]}]')
print(f'попаданий: {n30}/30')
