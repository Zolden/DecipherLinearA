# -*- coding: utf-8 -*-
"""Этап 16 (§BO): позиционная типология операторов LA — тест кросс-проектной
гипотезы из DecipherEtruscan (CROSS_PROJECT 2026-07-08, п.1).

Гипотеза (перенос с этрусского): начальную позицию документов монополизируют
дейктико-заголовочные элементы, финальную — предикатные; в LA ожидаем:
KU-RO/PO-TO-KU-RO/KI-RO (итоги) — финальный избыток «предикатного» типа,
TE/A-DU/I-DA (заголовочные) — начальный избыток «дейктического» типа.

Нуль-модель (как в etr_operators.py): позиция каждого вхождения равновероятна
внутри последовательности слов своего документа (записи с >=2 словами);
R=10000, seed=42, односторонние p; семейный контроль — Westfall–Young min-p
(портирован из DecipherEtruscan/tools/etr_operators.py).
"""
import sys, pickle
import numpy as np
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
R = 10000
SEED = 42

corpus = pickle.load(open('corpus.pkl', 'rb'))

OPERATORS = [
    ('KU-RO',       'итог',              'предикат?'),
    ('PO-TO-KU-RO', 'гранд-итог',        'предикат?'),
    ('KI-RO',       'недоимка',          'предикат?'),
    ('TE',          'транзакц. метка',   'дейксис?'),
    ('A-DU',        'загол. оператор',   'дейксис?'),
    ('I-DA',        'религ. элемент',    'дейксис?'),
    ('SI-RU-TE',    'финал формулы',     'предикат?'),
    ('SA-RA2',      'учётный термин',    '?'),
    ('KI',          'под-колонки',       '?'),
    ('A-TA-I-*301-WA-JA', 'открытие формулы', 'дейксис?'),
]

docs_words = []
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) >= 2:
        docs_words.append(ws)
print(f'документов с >=2 словами: {len(docs_words)}')

occ = defaultdict(list)   # name -> [(pos, len)]
for ws in docs_words:
    L = len(ws)
    for i, w in enumerate(ws):
        for name, *_ in OPERATORS:
            if w == name:
                occ[name].append((i, L))

tests = []
for name, gloss, pred in OPERATORS:
    o = occ.get(name, [])
    if len(o) < 5: continue
    n = len(o)
    ini = sum(1 for i, L in o if i == 0)
    fin = sum(1 for i, L in o if i == L - 1)
    tests.append((name, 'нач', ini, n, o, gloss, pred))
    tests.append((name, 'фин', fin, n, o, gloss, pred))

rng = np.random.default_rng(SEED)
sims = np.zeros((R, len(tests)), dtype=np.int32)
for j, (name, side, obs, n, o, gloss, pred) in enumerate(tests):
    Ls = np.array([L for _, L in o])
    u = rng.random((R, len(o)))
    if side == 'нач':
        sims[:, j] = (u < 1.0 / Ls).sum(axis=1)
    else:
        sims[:, j] = (u >= 1.0 - 1.0 / Ls).sum(axis=1)
obs_arr = np.array([t[2] for t in tests])
p_raw = ((sims >= obs_arr).sum(axis=0) + 1) / (R + 1)
# Westfall–Young min-p (порт из DecipherEtruscan)
p_sim = np.zeros_like(sims, dtype=np.float64)
for j in range(len(tests)):
    col = sims[:, j]
    order = np.sort(col)
    idx = np.searchsorted(order, col, side='left')
    p_sim[:, j] = (R - idx + 1) / (R + 1)
minp = p_sim.min(axis=1)
p_adj = np.array([((minp <= p).sum() + 1) / (R + 1) for p in p_raw])

print(f'\n{"оператор":<20}{"тип-гипотеза":<12}{"n":>4}{"нач%":>6}{"фин%":>6}'
      f'{"p(нач)":>9}{"p(фин)":>9}{"p̃сем(н)":>9}{"p̃сем(ф)":>9}')
by_name = {}
for j, (name, side, obs, n, o, gloss, pred) in enumerate(tests):
    by_name.setdefault(name, {})[side] = (obs, n, p_raw[j], p_adj[j], pred)
for name, gloss, pred in OPERATORS:
    if name not in by_name: continue
    d = by_name[name]
    ini, n, pi, pai, _ = d['нач']
    fin, _, pf, paf, _ = d['фин']
    print(f'{name:<20}{pred:<12}{n:>4}{ini / n:>6.0%}{fin / n:>6.0%}'
          f'{pi:>9.4f}{pf:>9.4f}{pai:>9.4f}{paf:>9.4f}')

print('''
Чтение: подтверждение гипотезы = у «предикатных» значим финальный избыток
(p̃сем(ф)<0.05 при незначимом начальном), у «дейктических» — начальный.''')
