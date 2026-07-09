# -*- coding: utf-8 -*-
"""Этап 23 (§CQ-а): карта сайт-предпочтений финалей с семейным контролем.

§CN показал геообусловленность вариантов финала в целом. Здесь — какие
именно (сайт, финаль) пары дают избыток: по каждому сайту с >=30 полными
словами — доля слов-токенов на каждую из топ-финалей против остального
корпуса; перестановка сайт-меток токенов, WY min-p по семейству
(сайты × финали). p разведочные.
"""
import sys, pickle
import numpy as np
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
R = 10000
rng = np.random.default_rng(42)

OPS = {'KU-RO', 'PO-TO-KU-RO', 'KI-RO', 'TE', 'A-DU', 'I-DA', 'SI-RU-TE',
       'SA-RA2', 'KI'}                     # §BC/§BO — геораспределение
                                           # операторов не «финальный слот»
corpus = pickle.load(open('corpus.pkl', 'rb'))
toks = []                                  # (site, final)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']) \
           and v['norm'] not in OPS:
            toks.append((d['site'], v['signs'][-1]))
print('операторы §BC исключены (их география — не свойство финалей)')
sites = [s for s, c in Counter(s for s, _ in toks).items() if c >= 30]
finals = [f for f, c in Counter(f for _, f in toks).items() if c >= 30]
print(f'токенов: {len(toks)}; сайтов (>=30): {sites}; '
      f'финалей (>=30): {finals}')

site_arr = np.array([s for s, _ in toks])
fin_arr = np.array([f for _, f in toks])
tests = []
for s in sites:
    m_site = site_arr == s
    for f in finals:
        m_fin = fin_arr == f
        obs = int((m_site & m_fin).sum())
        tests.append((s, f, obs, int(m_site.sum()), int(m_fin.sum())))

n = len(toks)
sims = np.zeros((R, len(tests)), dtype=np.int32)
for r_i in range(R):
    perm = rng.permutation(n)
    sa = site_arr[perm]
    for j, (s, f, obs, ns, nf) in enumerate(tests):
        sims[r_i, j] = int(((sa == s) & (fin_arr == f)).sum())
p_raw = ((sims >= np.array([t[2] for t in tests])).sum(axis=0) + 1) / (R + 1)
p_sim = np.zeros_like(sims, dtype=np.float64)
for j in range(len(tests)):
    order = np.sort(sims[:, j])
    idx = np.searchsorted(order, sims[:, j], side='left')
    p_sim[:, j] = (R - idx + 1) / (R + 1)
minp = p_sim.min(axis=1)
p_adj = np.array([((minp <= p).sum() + 1) / (R + 1) for p in p_raw])

print(f'\n{"сайт":<6}{"финаль":<8}{"набл":>5}{"ожид":>7}{"p":>9}{"p̃сем":>9}')
rows = sorted(zip(tests, p_raw, p_adj), key=lambda x: x[1])
for (s, f, obs, ns, nf), pr, pa in rows:
    exp = ns * nf / n
    if pr < 0.05:
        star = ' *' if pa < 0.05 else ''
        print(f'{s:<6}{f:<8}{obs:>5}{exp:>7.1f}{pr:>9.4f}{pa:>9.4f}{star}')
print('''
Чтение: показаны только пары с raw p<0.05; вывод делать по p̃сем
(семейство = все пары сайт×финаль). p разведочные.''')
