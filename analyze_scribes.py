# -*- coding: utf-8 -*-
"""Задача G: писцовая обусловленность вариантов.

Вопрос: зависят ли варианты -JA/∅ (финаль), A-/JA-/∅ (приставка) и
орфографические дублеты (пары слов с одной заменой знака) от писца?

Метаданные: поле scribe (592 док., 102 писца; для табличек HT — «HT Scribe N»).
Тесты:
  1) По каждой конкретной паре вариантов (W ~ W-JA; A-W ~ JA-W ~ W; дублеты
     Хэмминг-1): таблица сопряжённости писец × вариант, точный тест Фишера
     (2×2 после сведения «писец с макс. долей варианта A против остальных» —
     НЕ делаем, чтобы не подгонять; вместо этого r×c-перестановочный тест χ²
     и Фишер для честных 2×2). Требование: ≥2 писцов и ≥4 токенов на пару.
  2) Глобально: доля слов на -JA у писца (лексиконные токены, HT-таблички) —
     χ² с перестановочным p (метки писцов переставляются по токенам).
R=10000, seed=42; p разведочные.
"""
import sys, pickle, random, itertools
from collections import Counter, defaultdict
from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))

# лексиконные вхождения с писцом
tok_scribe = []   # (word tuple, scribe, doc)
for d in corpus:
    if not d['scribe']: continue
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            tok_scribe.append((tuple(v['signs']), d['scribe'], d['id']))
lex = Counter(w for w, _, _ in tok_scribe)
words_all = set()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            words_all.add(tuple(v['signs']))
print(f'лексиконных токенов с писцом: {len(tok_scribe)}; типов: {len(lex)}')

by_word = defaultdict(Counter)
for w, s, _ in tok_scribe: by_word[w][s] += 1

def variant_test(pairs, title):
    """pairs: список (вариант_A, вариант_B) кортежей знаков."""
    print(f'\n=== {title}: {len(pairs)} пар ===')
    tested = 0; sig = 0
    for a, b in pairs:
        ca, cb = by_word.get(a, Counter()), by_word.get(b, Counter())
        scr = sorted(set(ca) | set(cb))
        na, nb = sum(ca.values()), sum(cb.values())
        if len(scr) < 2 or na + nb < 4: continue
        table = [[ca.get(s, 0) for s in scr], [cb.get(s, 0) for s in scr]]
        # перестановочный χ² (r×c)
        toks = [(s, 0) for s in ca.elements()] + [(s, 1) for s in cb.elements()]
        def chi2(tab):
            tot = sum(sum(r) for r in tab)
            cs = [sum(tab[r][c] for r in range(2)) for c in range(len(scr))]
            rs = [sum(tab[r]) for r in range(2)]
            x = 0.0
            for r in range(2):
                for c in range(len(scr)):
                    e = rs[r] * cs[c] / tot
                    if e > 0: x += (tab[r][c] - e) ** 2 / e
            return x
        obs = chi2(table)
        labels = [v for _, v in toks]; scrs = [s for s, _ in toks]
        ge = 0
        for _ in range(R):
            random.shuffle(labels)
            t2 = [[0] * len(scr), [0] * len(scr)]
            si = {s: i for i, s in enumerate(scr)}
            for s, l in zip(scrs, labels): t2[l][si[s]] += 1
            if chi2(t2) >= obs - 1e-12: ge += 1
        p = ge / R
        tested += 1; sig += p < 0.05
        # 2×2 Фишер, если ровно 2 писца
        fish = ''
        if len(scr) == 2:
            _, pf = fisher_exact([[table[0][0], table[0][1]],
                                  [table[1][0], table[1][1]]])
            fish = f', Фишер p={pf:.4f}'
        print(f'  {"-".join(a)} ({na}) ~ {"-".join(b)} ({nb}): писцов {len(scr)}, '
              f'χ²={obs:.2f}, p(перест.)={p:.4f}{fish}')
        for s in scr:
            print(f'      {s}: {ca.get(s, 0)} / {cb.get(s, 0)}')
    print(f'проверено пар: {tested}, значимых (p<0.05): {sig} '
          f'(ожидание под нулём ~{0.05 * tested:.1f})')

# --- 1) -JA/∅
ja_pairs = [(w, w + ('JA',)) for w in words_all if w + ('JA',) in words_all]
variant_test(ja_pairs, 'финаль ∅ ~ -JA')

# --- 2) приставки A-/JA-/∅
pref_pairs = []
for w in words_all:
    for p1, p2 in [(('A',), ('JA',))]:
        if w[:1] == p1 and (p2 + w[1:]) in words_all:
            pref_pairs.append((w, p2 + w[1:]))
    # A-W ~ W и JA-W ~ W
    for p in (('A',), ('JA',)):
        if w[:1] == p and w[1:] in words_all and len(w[1:]) >= 2:
            pref_pairs.append((w, w[1:]))
variant_test(sorted(set(pref_pairs)), 'приставки A-/JA-/∅')

# --- 3) орфографические дублеты (Хэмминг-1, длина >=3)
dup_pairs = []
wl = sorted(w for w in words_all if len(w) >= 3)
for a, b in itertools.combinations(wl, 2):
    if len(a) != len(b): continue
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    if len(diff) == 1: dup_pairs.append((a, b))
variant_test(dup_pairs, 'дублеты (замена одного знака, длина >=3)')

# --- 4) глобально: доля -JA финалей по писцам
print('\n=== глобально: -JA-финаль по писцам (таблички с писцом) ===')
sc_tok = [(s, w[-1] == 'JA') for w, s, _ in tok_scribe]
scr_cnt = Counter(s for s, _ in sc_tok)
big = {s for s, n in scr_cnt.items() if n >= 8}
sel = [(s, j) for s, j in sc_tok if s in big]
cnt = defaultdict(lambda: [0, 0])
for s, j in sel: cnt[s][j] += 1
for s in sorted(big):
    a, b = cnt[s][0], cnt[s][1]
    print(f'  {s}: -JA {b}/{a + b} ({b / (a + b):.0%})')
def chi2g(pairs_):
    c = defaultdict(lambda: [0, 0])
    for s, j in pairs_: c[s][j] += 1
    tot = len(pairs_); tj = sum(j for _, j in pairs_)
    x = 0.0
    for s, (n0, n1) in c.items():
        n = n0 + n1
        e1 = n * tj / tot; e0 = n - e1
        if e1 > 0: x += (n1 - e1) ** 2 / e1
        if e0 > 0: x += (n0 - e0) ** 2 / e0
    return x
obs = chi2g(sel)
labs = [j for _, j in sel]; scrs = [s for s, _ in sel]
ge = 0
for _ in range(R):
    random.shuffle(labs)
    if chi2g(list(zip(scrs, labs))) >= obs - 1e-12: ge += 1
print(f'χ²={obs:.2f}, p(перест.)={ge / R:.4f} (писцов {len(big)}, токенов {len(sel)}, '
      f'R={R}, seed=42)')
