# -*- coding: utf-8 -*-
"""Этап 8.7 (§AE): расширение таблицы слотов формулы возлияний на все
rel-документы и пере-тест географичности слота 2.

Якоря слотов (по вариантам из таблицы этапа 2):
  слот 1: слова, начинающиеся с (J)A-TA-I-*301 / TA-I-*301;
  слот 3: содержит SA-SA-RA / SA-SA-*802 (…(J)A-SA-SA-RA-ME/-MA-NA);
  слот 4: начинается с U-NA-KA / U-NA-RU / JA-SA-U-NA;
  слот 5: начинается с I-PI-NA;
  слот 6: SI-RU / SI-RU-TE / SI-RU-MA-…
Разметка нового документа: слова до первого якоря слота >=3 (исключая якорь
слота 1) → кандидаты слота 2. Требование: в документе есть хотя бы один якорь
слотов 3–6 (иначе структура формулы не опознана).
Пере-тест сайт-специфичности слота 2 (точное слово / общий биграм; нуль —
перестановка сайтов, R=10000, seed=42) на объединённой таблице.
"""
import sys, pickle, random, itertools
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
res = pickle.load(open('results.pkl', 'rb'))
docsx = {d['id']: d for d in corpus}

def slot_of(word):
    n = word
    if n.startswith(('A-TA-I-*301', 'JA-TA-I-*301', 'TA-I-*301')): return 1
    if 'SA-SA-RA' in n or 'SA-SA-*802' in n or n.startswith(('A-SA-SA', 'JA-SA-SA')):
        return 3
    if n.startswith(('U-NA-KA', 'U-NA-RU', 'JA-SA-U-NA')): return 4
    if n.startswith('I-PI-NA'): return 5
    if n == 'SI-RU' or n.startswith(('SI-RU-TE', 'SI-RU-MA')): return 6
    return None

# уже размеченные этапом 2 (только rel)
known = {}
for doc, typ, lanes in res['rows']:
    if doc in docsx and docsx[doc]['typ'] != 'rel': continue
    ws = [w.replace('…', '').strip('-') for w in lanes.get(2, [])]
    ws = [w for w in ws if w]
    if ws: known[doc] = ws

# авторазметка остальных rel-документов
auto = {}
for d in corpus:
    if d['typ'] != 'rel' or d['id'] in known: continue
    words = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if not words: continue
    slots = [slot_of(w) for w in words]
    if not any(s in (3, 4, 5, 6) for s in slots): continue
    first_late = next(i for i, s in enumerate(slots) if s in (3, 4, 5, 6))
    cands = [w for w, s in zip(words[:first_late], slots[:first_late])
             if s is None and len(w.split('-')) >= 1]
    if cands: auto[d['id']] = cands

print(f'слот-2 из этапа 2 (rel): {len(known)} док.; авторазметка добавила: '
      f'{len(auto)} док.')
for doc, ws in sorted(auto.items()):
    print(f'   + {doc:<12} {docsx[doc]["site"]:<5} {ws}')

merged = dict(known); merged.update(auto)
entries = [(doc, docsx[doc]['site'], ws) for doc, ws in merged.items()]
print(f'итого документов со слотом 2: {len(entries)}')

def bigrams(word):
    s = word.split('-')
    return {(s[i], s[i + 1]) for i in range(len(s) - 1)}
def share_exact(a, b): return bool(set(a) & set(b))
def share_bigram(a, b):
    ba = set().union(*[bigrams(w) for w in a]) if a else set()
    bb = set().union(*[bigrams(w) for w in b]) if b else set()
    return bool(ba & bb)

sites = [s for _, s, _ in entries]
words_l = [ws for _, _, ws in entries]
pairs = list(itertools.combinations(range(len(entries)), 2))
def delta(site_vec, sharef):
    same = [sharef(words_l[i], words_l[j]) for i, j in pairs
            if site_vec[i] == site_vec[j]]
    diff = [sharef(words_l[i], words_l[j]) for i, j in pairs
            if site_vec[i] != site_vec[j]]
    if not same or not diff: return None
    return sum(same) / len(same) - sum(diff) / len(diff)
for name, fn in [('точное слово', share_exact), ('общий биграм', share_bigram)]:
    dE = delta(sites, fn)
    sv = sites[:]; ge = 0
    for _ in range(R):
        random.shuffle(sv)
        d2 = delta(sv, fn)
        if d2 is not None and d2 >= dE - 1e-12: ge += 1
    print(f'слот 2 ({name}): Δ={dE:+.3f}, p={ge / R:.4f} '
          f'(док. {len(entries)}, R={R}, seed=42)')

# повторы между документами
cnt = Counter()
for _, _, ws in entries:
    for w in set(ws): cnt[w] += 1
print('\nэлементы слота 2, встречающиеся в >=2 документах:')
for w, c in cnt.most_common():
    if c < 2: break
    where = sorted((doc, s) for doc, s, ws in entries if w in ws)
    print(f'   {w}: ×{c} {where}')
