# -*- coding: utf-8 -*-
"""Этап 19 (§CC): кроссворд v4 — мишень «слот-имена + финальные варианты».

v3 (§BS) дал ноль на точной мишени. Если правило §BZ (финальное
чередование гласной) реально, честная мишень для слов с одним неизвестным
знаком — NS ∪ {варианты NS по финальной гласной той же строки}.
Разведочные голоса без p (как v3), сверка с §AV/§BJ.
"""
import sys, pickle, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

NS = set()
for fn in ('lb_name_slots.tsv', 'lb2_name_slots.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            NS.add(tuple(line.split('\t')[0].split('-')))

LA_SIGNS_L = {'a','e','i','o','u','da','de','di','du','ja','je','ju','ka',
              'ke','ki','ko','ku','ma','me','mi','mu','na','ne','ni','nu',
              'pa','pe','pi','po','pu','qa','qe','qi','ra','re','ri','ro',
              'ru','sa','se','si','su','ta','te','ti','to','tu','wa','wi',
              'za','ze','zo','zu'}

# расширение мишени — LA-сторонними финалами (кандидат-слово читается
# по-минойски, поэтому его финал обязан быть LA-знаком)
NS_EXT = set(NS)
for nm in NS:
    m = re.fullmatch(r'([a-z]?)([aeiou])', nm[-1])
    if not m:
        continue
    row = m.group(1)
    for v2 in 'aeiou':
        syl = row + v2
        if syl in LA_SIGNS_L:
            NS_EXT.add(nm[:-1] + (syl,))
print(f'мишень: {len(NS)} имён → {len(NS_EXT)} с финальными вариантами')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1

LA_SIGNS = {s.upper() for s in LA_SIGNS_L}
CONS = set('djkmnpqrstwz')
row_freq = Counter(); tot = 0
for w in NS_EXT:
    for s in w:
        m = re.fullmatch(r'([a-z]?)([aeiou])[23]?', s)
        if m:
            row_freq[m.group(1) or '∅'] += 1; tot += 1

def known(s):
    return not (s.startswith('*') or '+' in s)

UNK = ['*301', '*118', '*306', '*304', '*305', '*86']
print('=== кроссворд v4: голоса рядов (мишень с вариантами финала) ===')
for target in UNK:
    words_t = [w for w in lex
               if w.count(target) == 1 and len(w) >= 3
               and all(known(s) for s in w if s != target)]
    if not words_t:
        print(f'{target}: подходящих слов нет')
        continue
    scores = []
    for row in ['∅'] + sorted(CONS):
        h = 0; det = []
        for vow in 'aeiou':
            syl = (row if row != '∅' else '') + vow
            if syl.upper() not in LA_SIGNS:
                continue
            for w in words_t:
                cand = tuple(syl if s == target else s.lower() for s in w)
                if cand in NS_EXT:
                    h += 1
                    det.append(f'{"-".join(w)}→{"-".join(cand)}')
        f = row_freq.get(row, 0) / tot
        if h and f > 0:
            scores.append((h / f, h, row, det))
    scores.sort(reverse=True)
    if scores:
        print(f'{target} ({len(words_t)} слов): ' + '; '.join(
            f'{row}: {h} [{det[0]}]' + (f'+{len(det)-1}' if len(det) > 1 else '')
            for _, h, row, det in scores[:3]))
    else:
        print(f'{target} ({len(words_t)} слов): попаданий нет')
print('''
Чтение: разведочные голоса без p; мишень расширена «правилом финала» §BZ —
если и здесь ноль, именной канал для этих знаков закрыт окончательно;
единичные голоса сверять с §AV/§BJ (*306→Z, *118→R).''')
