# -*- coding: utf-8 -*-
"""Этап 36 (§DT-а): механика провала «o-da-a2 начальна» (гипотеза
этрусков: заголовки списков конкурируют с частицей за позицию 1).

По DĀMOS-кэшу: документы с o-da-a2 — что стоит на позиции 1? Если
первая позиция занята открытым словарём заголовков (TTR высок), а
o-da-a2 систематически вторая/внутренняя — механика та же, что у их mi
против larthi-заголовков. Вне ростера (кэш .damos_cache/).
"""
import sys, json, os, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')

docs = []
for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    ws = []
    for raw_line in (item.get('content') or '').split('\n'):
        for rt in raw_line.replace(',', ' ').split():
            if '[' in rt or ']' in rt or '?' in rt:
                continue
            if WORD_RE.match(rt):
                ws.append(rt)
    if 'o-da-a2' in ws and len(ws) >= 2:
        docs.append((item.get('heading_short', fn), ws))

print(f'документов DĀMOS с o-da-a2 (>=2 слов): {len(docs)}')
first = Counter()
oda_pos = Counter()
for hid, ws in docs:
    first[ws[0]] += 1
    for i, w in enumerate(ws):
        if w == 'o-da-a2':
            oda_pos['нач' if i == 0 else
                    ('вт' if i == 1 else
                     ('фин' if i == len(ws) - 1 else 'сред'))] += 1
print(f'TTR первых слов: {len(first)}/{len(docs)} = '
      f'{len(first) / len(docs):.2f}')
print('топ первых слов:', first.most_common(6))
print('позиции o-da-a2:', dict(oda_pos))
n_oda_first = sum(1 for hid, ws in docs if ws[0] == 'o-da-a2')
print(f'o-da-a2 сама первая: {n_oda_first}/{len(docs)}')
print('''
Чтение: если TTR первых слов высок (открытые заголовки) и o-da-a2
системно не-первая — провал предзаявки §DP объясняется конкуренцией
заголовков за позицию 1 (механика этрусков: mi против larthi).
Дескриптивно.''')
