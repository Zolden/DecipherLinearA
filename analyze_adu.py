# -*- coding: utf-8 -*-
"""Этап 10.4 (§AO): A-DU — учётный элемент (протокол I-DA/PU2-RE).

A-DU — лидер профиля «свободное слово × расширения» (§AK): свободно ×7,
префикс 3 слов. Досье: все вхождения A-DU и A-DU-* с контекстами (позиция,
число, логограммы рядом, KU-RO-окно); сравнение с I-DA (религиозный элемент):
регистры, сайты; связь с гипотезой «заголовочный термин» (шорт-лист §H).
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

print('=== все вхождения A-DU и A-DU-* ===')
fam_docs = []
for d in corpus:
    toks = d['toks']
    widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
    for i in widx:
        v = toks[i][1]
        if not v['syllabic']: continue
        sg = v['signs']
        if not (sg[:2] == ['A', 'DU'] or v['norm'] == 'A-DU'): continue
        nval = None
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM': nval = toks[j][1]['val']; break
            if toks[j][0] == 'DIV': continue
            break
        nxt = None
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'WORD': nxt = toks[j][1]['norm']; break
        fam_docs.append(d['id'])
        print(f'   {v["norm"]:<16} {d["id"]:<10} {d["site"]:<4} {d["typ"]:<4} '
              f'{"ЗАГОЛОВОК" if i == widx[0] else "запись":<10} '
              f'{"число=" + str(nval) if nval is not None else "без числа":<14} '
              f'след: {nxt}')

# что идёт после A-DU-заголовка (тип документа)
print('\n=== содержимое документов с заголовком A-DU ===')
for did in ('HT85a', 'HT86a', 'HT88', 'HT133', 'HT95a', 'HT95b', 'HT99a'):
    for d in corpus:
        if d['id'] != did: continue
        out = []
        for k, v in d['toks']:
            if k == 'WORD': out.append(v['norm'])
            elif k == 'NUM': out.append(str(v['val']))
            elif k == 'LB': out.append('/')
        print(f'   {did}: ' + ' '.join(out[:18]) + (' …' if len(out) > 18 else ''))

# сравнение элементов: A-DU vs I-DA vs PU2-RE
print('\n=== сравнение элементов ===')
lex = Counter(); lex_meta = defaultdict(list)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1
            lex_meta[w].append((d['site'], d['typ']))
for el in [('A', 'DU'), ('I', 'DA'), ('PU2', 'RE')]:
    free = lex.get(el, 0)
    exts = [w for w in lex if len(w) > 2 and (w[:2] == el or w[-2:] == el)]
    metas = list(lex_meta.get(el, []))
    for w in exts: metas += lex_meta[w]
    rel = sum(1 for _, t in metas if t == 'rel')
    sites = sorted({s for s, _ in metas})
    print(f'   {"-".join(el):<8} свободно ×{free}, расширений {len(exts)} '
          f'({[",".join(w) for w in exts][:4]}), rel-доля {rel}/{len(metas)}, '
          f'сайты {sites}')
