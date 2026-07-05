# -*- coding: utf-8 -*-
"""Этап 6, п.8 (§O): репликация морфологических маркеров по срезам корпуса.

Вопрос: маркеры второго эшелона (§L: -RO, -ME; DA-, SI-, QE-, KI-, PI-) — не
случайные ли лидеры одного архива? Тест: поддержка маркера считается отдельно
в срезе HT (Айя-Триада, самый большой архив) и в срезе НЕ-HT; нуль-калибровка
(Null-B, позиционно-стратифицированная перестановка, R=2000) в каждом срезе.
Маркер «реплицируется», если его поддержка значима (p<0.05) в обоих срезах.
Мощность среза не-HT мала — отсутствие репликации не приговор, а статус
«не подтверждено на независимом материале».
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
R = 2000

corpus = pickle.load(open('corpus.pkl', 'rb'))

def build_lex(pred):
    lex = Counter()
    for d in corpus:
        if not pred(d): continue
        for k, v in d['toks']:
            if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
               and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
                lex[tuple(v['signs'])] += 1
    return lex

SPLITS = {
    'HT': build_lex(lambda d: d['site'] == 'HT'),
    'не-HT': build_lex(lambda d: d['site'] != 'HT'),
    'весь': build_lex(lambda d: True),
}
for name, lx in SPLITS.items():
    print(f'{name}: {len(lx)} типов / {sum(lx.values())} токенов')

def supports(word_set):
    suf = defaultdict(set); pre = defaultdict(set)
    for w in word_set:
        if len(w) - 1 >= 2:
            suf[w[-1]].add(w[:-1]); pre[w[0]].add(w[1:])
    out_s = {}
    for S, stems in suf.items():
        good = {T for T in stems if T in word_set or
                any(T in st for S2, st in suf.items() if S2 != S)}
        if good: out_s[S] = len(good)
    out_p = {}
    for P, tails in pre.items():
        good = {T for T in tails if T in word_set or
                any(T in t2 for P2, t2 in pre.items() if P2 != P)}
        if good: out_p[P] = len(good)
    return out_s, out_p

def null_machine(lex):
    words_list = sorted(lex)
    lengths = [len(w) for w in words_list]
    pools = {0: [], 1: [], 2: []}
    for w in words_list:
        for i, s in enumerate(w):
            j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
            pools[j].append(s)
    def gen():
        for p in pools.values(): random.shuffle(p)
        idx = {0: 0, 1: 0, 2: 0}; out = set()
        for L in lengths:
            w = []
            for i in range(L):
                j = 0 if i == 0 else (2 if i == L - 1 else 1)
                w.append(pools[j][idx[j]]); idx[j] += 1
            out.add(tuple(w))
        return out
    return gen

MARKERS_S = ['JA', 'RO', 'ME', 'TE', 'RA', 'TI', 'TA']
MARKERS_P = ['A', 'DA', 'SI', 'QE', 'KI', 'PI', 'JA', 'I']

results = {}
for name, lx in SPLITS.items():
    random.seed(42)
    ws = set(lx)
    obs_s, obs_p = supports(ws)
    gen = null_machine(lx)
    null_s = defaultdict(list); null_p = defaultdict(list)
    for _ in range(R):
        ns, np_ = supports(gen())
        for m in MARKERS_S: null_s[m].append(ns.get(m, 0))
        for m in MARKERS_P: null_p[m].append(np_.get(m, 0))
    res = {}
    for m in MARKERS_S:
        o = obs_s.get(m, 0)
        p = sum(1 for x in null_s[m] if x >= o) / R if o else 1.0
        res[('suf', m)] = (o, p)
    for m in MARKERS_P:
        o = obs_p.get(m, 0)
        p = sum(1 for x in null_p[m] if x >= o) / R if o else 1.0
        res[('pre', m)] = (o, p)
    results[name] = res

print(f'\n{"маркер":<10}' + ''.join(f'{n:>16}' for n in SPLITS))
print(f'{"":<10}' + ''.join(f'{"осн. (p)":>16}' for _ in SPLITS))
for kind, ms in [('suf', MARKERS_S), ('pre', MARKERS_P)]:
    for m in ms:
        lab = ('-' + m) if kind == 'suf' else (m + '-')
        row = f'{lab:<10}'
        for name in SPLITS:
            o, p = results[name][(kind, m)]
            row += f'{o:>8} ({p:.3f})'
        # вердикт репликации
        pht = results['HT'][(kind, m)][1]
        pnh = results['не-HT'][(kind, m)][1]
        verdict = ' РЕПЛ.' if (pht < 0.05 and pnh < 0.05) else \
                  (' только HT' if pht < 0.05 else
                   (' только не-HT' if pnh < 0.05 else ''))
        print(row + verdict)
