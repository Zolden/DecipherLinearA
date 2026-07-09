# -*- coding: utf-8 -*-
"""Этап 25 (§CX): туман v3 — слова списков HT86/95 и новые арбитры.

(а) Остальные слова зерновых списков (SA-RU, MI-NU-TE, DA-ME, A-KA-RU,
PA-SE — HT86/95): GRA-ко-встречаемость (точная гипергеометрика) +
метрологический профиль — принадлежат ли классу «статей списка».
(б) Арбитры для нетоварных доменов тумана §CP:
    - домен action (глаголы to-give/to-dedicate…): по этрусской рамке
      (§BO/§BR: предикаты финальны/второпозиционны) кандидат обязан иметь
      позиционный перекос; позитивный контроль — операторы §BC.
    - домен ritual: кандидат обязан концентрироваться в Z*-объектах
      (религиозный регистр); контроль — формульные слова.
p точные (hypergeom) либо перестановочные; разведочно.
"""
import sys, pickle, re, csv
from fractions import Fraction
from collections import Counter, defaultdict

from scipy.stats import hypergeom

sys.stdout.reconfigure(encoding='utf-8')

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex_docs = defaultdict(set)
doc_logo = defaultdict(set)
doc_nums = defaultdict(list)
all_docs = set()
rel_docs = set()
word_pos = defaultdict(list)          # слово -> [(i, L)]
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    rel = any(z in d['id'] for z in ('Za', 'Zb', 'Zc', 'Zd', 'Ze', 'Zf', 'Zg'))
    if rel:
        rel_docs.add(d['id'])
    has_w = False
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex_docs[v['norm']].add(d['id'])
            has_w = True
        if k == 'WORD' and not v['syllabic']:
            doc_logo[d['id']].add(re.split(r'[+]', v['norm'])[0])
        if k == 'NUM' and v.get('val') is not None:
            doc_nums[d['id']].append(v['val'])
    if has_w:
        all_docs.add(d['id'])
    if len(ws) >= 2:
        L = len(ws)
        for i, w in enumerate(ws):
            word_pos[w].append((i, L))
N = len(all_docs)
K_gra = sum(1 for d in all_docs if 'GRA' in doc_logo.get(d, ()))

def num_class(fr):
    if fr == int(fr):
        return 'целое'
    den = Fraction(fr).limit_denominator(1000).denominator
    if den & (den - 1) == 0:
        return 'бинарное'
    if den % 3 == 0:
        return '12-ричное'
    return 'прочее'

print('=== (а) слова списков HT86/95 ===')
print(f'{"слово":<10}{"GRA":>7}{"p":>9}{"чисел":>7}{"целые":>7}'
      f'{"бинарн":>8}{"12-р":>6}')
for wname in ('SA-RU', 'MI-NU-TE', 'DA-ME', 'A-KA-RU', 'PA-SE'):
    docs = lex_docs.get(wname, set()) & all_docs
    if not docs:
        print(f'{wname:<10} нет полных вхождений')
        continue
    n = len(docs)
    hit = sum(1 for d in docs if 'GRA' in doc_logo.get(d, ()))
    p = float(hypergeom.sf(hit - 1, N, K_gra, n))
    c = Counter()
    for d in docs:
        for v in doc_nums.get(d, []):
            try:
                c[num_class(Fraction(v))] += 1
            except (TypeError, ValueError):
                pass
    tot = sum(c.values()) or 1
    print(f'{wname:<10}{hit}/{n:>4}{p:>9.4f}{tot:>7}'
          f'{c["целое"] / tot:>7.0%}{c["бинарное"] / tot:>8.0%}'
          f'{c["12-ричное"] / tot:>6.0%}')

print('\n=== (б) арбитры нетоварных доменов ===')
fog = list(csv.DictReader(open('concept_fog_la.csv', encoding='utf-8')))

def pos_profile(wname):
    occ = word_pos.get(wname, [])
    if len(occ) < 4:
        return None
    n = len(occ)
    ini = sum(1 for i, L in occ if i == 0) / n
    sec = sum(1 for i, L in occ if i == 1) / n
    fin = sum(1 for i, L in occ if i == L - 1) / n
    return n, ini, sec, fin

print('--- домен action (ожидание: перекос к финалу/второй позиции) ---')
print(f'{"слово":<16}{"концепт":<22}{"n":>3}{"нач":>6}{"вт":>6}{"фин":>6}')
n_act = 0
for row in fog:
    if row['domain'] != 'action':
        continue
    pp = pos_profile(row['word'])
    if pp is None:
        continue
    n, ini, sec, fin = pp
    n_act += 1
    print(f'{row["word"]:<16}{row["concept_en"][:20]:<22}{n:>3}'
          f'{ini:>6.0%}{sec:>6.0%}{fin:>6.0%}')
print(f'(кандидатов action с n>=4: {n_act})')
print('позитивные контроли (операторы §BC):')
for op in ('KU-RO', 'A-DU', 'TE', 'SA-RA2'):
    pp = pos_profile(op)
    if pp:
        n, ini, sec, fin = pp
        print(f'   {op:<12} n={n:<4} нач {ini:.0%} / вт {sec:.0%} / '
              f'фин {fin:.0%}')

print('\n--- домен ritual (ожидание: концентрация в Z*-объектах) ---')
lex_all = {w: ds for w, ds in lex_docs.items()}
base_rel = sum(1 for d in all_docs if d in rel_docs)
print(f'база: {base_rel}/{N} документов религиозные')
print(f'{"слово":<18}{"концепт":<20}{"religion":>10}{"p":>9}')
for row in fog:
    if row['domain'] != 'ritual':
        continue
    docs = lex_docs.get(row['word'], set()) & all_docs
    if len(docs) < 2:
        continue
    hit = sum(1 for d in docs if d in rel_docs)
    p = float(hypergeom.sf(hit - 1, N, base_rel, len(docs)))
    mark = ' *' if p < 0.05 else ''
    print(f'{row["word"]:<18}{row["concept_en"][:18]:<20}'
          f'{hit}/{len(docs):>6}{p:>9.4f}{mark}')
print('''
Чтение: p точные гипергеометрические, разведочные; арбитры (позиция для
action, регистр для ritual) — вторичные фильтры тумана; ни одна строка
не «перевод».''')
