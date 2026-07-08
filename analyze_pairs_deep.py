# -*- coding: utf-8 -*-
"""Этап 21 (§CI): пять внутриминойских пар финала (§CE) — контексты.

Для каждой пары: сайты/документы, регистр (Z*-объект или табличка),
позиция в документе (первая/средняя/последняя), сосед справа — число?,
частоты; появляются ли обе формы в одном документе (внутридокументная
парадигма) или разнесены по сайтам (диалект/орфография). Дистрибутивные
вердикты, без чтений. Плюс эпохи из dating.tsv.
"""
import sys, pickle
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

PAIRS = [
    (('A', 'DA', 'RA'), ('A', 'DA', 'RO')),
    (('A', 'MI', 'DA', 'O'), ('A', 'MI', 'DA', 'U')),
    (('DA', 'TA', 'RA'), ('DA', 'TA', 'RE')),
    (('SI', 'DA', 'RE'), ('SI', 'DA', 'RO')),
    (('TA', 'NA', 'TE'), ('TA', 'NA', 'TI')),
]

dating = {}
try:
    for line in open('dating.tsv', encoding='utf-8'):
        if not line.startswith('doc\t'):
            p = line.rstrip('\n').split('\t')
            dating[p[0]] = p[3]
except FileNotFoundError:
    pass

corpus = pickle.load(open('corpus.pkl', 'rb'))
occ = defaultdict(list)
for d in corpus:
    toks = d['toks']
    ws = [(i, tuple(v['signs'])) for i, (k, v) in enumerate(toks)
          if k == 'WORD' and v['syllabic']]
    seq = [w for _, w in ws]
    rel = any(z in d['id'] for z in
              ('Za', 'Zb', 'Zc', 'Zd', 'Ze', 'Zf', 'Zg'))
    for j, (i, w) in enumerate(ws):
        nxt_num = i + 1 < len(toks) and toks[i + 1][0] == 'NUM'
        pos = ('перв' if j == 0 else
               ('посл' if j == len(ws) - 1 else 'сред'))
        occ[w].append((d['id'], d['site'], rel, pos, nxt_num,
                       dating.get(d['id'], '')))

for w1, w2 in PAIRS:
    print(f'=== {"-".join(w1)} ~ {"-".join(w2)} ===')
    docs1 = {o[0] for o in occ[w1]}
    docs2 = {o[0] for o in occ[w2]}
    for w in (w1, w2):
        for did, site, rel, pos, num, ep in occ[w]:
            print(f'   {"-".join(w):<14} {did:<10} {site:<5} '
                  f'{"религ" if rel else "адм":<6} {pos:<5} '
                  f'{"+число" if num else "      "} {ep}')
    same_doc = docs1 & docs2
    sites1 = {o[1] for o in occ[w1]}
    sites2 = {o[1] for o in occ[w2]}
    print(f'   → один документ: {sorted(same_doc) or "нет"}; '
          f'сайты: {sorted(sites1)} vs {sorted(sites2)}'
          f'{" (разнесены)" if not (sites1 & sites2) else " (пересекаются)"}')
print('''
Чтение: «внутридокументная парадигма» (обе формы в одном документе) —
сильнейший тип свидетельства морфологического слота; разнесённость по
сайтам без пересечения совместима и с орфографией/диалектом. Вердикты
дистрибутивные; чтения не приписываются.''')
