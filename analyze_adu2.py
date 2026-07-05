# -*- coding: utf-8 -*-
"""Этап 11.3 (§AU): что меняет оператор A-DU — состав документов.

Сравнение табличек с A-DU(-X) в заголовке против остальных табличек тех же
сайтов (HT, KH): наличие KU-RO, число записей, доля дробных чисел, набор
товарных логограмм, присутствие VIR (люди). Точные тесты Фишера / Манна-Уитни
(перестановочный), с оговоркой о малом n.
"""
import sys, pickle, random
from collections import Counter, defaultdict
from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))

def doc_features(d):
    toks = d['toks']
    widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
    if not widx: return None
    first = toks[widx[0]][1]
    head_adu = first['syllabic'] and first['signs'][:2] == ['A', 'DU']
    n_num = n_frac = 0
    logos = set()
    has_kuro = False
    n_entries = 0
    for i, (k, v) in enumerate(toks):
        if k == 'WORD':
            if not v['syllabic']:
                logos.add(v['norm'].split('+')[0])
            if v['norm'] in ('KU-RO', 'PO-TO-KU-RO'): has_kuro = True
        elif k == 'NUM':
            n_num += 1
            if v['val'] != int(v['val']): n_frac += 1
    # запись = слово с числом сразу после
    for i in widx:
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM': n_entries += 1; break
            if toks[j][0] == 'DIV': continue
            break
    return {'head_adu': head_adu, 'site': d['site'], 'id': d['id'],
            'kuro': has_kuro, 'n_entries': n_entries,
            'frac_share': n_frac / n_num if n_num else 0.0,
            'logos': logos, 'vir': any(l.startswith('VIR') for l in logos)}

docs = [doc_features(d) for d in corpus
        if d['is_tablet'] and d['site'] in ('HT', 'KH', 'ARKH')]
docs = [x for x in docs if x and x['n_entries'] >= 1]
adu = [x for x in docs if x['head_adu']]
oth = [x for x in docs if not x['head_adu']]
print(f'табличек с записями (HT/KH/ARKH): {len(docs)}; с A-DU-заголовком: {len(adu)}')
print('A-DU-документы:', [x['id'] for x in adu])

def fisher(feat):
    a1 = sum(1 for x in adu if x[feat]); a0 = len(adu) - a1
    b1 = sum(1 for x in oth if x[feat]); b0 = len(oth) - b1
    OR, p = fisher_exact([[a1, a0], [b1, b0]])
    print(f'{feat}: A-DU {a1}/{len(adu)} ({a1 / len(adu):.0%}) против прочих '
          f'{b1}/{len(oth)} ({b1 / len(oth):.0%}), Фишер p={p:.4f}')
fisher('kuro')
fisher('vir')

def mw(feat):
    a = [x[feat] for x in adu]; b = [x[feat] for x in oth]
    obs = sum(1 for x in a for y in b if x > y) + 0.5 * sum(
        1 for x in a for y in b if x == y)
    allv = a + b; ge = 0
    for _ in range(R):
        random.shuffle(allv)
        a2, b2 = allv[:len(a)], allv[len(a):]
        u = sum(1 for x in a2 for y in b2 if x > y) + 0.5 * sum(
            1 for x in a2 for y in b2 if x == y)
        if abs(u - len(a) * len(b) / 2) >= abs(obs - len(a) * len(b) / 2) - 1e-9:
            ge += 1
    auc = obs / (len(a) * len(b))
    med_a = sorted(a)[len(a) // 2]; med_b = sorted(b)[len(b) // 2]
    print(f'{feat}: медианы A-DU {med_a} против {med_b}, AUC={auc:.2f}, '
          f'p(перест., двустор.)={ge / R:.4f}')
mw('n_entries')
mw('frac_share')

print('\nтоварные логограммы в A-DU-документах:')
cnt = Counter()
for x in adu:
    for l in x['logos']: cnt[l] += 1
print('  ', dict(cnt.most_common(10)))
cnt_o = Counter()
for x in oth:
    for l in x['logos']: cnt_o[l] += 1
tot_o = len(oth)
print('фон (доля документов с логограммой):')
for l, c in cnt.most_common(6):
    print(f'   {l}: A-DU {c}/{len(adu)}, прочие {cnt_o.get(l, 0)}/{tot_o} '
          f'({cnt_o.get(l, 0) / tot_o:.0%})')
