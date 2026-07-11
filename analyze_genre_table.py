# -*- coding: utf-8 -*-
"""Этап 40 (§DZ): единая жанровая таблица — TTR слота 1 (первого слова)
одной метрикой по трём традициям.

Строки LA/LB считаются здесь; строки Этрурии — внешние числа их
статистика (CROSS_PROJECT 2026-07-11, тот же TTR слота 1). CI не даём:
бутстрэп TTR систематически смещён вниз (перевыборка с возвращением
теряет типы; ср. их оговорку про artifact-bootstrap) — сравниваем точки.
Метрика: число РАЗНЫХ типов первого слова / число документов (>=2
слоговых слов). Дескриптивная таблица; перестановочные версии (§CM, §DU)
не пересматриваются — это единая линейка межтрадиционного сравнения.
"""
import sys, pickle, json, os, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def ttr(firsts):
    return len(set(firsts)) / len(firsts), len(firsts)

corpus = pickle.load(open('corpus.pkl', 'rb'))
rows = []

# LA административные (HT-таблички) и религиозные (Za и др. каменные)
la_adm, la_rel = [], []
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) < 2:
        continue
    if re.match(r'^(HT|ZA|KH|PH|TY|PE|MA|GO)\d', d['id']):
        la_adm.append(ws[0])
    elif re.search(r'Z[ab]', d['id']):
        la_rel.append(ws[0])
rows.append(('LA административные таблички', *ttr(la_adm)))
rows.append(('LA религиозные (Za/Zb камень)', *ttr(la_rel)))

# LB: D-серии (пастухи) и Fp/Fh (жертвенное масло — ближе к культовому)
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')
lb = defaultdict(list)
for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    head = (item.get('heading_short') or '')
    m = re.match(r'^(KN|PY) ([A-Z])[a-z]?\b', head)
    if not m:
        continue
    ws = []
    for raw_line in (item.get('content') or '').split('\n'):
        for rt in raw_line.replace(',', ' ').split():
            if '[' in rt or ']' in rt or '?' in rt:
                continue
            if WORD_RE.match(rt):
                ws.append(rt)
    if len(ws) >= 2:
        lb[(m.group(1), m.group(2))].append(ws[0])
for key, label in ((('KN', 'D'), 'LB KN D-серии (стада)'),
                   (('KN', 'F'), 'LB KN F-серии (масло/зерно)'),
                   (('PY', 'E'), 'LB PY E-серии (земля)'),
                   (('PY', 'A'), 'LB PY A-серии (люди)')):
    if len(lb[key]) >= 20:
        rows.append((label, *ttr(lb[key])))

print(f'{"жанр":<34} {"TTR":>5} {"n":>5}')
for name, t, n in rows:
    print(f'{name:<34} {t:>5.2f} {n:>5}')
print('внешние строки (их статистик, тот же TTR слота 1, artifact-bootstrap):')
print(f'{"Этрусские эпитафии":<34} {0.84:>5.2f}  {"(имена)":>13}')
print(f'{"Этрусские посвятительные":<34} {0.42:>5.2f}  {"(дейксис mi)":>13}')
print(f'{"Этрусские прочие":<34} {0.44:>5.2f}')
print('''
Чтение: одна метрика через три традиции. Открытый слот 1 (TTR высок) —
там, где документ начинается ИМЕНЕМ (учётные списки, эпитафии); закрытый
— там, где жанр начинается ФОРМУЛОЙ/дейксисом (возлияния, посвящения).
Открытость позиции — свойство жанра, не языка и не письменности.''')
