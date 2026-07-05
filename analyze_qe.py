# -*- coding: utf-8 -*-
"""Этап 10.5 (§AP): суффикс -QE на всём материале — тест гипотезы энклитики.

Если -QE аналогичен LB -qe (= 'и', энклитический союз, ср. лат. -que), то
X-QE-формы должны: (а) НЕ открывать документ; (б) следовать за другой
записью того же типа (продолжение перечня); (в) вести себя в остальном как
базовая форма (число после — как у соседей по списку).

Тесты: доля документо-начальных у -QE-форм против всех слов; доля «есть
предыдущая запись со словом+числом» против фона; пары база~база+QE.
Точные тесты Фишера; перечень всех -QE-форм с контекстами.
"""
import sys, pickle
from collections import Counter, defaultdict
from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

occ_qe = []; occ_all = []
lex = Counter()
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
        nval = None
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM': nval = toks[j][1]['val']; break
            if toks[j][0] == 'DIV': continue
            break
        # предыдущая запись = раньше в документе есть слово, за которым число
        prev_rec = False; prev_w = None
        for j in range(i - 1, -1, -1):
            if toks[j][0] == 'WORD':
                prev_w = toks[j][1]['norm']
                for j2 in range(j + 1, i):
                    if toks[j2][0] == 'NUM': prev_rec = True; break
                break
        rec = {'w': w, 'doc': d['id'], 'site': d['site'], 'typ': d['typ'],
               'init': i == widx[0], 'num': nval, 'prev_rec': prev_rec,
               'prev_w': prev_w}
        occ_all.append(rec)
        if w[-1] == 'QE': occ_qe.append(rec)

print(f'=== -QE-формы: {len(set(r["w"] for r in occ_qe))} типов, '
      f'{len(occ_qe)} вхождений ===')
for r in occ_qe:
    base = r['w'][:-1]
    base_in = 'база есть' if base in lex else ''
    print(f'   {"-".join(r["w"]):<18} {r["doc"]:<12} {r["site"]:<4} '
          f'{"ЗАГОЛОВОК" if r["init"] else "запись":<10} '
          f'{"число=" + str(r["num"]) if r["num"] is not None else "без числа":<14} '
          f'{"пред.запись✓" if r["prev_rec"] else "нет пред.записи":<16} '
          f'после «{r["prev_w"]}» {base_in}')

qe_i = sum(1 for r in occ_qe if r['init'])
all_i = sum(1 for r in occ_all if r['init'])
qe_p = sum(1 for r in occ_qe if r['prev_rec'])
all_p = sum(1 for r in occ_all if r['prev_rec'])
n_qe, n_all = len(occ_qe), len(occ_all)
_, p1 = fisher_exact([[qe_i, n_qe - qe_i], [all_i, n_all - all_i]])
_, p2 = fisher_exact([[qe_p, n_qe - qe_p], [all_p, n_all - all_p]])
print(f'\nдокументо-начальность: -QE {qe_i}/{n_qe} ({qe_i / n_qe:.0%}) против фона '
      f'{all_i}/{n_all} ({all_i / n_all:.0%}), Фишер p={p1:.4f}')
print(f'«есть предыдущая запись с числом»: -QE {qe_p}/{n_qe} ({qe_p / n_qe:.0%}) '
      f'против фона {all_p}/{n_all} ({all_p / n_all:.0%}), Фишер p={p2:.4f}')
qe_n = sum(1 for r in occ_qe if r['num'] is not None)
all_n = sum(1 for r in occ_all if r['num'] is not None)
_, p3 = fisher_exact([[qe_n, n_qe - qe_n], [all_n, n_all - all_n]])
print(f'число после: -QE {qe_n}/{n_qe} ({qe_n / n_qe:.0%}) против фона '
      f'{all_n}/{n_all} ({all_n / n_all:.0%}), Фишер p={p3:.4f}')
bases = [r['w'][:-1] for r in occ_qe]
print(f'\nбазы, самостоятельно засвидетельствованные: '
      f'{sum(1 for b in set(bases) if b in lex)}/{len(set(bases))}')
