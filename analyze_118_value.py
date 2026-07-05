# -*- coding: utf-8 -*-
"""Этап 11.4 (§AV): *118 — систематическая проверка чтений по всем рядам.

Метод «подстановочного турнира»: во все LA-слова с *118 подставляем каждое
CV-значение (12 согласных рядов × 5 гласных + чистые гласные) и считаем:
  (а) совпадения с лексиконом LB (3694);
  (б) совпадения со слот-именами (1641);
  (в) внутренние коллизии LA (подстановка воспроизводит уже существующее
      LA-слово — свидетельство ПРОТИВ: зачем два написания?).
Ряд-победитель по (а)+(б) при минимуме (в) сравнивается с предсказанием
конвергенции §AP (ряд R). То же — контрольно — для *301 и *306.
"""
import sys, pickle, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
WORDS = set(lex)

CONS = set('djkmnpqrstwz')
def valid_syl(s):
    if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): return True
    m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
    return bool(m and m.group(1) in CONS)
lb_all = set()
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    syls = tuple(line.split('\t')[0].split('-'))
    if len(syls) >= 2 and all(valid_syl(s) for s in syls):
        lb_all.add(syls)
name_slot = set()
for line in open('lb_name_slots.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        name_slot.add(tuple(line.split('\t')[0].split('-')))

LA_SIGNS = {'A','E','I','O','U','DA','DE','DI','DU','JA','JE','JU','KA','KE',
            'KI','KO','KU','MA','ME','MI','MU','NA','NE','NI','NU','PA','PE',
            'PI','PO','PU','QA','QE','QI','RA','RE','RI','RO','RU','SA','SE',
            'SI','SU','TA','TE','TI','TO','TU','WA','WI','ZA','ZE','ZO','ZU'}

def tourney(target):
    words_t = [w for w in WORDS if target in w]
    print(f'\n=== {target}: {len(words_t)} слов ===')
    rows = ['∅'] + sorted(CONS)
    results = []
    for row in rows:
        hits_lb = hits_ns = coll = 0
        det = []
        for vow in 'aeiou':
            syl = (row if row != '∅' else '') + vow
            SYL = syl.upper()
            if SYL not in LA_SIGNS: continue
            for w in words_t:
                cand = tuple(syl if s == target else s.lower() for s in w)
                if any(x.startswith('*') or '+' in x for x in cand): continue
                if cand in lb_all:
                    hits_lb += 1
                    det.append(f'{"-".join(w)}->{"-".join(cand)}[LB]')
                if cand in name_slot:
                    hits_ns += 1
                cand_la = tuple(SYL if s == target else s for s in w)
                if cand_la in WORDS: coll += 1
        results.append((hits_lb + hits_ns, hits_lb, hits_ns, coll, row, det))
    results.sort(key=lambda x: (-x[0], x[3]))
    print(f'{"ряд":>4}{"LB":>4}{"слоты":>6}{"коллизии LA":>12}   примеры')
    for tot, hlb, hns, coll, row, det in results:
        if tot == 0 and coll == 0: continue
        print(f'{row:>4}{hlb:>4}{hns:>6}{coll:>12}   {"; ".join(det[:3])}')

for target in ('*118', '*301', '*306'):
    tourney(target)

# ---------------- нормировка на частоту ряда в LB (контроль конфаунда частоты)
print('\n=== нормированный турнир: (LB-попадания) / (частота ряда в LB) ===')
row_freq = Counter()
tot_syl = 0
for w in lb_all:
    for s in w:
        m = re.fullmatch(r'([a-z]?)([aeiou])[23]?', s)
        if m:
            row_freq[m.group(1) or '∅'] += 1
            tot_syl += 1
for target in ('*118', '*301', '*306'):
    words_t = [w for w in WORDS if target in w]
    scores = []
    for row in ['∅'] + sorted(CONS):
        hits = 0
        for vow in 'aeiou':
            syl = (row if row != '∅' else '') + vow
            if syl.upper() not in LA_SIGNS: continue
            for w in words_t:
                cand = tuple(syl if s == target else s.lower() for s in w)
                if any(x.startswith('*') or '+' in x for x in cand): continue
                if cand in lb_all: hits += 1
        f = row_freq.get(row, 0) / tot_syl
        if f > 0 and hits:
            scores.append((hits / f, hits, f, row))
    scores.sort(reverse=True)
    top = ', '.join(f'{row}:{ratio:.0f} (попад.{h}, част.{f:.3f})'
                    for ratio, h, f, row in scores[:4])
    print(f'{target}: {top}')
