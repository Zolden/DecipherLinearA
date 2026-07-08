# -*- coding: utf-8 -*-
"""Этап 21 (§CJ): остаток каталога разночтений §CA.

(а) Два случая «чтение-1», где нашего слова НЕ оказалось в сыром
translatedWords (§CF: 39/41) — найти и диагностировать.
(б) 79 corpus-слов класса «прочее» (нет в SigLA, автокласс не сработал):
раскладка по флагам повреждений/редким знакам — «SigLA прорисовывает
только уверенное» против «реальный пропуск чистого слова».
Вне стресс-ростера (читает corpus_raw.json).
"""
import sys, json, pickle
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

raw = json.load(open('corpus_raw.json', encoding='utf-8'))

def norm_word(s):
    return s.replace('₂', '2').replace('₃', '3').upper()

def raw_words(rid):
    r = raw.get(rid)
    if not r:
        return []
    return [norm_word(w) for w in r.get('translatedWords', [])
            if w.strip() and w != '\n']

corpus = pickle.load(open('corpus.pkl', 'rb'))
tok_by_doc = {}
for d in corpus:
    tok_by_doc[d['id']] = [v for k, v in d['toks'] if k == 'WORD'
                           and v['syllabic']]

# --- (а) два непроверенных «чтение-1»
print('(а) случаи «чтение-1» без слова в сыром источнике:')
for line in open('divergences.tsv', encoding='utf-8'):
    if line.startswith('doc\t'):
        continue
    doc, side, word, cl, match = line.rstrip('\n').split('\t')
    if cl != 'чтение-1' or side != 'corpus':
        continue
    rws = raw_words(doc)
    if not rws:
        for suf in 'ab':
            rws += raw_words(doc + suf)
    if word not in rws:
        near = [r for r in rws if abs(len(r) - len(word)) <= 3
                and r[:2] == word[:2]]
        print(f'   {doc}: {word}')
        print(f'      в raw похожие: {near or rws[:6]}')

# --- (б) corpus-«прочее»
others = []
for line in open('divergences.tsv', encoding='utf-8'):
    if line.startswith('doc\t'):
        continue
    doc, side, word, cl, match = line.rstrip('\n').split('\t')
    if cl == 'прочее' and side == 'corpus':
        others.append((doc, tuple(word.split('-'))))

cls = Counter()
examples = {}
for doc, w in others:
    toks = tok_by_doc.get(doc, [])
    for suf in 'ab':
        if not toks:
            toks = tok_by_doc.get(doc + suf, [])
    v = next((t for t in toks if tuple(t['signs']) == w), None)
    if v is None:
        cat = 'не найден (сторона/склейка)'
    elif v.get('gap') or v.get('trunc_l') or v.get('trunc_r') \
            or not v.get('complete', True):
        cat = 'повреждено/неполно'
    elif any(s.startswith('*') or '+' in s for s in w):
        cat = 'редкий/связанный знак'
    elif len(w) == 2:
        cat = 'чистое короткое (2 знака)'
    else:
        cat = 'чистое длинное — реальный пропуск SigLA'
    cls[cat] += 1
    examples.setdefault(cat, []).append((doc, '-'.join(w)))

print(f'\n(б) corpus-«прочее»: {len(others)} слов')
for cat, c in cls.most_common():
    ex = '; '.join(f'{d}:{w}' for d, w in examples[cat][:4])
    print(f'   {cat:<38} {c:>3}  [{ex}]')
print('''
Чтение: «повреждено/неполно» и «редкий знак» подтверждают гипотезу
«SigLA прорисовывает только уверенно читаемое»; класс «чистое длинное —
реальный пропуск» — истинный остаток для будущей сверки.''')
