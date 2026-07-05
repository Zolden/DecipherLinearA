# -*- coding: utf-8 -*-
"""Этап 6, п.2 (§N): устойчивость ключевых результатов к сомнительным чтениям.

«Надёжный» лексикон: из подсчёта исключаются токены слов, несущие (а) underdot
Янгера (underdots_layer.pkl — любой знак или всё слово) ИЛИ (б) флаг doubtful
самого корпуса. Тип слова остаётся, если у него есть >=1 надёжный токен;
частота = число надёжных токенов.

Пересчитываются: §C (same-C финальных чередований, основа >=2 и >=1),
§D (V/CV позиционность), §E (омографы-топонимы), §L (поддержка -JA и A-).
Все нули и seed те же, что в исходных разделах.
"""
import sys, pickle, random, itertools, math
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
layer = pickle.load(open('underdots_layer.pkl', 'rb'))

def build_lex(reliable_only):
    lex = Counter(); lost_tok = 0
    for d in corpus:
        for i, (k, v) in enumerate(d['toks']):
            if k != 'WORD': continue
            if not (v['syllabic'] and len(v['signs']) >= 2 and v['complete']
                    and not (v['gap'] or v['trunc_l'] or v['trunc_r'])):
                continue
            if reliable_only and ((d['id'], i) in layer or v['doubtful']):
                lost_tok += 1; continue
            lex[tuple(v['signs'])] += 1
    return lex, lost_tok

lex_full, _ = build_lex(False)
lex_rel, lost = build_lex(True)
print(f'полный лексикон: {len(lex_full)} типов / {sum(lex_full.values())} токенов')
print(f'надёжный лексикон: {len(lex_rel)} типов / {sum(lex_rel.values())} токенов '
      f'(исключено токенов: {lost})')

VOWELS = {'A', 'E', 'I', 'O', 'U'}
def lb_value(s):
    if s.startswith('*') or '+' in s or s == 'AU': return None
    base = s.rstrip('23')
    if base in VOWELS: return ('', base)
    if len(base) >= 2 and base[-1] in VOWELS and base[:-1].isalpha():
        return (base[:-1], base[-1])
    return None

def sameC_test(lex, min_stem, label):
    words = set(lex)
    groups = defaultdict(set)
    for w in words:
        if len(w[:-1]) >= min_stem: groups[w[:-1]].add(w[-1])
    pairs = []
    for stem, alts in groups.items():
        for x, y in itertools.combinations(sorted(alts), 2):
            if lb_value(x) and lb_value(y): pairs.append((x, y))
    if not pairs:
        print(f'{label}: пар нет'); return
    nodes = sorted({s for p in pairs for s in p})
    vals = {s: lb_value(s) for s in nodes}
    def stat(a):
        return sum(1 for x, y in pairs if a[x][0] == a[y][0])
    obs = stat(vals)
    random.seed(42)
    vlist = [vals[s] for s in nodes]; ge = 0
    for _ in range(R):
        random.shuffle(vlist)
        if stat(dict(zip(nodes, vlist))) >= obs: ge += 1
    print(f'{label}: пар {len(pairs)}, same-C {obs} ({obs / len(pairs):.1%}), '
          f'p={ge / R:.4f}')

def positions_test(lex, label):
    pos = defaultdict(lambda: [0, 0, 0])
    for w in lex:
        for i, s in enumerate(w):
            j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
            pos[s][j] += 1
    elig = []
    for s, p in pos.items():
        if sum(p) < 5: continue
        if s in VOWELS: elig.append((s, 'V', p))
        elif lb_value(s): elig.append((s, 'CV', p))
    v = [x for x in elig if x[1] == 'V']
    obs = sum(x[2][0] for x in v) / max(1, sum(sum(x[2]) for x in v))
    cv = [x for x in elig if x[1] == 'CV']
    cvr = sum(x[2][0] for x in cv) / max(1, sum(sum(x[2]) for x in cv))
    random.seed(42); ge = 0
    for _ in range(R):
        samp = random.sample(elig, len(v))
        if sum(x[2][0] for x in samp) / max(1, sum(sum(x[2]) for x in samp)) >= obs:
            ge += 1
    print(f'{label}: V нач. {obs:.1%} (CV {cvr:.1%}), p={ge / R:.4f} '
          f'(V-знаков {len(v)} из {len(elig)})')

def homographs_test(lex, label):
    TARGETS = ['pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'ku-do-ni-ja', 'tu-ri-so',
               'su-ki-ri-ta', 'se-to-i-ja', 'di-ka-ta', 'ru-ki-to', 'e-ko-so',
               'pu-so', 'a-pa-ta-wa', 'da-wo', 'do-ti-ja', 'e-ra', 'ku-ta-to',
               'qa-ra', 'ra-ja', 'ra-su-to', 'ra-to', 'ri-jo-no', 'si-ra-ro',
               'su-ri-mo', 'tu-ni-ja', 'u-ta-no', 'wa-to', 'pu-na-so',
               'ti-ri-to', 'qa-mo']
    words = sorted(lex)
    def read(w):
        out = []
        for s in w:
            if s.startswith('*') or '+' in s: return None
            out.append(s.lower())
        return '-'.join(out)
    hits = [w for w in words if read(w) in set(TARGETS)]
    lengths = [len(w) for w in words]
    pool = [s for w in words for s in w]
    random.seed(42); cnts = []
    for _ in range(R):
        random.shuffle(pool)
        i = 0; c = 0
        for L in lengths:
            r = read(tuple(pool[i:i + L])); i += L
            if r in set(TARGETS): c += 1
        cnts.append(c)
    m = sum(cnts) / R
    p = sum(1 for c in cnts if c >= len(hits)) / R
    print(f'{label}: наблюдаемо {len(hits)} ({[",".join(w) for w in hits]}), '
          f'нуль {m:.2f}, p={p:.4f}')

def marker_support(lex, label):
    words = set(lex)
    suf = defaultdict(set); pre = defaultdict(set)
    for w in words:
        if len(w) - 1 >= 2:
            suf[w[-1:]].add(w[:-1]); pre[w[:1]].add(w[1:])
    def indep(T, M, table, self_key):
        if T in words: return True
        return any(T in st for S2, st in table.items() if S2 != self_key)
    ja = sum(1 for T in suf.get(('JA',), ()) if indep(T, ('JA',), suf, ('JA',)))
    a = sum(1 for T in pre.get(('A',), ()) if indep(T, ('A',), pre, ('A',)))
    print(f'{label}: поддержка -JA {ja} основ, A- {a} основ')

print('\n=== §C same-C финальных чередований ===')
for min_stem in (2, 1):
    sameC_test(lex_full, min_stem, f'полный, основа >={min_stem}')
    sameC_test(lex_rel, min_stem, f'надёжный, основа >={min_stem}')
print('\n=== §D позиционность V/CV ===')
positions_test(lex_full, 'полный')
positions_test(lex_rel, 'надёжный')
print('\n=== §E омографы-топонимы (список 29) ===')
homographs_test(lex_full, 'полный')
homographs_test(lex_rel, 'надёжный')
print('\n=== §L поддержка главных маркеров ===')
marker_support(lex_full, 'полный')
marker_support(lex_rel, 'надёжный')

# сомнительны ли токены самих топонимов-якорей
print('\nтокены якорей в underdot-слое / doubtful:')
for d in corpus:
    for i, (k, v) in enumerate(d['toks']):
        if k == 'WORD' and v['norm'] in ('PA-I-TO', 'SE-TO-I-JA', 'SU-KI-RI-TA',
                                         'SU-KI-RI-TE-I-JA'):
            dot = (d['id'], i) in layer
            print(f'   {v["norm"]} @ {d["id"]}: underdot={dot}, '
                  f'corpus_doubtful={v["doubtful"]}')
