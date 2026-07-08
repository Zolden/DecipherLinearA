# -*- coding: utf-8 -*-
"""Этап 14 (§BJ, часть 2): ономастикон v6 и турнир значений на полном LB
(linearb.xyz, 5832 док., 4791 тип слова, 1638 слот-имён).

V6-a: длина-стратифицированный тест LA×lb2 (Null-B, R=10000);
V6-b: строгий слот-тест (длинные >=3);
V6-c: перезапуск подстановочного турнира для *118/*301/*306 на lb2;
V6-d: кроссворд-голоса v2 (шаблоны с одним неизвестным знаком против lb2).
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

lb2 = {}
for line in open('lb2_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    w, c, sites, nd = line.rstrip('\n').split('\t')
    lb2[tuple(w.split('-'))] = int(c)
LB2 = set(lb2)
NS2 = set()
for line in open('lb2_name_slots.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        NS2.add(tuple(line.split('\t')[0].split('-')))
print(f'lb2: {len(LB2)} слов; слот-имён {len(NS2)}')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); lex_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1; lex_docs[w].add(d['id'])
words = sorted(lex)

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s: return None
        out.append(s.lower())
    return tuple(out)

# ---------- V6-a/b
hits = [(w, read_lb(w)) for w in words if read_lb(w) in LB2]
long_hits = [(w, r) for w, r in hits if len(w) >= 3]
slot_long = [(w, r) for w, r in long_hits if r in NS2]
print(f'\nсовпадений всего: {len(hits)}; длинных >=3: {len(long_hits)}; '
      f'из них в слот-именах: {len(slot_long)}')
for w, r in sorted(long_hits, key=lambda x: -len(x[0])):
    tag = ' [СЛОТ-ИМЯ]' if r in NS2 else ''
    print(f'   {"-".join(r):<18} len={len(w)} LA×{lex[w]} '
          f'{sorted(lex_docs[w])[:3]}{tag}')

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
c3 = []; c4 = []; cs = []
for _ in range(R):
    wl = gen_B()
    n3 = n4 = ns = 0
    for w in wl:
        r = read_lb(w)
        if r and r in LB2:
            if len(w) == 3: n3 += 1
            if len(w) >= 4: n4 += 1
            if len(w) >= 3 and r in NS2: ns += 1
    c3.append(n3); c4.append(n4); cs.append(ns)
obs3 = sum(1 for w, _ in long_hits if len(w) == 3)
obs4 = sum(1 for w, _ in long_hits if len(w) >= 4)
for label, obs, cc in [('длина 3', obs3, c3), ('длина >=4', obs4, c4),
                       ('слот-имена >=3', len(slot_long), cs)]:
    m = sum(cc) / R
    sd = (sum((x - m) ** 2 for x in cc) / R) ** 0.5
    p = sum(1 for x in cc if x >= obs) / R
    print(f'{label}: наблюдаемо {obs}, нуль {m:.2f}±{sd:.2f}, p={p:.4f}')

# ---------- V6-c: турнир значений
LA_SIGNS = {'A','E','I','O','U','DA','DE','DI','DU','JA','JE','JU','KA','KE',
            'KI','KO','KU','MA','ME','MI','MU','NA','NE','NI','NU','PA','PE',
            'PI','PO','PU','QA','QE','QI','RA','RE','RI','RO','RU','SA','SE',
            'SI','SU','TA','TE','TI','TO','TU','WA','WI','ZA','ZE','ZO','ZU'}
CONS = set('djkmnpqrstwz')
row_freq = Counter(); tot_syl = 0
for w in LB2:
    for s in w:
        m = re.fullmatch(r'([a-z]?)([aeiou])[23]?', s)
        if m:
            row_freq[m.group(1) or '∅'] += 1; tot_syl += 1
print('\n=== турнир значений на lb2 (нормировка на частоту ряда) ===')
def is_unknown(s): return s.startswith('*') or '+' in s
for target in ('*118', '*301', '*306', '*21F'):
    words_t = [w for w in words if target in w]
    scores = []
    for row in ['∅'] + sorted(CONS):
        hits_n = 0; det = []
        for vow in 'aeiou':
            syl = (row if row != '∅' else '') + vow
            if syl.upper() not in LA_SIGNS: continue
            for w in words_t:
                cand = tuple(syl if s == target else s.lower() for s in w)
                if any(is_unknown(x.upper()) or x.startswith('*') for x in cand):
                    continue
                if cand in LB2:
                    hits_n += 1
                    det.append(f'{"-".join(w)}→{"-".join(cand)}')
        f = row_freq.get(row, 0) / tot_syl
        if hits_n and f > 0:
            scores.append((hits_n / f, hits_n, row, det))
    scores.sort(reverse=True)
    print(f'{target} ({len(words_t)} слов): ' + '; '.join(
        f'{row}: {h} попад. (норм {ratio:.0f}) [{det[0] if det else ""}]'
        for ratio, h, row, det in scores[:4]))
