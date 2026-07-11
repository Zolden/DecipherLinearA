# -*- coding: utf-8 -*-
"""Этап 39 (§DY): арифметика to-so/to-sa в DĀMOS — параллель §A
(KU-RO считает: 40/40 в полностью сохранных HT-документах).

Универсум: документы DĀMOS без следов лакун (нет [, ], ?), содержащие
to-so или to-sa со следующим целым числом; все числовые токены —
чистые целые. Проверка: число после ПОСЛЕДНЕГО to-so == сумма целых до
него. Контроль случайного совпадения: доля документов, где сумма
случайного подмножества прочих чисел даёт то же значение (эмпирика не
нужна — сообщаем распределение расхождений). Вне ростера (кэш DĀMOS).
"""
import sys, json, os, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')
INT_RE = re.compile(r'^\d+$')

n_docs = n_exact = 0
diffs = []
examples = []
for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    content = item.get('content') or ''
    if any(c in content for c in '[]?'):
        continue
    toks = []
    for raw_line in content.split('\n'):
        for rt in raw_line.replace(',', ' ').split():
            if WORD_RE.match(rt):
                toks.append(('W', rt))
            elif INT_RE.match(rt):
                toks.append(('N', int(rt)))
    idx = [i for i, (k, v) in enumerate(toks)
           if k == 'W' and v in ('to-so', 'to-sa')]
    if not idx:
        continue
    i = idx[-1]
    if i + 1 >= len(toks) or toks[i + 1][0] != 'N':
        continue
    total = toks[i + 1][1]
    s = sum(v for k, v in toks[:i] if k == 'N')
    if s == 0:
        continue
    n_docs += 1
    ok = (s == total)
    n_exact += ok
    diffs.append(total - s)
    if len(examples) < 12:
        examples.append((item.get('heading_short', fn), s, total, ok))

print(f'чистых документов с to-so/to-sa + число: {n_docs}')
print(f'точное совпадение (сумма до == итог): {n_exact} '
      f'({n_exact / n_docs:.0%})')
c = Counter(('=0' if d == 0 else ('+' if d > 0 else '-')) for d in diffs)
print(f'знак расхождения (итог − сумма): {dict(c)}')
print('примеры:')
for h, s, t, ok in examples:
    print(f'   {h:<22} сумма={s:<6} итог={t:<6} {"ТОЧНО" if ok else ""}')
print('''
Чтение: если to-so ведёт себя как KU-RO (§A: 40/40), микенский формуляр
наследует и арифметическую роль итога — независимая валидация нашего
чтения структуры записи без обращения к значениям слов. Несовпадения
ожидаемы там, где документ содержит подытоги/веса (единицы T, M —
не целые уровни), фильтр этого не различает; сообщаем как есть.''')
