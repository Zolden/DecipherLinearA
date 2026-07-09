# -*- coding: utf-8 -*-
"""Этап 24 (§CU): микроструктура зерновой серии HT.

Документы зерновых кандидатов §CP (KU-NI-SU, KI-RI-TA2, KI-RE-TA-NA,
KI-RE-TA2) + их соседи по §BZ (DI-DE-RU, QA-RA2-WA): полная разметка
токенов (слово/логограмма/число со значением), ко-встречаемость
кандидатов, числа при кандидатах. Дистрибутивный вопрос: ведут ли себя
кандидаты как ПАРАЛЛЕЛЬНЫЕ статьи одного списка (несколько кандидатов в
документе, каждый со своим числом при общей логограмме GRA) — профиль
«списка сортов», без чтений.
"""
import sys, pickle
from fractions import Fraction
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

CAND = [('KU', 'NI', 'SU'), ('KI', 'RI', 'TA2'), ('KI', 'RE', 'TA', 'NA'),
        ('KI', 'RE', 'TA2'), ('DI', 'DE', 'RU'), ('QA', 'RA2', 'WA')]
CSET = set(CAND)

corpus = pickle.load(open('corpus.pkl', 'rb'))
by_id = {d['id']: d for d in corpus}
docs = set()
occ = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and tuple(v['signs']) in CSET:
            docs.add(d['id'])
            occ[tuple(v['signs'])].add(d['id'])

print('документы кандидатов:', sorted(docs))
print('\nко-встречаемость (документ × кандидаты):')
for did in sorted(docs):
    here = [('-'.join(c)) for c in CAND if did in occ[c]]
    print(f'   {did:<10} {", ".join(here)}')

def fmt(v):
    try:
        f = Fraction(v)
        return str(int(f)) if f == int(f) else str(f)
    except (TypeError, ValueError):
        return str(v)

print('\n=== полная разметка документов ===')
for did in sorted(docs):
    d = by_id[did]
    print(f'--- {did} ({d["site"]}) ---')
    line = []
    for k, v in d['toks']:
        if k == 'WORD':
            t = v['norm']
            if v['syllabic'] and tuple(v['signs']) in CSET:
                t = f'>>{t}<<'
            line.append(t)
        elif k == 'NUM':
            line.append(f'[{fmt(v.get("val"))}]')
        elif k == 'LB':
            if line:
                print('   ' + ' '.join(line))
            line = []
        elif k == 'GAP':
            line.append('…')
    if line:
        print('   ' + ' '.join(line))

print('\n=== числа непосредственно после кандидатов ===')
for c in CAND:
    vals = []
    for did in sorted(occ[c]):
        toks = by_id[did]['toks']
        for i, (k, v) in enumerate(toks):
            if k == 'WORD' and v['syllabic'] and tuple(v['signs']) == c:
                if i + 1 < len(toks) and toks[i + 1][0] == 'NUM':
                    vals.append((did, fmt(toks[i + 1][1].get('val'))))
    print(f'   {"-".join(c):<14} {vals}')
print('''
Чтение: дистрибутивная разметка; «профиль списка сортов» = несколько
кандидатов в одном документе, каждый со своим числом, при документной
логограмме GRA. Чтения не приписываются.''')
