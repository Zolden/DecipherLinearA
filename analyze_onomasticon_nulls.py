# -*- coding: utf-8 -*-
"""Этап 33 (§DQ): батарея нулей для подтверждённого ономастикона —
требование аудита №2 (INPUT_FROM_SOL): «минимум три заранее заявленных
нуля». Конечная точка та же, что в §DH (число точных LA-омографов >=3 в
слот-именах DĀMOS; наблюдаемо 6); варьируется ТОЛЬКО нуль-модель:

  Null-B   — исходный (пулы нач/сред/фин; §DH: p=0.0002);
  Null-LP  — пулы длина × точная позиция (строже сохраняет структуру);
  Null-MK  — марковский биграммный (цепь 1-го порядка по знакам лексикона,
             с началом/концом слова; длины сохранены);
  Null-PT  — плацебо-мишень: вместо слот-имён — случайные наборы НЕ-слотных
             слов DĀMOS того же размера и длинового профиля (сигнал должен
             ИСЧЕЗНУТЬ: p не мал, а наблюдаемое типично).
R=10000, seed=42. Устойчивость = вывод не зависит от выбора нуля.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

NS = set()
for line in open('damos_name_slots.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        NS.add(tuple(line.split('\t')[0].split('-')))
LEX_D = {}
for line in open('damos_lexicon.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        p = line.rstrip('\n').split('\t')
        LEX_D[tuple(p[0].split('-'))] = int(p[1])
NONNS = [w for w in LEX_D if w not in NS]

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words = sorted(lex)
lengths = [len(w) for w in words]

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s:
            return None
        out.append(s.lower())
    return tuple(out)

def stat(word_list, target):
    return sum(1 for w in word_list
               if len(w) >= 3 and read_lb(w) in target)

OBS = stat(words, NS)
print(f'конечная точка (§DH): наблюдаемо {OBS} слот-омографов >=3')

# --- Null-B (грубые пулы)
poolsB = {0: [], 1: [], 2: []}
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        poolsB[j].append(s)

def gen_B():
    for p in poolsB.values():
        random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = []
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(poolsB[j][idx[j]]); idx[j] += 1
        out.append(tuple(w))
    return out

# --- Null-LP (длина × точная позиция)
poolsLP = defaultdict(list)
for w in words:
    for i, s in enumerate(w):
        poolsLP[(len(w), i)].append(s)

def gen_LP():
    sh = {k: random.sample(v, len(v)) for k, v in poolsLP.items()}
    idx = {k: 0 for k in poolsLP}
    out = []
    for L in lengths:
        w = []
        for i in range(L):
            k = (L, i)
            w.append(sh[k][idx[k]]); idx[k] += 1
        out.append(tuple(w))
    return out

# --- Null-MK (марковская цепь 1-го порядка)
START = '<'
END = '>'
trans = defaultdict(Counter)
for w in words:
    prev = START
    for s in w:
        trans[prev][s] += 1
        prev = s
    trans[prev][END] += 1
tkeys = {k: list(v.keys()) for k, v in trans.items()}
twts = {k: list(v.values()) for k, v in trans.items()}

def gen_MK():
    out = []
    for L in lengths:
        for _try in range(50):
            w = []
            prev = START
            ok = True
            for i in range(L):
                ks = tkeys.get(prev)
                if not ks:
                    ok = False
                    break
                s = random.choices(ks, weights=twts[prev])[0]
                if s == END:
                    ok = False
                    break
                w.append(s)
                prev = s
            if ok:
                out.append(tuple(w))
                break
        else:
            out.append(tuple(random.choices(list(lex), k=1)[0]))
    return out

def run_null(gen, label):
    sims = []
    for _ in range(R):
        sims.append(stat(gen(), NS))
    mu = sum(sims) / R
    sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
    p = (sum(1 for x in sims if x >= OBS) + 1) / (R + 1)
    print(f'{label:<10} нуль {mu:.2f}±{sd:.2f}, p={p:.4f}')
    return p

print()
run_null(gen_B, 'Null-B')
run_null(gen_LP, 'Null-LP')
run_null(gen_MK, 'Null-MK')

# --- Null-PT (плацебо-мишень)
by_len = defaultdict(list)
for w in NONNS:
    by_len[len(w)].append(w)
ns_lens = Counter(len(w) for w in NS)
sims = []
for _ in range(R):
    placebo = set()
    for L, c in ns_lens.items():
        pool = by_len.get(L, [])
        if len(pool) >= c:
            placebo.update(random.sample(pool, c))
        else:
            placebo.update(pool)
    sims.append(stat(words, placebo))
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
ge = sum(1 for x in sims if x >= OBS)
print(f'{"Null-PT":<10} плацебо-мишени дают {mu:.2f}±{sd:.2f} попаданий; '
      f'P(плацебо >= {OBS}) = {(ge + 1) / (R + 1):.4f} '
      f'(сигнал специфичен слот-именам, если мало)')
print('''
Чтение: если p мал при B/LP/MK и наблюдаемое НЕтипично для плацебо-мишеней,
конечная точка §DH устойчива к выбору нуля и специфична именно слот-именам
(требование аудита №2 выполнено).''')
