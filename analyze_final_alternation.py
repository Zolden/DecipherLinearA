# -*- coding: utf-8 -*-
"""Этап 19 (§BZ): системный тест чередования финальной гласной
(кандидатное «правило адаптации» LA -a ↔ LB -o из §BX).

Для каждого полного слова LA длины >=3 без точного совпадения: меняем
ТОЛЬКО гласную последнего знака внутри той же согласной строки (ca→co,
re→ro, a→o…; субскриптные финалы ra2/ta2/pa3 не варьируются) и ищем
результат в union слот-имён LB (2053). Счёт по упорядоченным парам
(гласная LA → гласная LB); нуль Null-B (gen_B, R=10000, seed=42);
семейный контроль — max-статистика по парам гласных.

Дисциплина: это тест ОДНОЙ гипотезы, заявленной в §BX до теста (a→o);
остальные пары — контрольное семейство.
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
LB = set(NS)
for fn in ('lb_lexicon.tsv', 'lb2_lexicon.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            LB.add(tuple(line.split('\t')[0].split('-')))
print(f'union слот-имён: {len(NS)}; union лексикон: {len(LB)}')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); lex_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1; lex_docs[w].add(d['id'])
words = sorted(lex)
lengths = [len(w) for w in words]

# инвентарь ВАРИАНТОВ — слоговарь LB (вариант ищется в LB-наборах):
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

def final_variants(r):
    """[(v_la, v_lb, вариант)] — только замена гласной финала в той же строке."""
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

PAIRS = [(a, b) for a in 'aeiou' for b in 'aeiou' if a != b]

def count_hits(word_list, target):
    per_pair = Counter()
    matched = []
    for w in word_list:
        if len(w) < 3:
            continue
        r = read_lb(w)
        if r is None or r in target:
            continue
        for v, v2, var in final_variants(r):
            if var in target:
                per_pair[(v, v2)] += 1
                matched.append((w, var, v, v2))
    return per_pair, matched

obs_pp, obs_list = count_hits(words, NS)
print('\nнаблюдаемые финальные варианты (мишень — слот-имена):')
for (v, v2), c in obs_pp.most_common():
    print(f'   -{v} → -{v2}: {c}')
for w, var, v, v2 in obs_list:
    print(f'      {"-".join(w):<20} → {"-".join(var)} '
          f'({sorted(lex_docs[w])[:2]})')

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

sim_pp = defaultdict(list)
sim_tot = []
sim_max = []
sim_tgt = defaultdict(list)          # агрегат по целевой гласной
sim_tmax = []
for _ in range(R):
    pp, _m = count_hits(gen_B(), NS)
    for pr in PAIRS:
        sim_pp[pr].append(pp.get(pr, 0))
    sim_tot.append(sum(pp.values()))
    sim_max.append(max(pp.values()) if pp else 0)
    tg = Counter()
    for (v, v2), c in pp.items():
        tg[v2] += c
    for v2 in 'aeiou':
        sim_tgt[v2].append(tg.get(v2, 0))
    sim_tmax.append(max(tg.values()) if tg else 0)

tot_obs = sum(obs_pp.values())
m = sum(sim_tot) / R
sd = (sum((x - m) ** 2 for x in sim_tot) / R) ** 0.5
p_tot = sum(1 for x in sim_tot if x >= tot_obs) / R
print(f'\nвсего вариантных попаданий: {tot_obs} (нуль {m:.2f}±{sd:.2f}, '
      f'p={p_tot:.4f})')
print(f'{"пара":<8}{"набл.":>6}{"нуль μ":>8}{"p":>9}{"p_max":>9}')
for pr in PAIRS:
    o = obs_pp.get(pr, 0)
    if o == 0:
        continue
    sims = sim_pp[pr]
    mu = sum(sims) / R
    p = sum(1 for x in sims if x >= o) / R
    pmax = sum(1 for x in sim_max if x >= o) / R
    star = ' *' if pmax < 0.05 else ''
    print(f'-{pr[0]}→-{pr[1]:<4}{o:>6}{mu:>8.2f}{p:>9.4f}{pmax:>9.4f}{star}')
print(f'\nагрегат по ЦЕЛЕВОЙ гласной (семейство из 5):')
print(f'{"→гласная":<10}{"набл.":>6}{"нуль μ":>8}{"p":>9}{"p_max5":>9}')
obs_tgt = Counter()
for (v, v2), c in obs_pp.items():
    obs_tgt[v2] += c
for v2 in 'aeiou':
    o = obs_tgt.get(v2, 0)
    if o == 0:
        continue
    sims = sim_tgt[v2]
    mu = sum(sims) / R
    p = sum(1 for x in sims if x >= o) / R
    pmax = sum(1 for x in sim_tmax if x >= o) / R
    star = ' *' if pmax < 0.05 else ''
    print(f'→ -{v2:<7}{o:>6}{mu:>8.2f}{p:>9.4f}{pmax:>9.4f}{star}')
print('''
Чтение: гипотеза §BX заявлена как a→o; p(a→o) — её прямой тест; p_max —
контроль по 20 парам, p_max5 — по 5 целевым гласным (естественная
агрегация «к чему приводится финал»). p разведочные; правило (если
выживет) формулируется как «кандидат правила адаптации» без
фонологических утверждений о направлении заимствования.''')
