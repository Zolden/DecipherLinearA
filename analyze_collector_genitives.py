# -*- coding: utf-8 -*-
"""Этап 49 (§EF): морфологическая маркировка класса коллекторов —
пары X / X-jo в слоте 1 KN D-серий.

Известно (внешний факт): коллекторы пишутся и именительным (u-ta-jo),
и генитивом (u-ta-jo-jo). Слепой тест: среди ПОВТОРЯЕМЫХ (>=2 док.)
типов слота 1 доля состоящих в паре «X ~ X-jo» выше, чем среди
уникальных типов слота 1 (Fisher). Если да — сверхповторяемый класс
морфологически маркирован, и пара «повторяемость + падежная пара» может
служить детектором класса без чтения. LA-зеркало: есть ли у кураторов
HT (KA-PA, A-KA-RU, JE-DI, *21F-TU-NE) внутрикорпусные пары по решётке
(±1 финальный знак). Вне ростера (кэш DĀMOS).
"""
import sys, json, os, re, pickle
from collections import defaultdict

from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')

first_docs = defaultdict(set)
for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    head = (item.get('heading_short') or '')
    if not re.match(r'^KN D[a-z]?\b', head):
        continue
    ws = []
    for line in (item.get('content') or '').split('\n'):
        for rt in line.replace(',', ' ').split():
            if '[' in rt or ']' in rt or '?' in rt:
                continue
            if WORD_RE.match(rt):
                ws.append(rt)
    if len(ws) >= 2:
        first_docs[ws[0]].add(head)

types = set(first_docs)
def in_pair(t):
    return (t + '-jo' in types) or (t.endswith('-jo') and t[:-3] in types)

rep = [t for t in types if len(first_docs[t]) >= 2 and len(t) > 2]
uni = [t for t in types if len(first_docs[t]) == 1 and len(t) > 2]
rp = sum(1 for t in rep if in_pair(t))
up = sum(1 for t in uni if in_pair(t))
odds, p = fisher_exact([[rp, len(rep) - rp], [up, len(uni) - up]],
                       alternative='greater')
print(f'повторяемых типов слота 1: {len(rep)}, из них в паре X~X-jo: {rp} '
      f'({rp / len(rep):.0%})')
print(f'уникальных типов слота 1: {len(uni)}, из них в паре: {up} '
      f'({up / len(uni):.0%})')
print(f'Fisher (односторонний, повторяемые богаче парами): p={p:.5f}, '
      f'OR={odds:.1f}')
print('пары повторяемых:', sorted(t for t in rep if in_pair(t)))

# LA-зеркало: пары кураторов по ±1 финальному знаку
corpus = pickle.load(open('corpus.pkl', 'rb'))
la_types = {v['norm'] for d in corpus for k, v in d['toks']
            if k == 'WORD' and v['syllabic']}
CUR = ['KA-PA', 'A-KA-RU', 'JE-DI', '*21F-TU-NE']
print('\nLA-зеркало (внутрикорпусные соседи кураторов по финалу):')
for c in CUR:
    base = c.split('-')
    mates = [t for t in la_types if t != c and
             (t.split('-')[:-1] == base or base[:-1] == t.split('-')[:-1]
              and len(t.split('-')) == len(base))]
    print(f'   {c:<12} {sorted(mates)[:6] if mates else "—"}')
print('''
Чтение: если сверхповторяемый слот-1 класс LB морфологически маркирован
(X~X-jo пары), то «повторяемость + падежная пара» — сигнатура
институционального агента, переносимая на нечитаемые корпуса как чистая
комбинаторика. LA-зеркало — дескриптивная разведка той же сигнатуры.''')
