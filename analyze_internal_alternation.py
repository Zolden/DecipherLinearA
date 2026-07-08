# -*- coding: utf-8 -*-
"""Этап 20 (§CE): внутриминойские пары чередования финальной гласной.

TA-NA-TE (ZA10a) и TA-NA-TI (HT) — пара LA↔LA, различающаяся только
гласной финала той же строки. Если таких пар больше случайного, финальная
гласная варьирует ВНУТРИ минойского (морфология/диалект), и правило §BZ
(LA -u/-e/-a ↔ LB -o) может быть не только греческой адаптацией.
Родствен §C (чередования на общей основе делят согласную, p=0.0018);
здесь — строго «та же строка, другая гласная» с собственным нулём.

Статистика: число НЕупорядоченных пар слов LA (len>=3, полные),
идентичных всюду кроме гласной финала (строка и субскрипт совпадают);
нуль gen_B (R=10000, seed=42). Инвентарь гласных пар сравнивается с
адаптационным набором §BZ.
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

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

SIGN_RE = re.compile(r'^([DJKMNPQRSTWZ]{0,2})([AEIOU])([23]?)$')

def split_final(w):
    m = SIGN_RE.fullmatch(w[-1])
    if not m:
        return None
    return w[:-1], m.group(1), m.group(2), m.group(3)

def count_pairs(word_list):
    groups = defaultdict(set)          # (stem, row, sub) -> {vowels}
    for w in word_list:
        if len(w) < 3:
            continue
        sp = split_final(w)
        if sp:
            stem, row, v, sub = sp
            groups[(stem, row, sub)].add(v)
    npairs = 0
    vow_pairs = Counter()
    plist = []
    for (stem, row, sub), vs in groups.items():
        vs = sorted(vs)
        if len(vs) >= 2:
            for i in range(len(vs)):
                for j in range(i + 1, len(vs)):
                    npairs += 1
                    vow_pairs[(vs[i], vs[j])] += 1
                    plist.append((stem, row, sub, vs[i], vs[j]))
    return npairs, vow_pairs, plist

obs_n, obs_vp, obs_list = count_pairs(words)
print(f'внутриминойских пар финального чередования: {obs_n}')
for stem, row, sub, v1, v2 in sorted(obs_list):
    w1 = stem + (row + v1 + sub,)
    w2 = stem + (row + v2 + sub,)
    print(f'   {"-".join(w1):<20} ~ {"-".join(w2):<20} '
          f'({sorted(lex_docs[w1])[:2]} | {sorted(lex_docs[w2])[:2]})')
print('инвентарь гласных пар:', dict(obs_vp.most_common()))

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

sims = []
for _ in range(R):
    n, _v, _l = count_pairs(gen_B())
    sims.append(n)
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
p = sum(1 for x in sims if x >= obs_n) / R
print(f'\nнуль: {mu:.2f}±{sd:.2f}, p={p:.4f}')
print('''
Чтение: p разведочное. Значимый избыток = финальная гласная варьирует
внутри LA (морфологический слот финала); сопоставить инвентарь пар с
§BZ (-u/-e/-a → -o): совпадение инвентарей поддержало бы «внутреннюю»
интерпретацию правила, дизъюнктность — адаптационную.''')
