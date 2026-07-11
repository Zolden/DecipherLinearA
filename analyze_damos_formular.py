# -*- coding: utf-8 -*-
"""Этап 36 (§DU-б): формуляр D-серий Кносса (DĀMOS) — открытость позиций
в административном жанре LB (продолжение жанровой таблицы §CM и
этрусского п.9-10).

KN D-серии (учёт овец): TTR позиций 1/2 (метрика этрусков, нуль обмена
внутри документа); ожидание по нашей рамке: позиция 1 = пастух (открытый
словарь), позиция 2 = коллектор/топоним (закрытее). Вне ростера (кэш).
"""
import sys, json, os, re, random
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')

pairs = []
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
    for raw_line in (item.get('content') or '').split('\n'):
        for rt in raw_line.replace(',', ' ').split():
            if '[' in rt or ']' in rt or '?' in rt:
                continue
            if WORD_RE.match(rt):
                ws.append(rt)
    if len(ws) >= 2:
        pairs.append((ws[0], ws[1]))

print(f'KN D-документов с >=2 чистыми словами: {len(pairs)}')
t1 = len({a for a, _ in pairs}) / len(pairs)
t2 = len({b for _, b in pairs}) / len(pairs)
d_obs = t1 - t2
print(f'TTR1={t1:.2f} (пастуший слот), TTR2={t2:.2f}; Δ={d_obs:+.3f}')
print('топ позиции 1:', Counter(a for a, _ in pairs).most_common(5))
print('топ позиции 2:', Counter(b for _, b in pairs).most_common(5))
sims = []
for _ in range(R):
    sw = [(b, a) if random.random() < 0.5 else (a, b) for a, b in pairs]
    s1 = len({a for a, _ in sw}) / len(sw)
    s2 = len({b for _, b in sw}) / len(sw)
    sims.append(s1 - s2)
p = (sum(1 for x in sims if abs(x) >= abs(d_obs) - 1e-12) + 1) / (R + 1)
print(f'нуль обмена: p={p:.4f} (двусторонний)')
print('''
Чтение: продолжение жанровой таблицы (§CM, этруски пп.9-10): у
административного LB-формуляра овечьих записей ожидаем «открытый пастух
→ закрытее второй слот». Дескриптивно+перестановка; жанровая рамка
теперь на: LA-адм, LA-религ, этр-эпитафии, этр-ритуал, LB-адм.''')
