# -*- coding: utf-8 -*-
"""Этап 7.2 (§V): §T v2 — где именно сидит избыток совпадений LA↔LB:
в именах, топонимах или греческой лексике?

Классификация LB-слов (по сериям аттестаций и спискам):
- TOP: замкнутый список критских топонимов (29, §E/§H);
- GREEK: стоп-лист высоконадёжной микенской греческой лексики (~50 слов:
  служебные, титулы, термины землевладения/учёта; НЕ включаем спорные
  da-ma-te, i-ja-te и т.п.);
- NAME: слово аттестовано в именных сериях (KN D*, As, B, V(c), Sc, Ap;
  PY Jn, Cn, An) и не входит в TOP/GREEK — прокси «ономастикон»;
- OTHER: остальное.
Тест: длина-стратифицированные совпадения по классам; нуль Null-B — те же
псевдолексиконы LA, их совпадения классифицируются той же процедурой.
R=10000, seed=42. Предсказание гипотезы ономастикона: избыток длинных
совпадений концентрируется в NAME(+TOP), а не в GREEK.
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

# ---------------- LB-словарь и классы
CONS = set('djkmnpqrstwz')
def valid_syl(s):
    if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): return True
    m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
    return bool(m and m.group(1) in CONS)

lb = {}
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    w, c, ser, sites = (line.rstrip('\n').split('\t') + ['', ''])[:4]
    syls = w.split('-')
    if len(syls) < 2 or not all(valid_syl(s) for s in syls): continue
    lb[w] = set(ser.split(',')) if ser else set()

TOP = {'pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'ku-do-ni-ja', 'tu-ri-so',
       'su-ki-ri-ta', 'se-to-i-ja', 'di-ka-ta', 'ru-ki-to', 'e-ko-so', 'pu-so',
       'a-pa-ta-wa', 'da-wo', 'do-ti-ja', 'e-ra', 'ku-ta-to', 'qa-ra', 'ra-ja',
       'ra-su-to', 'ra-to', 'ri-jo-no', 'si-ra-ro', 'su-ri-mo', 'tu-ni-ja',
       'u-ta-no', 'wa-to', 'pu-na-so', 'ti-ri-to', 'qa-mo'}
GREEK = {'to-so', 'to-sa', 'to-so-de', 'to-sa-de', 'o-pe-ro', 'do-e-ro',
         'do-e-ra', 'ko-wo', 'ko-wa', 'pa-ro', 'e-ke', 'e-ke-qe', 'e-ko-si',
         'o-na-to', 'ko-to-na', 'ko-to-i-na', 'ke-ke-me-na', 'ki-ti-me-na',
         'da-mo', 'te-o', 'te-o-jo', 'i-je-re-ja', 'i-je-re-u', 'i-je-ro',
         'ka-ko', 'ku-ru-so', 'e-ra-wo', 'a-pu-do-si', 'do-so-mo',
         'e-re-u-te-ro', 'e-re-u-te-ra', 'o-pi', 'qa-si-re-u', 'ra-wa-ke-ta',
         'wa-na-ka', 'wa-na-ka-te-ro', 'me-zo', 'me-zo-e', 'me-u-jo',
         'me-wi-jo', 'ne-wo', 'ne-wa', 'pa-ra-jo', 'pe-mo', 'pe-ma',
         'ta-ra-si-ja', 'we-to', 'di-do-si', 'e-u-ke-to', 'o-da-a2', 'te-ke',
         'a-pe-o', 'e-qe-ta', 'pe-ru-si-nu-wo', 'a-ni-ja', 'to-pe-za',
         'pa-we-a', 'pa-we-a2', 'tu-na-no', 'a-ro2-a', 'e-ne-wo', 'we-pe-za'}
NAME_SERIES = re.compile(r'^(KN D[a-z]?|KN As|KN B|KN V[c]?|KN Sc|KN Ap|'
                         r'PY Jn|PY Cn|PY An)$')

def classify(w):
    if w in TOP: return 'TOP'
    if w in GREEK: return 'GREEK'
    if any(NAME_SERIES.match(s.strip()) for s in lb.get(w, ())): return 'NAME'
    return 'OTHER'

lb_all = set(lb)
cls_counts = Counter(classify(w) for w in lb_all)
print(f'LB-словарь {len(lb_all)}; классы: {dict(cls_counts)}')

# ---------------- LA-лексикон
corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words = sorted(lex)

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s: return None
        out.append(s.lower())
    return '-'.join(out)

def matches_of(word_list):
    out = []
    for w in word_list:
        r = read_lb(w)
        if r and r in lb_all:
            out.append((min(len(w), 4), classify(r)))
    return out

obs = Counter(matches_of(words))
print('\nнаблюдаемые совпадения (длина × класс):')
for (L, c), n in sorted(obs.items()):
    print(f'   длина {L if L < 4 else ">=4"} × {c}: {n}')

# ---------------- нуль Null-B
lengths = [len(w) for w in words]
pos_pools = {0: [], 1: [], 2: []}
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)

def gen_B():
    for p in pos_pools.values(): random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = []
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.append(tuple(w))
    return out

ALL_KEYS = [(L, c) for L in (2, 3, 4) for c in ('TOP', 'GREEK', 'NAME', 'OTHER')]
null_counts = {k: [] for k in ALL_KEYS}
for _ in range(R):
    nc = Counter(matches_of(gen_B()))
    for key in ALL_KEYS:
        null_counts[key].append(nc.get(key, 0))

print('\n=== длина × класс: наблюдаемо против нуля (Null-B, R=10000) ===')
for key in ALL_KEYS:
    L, c = key
    o = obs.get(key, 0)
    ns = null_counts[key]
    m = sum(ns) / R
    sd = (sum((x - m) ** 2 for x in ns) / R) ** 0.5
    p = sum(1 for x in ns if x >= o) / R
    lab = f'{L}' if L < 4 else '>=4'
    star = ' *' if p < 0.05 and o > 0 else ''
    print(f'   длина {lab:<3} {c:<6}: наблюдаемо {o:>2}, нуль {m:5.2f}±{sd:4.2f}, '
          f'p={p:.4f}{star}')

# агрегат по классам для длинных (>=3)
print('\n=== агрегат: длинные (>=3) по классам ===')
for c in ('NAME', 'TOP', 'GREEK', 'OTHER'):
    o = sum(v for (L, cc), v in obs.items() if L >= 3 and cc == c)
    ns = [null_counts[(3, c)][i] + null_counts[(4, c)][i] for i in range(R)]
    m = sum(ns) / R
    p = sum(1 for x in ns if x >= o) / R
    print(f'   {c:<6}: наблюдаемо {o}, нуль {m:.2f}, p={p:.4f}')
# NAME+TOP против GREEK
oN = sum(v for (L, cc), v in obs.items() if L >= 3 and cc in ('NAME', 'TOP'))
nsN = [null_counts[(3, 'NAME')][i] + null_counts[(4, 'NAME')][i] +
       null_counts[(3, 'TOP')][i] + null_counts[(4, 'TOP')][i] for i in range(R)]
pN = sum(1 for x in nsN if x >= oN) / R
print(f'   NAME+TOP: наблюдаемо {oN}, нуль {sum(nsN) / R:.2f}, p={pN:.4f}')
