# -*- coding: utf-8 -*-
"""Этап 17 (§BT): ономастикон v8 — объединение слот-имён двух независимых
оцифровок LB + разведка двусловных последовательностей.

v8-a: длина-стратифицированный тест LA×(lb1 ∪ lb2 лексиконы) и
слот-подтверждение против union слот-имён (Null-B, R=10000, seed=42) —
максимальная мощность на всём, что у нас есть.
v8-b: двусловные последовательности: соседние пары полных слоговых слов LA,
обе части которых читаются в union-лексикон LB / union-слот-имена
(разведочный подсчёт с приблизительным ожиданием).
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

LB = set()
for fn in ('lb_lexicon.tsv', 'lb2_lexicon.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            LB.add(tuple(line.split('\t')[0].split('-')))
NS = set()
for fn in ('lb_name_slots.tsv', 'lb2_name_slots.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            NS.add(tuple(line.split('\t')[0].split('-')))
print(f'union лексикон LB: {len(LB)}; union слот-имён: {len(NS)} '
      f'(слот-имена ⊂ лексикон: {len(NS - LB)} вне)')
LB |= NS

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); lex_docs = defaultdict(set)
doc_seqs = []
for d in corpus:
    seq = []
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1; lex_docs[w].add(d['id'])
            seq.append(w)
        else:
            seq.append(None)       # разрыв смежности на любом другом токене
    doc_seqs.append(seq)
words = sorted(lex)

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s:
            return None
        out.append(s.lower())
    return tuple(out)

# ---------- v8-a
hits = [(w, read_lb(w)) for w in words if read_lb(w) in LB]
long_hits = [(w, r) for w, r in hits if len(w) >= 3]
slot_long = [(w, r) for w, r in long_hits if r in NS]
print(f'\nсовпадений всего: {len(hits)}; длинных >=3: {len(long_hits)}; '
      f'из них в union слот-именах: {len(slot_long)}')
for w, r in sorted(long_hits, key=lambda x: -len(x[0])):
    tag = ' [СЛОТ-ИМЯ]' if r in NS else ''
    print(f'   {"-".join(r):<18} len={len(w)} LA×{lex[w]} '
          f'{sorted(lex_docs[w])[:3]}{tag}')

lengths = [len(w) for w in words]
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

c3 = []; c4 = []; cs = []
for _ in range(R):
    wl = gen_B()
    n3 = n4 = ns_ = 0
    for w in wl:
        r = read_lb(w)
        if r and r in LB:
            if len(w) == 3: n3 += 1
            if len(w) >= 4: n4 += 1
            if len(w) >= 3 and r in NS: ns_ += 1
    c3.append(n3); c4.append(n4); cs.append(ns_)
obs3 = sum(1 for w, _ in long_hits if len(w) == 3)
obs4 = sum(1 for w, _ in long_hits if len(w) >= 4)
for label, obs, cc in [('длина 3', obs3, c3), ('длина >=4', obs4, c4),
                       ('слот-имена >=3', len(slot_long), cs)]:
    m = sum(cc) / R
    sd = (sum((x - m) ** 2 for x in cc) / R) ** 0.5
    p = sum(1 for x in cc if x >= obs) / R
    print(f'{label}: наблюдаемо {obs}, нуль {m:.2f}±{sd:.2f}, p={p:.4f}')

# ---------- v8-b: двусловные
print('\n=== v8-b: соседние пары, обе части в LB-union ===')
match = {w for w, _ in hits}
pairs_seen = []
n_pairs = 0
for seq in doc_seqs:
    for a, b in zip(seq, seq[1:]):
        if a and b:
            n_pairs += 1
            if a in match and b in match:
                pairs_seen.append((a, b))
p1 = len(match) and sum(lex[w] for w in match) / sum(lex.values())
print(f'смежных пар полных слов: {n_pairs}; токен-доля слов-совпадений: '
      f'{p1:.3f}; грубое ожидание пар: {n_pairs * p1 * p1:.1f}; '
      f'наблюдаемо: {len(pairs_seen)}')
for a, b in pairs_seen[:10]:
    ra, rb = read_lb(a), read_lb(b)
    ta = '[СЛОТ]' if ra in NS else ''
    tb = '[СЛОТ]' if rb in NS else ''
    print(f'   {"-".join(a)}{ta} + {"-".join(b)}{tb}')
print('''
Чтение: v8-a — Null-B как в v6/v7, p разведочные; v8-b — грубый подсчёт
(ожидание в предположении независимости соседей, без нуль-модели пар),
короткие слова доминируют — интерпретировать осторожно.''')
