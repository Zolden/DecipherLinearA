# -*- coding: utf-8 -*-
"""Этап 9.4 (§AJ): микроконтексты минимальных контрастов.

Для каждой внутридокументной пары одной основы (§AF) — полный микроконтекст:
предыдущее/следующее слово, число после каждой формы, позиция (заголовок?).
Сводка: у скольких пар формы различаются наличием/типом числа; направление.
Плюс межсайтовые аффиксные дублеты: таблица «форма ← сайт» (локальная норма).
"""
import sys, pickle, itertools
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))
docsx = {d['id']: d for d in corpus}

def lex_words_of(d):
    out = []
    toks = d['toks']
    widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
    for i in widx:
        v = toks[i][1]
        if v['syllabic'] and len(v['signs']) >= 2 and v['complete'] \
           and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            out.append((i, tuple(v['signs'])))
    return out

def relation(a, b):
    if len(a) == len(b):
        diff = [i for i in range(len(a)) if a[i] != b[i]]
        return f'знак@{diff[0]}' if len(diff) == 1 else None
    if abs(len(a) - len(b)) > 2: return None
    if len(a) > len(b): a, b = b, a
    if b[:len(a)] == a: return f'суфф+{"-".join(b[len(a):])}'
    if b[-len(a):] == a: return f'преф {"-".join(b[:len(b) - len(a)])}+'
    return None

def ctx(d, i):
    toks = d['toks']
    nval = None
    for j in range(i + 1, len(toks)):
        if toks[j][0] == 'NUM':
            nval = toks[j][1]['val']
            for j2 in range(j + 1, len(toks)):
                if toks[j2][0] == 'NUM': nval += toks[j2][1]['val']
                else: break
            break
        if toks[j][0] == 'DIV': continue
        break
    prev = nxt = None
    for j in range(i - 1, -1, -1):
        if toks[j][0] == 'WORD': prev = toks[j][1]['norm']; break
    for j in range(i + 1, len(toks)):
        if toks[j][0] == 'WORD': nxt = toks[j][1]['norm']; break
    return nval, prev, nxt

print('=== микроконтексты внутридокументных пар ===')
summary = Counter()
for d in corpus:
    ws = lex_words_of(d)
    seen = set()
    for (i1, a), (i2, b) in itertools.combinations(ws, 2):
        if a == b: continue
        r = relation(a, b)
        if not r: continue
        key = (d['id'], tuple(sorted((a, b))))
        if key in seen: continue
        seen.add(key)
        n1, p1, x1 = ctx(d, i1)
        n2, p2, x2 = ctx(d, i2)
        print(f'\n{d["id"]} ({d["site"]}, {d["typ"]}) [{r}]')
        print(f'   {"-".join(a):<22} число={str(n1):<8} [{p1} _ {x1}]')
        print(f'   {"-".join(b):<22} число={str(n2):<8} [{p2} _ {x2}]')
        if (n1 is None) != (n2 is None):
            summary['одна форма с числом, другая без'] += 1
            # какая именно без числа — длиннее или короче?
            longer_no_num = (len(a) > len(b) and n1 is None) or \
                            (len(b) > len(a) and n2 is None)
            if len(a) != len(b):
                summary['длинная форма БЕЗ числа'] += longer_no_num
                summary['длинная форма С числом'] += (not longer_no_num)
        elif n1 is not None:
            summary['обе с числами'] += 1
        else:
            summary['обе без чисел'] += 1
print(f'\nсводка: {dict(summary)}')

# ---------------- межсайтовые аффиксные дублеты: локальная норма
print('\n=== межсайтовые аффиксные пары: форма ← сайт ===')
lex_sites = defaultdict(set); lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1; lex_sites[w].add(d['site'])
WORDS = set(lex)
n_pairs = 0
for a, b in itertools.combinations(sorted(WORDS), 2):
    r = relation(a, b)
    if not r or r.startswith('знак'): continue
    if lex_sites[a] & lex_sites[b]: continue
    n_pairs += 1
    print(f'   {"-".join(a):<20} @{",".join(sorted(lex_sites[a])):<8} ~ '
          f'{"-".join(b):<26} @{",".join(sorted(lex_sites[b])):<8} [{r}]')
print(f'итого межсайтовых аффиксных пар: {n_pairs}')
