# -*- coding: utf-8 -*-
"""Этап 8.3 (§AB): рамка I- как маркер; семейство I-DA.

1. Поддержка I- в КОМБИНИРОВАННОЙ модели (§W): основа T считается независимо
   засвидетельствованной, если T — слово, ИЛИ есть P'+T (P'≠I), ИЛИ T+S.
   Калибровка Null-B (R=2000), сравнение с узкой моделью §L (там I-: p=0.215).
2. Функциональный тест I-форм против альтернативных форм тех же основ
   (признаки: число после, rel-документ, заголовок, табличка).
3. Досье I-DA-семейства и DA-MA-TE / I-DA-MA-TE (все вхождения, сайты, типы).
"""
import sys, pickle, random, itertools
from collections import Counter, defaultdict
from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 2000

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); occ = defaultdict(list)
for d in corpus:
    toks = d['toks']
    widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
    for i in widx:
        v = toks[i][1]
        if not (v['syllabic'] and len(v['signs']) >= 2 and v['complete']
                and not (v['gap'] or v['trunc_l'] or v['trunc_r'])):
            continue
        w = tuple(v['signs'])
        lex[w] += 1
        nval = False
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM': nval = True; break
            if toks[j][0] == 'DIV': continue
            break
        occ[w].append({'num': nval, 'rel': d['typ'] == 'rel',
                       'init': i == widx[0], 'tab': d['is_tablet'],
                       'doc': d['id'], 'site': d['site']})
WORDS = set(lex)
words_list = sorted(lex)

# ---------------- 1. поддержка в комбинированной модели
def combined_support(word_set, prefix):
    """основы T: prefix+T in set; T независимо засвидетельствована."""
    pre = defaultdict(set); suf = defaultdict(set)
    for w in word_set:
        if len(w) - 1 >= 2:
            pre[w[0]].add(w[1:])
            suf[w[-1]].add(w[:-1])
        if len(w) - 2 >= 2:
            suf[w[-2], w[-1]].add(w[:-2])
    good = set()
    for T in pre.get(prefix, ()):
        if T in word_set: good.add(T); continue
        if any(T in tl for P2, tl in pre.items() if P2 != prefix):
            good.add(T); continue
        if any(T in st for st in suf.values()):
            good.add(T)
    return good

obs_i = combined_support(WORDS, 'I')
print(f'=== поддержка I- (комбинированная модель): {len(obs_i)} основ ===')
for T in sorted(obs_i):
    forms = ['-'.join(('I',) + T)]
    print(f'   I+{"-".join(T)}   (I-форма: {forms[0]})')

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

null_i = []; null_all_pre = defaultdict(list)
for _ in range(R):
    ns = gen_B()
    null_i.append(len(combined_support(ns, 'I')))
m = sum(null_i) / R
sd = (sum((x - m) ** 2 for x in null_i) / R) ** 0.5
p = sum(1 for x in null_i if x >= len(obs_i)) / R
print(f'нуль (Null-B, R={R}): {m:.2f}±{sd:.2f}, p={p:.4f}')

# ---------------- 2. функциональный тест
FEATS = ['num', 'rel', 'init', 'tab']
def share(w, f):
    return sum(o[f] for o in occ[w]) / len(occ[w])
pairs = []
pre = defaultdict(set); suf1 = defaultdict(set)
for w in WORDS:
    if len(w) - 1 >= 2:
        pre[w[0]].add(w[1:]); suf1[w[-1]].add(w[:-1])
for T in obs_i:
    formI = ('I',) + T
    alts = [T] if T in WORDS else []
    alts += [(P,) + T for P in pre if P != 'I' and (P,) + T in WORDS and T in pre[P]]
    alts += [T + (S,) for S in suf1 if T + (S,) in WORDS and T in suf1[S]]
    alts = sorted(set(a for a in alts if a != formI))
    if alts: pairs.append((formI, alts))
print(f'\n=== функциональный тест: {len(pairs)} основ с альтернативами ===')
for formI, alts in pairs:
    print(f'   {"-".join(formI)} ~ ' + ', '.join('-'.join(a) for a in alts))
for f in FEATS:
    if not pairs: break
    s1 = sum(o[f] for formI, _ in pairs for o in occ[formI])
    st = sum(len(occ[formI]) for formI, _ in pairs)
    a1 = sum(o[f] for _, alts in pairs for a in alts for o in occ[a])
    at = sum(len(occ[a]) for _, alts in pairs for a in alts)
    if (s1 + a1) and ((st - s1) + (at - a1)):
        _, pf = fisher_exact([[s1, st - s1], [a1, at - a1]])
    else:
        pf = float('nan')
    print(f'   {f}: I-формы {s1}/{st}, альтернативы {a1}/{at}, Фишер p={pf:.4f}')

# ---------------- 3. досье I-DA и DA-MA-TE
print('\n=== досье: все слова, начинающиеся с I-DA, и DA-MA-TE ===')
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and (v['norm'].startswith('I-DA') or
                            v['norm'] in ('DA-MA-TE', 'I-DA-MA-TE')):
            print(f'   {v["norm"]:<18} {d["id"]:<12} {d["site"]:<5} '
                  f'{d["site_full"]:<14} {d["typ"]:<4} {d["support"]}')
