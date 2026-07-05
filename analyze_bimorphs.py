# -*- coding: utf-8 -*-
"""Этап 13, п.7 (§BI): биморфы — класс «свободный + связанный» систематически.

Биморф = двузнаковая последовательность X, которая (а) встречается как
самостоятельное слово (free >= 1), (б) входит в >= 2 более длинных слова
(префиксом или финалью). Прототипы: I-DA (§AK), PU2-RE (§X), A-DU (§AQ).
Калибровка: сколько биморфов даёт Null-B-лексикон (R=1000); наблюдаемый
список с регистрами (доля rel) и «валентностью» (префикс/финаль).
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 1000

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); meta = defaultdict(list)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1
            meta[w].append((d['site'], d['typ']))
WORDS = set(lex)
words_list = sorted(lex)

def bimorphs(word_set, counts=None):
    out = {}
    two = [w for w in word_set if len(w) == 2]
    for x in two:
        pre = sum(1 for w in word_set if len(w) > 2 and w[:2] == x)
        suf = sum(1 for w in word_set if len(w) > 2 and w[-2:] == x)
        if pre + suf >= 2:
            out[x] = (counts.get(x, 1) if counts else 1, pre, suf)
    return out

obs = bimorphs(WORDS, lex)
print(f'=== наблюдаемые биморфы (free>=1, расширений >=2): {len(obs)} ===')
print(f'{"биморф":<10}{"free":>5}{"преф":>5}{"фин":>5}{"rel%":>6}  расширения (примеры)')
for x, (fr, pre, suf) in sorted(obs.items(), key=lambda kv: -(kv[1][0] * (kv[1][1] + kv[1][2]))):
    ms = meta[x]
    rel = sum(1 for _, t in ms if t == 'rel') / len(ms) if ms else 0
    exts = [w for w in WORDS if len(w) > 2 and (w[:2] == x or w[-2:] == x)]
    ex = ', '.join('-'.join(w) for w in sorted(exts)[:3])
    print(f'{"-".join(x):<10}{fr:>5}{pre:>5}{suf:>5}{rel:>6.0%}  {ex}')

# калибровка Null-B
lengths = [len(w) for w in words_list]
pos_pools = {0: [], 1: [], 2: []}
for w in words_list:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)
def gen_B():
    for p in pos_pools.values(): random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = set()
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.add(tuple(w))
    return out
null_n = []
for _ in range(R):
    null_n.append(len(bimorphs(gen_B())))
m = sum(null_n) / R
sd = (sum((x - m) ** 2 for x in null_n) / R) ** 0.5
p = sum(1 for x in null_n if x >= len(obs)) / R
print(f'\nнуль (Null-B, R={R}): {m:.1f}±{sd:.1f} биморфов; наблюдаемо {len(obs)}, '
      f'p={p:.4f}')
print('интерпретация: избыток биморфов = слова-элементы, реально живущие и '
      'свободно, и в составе длинных слов (композиция/деривация).')
