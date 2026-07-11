# -*- coding: utf-8 -*-
"""Этап 48 (§EE): ПРЕДРЕГИСТРАЦИЯ №5 (коммит e23a49a, до этого файла).

Замороженный эндпойнт: доля адресатных токенов KN Fp, чей тип живёт в
>=2 разных Fp-документах, ВЫШЕ аналогичной доли слот-1 токенов KN D
(правила №4). Нуль — перестановка токенов между группами с сохранением
размеров, R=10000, seed=42, односторонний p<0.05. Один прогон.
Вне ростера (кэш DĀMOS).
"""
import sys, json, os, re, random
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')

fp_tokens = []            # (doc, type) адресатные токены Fp
d_tokens = []             # (doc, type) слот-1 токены KN D
for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    head = (item.get('heading_short') or '')
    raw = []
    for line in (item.get('content') or '').split('\n'):
        raw.extend(t.strip("'") for t in line.replace(',', ' ').split())
    clean = [t for t in raw if WORD_RE.match(t)]
    if re.match(r'^KN Fp\b', head):
        if 'me-no' in clean:
            i = raw.index('me-no') if 'me-no' in raw else -1
            month = None
            if i > 0:
                prev = raw[i - 1].strip("'")
                if WORD_RE.match(prev):
                    month = prev
        else:
            month = (clean[0] if clean and
                     re.search(r'-jo(-jo)?$', clean[0]) else None)
        rec = [t for t in clean if t != 'me-no' and t != month]
        for t in rec:
            fp_tokens.append((head, t))
    elif re.match(r'^KN D[a-z]?\b', head):
        ws = clean
        if len(ws) >= 2:
            d_tokens.append((head, ws[0]))

def rep_share(tokens):
    docs_of = defaultdict(set)
    for doc, t in tokens:
        docs_of[t].add(doc)
    return sum(1 for doc, t in tokens if len(docs_of[t]) >= 2) / len(tokens)

fp_share = rep_share(fp_tokens)
d_share = rep_share(d_tokens)
d_obs = fp_share - d_share
print(f'Fp адресатных токенов: {len(fp_tokens)}; KN D слот-1 токенов: '
      f'{len(d_tokens)}')
print(f'повторяемость Fp-адресатов: {fp_share:.3f}; пастухов D: '
      f'{d_share:.3f}; Δ={d_obs:+.3f}')

# нуль: перестановка токенов между группами с сохранением размеров
all_tok = fp_tokens + d_tokens
nf = len(fp_tokens)
cnt = 0
for _ in range(R):
    random.shuffle(all_tok)
    s = rep_share(all_tok[:nf]) - rep_share(all_tok[nf:])
    if s >= d_obs:
        cnt += 1
p = (cnt + 1) / (R + 1)
print(f'нуль перестановки групп: p={p:.4f} (односторонний)')
ok = (d_obs > 0) and (p < 0.05)
print(f'ПРЕДРЕГИСТРАЦИЯ №5: {"ПОДТВЕРЖДЕНА" if ok else "НЕ ПОДТВЕРЖДЕНА"}'
      f' (замороженный эндпойнт требует Δ>0; наблюдаемое Δ отрицательно)'
      if not ok else 'ПРЕДРЕГИСТРАЦИЯ №5: ПОДТВЕРЖДЕНА')
print('''
Честный разбор (диагноз, НЕ спасение результата): заявленное «доля Fp
выше» не выполнено в сырых долях (0.481 < 0.574). Значимое p против
перестановочного нуля — артефакт дизайна: доля повторяемых токенов
растёт с числом документов группы (D-серии 369 док. против Fp 15),
перетасовка между группами разного размера смещает базлайн вниз для
малой группы. Урок для будущей №6: сравнивать классы повторяемости
надо при выровненном числе документов (подвыборки D до 15 док.) — это
заявляется ЗАРАНЕЕ, не после взгляда. Вердикт по замороженной букве:
НЕ ПОДТВЕРЖДЕНА; ошибка вердикта скрипта (проверял только хвост p)
поймана до публикации и исправлена. Один прогон, результат как вышел.''')
