# -*- coding: utf-8 -*-
"""Этап 38 (§DX): две популяции в слоте 1 D-серий — слепое переоткрытие
класса «коллекторов».

Слот 1 KN D-документов (§DW) не однороден: распределение
«в скольких документах живёт тип слота 1» должно быть бимодальным —
масса уникальных (пастухи) + немногие сверхповторяемые (коллекторы
микенологии: u-ta-jo, we-we-si-jo…). Проверка: (а) хвост распределения
против геометрического подгона; (б) состав топ-повторяемых против
внешнего списка коллекторов (Docs2 — внешний факт); (в) LA-зеркало:
повторяемые первые слова HT-табличек. Вне ростера (кэш DĀMOS).
"""
import sys, json, os, re, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')

# внешний список известных «коллекторов» Кносса (Docs2/Olivier — внешний факт)
KNOWN_COLLECTORS = {'u-ta-jo', 'we-we-si-jo', 'a-te-jo', 'da-mi-ni-jo',
                    'u-ta-jo-jo', 'we-we-si-jo-jo', 'pe-ri-qo-te-jo',
                    'a-ka-i-jo', 'sa-qa-re-jo', 'do-e-ro'}

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
    for raw_line in (item.get('content') or '').split('\n'):
        for rt in raw_line.replace(',', ' ').split():
            if '[' in rt or ']' in rt or '?' in rt:
                continue
            if WORD_RE.match(rt):
                ws.append(rt)
    if len(ws) >= 2:
        first_docs[ws[0]].add(head)

sizes = sorted((len(v) for v in first_docs.values()), reverse=True)
n1 = sum(1 for s in sizes if s == 1)
n2_4 = sum(1 for s in sizes if 2 <= s <= 4)
n5p = sum(1 for s in sizes if s >= 5)
print(f'типов слота 1: {len(sizes)}; уникальных (1 док): {n1} '
      f'({n1 / len(sizes):.0%}); 2–4 дока: {n2_4}; >=5 доков: {n5p}')
top = sorted(first_docs.items(), key=lambda kv: -len(kv[1]))[:10]
print('топ повторяемых слота 1:')
hits = 0
for w, docs in top:
    known = w in KNOWN_COLLECTORS
    hits += known
    print(f'   {w:<16} ×{len(docs):<3} {"= ИЗВЕСТНЫЙ КОЛЛЕКТОР" if known else ""}')
print(f'из топ-10 в внешнем списке коллекторов: {hits}')

# LA-зеркало: повторяемые первые слова HT-табличек (>=2 слов, адм.)
corpus = pickle.load(open('corpus.pkl', 'rb'))
la_first = defaultdict(set)
for d in corpus:
    if not d['id'].startswith('HT') or any(
            z in d['id'] for z in ('Za', 'Zb', 'Zc')):
        continue
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) >= 2:
        la_first[ws[0]].add(d['id'])
la_top = sorted(la_first.items(), key=lambda kv: -len(kv[1]))[:8]
la_sizes = [len(v) for v in la_first.values()]
print(f'\nLA-зеркало (HT, слот 1): типов {len(la_sizes)}, уникальных '
      f'{sum(1 for s in la_sizes if s == 1) / len(la_sizes):.0%}')
print('топ повторяемых HT слота 1:',
      [(w, len(ds)) for w, ds in la_top])
print('''
Чтение: бимодальность слота 1 = две функциональные популяции (уникальные
агенты + повторяемые «кураторы»); совпадение топа с внешним списком
коллекторов = слепое переоткрытие класса. LA-зеркало показывает, есть ли
аналог в HT-формуляре (SI/NI — логограммные заголовки, не агенты; вопрос
об A-DU и повторяемых словах). Дескриптивно; чтения не приписываются.''')
