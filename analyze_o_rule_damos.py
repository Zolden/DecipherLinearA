# -*- coding: utf-8 -*-
"""Этап 31 (§DN-б): правило «→ -o» (§BZ) на курируемых слот-именах DĀMOS.

Проверка адаптационного правила на третьей базе: слова LA >=3 знаков без
точного совпадения; замена гласной финала в той же строке (слоговарь LB);
мишень — damos_name_slots.tsv (1465). Агрегат по целевой гласной,
контроль max по 5 целям (как §BZ). Null-B, R=10000, seed=42.
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

NS = set()
for line in open('damos_name_slots.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        NS.add(tuple(line.split('\t')[0].split('-')))
print(f'слот-имена DĀMOS: {len(NS)}')

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

def variants(r):
    m = re.fullmatch(r'([a-z]?)([aeiou])', r[-1])
    if not m:
        return []
    row, v = m.group(1), m.group(2)
    out = []
    for v2 in 'aeiou':
        if v2 == v:
            continue
        syl = row + v2
        if syl in LB_SYLS:
            out.append((v, v2, r[:-1] + (syl,)))
    return out

def count(word_list):
    tgt = Counter()
    matched = []
    for w in word_list:
        if len(w) < 3:
            continue
        r = read_lb(w)
        if r is None or r in NS:
            continue
        for v, v2, var in variants(r):
            if var in NS:
                tgt[v2] += 1
                matched.append((w, var))
    return tgt, matched

obs_t, obs_list = count(words)
print('вариантные попадания по целевой гласной:', dict(obs_t))
for w, var in obs_list:
    print(f'   {"-".join(w)} → {"-".join(var)}')

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

sim_t = defaultdict(list)
sim_max = []
sim_tot = []
for _ in range(R):
    tg, _m = count(gen_B())
    for v2 in 'aeiou':
        sim_t[v2].append(tg.get(v2, 0))
    sim_max.append(max(tg.values()) if tg else 0)
    sim_tot.append(sum(tg.values()))

tot_obs = sum(obs_t.values())
mu = sum(sim_tot) / R
p_tot = (sum(1 for x in sim_tot if x >= tot_obs) + 1) / (R + 1)
print(f'\nвсего попаданий: {tot_obs} (нуль {mu:.2f}, p={p_tot:.4f})')
print(f'{"→гласная":<10}{"набл":>5}{"нуль μ":>8}{"p":>9}{"p_max5":>9}')
for v2 in 'aeiou':
    o = obs_t.get(v2, 0)
    if o == 0:
        continue
    sims = sim_t[v2]
    m2 = sum(sims) / R
    p = (sum(1 for x in sims if x >= o) + 1) / (R + 1)
    pm = (sum(1 for x in sim_max if x >= o) + 1) / (R + 1)
    star = ' *' if pm < 0.05 else ''
    print(f'→ -{v2:<7}{o:>5}{m2:>8.2f}{p:>9.4f}{pm:>9.4f}{star}')
print('''
Чтение: правило §BZ было заявлено на некурируемых базах; здесь его
проверка на курируемой (третьей). p разведочные; агрегат «→o» — главная
линия, прочие цели — контрольное семейство.''')
