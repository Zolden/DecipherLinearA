# -*- coding: utf-8 -*-
"""Этап 32 (§DP): грамматика записи В САМОМ LB (DĀMOS) — тест наследования.

Предзаявка (коммит 10ffe39): to-so/to-sa (итоги) финально-смещены, как
KU-RO в LA (§BO); частица o-da-a2 — начально/второпозиционна, как
A-DU/TE. Метод — как analyze_record_syntax2.py: чистые слова (без ][ и
не-словных токенов), документы >=2 слов; совместная перестановка порядка
слов внутри документа (R=10000, seed=42); minP по семейству
{to-so, to-sa, to-so-de, o-pe-ro, o-da-a2} × {нач, вт, пп, фин}.
Читает damos_context не нужно — работаем по кэшу? Нет: по закоммиченному
damos-слою нельзя восстановить порядок слов, поэтому этот скрипт читает
кэш .damos_cache/ и ВНЕ стресс-ростера; его лог — канонический.
"""
import sys, json, os, re
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
R = 10000
rng = np.random.default_rng(42)
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')
OPS = ['to-so', 'to-sa', 'to-so-de', 'o-pe-ro', 'o-da-a2']
OPSET = set(OPS)

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
    if len(ws) >= 2:
        docs.append(ws)
print(f'документов DĀMOS с >=2 чистыми словами: {len(docs)}')

def positions(ws_list):
    c = {}
    for ws in ws_list:
        L = len(ws)
        for i, w in enumerate(ws):
            if w not in OPSET:
                continue
            if i == 0:
                c[(w, 'нач')] = c.get((w, 'нач'), 0) + 1
            if i == 1:
                c[(w, 'вт')] = c.get((w, 'вт'), 0) + 1
            if i == L - 2:
                c[(w, 'пп')] = c.get((w, 'пп'), 0) + 1
            if i == L - 1:
                c[(w, 'фин')] = c.get((w, 'фин'), 0) + 1
            c[(w, 'n')] = c.get((w, 'n'), 0) + 1
    return c

obs = positions(docs)
tests = [(w, pos) for w in OPS for pos in ('нач', 'вт', 'пп', 'фин')
         if obs.get((w, 'n'), 0) >= 5]
print('операторы (n):', {w: obs.get((w, 'n'), 0) for w in OPS})

docs_arr = [np.array(ws, dtype=object) for ws in docs]
sims = np.zeros((R, len(tests)), dtype=np.int32)
for r_i in range(R):
    sim_docs = []
    for arr in docs_arr:
        perm = rng.permutation(len(arr))
        sim_docs.append(list(arr[perm]))
    sc = positions(sim_docs)
    for j, (w, pos) in enumerate(tests):
        sims[r_i, j] = sc.get((w, pos), 0)
obs_arr = np.array([obs.get(t, 0) for t in tests])
p_raw = ((sims >= obs_arr).sum(axis=0) + 1) / (R + 1)
p_sim = np.zeros_like(sims, dtype=np.float64)
for j in range(len(tests)):
    order = np.sort(sims[:, j])
    idx = np.searchsorted(order, sims[:, j], side='left')
    p_sim[:, j] = (R - idx + 1) / (R + 1)
minp = p_sim.min(axis=1)
p_adj = np.array([((minp <= p).sum() + 1) / (R + 1) for p in p_raw])

exp = sims.mean(axis=0)
print(f'\n{"оператор":<10}{"поз":>5}{"n":>5}{"набл":>6}{"ожид":>7}'
      f'{"p":>9}{"p̃сем":>9}')
for j, (w, pos) in enumerate(tests):
    if p_raw[j] < 0.10 or (w in ('to-so', 'o-da-a2') and
                           pos in ('фин', 'нач', 'вт')):
        star = ' *' if p_adj[j] < 0.05 else ''
        print(f'{w:<10}{pos:>5}{obs.get((w, "n"), 0):>5}{obs_arr[j]:>6}'
              f'{exp[j]:>7.2f}{p_raw[j]:>9.4f}{p_adj[j]:>9.4f}{star}')
print('''
Предзаявка (10ffe39): to-so/to-sa финальны, o-da-a2 начальна/вторая.
Совпадение с LA-полярностью (§BO: KU-RO фин, A-DU нач) = наследование
документной грамматики письменной традицией.''')
