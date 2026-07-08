# -*- coding: utf-8 -*-
"""Этап 18 (§BX): ономастикон v9 — «почти-омографы» (расстояние Хэмминга 1).

Точные омографы длины >=4 исчерпаны (3, p<0.0001, §BT). Вопрос: даёт ли
допуск в ОДИН знак (та же длина, одна позиция расходится) значимый прирост
совпадений с union слот-имён LB — как ожидалось бы, если часть имён
записана с орфографической вариацией (l/r, вокализация, знаки-серии).

Только длина >=4 (для длины 3 допуск в 1 знак из 3 создаёт огромное
пространство ложных попаданий). Нуль: Null-B (позиционная перетасовка,
gen_B как в v6–v8), R=10000, seed=42. Точные совпадения исключаются из
«почти»-счёта (считаются отдельно, они = v8).
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

NS = set()
for fn in ('lb_name_slots.tsv', 'lb2_name_slots.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            NS.add(tuple(line.split('\t')[0].split('-')))
print(f'union слот-имён: {len(NS)}')

# вайлдкард-индекс: (len, pos, слово-без-позиции) -> имена
wc = defaultdict(set)
for nm in NS:
    L = len(nm)
    if L < 4:
        continue
    for i in range(L):
        wc[(L, i, nm[:i] + nm[i + 1:])].add(nm)

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); lex_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1; lex_docs[w].add(d['id'])
words = sorted(lex)
lengths = [len(w) for w in words]

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s:
            return None
        out.append(s.lower())
    return tuple(out)

def near_names(r):
    """Имена на Хэмминге ровно 1 от чтения r (длина >=4)."""
    L = len(r)
    out = set()
    for i in range(L):
        out |= wc.get((L, i, r[:i] + r[i + 1:]), set())
    out.discard(r)
    return out

exact = []
near = []
for w in words:
    if len(w) < 4:
        continue
    r = read_lb(w)
    if r is None:
        continue
    if r in NS:
        exact.append((w, r))
    else:
        nn = near_names(r)
        if nn:
            near.append((w, r, nn))
print(f'\nLA-слов длины >=4 (полных): '
      f'{sum(1 for w in words if len(w) >= 4)}')
print(f'точных слот-совпадений >=4 (=v8): {len(exact)} '
      f'{[("-".join(r)) for _, r in exact]}')
print(f'почти-омографов (Хэмминг=1, не точных): {len(near)}')
for w, r, nn in sorted(near, key=lambda x: -lex[x[0]])[:15]:
    ex = sorted(nn)[:2]
    print(f'   {"-".join(w):<20} LA×{lex[w]} ~ '
          f'{"; ".join("-".join(x) for x in ex)}'
          f'{" +" + str(len(nn) - 2) if len(nn) > 2 else ""}')

# нуль
pos_pools = {0: [], 1: [], 2: []}
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)

def gen_B():
    for p in pos_pools.values():
        random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = []
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.append(tuple(w))
    return out

ce = []; cn = []
for _ in range(R):
    wl = gen_B()
    ne = nn_ = 0
    for w in wl:
        if len(w) < 4:
            continue
        r = read_lb(w)
        if r is None:
            continue
        if r in NS:
            ne += 1
        elif near_names(r):
            nn_ += 1
    ce.append(ne); cn.append(nn_)
for label, obs, cc in [('точные >=4', len(exact), ce),
                       ('почти (Хэмминг=1) >=4', len(near), cn)]:
    m = sum(cc) / R
    sd = (sum((x - m) ** 2 for x in cc) / R) ** 0.5
    p = sum(1 for x in cc if x >= obs) / R
    print(f'{label}: наблюдаемо {obs}, нуль {m:.2f}±{sd:.2f}, p={p:.4f}')
print('''
Чтение: p разведочные. «Почти»-слой без значимости НЕ добавляет якорей —
допусковые совпадения используются только как кандидатный список для
будущей точечной проверки контекстов, не как подтверждения.''')
