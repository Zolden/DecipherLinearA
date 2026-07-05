# -*- coding: utf-8 -*-
"""Этап 9.5 (§AK): I-DA — свободное слово + связанный первый элемент.

Тест: насколько необычен профиль I-DA — двузнаковое слово, которое (а) само
частотно как отдельное слово, (б) служит началом многих более длинных слов?
Статистика: pairs-профиль (free_tokens, n_extensions) для ВСЕХ двузнаковых
слов лексикона; ранг I-DA; нуль Null-B (R=2000): доля псевдолексиконов, где
хоть одно двузнаковое слово имеет профиль >= (free_I-DA, ext_I-DA).
География: распределение I-DA-семейства по сайтам и типам носителей против
фона лексикона (без утверждений о горе Ида — только дистрибуция).
Параллель: PU2-RE (§X) тем же тестом.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 2000

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); lex_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1
            lex_docs[w].add((d['id'], d['site'], d['typ'], d['support']))
WORDS = set(lex)

def profile2(word_set, counts):
    """для каждого 2-знакового слова: (free_tokens, n_расширений-префиксов,
    n_расширений-суффиксом (слово на конце))."""
    out = {}
    for w in word_set:
        if len(w) != 2: continue
        ext_pre = sum(1 for x in word_set if len(x) > 2 and x[:2] == w)
        ext_suf = sum(1 for x in word_set if len(x) > 2 and x[-2:] == w)
        out[w] = (counts.get(w, 1), ext_pre, ext_suf)
    return out

obs = profile2(WORDS, lex)
print('=== профили двузнаковых слов (free × расширения) ===')
ranked = sorted(obs.items(), key=lambda kv: -(kv[1][0] * (kv[1][1] + kv[1][2])))
for w, (fr, ep, es) in ranked[:12]:
    print(f'   {"-".join(w):<8} свободно ×{fr}, префикс {ep} слов, '
          f'финаль {es} слов, море={fr * (ep + es)}')
ida = obs.get(('I', 'DA'))
pure = obs.get(('PU2', 'RE'))
print(f'\nI-DA: {ida}; PU2-RE: {pure}')
ida_score = ida[0] * ida[1]

# нуль: макс. score (free × prefix-ext) двузнаковых слов в псевдолексиконах
lengths = [len(w) for w in sorted(lex)]
words_list = sorted(lex)
pos_pools = {0: [], 1: [], 2: []}
for w in words_list:
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
ge_any = 0; ge_ida = 0
for _ in range(R):
    wl = gen_B()
    ws = set(wl)
    cnt = Counter(wl)
    pr = profile2(ws, cnt)
    mx = max((fr * ep for fr, ep, es in pr.values()), default=0)
    if mx >= ida_score: ge_any += 1
    v = pr.get(('I', 'DA'))
    if v and v[0] * v[1] >= ida_score: ge_ida += 1
print(f'score I-DA (free × префиксные расширения) = {ida_score}')
print(f'нуль: P(какое-нибудь 2-знаковое слово с score >= I-DA) = {ge_any / R:.4f}; '
      f'P(именно I-DA) = {ge_ida / R:.4f} (R={R})')

# география семейства
print('\n=== география I-DA-семейства ===')
fam = [w for w in WORDS if w[:2] == ('I', 'DA')] + [('I', 'DA')] if ('I', 'DA') in WORDS else \
      [w for w in WORDS if w[:2] == ('I', 'DA')]
fam = sorted(set(fam))
sites = Counter(); sups = Counter()
for w in fam:
    for did, site, typ, sup in lex_docs[w]:
        sites[site] += 1; sups[(typ, sup)] += 1
        print(f'   {"-".join(w):<18} {did:<12} {site:<5} {typ:<4} {sup}')
print(f'сайтов: {len(sites)} {dict(sites)}')
print(f'носители: {dict(sups)}')
rel_share = sum(v for (t, s), v in sups.items() if t == 'rel') / sum(sups.values())
print(f'доля rel-контекстов: {rel_share:.0%} (фон лексикона ~17%)')
