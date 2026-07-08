# -*- coding: utf-8 -*-
"""Этап 20 (§CD): правило «→ -o» по стратам мишени + LOO по якорям.

Если §BZ — адаптация ОНОМАСТИКОНА, обогащение «LA-финал → LB -o» должно
быть сильнее в слот-именах (NS), чем в остальном лексиконе LB (REST).
Мишени: NS (union слот-имён) и REST = union-лексикон \\ NS. Статистика на
слово: есть →o-вариант в страте (слово может попасть в обе). Нуль Null-B
(gen_B, R=10000); контраст обогащений: D = Z_NS − Z_REST, p по
перестановочному распределению D. LOO: пересчёт без слов-якорей §BN.
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

NS = set()
for fn in ('lb_name_slots.tsv', 'lb2_name_slots.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            NS.add(tuple(line.split('\t')[0].split('-')))
LB = set()
for fn in ('lb_lexicon.tsv', 'lb2_lexicon.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            LB.add(tuple(line.split('\t')[0].split('-')))
LB |= NS
REST = LB - NS
print(f'мишени: NS {len(NS)}; REST {len(REST)}')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words = sorted(lex)
lengths = [len(w) for w in words]

LB_SYLS = {'a','e','i','o','u',
           'da','de','di','do','du','ja','je','jo','ka','ke','ki','ko','ku',
           'ma','me','mi','mo','mu','na','ne','ni','no','nu',
           'pa','pe','pi','po','pu','qa','qe','qi','qo',
           'ra','re','ri','ro','ru','sa','se','si','so','su',
           'ta','te','ti','to','tu','wa','we','wi','wo',
           'za','ze','zo'}

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s:
            return None
        out.append(s.lower())
    return tuple(out)

def o_variant(r):
    m = re.fullmatch(r'([a-z]?)([aeiou])', r[-1])
    if not m or m.group(2) == 'o':
        return None
    syl = m.group(1) + 'o'
    if syl not in LB_SYLS:
        return None
    return r[:-1] + (syl,)

ANCHORS = {('se','to','i','ja'), ('su','ki','ri','ta'), ('pa','i','to'),
           ('da','i','pi','ta'), ('i','ta','ja'), ('ki','da','ro'),
           ('pa','ra','ne'), ('ta','na','ti'), ('i','ja','te')}

def count(word_list, exclude_anchors=False):
    h_ns = h_rest = 0
    hits_ns = []
    for w in word_list:
        if len(w) < 3:
            continue
        r = read_lb(w)
        if r is None or r in LB:
            continue
        if exclude_anchors and r in ANCHORS:
            continue
        var = o_variant(r)
        if var is None:
            continue
        if var in NS:
            h_ns += 1
            hits_ns.append((r, var))
        if var in REST:
            h_rest += 1
    return h_ns, h_rest, hits_ns

obs_ns, obs_rest, obs_list = count(words)
print(f'\nнаблюдаемо: →o в слот-имена {obs_ns}; →o в остальной лексикон '
      f'{obs_rest}')
for r, var in obs_list:
    print(f'   {"-".join(r)} → {"-".join(var)}')

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

s_ns = []; s_rest = []
for _ in range(R):
    a, b, _l = count(gen_B())
    s_ns.append(a); s_rest.append(b)

import statistics
res = {}
for label, obs, sims in [('слот-имена (NS)', obs_ns, s_ns),
                         ('остальной лексикон', obs_rest, s_rest)]:
    mu = sum(sims) / R
    sd = statistics.pstdev(sims) or 1e-12
    p = sum(1 for x in sims if x >= obs) / R
    res[label] = (obs, mu, sd)
    print(f'{label:<22} набл {obs:>3}, нуль {mu:.2f}±{sd:.2f}, '
          f'обогащение ×{obs / mu if mu else 0:.1f}, p={p:.4f}')

(o1, m1, sd1) = res['слот-имена (NS)']
(o2, m2, sd2) = res['остальной лексикон']
D_obs = (o1 - m1) / sd1 - (o2 - m2) / sd2
D_sim = [ (a - m1) / sd1 - (b - m2) / sd2 for a, b in zip(s_ns, s_rest)]
pD = sum(1 for x in D_sim if x >= D_obs) / R
print(f'контраст обогащений D = Z_NS − Z_REST = {D_obs:.2f}, p={pD:.4f}')

lo_ns, lo_rest, lo_list = count(words, exclude_anchors=True)
p_lo = sum(1 for x in s_ns if x >= lo_ns) / R
print(f'\nLOO без якорей §BN: →o в NS {lo_ns} (p={p_lo:.4f} против того же '
      f'нуля) — правило {"держится" if p_lo < 0.05 else "ослабевает"} '
      f'без якорных слов')
print('''
Чтение: p разведочные; положительный контраст D = обогащение специфично
для именной страты (адаптация ономастикона), D≈0 = свойство лексикона LB
в целом (и тогда интерпретация через адаптацию имён ослаблена).''')
