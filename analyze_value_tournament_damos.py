# -*- coding: utf-8 -*-
"""Этап 30 (§DJ): турнир значений неизвестных знаков на курируемом DĀMOS.

Пересборка §AV/§BJ на damos_lexicon.tsv (4044 типа): для слов LA с ровно
одним неизвестным знаком (*118, *301, *306, *21F-контроль) подстановка
кандидатных слогов; попадания в лексикон DĀMOS, голоса по рядам с
нормировкой на частоту ряда (как §AV). Сверка вердиктов трёх баз
(Wayback-§AV, lb2-§BJ, DĀMOS): устойчивое повторение ряда = усиление,
расхождение = честный минус. Разведочно.
"""
import sys, pickle, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

LB = set()
freqs = {}
for line in open('damos_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'):
        continue
    w, c, nd = line.rstrip('\n').split('\t')
    LB.add(tuple(w.split('-')))
    freqs[tuple(w.split('-'))] = int(c)
print(f'DĀMOS-лексикон: {len(LB)} типов')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1

LA_SIGNS = {'A','E','I','O','U','DA','DE','DI','DU','JA','JE','JU','KA','KE',
            'KI','KO','KU','MA','ME','MI','MU','NA','NE','NI','NU','PA','PE',
            'PI','PO','PU','QA','QE','QI','RA','RE','RI','RO','RU','SA','SE',
            'SI','SU','TA','TE','TI','TO','TU','WA','WI','ZA','ZE','ZO','ZU'}
CONS = set('djkmnpqrstwz')
row_freq = Counter(); tot = 0
for w in LB:
    for s in w:
        m = re.fullmatch(r'([a-z]?)([aeiou])[23]?', s)
        if m:
            row_freq[m.group(1) or '∅'] += 1; tot += 1

def known(s):
    return not (s.startswith('*') or '+' in s)

PRIOR = {'*118': 'R (§AV/§BJ)', '*301': 'Z слабый (§CC)',
         '*306': 'Z (§AV/§BJ) vs I (§CC) — конфликт', '*21F': 'CV-контроль'}
print('=== турнир на DĀMOS (нормированные голоса рядов) ===')
for target in ('*118', '*301', '*306', '*21F'):
    words_t = [w for w in lex
               if w.count(target) == 1 and len(w) >= 2
               and all(known(s) for s in w if s != target)]
    scores = []
    for row in ['∅'] + sorted(CONS):
        h = 0; det = []
        for vow in 'aeiou':
            syl = (row if row != '∅' else '') + vow
            if syl.upper() not in LA_SIGNS:
                continue
            for w in words_t:
                cand = tuple(syl if s == target else s.lower() for s in w)
                if cand in LB:
                    h += 1
                    det.append(f'{"-".join(w)}→{"-".join(cand)}')
        f = row_freq.get(row, 0) / tot
        if h and f > 0:
            scores.append((h / f, h, row, det))
    scores.sort(reverse=True)
    line = '; '.join(f'{row}: {h} (норм {r:.0f}) [{det[0]}]'
                     f'{"+" + str(len(det) - 1) if len(det) > 1 else ""}'
                     for r, h, row, det in scores[:4]) or 'попаданий нет'
    print(f'{target} ({len(words_t)} слов) [прежнее: {PRIOR[target]}]:')
    print(f'   {line}')
print('''
Чтение: разведочные голоса без p (как §AV/§BJ); вердикт — только по
устойчивости ряда через ТРИ независимые базы; конфликт ∅/Z по *306
разрешается или фиксируется.''')
