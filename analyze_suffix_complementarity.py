# -*- coding: utf-8 -*-
"""Этап 17 (§BU): комплементарность суффиксов — порт секции 4a
tools/etr_morphemes.py из DecipherEtruscan (CROSS_PROJECT п.5).

Идея: прямые парадигмы (одна основа с двумя суффиксами) в гапакс-тяжёлом
корпусе почти не видны, но НИЖНИЙ хвост того же гипергеометрического теста
выявляет значимо КОМПЛЕМЕНТАРНЫЕ пары суффиксов (основа берёт только один
из двух) = классы основ. На этрусском это дало 10 значимых пар (-s/-al:
16 общих основ при ожидании 177).

Для LA: кандидатные финальные знаки §L; A = основы (>=2 знаков),
засвидетельствованные с суффиксом s (полные слоговые слова >=3 знаков);
универсум U = объединение основ; нуль |A∩B| ~ Hypergeom(|U|,|A|,|B|);
двусторонне, Бонферрони ×2m. Оговорка: лексикон LA (618 типов) на два
порядка меньше этрусского — тест в первую очередь о МОЩНОСТИ метода здесь.
"""
import sys, pickle
from collections import Counter
from scipy.stats import hypergeom

sys.stdout.reconfigure(encoding='utf-8')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
print(f'лексикон: {len(lex)} типов')

CAND = ['JA', 'TE', 'RO', 'RA', 'TI', 'TA', 'RE', 'MA', 'ME', 'NE',
        'NA', 'RU', 'TU', 'U']            # финальные маркеры §L + -U (§W)
stems_of = {}
for s in CAND:
    stems_of[s] = {w[:-1] for w in lex if w[-1] == s and len(w) >= 3}
U = set()
for s in CAND:
    U |= stems_of[s]
NU = len(U)

pair_res = []
for i in range(len(CAND)):
    for j in range(i + 1, len(CAND)):
        A, B = stems_of[CAND[i]], stems_of[CAND[j]]
        if not A or not B:
            continue
        ov = len(A & B)
        E = len(A) * len(B) / NU
        p_hi = float(hypergeom.sf(ov - 1, NU, len(A), len(B)))
        p_lo = float(hypergeom.cdf(ov, NU, len(A), len(B)))
        pair_res.append((CAND[i], CAND[j], len(A), len(B), ov, E, p_hi, p_lo))
m = len(pair_res)
print(f'универсум основ |U|={NU}; пар протестировано: {m} '
      f'(двусторонне; Бонферрони ×{2 * m})')

print('\nОБОГАЩЕНИЕ (общая основа с двумя суффиксами = парадигма):')
print(f'{"пара":<12} {"|A|":>4} {"|B|":>4} {"∩":>3} {"E[∩]":>6} '
      f'{"p":>9} {"p_adj":>9}')
for s1, s2, a, b, ov, E, p_hi, p_lo in sorted(pair_res, key=lambda t: t[6])[:8]:
    padj = min(1.0, p_hi * 2 * m)
    mark = ' *' if padj < 0.05 else ''
    print(f'-{s1}/-{s2:<8} {a:>4} {b:>4} {ov:>3} {E:>6.1f} '
          f'{p_hi:>9.2e} {padj:>9.2e}{mark}')

print('\nДЕПРЕССИЯ (комплементарность — основа берёт только один из двух):')
print(f'{"пара":<12} {"|A|":>4} {"|B|":>4} {"∩":>3} {"E[∩]":>6} '
      f'{"p":>9} {"p_adj":>9}')
depl = []
for s1, s2, a, b, ov, E, p_hi, p_lo in sorted(pair_res, key=lambda t: t[7])[:10]:
    padj = min(1.0, p_lo * 2 * m)
    mark = ' *' if padj < 0.05 else ''
    print(f'-{s1}/-{s2:<8} {a:>4} {b:>4} {ov:>3} {E:>6.1f} '
          f'{p_lo:>9.2e} {padj:>9.2e}{mark}')
    if padj < 0.05:
        depl.append((s1, s2))
print(f'\nзначимо комплементарных пар: {len(depl)} → {depl or "нет"}')

# минимальная мощность: какое перекрытие вообще детектируемо при наших |A|,|B|
big = sorted(pair_res, key=lambda t: -t[2] * t[3])[:3]
for s1, s2, a, b, ov, E, *_ in big:
    p0 = float(hypergeom.cdf(0, NU, a, b))
    print(f'мощность: пара -{s1}/-{s2} (|A|={a},|B|={b}): даже ∩=0 даёт '
          f'p_lo={p0:.3f} (×{2*m} = {min(1, p0*2*m):.2f})')
print('''
Чтение: p разведочные; при 618 типах лексикона депрессионный тест LA,
в отличие от этрусского (20k типов), упирается в мощность — фиксируем
как методический результат и как задел на рост корпуса.''')
