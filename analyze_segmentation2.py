# -*- coding: utf-8 -*-
"""Этап 7.3 (§W): комбинированная сегментация — приставка и суффикс одновременно.

Модель: слово = P + T + S, где |P| ∈ {0,1}, |S| ∈ {0,1,2}, |T| >= 2.
Парадигма = основа T, засвидетельствованная в >=2 РАЗНЫХ рамках (P,S) из
>=2 разных слов. Считаем: (а) число парадигмных основ; (б) какие ПАРЫ рамок
повторяются между основами (обобщение чередований §C/§L); (в) двухзнаковые
суффиксы с калибровкой.
Нуль: Null-B (позиционная перестановка знаков; длины и позиционные частоты
сохранены), R=1000, seed=42. p разведочные.
"""
import sys, pickle, random, itertools
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 1000

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words_list = sorted(lex)

def frames(word_set):
    """стем T -> set of (P, S, слово)"""
    fr = defaultdict(set)
    for w in word_set:
        for lp in (0, 1):
            for ls in (0, 1, 2):
                if len(w) - lp - ls >= 2:
                    P, T, S = w[:lp], w[lp:len(w) - ls], w[len(w) - ls:]
                    fr[T].add((P, S, w))
    return fr

def paradigm_stats(word_set):
    fr = frames(word_set)
    stems = {}
    for T, entries in fr.items():
        fset = {(P, S) for P, S, w in entries}
        wset = {w for P, S, w in entries}
        if len(fset) >= 2 and len(wset) >= 2:
            stems[T] = fset
    return stems

obs_stems = paradigm_stats(set(lex))
print(f'парадигмных основ (>=2 рамки, >=2 слова): {len(obs_stems)}')

# нуль
lengths = [len(w) for w in words_list]
pos_pools = {0: [], 1: [], 2: []}
for w in words_list:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)
def gen_B():
    for p in pos_pools.values(): random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = set()
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.add(tuple(w))
    return out

null_n = []
for _ in range(R):
    null_n.append(len(paradigm_stats(gen_B())))
m = sum(null_n) / R
sd = (sum((x - m) ** 2 for x in null_n) / R) ** 0.5
p = sum(1 for x in null_n if x >= len(obs_stems)) / R
print(f'нуль (Null-B, R={R}): {m:.1f}±{sd:.1f}, p={p:.4f}')

# ---------------- пары рамок, повторяющиеся между основами
pair_cnt = Counter(); pair_stems = defaultdict(list)
for T, fset in obs_stems.items():
    for f1, f2 in itertools.combinations(sorted(fset), 2):
        key = (f1, f2)
        pair_cnt[key] += 1
        pair_stems[key].append(T)
def fmt_frame(f):
    P, S = f
    return (('-'.join(P) + '+') if P else '') + 'T' + (('+' + '-'.join(S)) if S else '')
print('\n=== повторяющиеся пары рамок (>=3 основ) ===')
null_pair_max = []
# нуль для пар: максимум счёта пары в случайном лексиконе
for _ in range(200):
    ns = paradigm_stats(gen_B())
    pc = Counter()
    for T, fset in ns.items():
        for f1, f2 in itertools.combinations(sorted(fset), 2):
            pc[(f1, f2)] += 1
    null_pair_max.append(max(pc.values()) if pc else 0)
nm = sum(null_pair_max) / len(null_pair_max)
print(f'(нуль: максимум счёта случайной пары рамок ~{nm:.1f}, '
      f'95-й перцентиль {sorted(null_pair_max)[int(0.95 * len(null_pair_max))]})')
for key, n in pair_cnt.most_common(20):
    if n < 3: break
    f1, f2 = key
    exs = ['-'.join(t) for t in pair_stems[key][:4]]
    print(f'   {fmt_frame(f1)} ~ {fmt_frame(f2)}: {n} основ  [{", ".join(exs)}]')

# ---------------- двухзнаковые суффиксы отдельно (с калибровкой §L-стиля)
def supports2(word_set):
    suf = defaultdict(set)
    for w in word_set:
        if len(w) - 2 >= 2: suf[w[-2:]].add(w[:-2])
    out = {}
    for S, stems in suf.items():
        good = {T for T in stems if T in word_set or
                any(T in st for S2, st in suf.items() if S2 != S)}
        if good: out[S] = good
    return out
obs2 = supports2(set(lex))
null2 = defaultdict(list); null2_max = []
for _ in range(R):
    n2 = supports2(gen_B())
    for S in obs2: null2[S].append(len(n2.get(S, ())))
    null2_max.append(max((len(v) for v in n2.values()), default=0))
print('\n=== двухзнаковые суффиксы (поддержка >=2) ===')
for S, stems in sorted(obs2.items(), key=lambda kv: -len(kv[1])):
    n = len(stems)
    if n < 2: continue
    nd = null2[S]
    mm = sum(nd) / len(nd)
    pp = sum(1 for x in nd if x >= n) / len(nd)
    pmax = sum(1 for x in null2_max if x >= n) / len(null2_max)
    ex = ', '.join('-'.join(t) for t in sorted(stems)[:3])
    print(f'   -{"-".join(S):<8} {n} основ, нуль {mm:.2f}, p={pp:.4f}, '
          f'p_max={pmax:.4f}  [{ex}]')
