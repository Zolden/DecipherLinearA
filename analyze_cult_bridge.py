# -*- coding: utf-8 -*-
"""Этап 14 (§BL): мостик регистров — общие слова «дозовых списков» (§BH)
и религиозной сети (камни возлияний, §AS).

Словарь 9 документов класса HT23a против словаря rel-документов: пересечение,
и контроль — насколько часто случайные 9 табличек дают такое же пересечение
(перестановка, R=10000).
"""
import sys, pickle, random
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
KLASS = ['HT100', 'HT140', 'HT21', 'HT23a', 'HT35', 'HT50a', 'HT91', 'KH12', 'TY3a']

def words_of(d):
    return {v['norm'] for k, v in d['toks']
            if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2
            and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r'])}

rel_vocab = set()
for d in corpus:
    if d['typ'] == 'rel': rel_vocab |= words_of(d)
tablets = [d for d in corpus if d['is_tablet']]
klass_docs = [d for d in tablets if d['id'] in KLASS]
klass_vocab = set()
for d in klass_docs: klass_vocab |= words_of(d)
inter = klass_vocab & rel_vocab
print(f'словарь класса HT23a: {len(klass_vocab)} слов; словарь rel: {len(rel_vocab)}')
print(f'пересечение: {len(inter)}: {sorted(inter)}')

sizes = [len(words_of(d)) for d in klass_docs]
ge = 0; ms = []
pool = [d for d in tablets]
for _ in range(R):
    samp = random.sample(pool, len(KLASS))
    v = set()
    for d in samp: v |= words_of(d)
    n = len(v & rel_vocab)
    ms.append(n)
    if n >= len(inter): ge += 1
m = sum(ms) / R
print(f'нуль (случайные {len(KLASS)} табличек): {m:.2f}, p={ge / R:.4f}')
