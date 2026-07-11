# -*- coding: utf-8 -*-
"""Этап 36 (§DU-а): restoration-линейка — порт п.4 этрусков.

Честная рамка «что формульная грамматика может дать для лакун»:
маскируем каждое слово в документах >=3 слов; предсказываем по рамке
(лев, прав) большинством из ДРУГИХ физических табличек (leave-one-tablet-
out); fallback — самое частое слово корпуса. Точность top-1 по классам
(операторы §BC / именной слой / прочее) против частотного базлайна.
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

OPS = {'KU-RO', 'PO-TO-KU-RO', 'KI-RO', 'TE', 'A-DU', 'I-DA', 'SI-RU-TE',
       'SA-RA2', 'KI', 'A-TA-I-*301-WA-JA'}
NAMES = {'PA-I-TO', 'SE-TO-I-JA', 'SU-KI-RI-TA', 'DA-I-PI-TA', 'I-TA-JA',
         'KI-DA-RO', 'PA-RA-NE', 'TA-NA-TI', 'I-JA-TE'}

def tablet(cid):
    return cid[:-1] if cid and cid[-1] in 'abcd' else cid

corpus = pickle.load(open('corpus.pkl', 'rb'))
freq = Counter()
docs = []
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) >= 3:
        docs.append((tablet(d['id']), ws))
    for w in ws:
        freq[w] += 1
BASE = freq.most_common(1)[0][0]

def wclass(w):
    if w in OPS:
        return 'оператор'
    if w in NAMES or (freq[w] == 1 and len(w.split('-')) >= 3):
        return 'имя-слой'
    return 'прочее'

frame_all = defaultdict(Counter)       # (лев,прав) -> Counter слов, по табличкам
frame_by_tab = defaultdict(lambda: defaultdict(Counter))
for tab, ws in docs:
    for i in range(1, len(ws) - 1):
        fr = (ws[i - 1], ws[i + 1])
        frame_all[fr][ws[i]] += 1
        frame_by_tab[tab][fr][ws[i]] += 1

res = defaultdict(lambda: [0, 0])      # класс -> [верно, всего]
base_res = defaultdict(lambda: [0, 0])
for tab, ws in docs:
    for i in range(1, len(ws) - 1):
        fr = (ws[i - 1], ws[i + 1])
        truth = ws[i]
        cnt = frame_all[fr] - frame_by_tab[tab][fr]     # LOTO
        pred = cnt.most_common(1)[0][0] if cnt else BASE
        cl = wclass(truth)
        res[cl][1] += 1
        base_res[cl][1] += 1
        if pred == truth:
            res[cl][0] += 1
        if BASE == truth:
            base_res[cl][0] += 1

print(f'{"класс":<12}{"позиций":>9}{"top-1 формуляр":>16}{"базлайн":>10}')
for cl in ('оператор', 'имя-слой', 'прочее'):
    c, t = res[cl]
    cb, tb = base_res[cl]
    if t:
        print(f'{cl:<12}{t:>9}{c / t:>16.1%}{cb / tb:>10.1%}')
tot_c = sum(v[0] for v in res.values())
tot_t = sum(v[1] for v in res.values())
print(f'{"всего":<12}{tot_t:>9}{tot_c / tot_t:>16.1%}')
print('''
Чтение: линейка честности для лакун (порт из DecipherEtruscan) —
формульная грамматика восстанавливает операторные слоты, но НЕ имена;
любые будущие предложения по восстановлению лакун обязаны сверяться с
этой линейкой. Внутрисловных позиций — leave-one-tablet-out.''')
