# -*- coding: utf-8 -*-
"""Этап 12.3 (§BA): SA-SA-RA вглубь — хвосты по позициям формулы; HT23a.

1. Для каждого вхождения формы SA-SA-*: позиция в формуле (слот по движку
   §AX), позиция в документе (порядковый номер слова), носитель, сайт.
   Вопрос: коррелируют ли хвосты (-ME / -MA-NA / ∅) с чем-то измеримым?
2. HT23a: полный текст, место SA-SA-ME, числа, соседи — омоним или теоним?
"""
import sys, pickle
from collections import defaultdict
from formula_template import assign

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

print('=== формы SA-SA-* в контексте формулы ===')
print(f'{"форма":<26}{"док":<10}{"слот":>4}{"поз":>4}{"из":>3}  хвост')
for d in corpus:
    words = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if not any('SA-SA' in w for w in words): continue
    slots = dict(assign(words)) if d['typ'] == 'rel' else {}
    for i, w in enumerate(words):
        if 'SA-SA' not in w: continue
        sg = w.split('-')
        idx = next(j for j in range(len(sg) - 1)
                   if sg[j] == 'SA' and sg[j + 1] == 'SA')
        core_end = idx + 2
        if core_end < len(sg) and sg[core_end] in ('RA', '*802'): core_end += 1
        tail = '-'.join(sg[core_end:]) or '∅'
        print(f'{w:<26}{d["id"]:<10}{slots.get(w, "-"):>4}{i + 1:>4}{len(words):>3}  {tail}')

# --- HT23a целиком
print('\n=== HT23a целиком ===')
for d in corpus:
    if d['id'] != 'HT23a': continue
    out = []
    for k, v in d['toks']:
        if k == 'WORD': out.append(v['norm'])
        elif k == 'NUM': out.append(str(v['val']))
        elif k == 'LB': out.append('/')
        elif k == 'DIV': out.append('•')
    print(' '.join(out))
    # контекст SA-SA-ME
    toks = d['toks']
    for i, (k, v) in enumerate(toks):
        if k == 'WORD' and v['norm'] == 'SA-SA-ME':
            nval = None
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM': nval = toks[j][1]['val']; break
                if toks[j][0] != 'DIV': break
            prev = next((toks[j][1]['norm'] for j in range(i - 1, -1, -1)
                         if toks[j][0] == 'WORD'), None)
            print(f'SA-SA-ME: число после = {nval}, перед ним «{prev}»')
