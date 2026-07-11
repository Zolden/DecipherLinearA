# -*- coding: utf-8 -*-
"""Этап 46 (§ED): кураторы-кандидаты HT (§DX-§DY: KA-PA, A-KA-RU, JE-DI,
*21F-TU-NE) против независимой экспертной разметки Хогана (AURA 2026,
transactions.js) и микроконтекст.

(1) Типы документов Хогана для кураторских табличек и роли, которые он
дал самим словам-кандидатам (его разметка не знает наших классов).
(2) Микроконтекст: что стоит сразу после куратора (оператор TE?
логограмма? имя?) — у коллекторов KN после имени коллектора идёт
пастуший контекст. (3) Контроль: те же профили для четырёх УНИКАЛЬНЫХ
первых слов (гапаксы-заголовки) — отличается ли поведение классов.
Вне ростера (гитигнорный .hogan_cache.js).
"""
import sys, json, pickle, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

CUR = ['KA-PA', 'A-KA-RU', 'JE-DI', '*21F-TU-NE']

txt = open('.hogan_cache.js', encoding='utf-8').read()
data = json.loads(txt[txt.find('['):txt.rfind(']') + 1])
type_of = {}
role_of_word = defaultdict(Counter)
for t in data:
    did = t['name'].replace(' ', '')
    type_of[did] = t.get('type', '?')
    for w in t.get('words', []):
        wd = ((w.get('transliteratedWord') or w.get('word') or '')
              .strip().upper())
        role = (w.get('description') or '').strip()
        if wd:
            role_of_word[wd][role or '(без роли)'] += 1

corpus = pickle.load(open('corpus.pkl', 'rb'))
by_id = {d['id']: d for d in corpus}

print('(1) кураторские таблички в разметке Хогана:')
for w in CUR:
    docs = [d['id'] for d in corpus
            if w in [v['norm'] for k, v in d['toks']
                     if k == 'WORD' and v['syllabic']]]
    tps = [f"{did}:{type_of[did]}" for did in docs if did in type_of]
    print(f'   {w:<12} {tps if tps else "нет в его 129"}')
    if w in role_of_word:
        print(f'      его роли слова: {dict(role_of_word[w])}')

print('\n(2) микроконтекст кураторов (токен сразу после):')
after = defaultdict(Counter)
for w in CUR:
    for d in corpus:
        toks = d['toks']
        for i, (k, v) in enumerate(toks):
            if k == 'WORD' and v['syllabic'] and v['norm'] == w:
                if i + 1 < len(toks):
                    nk, nv = toks[i + 1]
                    if nk == 'NUM':
                        lab = 'ЧИСЛО'
                    elif nk == 'WORD' and nv:
                        lab = (nv['norm'] if nv['syllabic']
                               else f'ЛОГО:{nv["norm"]}')
                    else:
                        lab = nk
                else:
                    lab = 'КОНЕЦ'
                after[w][lab] += 1
for w in CUR:
    print(f'   {w:<12} {dict(after[w].most_common(5))}')

# (3) контроль: 4 уникальных первых слова HT с документами схожей длины
uniq_firsts = []
for d in corpus:
    if not d['id'].startswith('HT') or any(
            z in d['id'] for z in ('Za', 'Zb', 'Zc')):
        continue
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) >= 7 and ws[0] not in CUR:
        uniq_firsts.append((d['id'], ws[0]))
print('\n(3) контроль — первые слова длинных HT-документов (не кураторы):')
seen = set()
n = 0
for did, w in uniq_firsts:
    if w in seen:
        continue
    seen.add(w)
    tp = type_of.get(did, '—')
    roles = dict(role_of_word.get(w, {}))
    print(f'   {w:<14} {did:<8} Хоган:{tp:<22} роли:{roles}')
    n += 1
    if n >= 6:
        break
print('''
Чтение: если Хоган независимо типизирует кураторские таблички одним
семейством и/или даёт кандидатам агентные роли — внешняя опора класса;
контрольные уникальные заголовки должны вести себя иначе (имена-гапаксы).
Дескриптивно; чтения не приписываются.''')
