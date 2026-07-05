# -*- coding: utf-8 -*-
"""Этап 8.8 (§AF): каталог минимальных контрастов.

(а) ВНУТРИдокументные пары одной основы: два слова в одном документе, связанные
    приставкой (w2 = P+w1), суффиксом (w2 = w1+S, |S|<=2) или заменой одного
    знака (Хэмминг-1). Это будущие тесты грамматики «в одном контексте».
(б) МЕЖсайтовые дублеты: те же связи между словами, чьи множества сайтов НЕ
    пересекаются (кандидаты «локальное оформление одной основы»).
Сводные счётчики: сколько аффиксных пар документо-дизъюнктны.
"""
import sys, pickle, itertools
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

lex_docs = defaultdict(set); lex_sites = defaultdict(set); lex = Counter()
doc_words = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1
            lex_docs[w].add(d['id']); lex_sites[w].add(d['site'])
            doc_words[d['id']].add(w)
WORDS = set(lex)

def relation(a, b):
    """тип связи между словами или None."""
    if len(a) == len(b):
        diff = [i for i in range(len(a)) if a[i] != b[i]]
        if len(diff) == 1: return f'знак@{diff[0]}'
        return None
    if len(b) - len(a) in (1, 2):
        a, b = a, b
    elif len(a) - len(b) in (1, 2):
        a, b = b, a
    else:
        return None
    if b[:len(a)] == a: return f'+{"-".join(b[len(a):])}'
    if b[-len(a):] == a: return f'{"-".join(b[:len(b) - len(a)])}+'
    return None

# ---------------- (а) внутридокументные
print('=== (а) минимальные контрасты внутри одного документа ===')
n_intra = 0
for doc, ws in sorted(doc_words.items()):
    ws = sorted(ws)
    for a, b in itertools.combinations(ws, 2):
        r = relation(a, b)
        if r:
            n_intra += 1
            print(f'   {doc:<12} {"-".join(a):<20} ~ {"-".join(b):<24} [{r}]')
print(f'итого внутридокументных пар: {n_intra}')

# ---------------- (б) межсайтовые дублеты
print('\n=== (б) связанные пары с НЕпересекающимися сайтами ===')
n_cross = 0
pairs_seen = set()
for a, b in itertools.combinations(sorted(WORDS), 2):
    r = relation(a, b)
    if not r: continue
    if lex_sites[a] & lex_sites[b]: continue
    key = (a, b)
    if key in pairs_seen: continue
    pairs_seen.add(key)
    n_cross += 1
    if n_cross <= 40:
        print(f'   {"-".join(a):<20} {",".join(sorted(lex_sites[a])):<8} ~ '
              f'{"-".join(b):<24} {",".join(sorted(lex_sites[b])):<8} [{r}]')
print(f'итого межсайтовых связанных пар: {n_cross}')

# ---------------- сводка по аффиксным парам: дизъюнктность документов
aff_pairs = []
for a, b in itertools.combinations(sorted(WORDS), 2):
    r = relation(a, b)
    if r and r.startswith('+') or (r and r.endswith('+')):
        aff_pairs.append((a, b, r))
n_disj = sum(1 for a, b, _ in aff_pairs if not (lex_docs[a] & lex_docs[b]))
n_site_disj = sum(1 for a, b, _ in aff_pairs if not (lex_sites[a] & lex_sites[b]))
print(f'\nаффиксных пар всего: {len(aff_pairs)}; документо-дизъюнктных: '
      f'{n_disj} ({n_disj / max(1, len(aff_pairs)):.0%}); '
      f'сайто-дизъюнктных: {n_site_disj} ({n_site_disj / max(1, len(aff_pairs)):.0%})')
# фон: ожидание сайто-дизъюнктности для случайных пар слов тех же частот
import random
random.seed(42)
allw = sorted(WORDS)
disj_bg = 0; trials = 20000
for _ in range(trials):
    a, b = random.sample(allw, 2)
    disj_bg += not (lex_sites[a] & lex_sites[b])
print(f'фон (случайные пары слов): сайто-дизъюнктных {disj_bg / trials:.0%}')
