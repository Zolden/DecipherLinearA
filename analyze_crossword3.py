# -*- coding: utf-8 -*-
"""Этап 17 (§BS): кроссворд v3 — неизвестные знаки против ОБЪЕДИНЁННОГО
набора слот-имён LB (обе оцифровки), с якорной мотивировкой.

Отличие от турниров §AV/§BJ: мишень — не весь лексикон LB, а union
слот-имён (lb_name_slots ∪ lb2_name_slots): 11 якорей §BN валидировали
именно именной канал переноса, поэтому спрашиваем: «если слово LA с одним
неизвестным знаком — имя, какое чтение знака сделало бы его именем LB?»
Голоса нормируются на частоту ряда в мишени (как §AV). Разведочно, без
p-значений (мишень мала); согласование с §AV/§BJ отмечается явно.
"""
import sys, pickle, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1

NS = set()
for fn in ('lb_name_slots.tsv', 'lb2_name_slots.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            NS.add(tuple(line.split('\t')[0].split('-')))
print(f'union слот-имён: {len(NS)}')

LA_SIGNS = {'A','E','I','O','U','DA','DE','DI','DU','JA','JE','JU','KA','KE',
            'KI','KO','KU','MA','ME','MI','MU','NA','NE','NI','NU','PA','PE',
            'PI','PO','PU','QA','QE','QI','RA','RE','RI','RO','RU','SA','SE',
            'SI','SU','TA','TE','TI','TO','TU','WA','WI','ZA','ZE','ZO','ZU'}
CONS = set('djkmnpqrstwz')

row_freq = Counter(); tot = 0
for w in NS:
    for s in w:
        m = re.fullmatch(r'([a-z]?)([aeiou])[23]?', s)
        if m:
            row_freq[m.group(1) or '∅'] += 1; tot += 1

def known(s):
    return not (s.startswith('*') or '+' in s)

UNK = ['*301', '*118', '*306', '*304', '*305', '*86']
print('=== кроссворд v3: голоса рядов по мишени «слот-имена» ===')
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
                if cand in NS:
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
        print(f'{target} ({len(words_t)} слов): попаданий в слот-имена нет')
print('''
Чтение: разведочные голоса (мишень ~2.3k имён, попадания единичны — p не
считаем); сверка с §AV/§BJ: устойчивое повторение ряда тем же знаком на
третьей независимой мишени = усиление кандидата, расхождение = честный
минус.''')
