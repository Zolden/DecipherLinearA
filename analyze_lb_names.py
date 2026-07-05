# -*- coding: utf-8 -*-
"""Этап 6, п.1 (часть 2, §T): лексикон LB против лексикона LA — контролируемый
омографический тест на ВЕСЬ словарь (расширение §E с топонимов на всё, включая
личные имена пастушьих D-серий Кносса).

LB-словарь: lb_lexicon.tsv (сборка parse_lb_lexicon.py из архивных страниц
minoan.deaditerranean.com). Фильтр валидности слога: V или CV с согласными LB
{d,j,k,m,n,p,q,r,s,t,w,z} (+ индексы 2/3) — это же отсекает англоязычный мусор
скрейпа (b,c,f,g,h,l,v-слоги в LB невозможны).

Тесты (все нули: Null-A пул знаков, Null-B позиционный; R=10000, seed=42):
T1: LA-лексикон × весь LB-словарь — число точных омографов.
T2: LA-лексикон × слова, аттестованные в KN D-сериях (пастушьи списки: в
    основном антропонимы + топонимы).
T3: только LA-гапаксы («именной» класс §F) × весь LB-словарь.
Совпадения — «кандидаты-омографы», не чтения.
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

# ---------------- LB-словарь
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
    lb[w] = (int(c), ser, sites)
print(f'LB-словарь после фильтра: {len(lb)} типов')
lb_all = set(lb)
lb_kn_d = {w for w, (c, ser, sites) in lb.items()
           if any(s.startswith('KN D') for s in ser.split(','))}
print(f'из них с аттестацией в KN D-сериях: {len(lb_kn_d)}')

# ---------------- LA-лексикон
corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); lex_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1; lex_docs[w].add(d['id'])
words = sorted(lex)
hapax = {w for w in words if lex[w] == 1}

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s: return None
        out.append(s.lower())
    return '-'.join(out)

def count_matches(word_list, targets, subset=None):
    hits = []
    for w in word_list:
        if subset is not None and w not in subset: continue
        r = read_lb(w)
        if r and r in targets: hits.append((w, r))
    return hits

# ---------------- наблюдаемое
print('\n=== T1: весь LB-словарь ===')
h1 = count_matches(words, lb_all)
for w, r in sorted(h1):
    c, ser, sites = lb[r]
    print(f'   {r:<16} LA: ×{lex[w]} {sorted(lex_docs[w])[:4]} | LB: ×{c} [{ser[:60]}]')
print(f'всего: {len(h1)}')
h2 = count_matches(words, lb_kn_d)
print(f'\n=== T2: KN D-серии ===\n' +
      '\n'.join(f'   {r}' for _, r in sorted(h2)) + f'\nвсего: {len(h2)}')
h3 = count_matches(words, lb_all, subset=hapax)
print(f'\n=== T3: только LA-гапаксы ===\nвсего: {len(h3)} из {len(hapax)} гапаксов')

# ---------------- нули
lengths = [len(w) for w in words]
hap_idx = [i for i, w in enumerate(words) if w in hapax]
sign_pool = [s for w in words for s in w]
pos_pools = {0: [], 1: [], 2: []}
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)

def gen_A():
    random.shuffle(sign_pool)
    out = []; i = 0
    for L in lengths:
        out.append(tuple(sign_pool[i:i + L])); i += L
    return out

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

obs_len = Counter(len(w) for w, _ in h1)
print(f'\nнаблюдаемые совпадения по длине слова: {dict(sorted(obs_len.items()))}')

for null_name, gen in [('Null-A', gen_A), ('Null-B', gen_B)]:
    random.seed(42)
    c1 = []; c2 = []; c3 = []
    clen = {2: [], 3: [], 4: []}   # 4 = длина >=4
    for _ in range(R):
        wl = gen()
        r1 = r2 = r3 = 0
        rl = {2: 0, 3: 0, 4: 0}
        for i, w in enumerate(wl):
            r = read_lb(w)
            if not r: continue
            if r in lb_all:
                r1 += 1
                rl[min(len(w), 4)] += 1
                if r in lb_kn_d: r2 += 1
        for i in hap_idx:
            r = read_lb(wl[i])
            if r and r in lb_all: r3 += 1
        c1.append(r1); c2.append(r2); c3.append(r3)
        for k in clen: clen[k].append(rl[k])
    for label, obs, cs in [('T1', len(h1), c1), ('T2', len(h2), c2),
                           ('T3', len(h3), c3)]:
        m = sum(cs) / R
        sd = (sum((x - m) ** 2 for x in cs) / R) ** 0.5
        p = sum(1 for x in cs if x >= obs) / R
        print(f'{label} / {null_name}: наблюдаемо {obs}, нуль {m:.2f}±{sd:.2f}, '
              f'p={p:.4f}')
    for k in (2, 3, 4):
        obs_k = sum(v for l, v in obs_len.items() if min(l, 4) == k)
        cs = clen[k]
        m = sum(cs) / R
        sd = (sum((x - m) ** 2 for x in cs) / R) ** 0.5
        p = sum(1 for x in cs if x >= obs_k) / R
        lab = f'{k}' if k < 4 else '>=4'
        print(f'   длина {lab}: наблюдаемо {obs_k}, нуль {m:.2f}±{sd:.2f}, p={p:.4f}')
