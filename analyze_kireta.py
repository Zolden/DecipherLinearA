# -*- coding: utf-8 -*-
"""Этап 23 (§CQ-в): микро-досье семейства KI-RE-TA2 / KI-RI-TA2.

Мотив: KI-RI-TA2 дважды открывает SA-RA2-документы (§BW/§CB);
KI-RE+{TA2, ZA} и KI-RI+{SI, TA2} — строки решётки §CK; KI-RE-TA2 —
в списке слов, непрорисованных SigLA (§CJ). Дистрибутивное досье:
вхождения, сайты, позиции, соседство с GRA/числами, родня по решётке.
Без чтений (созвучие с греч. kritha «ячмень» в литературе отмечаем как
внешний факт, не как наш вывод).
"""
import sys, pickle
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

FAM = [('KI', 'RE', 'TA2'), ('KI', 'RI', 'TA2'), ('KI', 'RE', 'ZA'),
       ('KI', 'RI', 'SI'), ('KI', 'RE', 'TA', 'NA')]

corpus = pickle.load(open('corpus.pkl', 'rb'))
dating = {}
try:
    for line in open('dating.tsv', encoding='utf-8'):
        if not line.startswith('doc\t'):
            p = line.rstrip('\n').split('\t')
            dating[p[0]] = p[3]
except FileNotFoundError:
    pass

for target in FAM:
    hits = []
    for d in corpus:
        toks = d['toks']
        ws = [(i, tuple(v['signs'])) for i, (k, v) in enumerate(toks)
              if k == 'WORD' and v['syllabic']]
        seq = [w for _, w in ws]
        for j, (i, w) in enumerate(ws):
            if w != target:
                continue
            nxt = toks[i + 1] if i + 1 < len(toks) else (None, None)
            nxt_s = (nxt[1]['norm'] if nxt[0] == 'WORD'
                     else ('ЧИСЛО' if nxt[0] == 'NUM' else nxt[0]))
            gra = any(k2 == 'WORD' and not v2['syllabic']
                      and v2['norm'].startswith('GRA')
                      for k2, v2 in toks)
            pos = ('перв' if j == 0 else
                   ('посл' if j == len(seq) - 1 else f'{j + 1}-я'))
            hits.append((d['id'], d['site'], pos, nxt_s, gra,
                         dating.get(d['id'], '')))
    if not hits:
        continue
    print(f'=== {"-".join(target)} — {len(hits)} вхождений ===')
    for did, site, pos, nxt, gra, ep in hits:
        print(f'   {did:<10} {site:<5} поз={pos:<5} далее={nxt:<14} '
              f'{"GRA в док." if gra else "":<12} {ep}')
print('''
Чтение: дистрибутивное досье; чтения не приписываются. Внешний факт
литературы (созвучие KI-RI-TA2 ~ греч. krithā «ячмень») зафиксирован
в докстринге как контекст, наш вклад — только распределения.''')
