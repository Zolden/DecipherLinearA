# -*- coding: utf-8 -*-
"""Этап 6, п.6 (§Q): знак *118 — конечный классификатор/единица?

Наблюдение §J: *118 резко финален в словах (8/10 типов), контекстные соседи
RA2/RO/RE; есть и одиночное употребление с числами. Гипотеза: *118 — счётный
классификатор или единица измерения, стоящая в конце составных обозначений.

Проверки:
1. Все слова с *118: позиция знака, следует ли число, целое/дробное, соседние
   логограммы, сайт/тип документа.
2. Доля «за словом идёт число» у *118-финальных слов против остального лексикона
   (точный Фишер) и против слов той же длины.
3. Основы перед *118: засвидетельствованы ли независимо (парадигма)?
4. Одиночный *118 с числами — значения.
"""
import sys, pickle
from collections import Counter, defaultdict
from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

lex = Counter(); occ = defaultdict(list)
for d in corpus:
    toks = d['toks']
    for i, (k, v) in enumerate(toks):
        if k != 'WORD': continue
        if not (v['syllabic'] and len(v['signs']) >= 2 and v['complete']
                and not (v['gap'] or v['trunc_l'] or v['trunc_r'])):
            continue
        w = tuple(v['signs'])
        lex[w] += 1
        nval = None
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM':
                nval = toks[j][1]['val']
                for j2 in range(j + 1, len(toks)):
                    if toks[j2][0] == 'NUM': nval += toks[j2][1]['val']
                    else: break
                break
            if toks[j][0] == 'DIV': continue
            break
        logo = any(toks[j][0] == 'WORD' and not toks[j][1]['syllabic']
                   for j in range(max(0, i - 2), min(len(toks), i + 3)))
        occ[w].append({'doc': d['id'], 'site': d['site'], 'typ': d['typ'],
                       'num': nval, 'logo': logo})
WORDS = set(lex)

w118 = sorted(w for w in WORDS if '*118' in w)
print(f'=== слова с *118: {len(w118)} типов ===')
for w in w118:
    pos = w.index('*118')
    role = 'ФИНАЛЬ' if pos == len(w) - 1 else ('нач' if pos == 0 else 'сред')
    for o in occ[w]:
        nv = o['num']
        frac = nv is not None and nv != int(nv)
        print(f'   {"-".join(w):<20} {role:<7} {o["doc"]:<12} {o["site"]:<4} '
              f'{"число=" + str(nv) if nv is not None else "без числа":<14} '
              f'{"ДРОБЬ" if frac else "":<6} {"логограмма рядом" if o["logo"] else ""}')

# --- 2. частота «за словом число» у *118-финальных
fin118 = [w for w in w118 if w[-1] == '*118']
n1 = sum(1 for w in fin118 for o in occ[w] if o['num'] is not None)
t1 = sum(len(occ[w]) for w in fin118)
others = [w for w in WORDS if w[-1] != '*118']
n0 = sum(1 for w in others for o in occ[w] if o['num'] is not None)
t0 = sum(len(occ[w]) for w in others)
_, p = fisher_exact([[n1, t1 - n1], [n0, t0 - n0]])
print(f'\nчисло после слова: *118-финальные {n1}/{t1} ({n1 / t1:.0%}) против прочих '
      f'{n0}/{t0} ({n0 / t0:.0%}), Фишер p={p:.4f}')
# дробность чисел
f1 = sum(1 for w in fin118 for o in occ[w]
         if o['num'] is not None and o['num'] != int(o['num']))
f0 = sum(1 for w in others for o in occ[w]
         if o['num'] is not None and o['num'] != int(o['num']))
_, pf = fisher_exact([[f1, n1 - f1], [f0, n0 - f0]])
print(f'из них дробные: *118 {f1}/{n1}; прочие {f0}/{n0}; Фишер p={pf:.4f}')

# --- 3. основы перед *118
print('\nосновы перед финальным *118 и их независимые аттестации:')
for w in fin118:
    T = w[:-1]
    forms = [x for x in WORDS if x != w and x[:len(T)] == T]
    print(f'   {"-".join(T):<16} -> {["-".join(x) for x in forms] or "нет"}')

# --- 4. одиночный *118
print('\nодиночный *118 (все вхождения):')
for d in corpus:
    toks = d['toks']
    for i, (k, v) in enumerate(toks):
        if k == 'WORD' and v['signs'] == ['*118']:
            nval = None
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM': nval = toks[j][1]['val']; break
                if toks[j][0] != 'DIV': break
            prev = None
            for j in range(i - 1, -1, -1):
                if toks[j][0] == 'WORD': prev = toks[j][1]['norm']; break
            print(f'   {d["id"]:<12} {d["site"]:<4} после «{prev}», '
                  f'{"число=" + str(nval) if nval is not None else "без числа"}')
