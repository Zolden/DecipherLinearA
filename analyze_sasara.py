# -*- coding: utf-8 -*-
"""Этап 11.5 (§AW): парадигма SA-SA-RA — формальная морфология
теонима-кандидата.

Все слова корпуса, содержащие SA-SA (включая повреждённые документы, с
пометой): таблица приставка(∅/A-/JA-/композит) × хвост(∅/-ME/-MA-NA/-*802-ME/
-*325) × сайт × носитель. Сопоставление с калиброванным инвентарём маркеров
(A-, JA-, -ME из §L/§M): какие комбинации засвидетельствованы, какие лакуны.
"""
import sys, pickle
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

print('=== все вхождения слов с SA-SA ===')
forms = defaultdict(list)
for d in corpus:
    for k, v in d['toks']:
        if k != 'WORD' or not v['syllabic']: continue
        sg = v['signs']
        ok = any(sg[i] == 'SA' and i + 1 < len(sg) and sg[i + 1] == 'SA'
                 for i in range(len(sg) - 1))
        if not ok: continue
        damaged = (v['gap'] or v['trunc_l'] or v['trunc_r'] or not v['complete'])
        forms[v['norm']].append((d['id'], d['site'], d['support'],
                                 'повр.' if damaged else 'цел.'))
for norm, occ in sorted(forms.items()):
    for did, site, sup, st in occ:
        print(f'   {norm:<28} {did:<10} {site:<4} {sup:<16} {st}')

# разбор структуры
print('\n=== структурный разбор форм (целые) ===')
print(f'{"форма":<28}{"приставка":<12}{"ядро":<14}{"хвост":<12}{"сайты"}')
CORE = ('SA', 'SA', 'RA')
for norm, occ in sorted(forms.items()):
    sg = norm.split('-')
    # найти ядро SA-SA(-RA / -*802)
    idx = next((i for i in range(len(sg) - 1)
                if sg[i] == 'SA' and sg[i + 1] == 'SA'), None)
    if idx is None: continue
    core_end = idx + 2
    core = 'SA-SA'
    if core_end < len(sg) and sg[core_end] in ('RA', '*802'):
        core = 'SA-SA-' + sg[core_end]; core_end += 1
    pre = '-'.join(sg[:idx]) or '∅'
    tail = '-'.join(sg[core_end:]) or '∅'
    sites = sorted({s for _, s, _, _ in occ})
    print(f'{norm:<28}{pre:<12}{core:<14}{tail:<12}{",".join(sites)}')

print('''
Сверка с калиброванным инвентарём маркеров (§L/§M):
  приставки A-/JA- — реплицируемое ядро инвентаря: обе засвидетельствованы
  на этом стеме (A-SA-SA-RA-ME против JA-SA-SA-RA-ME/-MA-NA);
  хвосты -ME / -MA-NA — чередование хвостов на одном стеме (кандидат-пара
  маркеров; -ME сам по себе значим в §L: p=0.03, семейно нет);
  голая основа (A-)SA-SA-RA без хвоста; композит RI-QE-TI-…-*325;
  вариант ядра SA-SA-*802 (PRZa1) — знаковая замена внутри стема.''')
