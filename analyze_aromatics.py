# -*- coding: utf-8 -*-
"""Этап 13, п.5 (§BH): класс HT23a — «дозовые списки масел/ароматики».

Критерий класса (структурный, без чтений): в документе (а) >=2 РАЗНЫХ
OLE+X-лигатуры ИЛИ >=1 из {AROM, MI+JA+RU} и (б) >=3 дробных значения.
Каталог документов класса, их признаки (сайты, размер, кванты, слова рядом),
пересечение с религиозным регистром и SA-SA-ME-вопросом (§BA).
"""
import sys, pickle
from fractions import Fraction
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

def doc_props(d):
    toks = d['toks']
    ole = set(); mark = False
    fracs = []
    words = []
    for i, (k, v) in enumerate(toks):
        if k == 'WORD':
            n = v['norm']
            if not v['syllabic']:
                if n.startswith('OLE+'): ole.add(n)
                if n in ('AROM', 'MI+JA+RU') or n.startswith('AROM'):
                    mark = True
            else:
                words.append(n)
            if n in ('MI+JA+RU',): mark = True
        elif k == 'NUM':
            if v['val'] != int(v['val']): fracs.append(v['val'])
    return ole, mark, fracs, words

klass = []
for d in corpus:
    if not d['is_tablet']: continue
    ole, mark, fracs, words = doc_props(d)
    if (len(ole) >= 2 or mark) and len(fracs) >= 3:
        klass.append((d, ole, fracs, words))

print(f'=== класс «дозовых списков»: {len(klass)} документов ===')
for d, ole, fracs, words in sorted(klass, key=lambda x: x[0]['id']):
    dens = sorted({f.denominator for f in fracs})
    print(f'\n{d["id"]:<10} {d["site"]:<4} лигатур OLE+ {len(ole)} '
          f'({",".join(sorted(ole))}); дробей {len(fracs)}, знаменатели {dens}')
    print(f'   слова: {", ".join(words[:10])}')

# сводка
sites = Counter(d['site'] for d, _, _, _ in klass)
all_words = Counter()
for _, _, _, ws in klass:
    for w in ws: all_words[w] += 1
print(f'\nсайты класса: {dict(sites)}')
print('слова, повторяющиеся в классе (>=2 док.):',
      [(w, c) for w, c in all_words.most_common(12) if c >= 2])
