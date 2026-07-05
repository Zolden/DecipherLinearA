# -*- coding: utf-8 -*-
"""Этап 7.4 (§X): семейство DI-KI-TE — эпитет или топоним; элемент (DU-)PU2-RE.

Вопросы:
1. Все формы стема DI-K- по корпусу: где, в каких документах, с какими
   приставками (A-/JA-/∅) и концовками (-TU/-TE/-TE-TE/-SE); локально ли
   оформление (IO против PK)?
2. Слова на -PU2-RE: JA-DI-KI-TE-TE-*307-PU2-RE и JA-DI-KI-TE-TE-DU-PU2-RE (PK),
   PA-TA-DA-DU-PU2-RE (HT) — композиты «X + (DU-)PU2-RE»? Есть ли другие
   вхождения элементов *307-PU2-RE / DU-PU2-RE / PU2-RE?
3. Сравнение с LB di-ka-ta (гласные) и поведением других слот-2 стемов.
Дескриптивно; каждое утверждение — структурное.
"""
import sys, pickle
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

def dump_word(v, d, note=''):
    print(f'   {v["norm"]:<32} {d["id"]:<10} {d["site"]:<5} {d["typ"]:<4} '
          f'{d["support"]:<14} {note}')

print('=== 1. все слова с DI-KI / DI-KA ===')
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and ('DI-KI' in v['norm'] or 'DI-KA' in v['norm']):
            dump_word(v, d)

print('\n=== 2. все слова с PU2 ===')
pu2_holders = []
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and 'PU2' in v['signs']:
            dump_word(v, d)
            pu2_holders.append((v['norm'], d['id'], d['site']))

print('\n=== 3. оформление стема DI-KI-T- по сайтам ===')
forms = defaultdict(list)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and 'DI-KI-T' in v['norm']:
            n = v['norm']
            pre = 'JA-' if n.startswith('JA-') else ('A-' if n.startswith('A-') else '∅')
            core = n.replace('JA-', '', 1).replace('A-', '', 1) if pre != '∅' else n
            forms[d['site']].append((pre, core, d['id']))
for site, lst in sorted(forms.items()):
    print(f'   {site}: ' + '; '.join(f'{p}{c} ({i})' for p, c, i in lst))

print('\nсправка: LB di-ka-ta/di-ka-ta-de/di-ka-ta-jo — гласные A-A против LA I-E:')
print('   DI-KI-TE ≠ di-ka-ta по 2-й и 3-й гласной; тождество НЕ утверждается,')
print('   фиксируется только совместная локализация культа (Палекастро) и слота.')

# концовки стема
print('\nконцовки после DI-KI-T-: ')
ends = defaultdict(set)
for site, lst in forms.items():
    for p, c, i in lst:
        tail = c.split('DI-KI-T')[-1]
        ends[tail].add(site)
for t, sites in sorted(ends.items()):
    print(f'   ...T{t}: {sorted(sites)}')
