# -*- coding: utf-8 -*-
"""Этап 12.4 (§BB): дожили ли слова слота 2 (кандидаты местных обозначений)
до греческих архивов?

Слот-2 словарь (§AE, 24 документа) читается через LB-значения и сверяется с
(а) полным LB-лексиконом, (б) слот-именами, (в) топонимами. Контроль: случайные
наборы слов LA того же профиля длин (R=10000) — избыточны ли совпадения
слота 2 против фона лексикона.
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
res = pickle.load(open('results.pkl', 'rb'))
docsx = {d['id']: d for d in corpus}

# слот-2 словарь: rows этапа 2 (rel) + авторазметка §AE
from formula_template import assign
slot2 = set()
for doc, typ, lanes in res['rows']:
    if doc in docsx and docsx[doc]['typ'] != 'rel': continue
    for w in lanes.get(2, []):
        w2 = w.replace('…', '').strip('-')
        if w2: slot2.add(w2)
for d in corpus:
    if d['typ'] != 'rel': continue
    words = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    for w, s in assign(words):
        if s == 2: slot2.add(w)
slot2 = sorted(slot2)
print(f'слот-2 словарь: {len(slot2)} слов')

CONS = set('djkmnpqrstwz')
def valid_syl(s):
    if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): return True
    m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
    return bool(m and m.group(1) in CONS)
lb_all = set()
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    syls = tuple(line.split('\t')[0].split('-'))
    if len(syls) >= 2 and all(valid_syl(s) for s in syls):
        lb_all.add('-'.join(syls))
name_slot = set()
for line in open('lb_name_slots.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        name_slot.add(line.split('\t')[0])
TOP = {'pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'ku-do-ni-ja', 'tu-ri-so',
       'su-ki-ri-ta', 'se-to-i-ja', 'di-ka-ta', 'ru-ki-to', 'e-ko-so', 'pu-so',
       'a-pa-ta-wa', 'da-wo', 'do-ti-ja', 'e-ra', 'ku-ta-to', 'qa-ra', 'ra-ja',
       'ra-su-to', 'ra-to', 'ri-jo-no', 'si-ra-ro', 'su-ri-mo', 'tu-ni-ja',
       'u-ta-no', 'wa-to', 'pu-na-so', 'ti-ri-to', 'qa-mo'}

def read_lb(norm):
    out = []
    for s in norm.split('-'):
        if s.startswith('*') or '+' in s or not s.isascii(): return None
        out.append(s.lower())
    return '-'.join(out)

print('\nсовпадения слота 2 с LB:')
obs = 0
readable = []
for w in slot2:
    r = read_lb(w)
    n = len(w.split('-'))
    if r: readable.append((w, n))
    if r and r in lb_all and n >= 3:
        tags = []
        if r in TOP: tags.append('TOP')
        if r in name_slot: tags.append('SLOT-ИМЯ')
        print(f'   {w:<22} == {r} {"/".join(tags)}')
        obs += 1
print(f'наблюдаемо (длина >=3): {obs}')

# контроль: случайные наборы слов лексикона того же профиля длин
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
by_len = defaultdict(list)
for w in lex:
    r = read_lb('-'.join(w))
    if r: by_len[len(w)].append(r)
need = Counter(n for w, n in readable if n >= 3)
cnts = []
for _ in range(R):
    c = 0
    for L, k in need.items():
        pool = by_len.get(L, [])
        if len(pool) >= k:
            for r in random.sample(pool, k):
                if r in lb_all: c += 1
    cnts.append(c)
m = sum(cnts) / R
p = sum(1 for x in cnts if x >= obs) / R
print(f'контроль (случайные слова LA того же профиля длин, R={R}): '
      f'{m:.2f}, p={p:.4f}')
print('замечание: значимый вклад слота 2 — SE-TO-I-JA (уже известный якорь); '
      'вопрос теста — есть ли избыток СВЕРХ него.')
