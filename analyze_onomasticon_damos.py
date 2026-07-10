# -*- coding: utf-8 -*-
"""Этап 29 (§DH): ПОДТВЕРЖДАЮЩИЙ ономастикон на отложенной выборке DĀMOS.

Предрегистрация: hypotheses.tsv, коммит 677a5da (ДО скачивания корпуса).
Первичная точка: число точных LA-омографов длины >=3, попадающих в
слот-имена DĀMOS (замороженные правила N1–N7); нуль Null-B (R=10000,
seed=42), p=(b+1)/(R+1); значимость = p<0.05. Вторичная: длинновая
стратификация по лексикону DĀMOS. ОДИН прогон; результат публикуется
каким вышел.
"""
import sys, pickle, random
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

NS = set()
for line in open('damos_name_slots.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        NS.add(tuple(line.split('\t')[0].split('-')))
LB = set(NS)
for line in open('damos_lexicon.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        LB.add(tuple(line.split('\t')[0].split('-')))
print(f'DĀMOS: лексикон {len(LB)}; слот-имена {len(NS)}')

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

hits_slot = [w for w in words if len(w) >= 3 and read_lb(w) in NS]
hits_lex3 = [w for w in words if len(w) == 3 and read_lb(w) in LB]
hits_lex4 = [w for w in words if len(w) >= 4 and read_lb(w) in LB]
print('ПЕРВИЧНАЯ ТОЧКА — слот-подтверждённые >=3:',
      [('-'.join(w)) for w in hits_slot])
print('вторичная — лексикон len3:', [('-'.join(w)) for w in hits_lex3])
print('вторичная — лексикон len>=4:', [('-'.join(w)) for w in hits_lex4])

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

cs = []; c3 = []; c4 = []
for _ in range(R):
    wl = gen_B()
    ns_ = n3 = n4 = 0
    for w in wl:
        r = read_lb(w)
        if r is None:
            continue
        if len(w) >= 3 and r in NS:
            ns_ += 1
        if r in LB:
            if len(w) == 3:
                n3 += 1
            elif len(w) >= 4:
                n4 += 1
    cs.append(ns_); c3.append(n3); c4.append(n4)

for label, obs, cc in [
        ('ПЕРВИЧНАЯ: слот-имена >=3', len(hits_slot), cs),
        ('вторичная: лексикон len3', len(hits_lex3), c3),
        ('вторичная: лексикон len>=4', len(hits_lex4), c4)]:
    mu = sum(cc) / R
    sd = (sum((x - mu) ** 2 for x in cc) / R) ** 0.5
    p = (sum(1 for x in cc if x >= obs) + 1) / (R + 1)
    print(f'{label}: наблюдаемо {obs}, нуль {mu:.2f}±{sd:.2f}, p={p:.4f}')
print('''
Статус: подтверждающий прогон по предрегистрации (hypotheses.tsv,
коммит 677a5da). Результат публикуется каким вышел; повторных прогонов
с изменёнными правилами не будет.''')
