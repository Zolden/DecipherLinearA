# -*- coding: utf-8 -*-
"""Этап 24 (§CT): туман v2 — семейный контроль товарных проверок §CP и
метрологический арбитр для зерновых кандидатов.

(1) Семейный контроль: у §CP было ~18 товарных проверок, 3 значимых
(raw p<0.05), все зерновые. Точные гипергеометрические p (scipy) вместо
симуляций; глобально: P(>=3 значимых) и P(>=3 значимых И все в зерновом
домене) при независимых нулях (симуляция R=100000, seed=42).

(2) Метрологический арбитр (§Y: зерно — целые/бинарная сетка 1/16;
масло/вино — 12-ричная): профиль ЧИСЕЛ в документах кандидатов против
профилей всех GRA- и OLE-документов. Зерновой кандидат обязан жить в
«зерновой» числовой среде. Дескриптивно + доли.
"""
import sys, pickle, re, csv
from fractions import Fraction
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import hypergeom

sys.stdout.reconfigure(encoding='utf-8')
rng = np.random.default_rng(42)

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex_docs = defaultdict(set)
doc_logo = defaultdict(set)
doc_nums = defaultdict(list)
all_docs = set()
for d in corpus:
    has_w = False
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            if all(not s.startswith('*') and '+' not in s for s in v['signs']):
                lex_docs[tuple(v['signs'])].add(d['id'])
                has_w = True
        if k == 'WORD' and not v['syllabic']:
            doc_logo[d['id']].add(re.split(r'[+]', v['norm'])[0])
        if k == 'NUM' and v.get('val') is not None:
            doc_nums[d['id']].append(v['val'])
    if has_w:
        all_docs.add(d['id'])
N = len(all_docs)

# --- (1) семейный контроль
cands = []
for row in csv.DictReader(open('concept_fog_la.csv', encoding='utf-8')):
    lc = row['logo_check']
    if not lc:
        continue
    logo = lc.split('(')[0]
    w = tuple(row['word'].split('-'))
    dom_grain = any(x in row['concept_en'] for x in
                    ('emmer', 'barley', 'wheat', 'grain'))
    cands.append((row['word'], w, logo, dom_grain))
print(f'товарных проверок: {len(cands)}')

K_logo = {lg: sum(1 for d in all_docs if lg in doc_logo.get(d, ()))
          for lg in {c[2] for c in cands}}
stats = []
for name, w, logo, grain in cands:
    docs = lex_docs[w] & all_docs
    n = len(docs)
    hit = sum(1 for d in docs if logo in doc_logo.get(d, ()))
    K = K_logo[logo]
    p = float(hypergeom.sf(hit - 1, N, K, n))
    # критическое значение и его точный уровень
    c = 0
    while float(hypergeom.sf(c - 1, N, K, n)) > 0.05:
        c += 1
        if c > n:
            break
    lvl = float(hypergeom.sf(c - 1, N, K, n)) if c <= n else 0.0
    stats.append((name, logo, hit, n, p, lvl, grain))
    mark = ' *' if p < 0.05 else ''
    print(f'   {name:<16} {logo:<5} {hit}/{n}  p={p:.4f}{mark}')

obs_sig = sum(1 for s in stats if s[4] < 0.05)
obs_grain_sig = sum(1 for s in stats if s[4] < 0.05 and s[6])
lvls = np.array([s[5] for s in stats])
grain_mask = np.array([s[6] for s in stats])
R = 100000
draws = rng.random((R, len(stats))) < lvls
n_sig = draws.sum(axis=1)
n_gr = (draws & grain_mask).sum(axis=1)
p_any3 = float(((n_sig >= obs_sig).sum() + 1) / (R + 1))
p_gr3 = float((((n_sig >= obs_sig) & (n_gr >= obs_grain_sig)).sum() + 1)
              / (R + 1))
print(f'\nзначимых (p<0.05): {obs_sig}, из них зерновых: {obs_grain_sig}')
print(f'глобально: P(>= {obs_sig} значимых) = {p_any3:.4f}; '
      f'P(>= {obs_sig} и все зерновые) = {p_gr3:.4f}')

# --- (2) метрологический арбитр
def num_class(fr):
    if fr == int(fr):
        return 'целое'
    den = Fraction(fr).limit_denominator(1000).denominator
    if den & (den - 1) == 0:
        return 'бинарное'
    if den % 3 == 0:
        return '12-ричное'
    return 'прочее'

def profile(docs):
    c = Counter()
    for d in docs:
        for v in doc_nums.get(d, []):
            try:
                c[num_class(Fraction(v))] += 1
            except (TypeError, ValueError):
                pass
    tot = sum(c.values())
    return c, tot

print('\n=== метрологический арбитр (профиль чисел в документах) ===')
base_gra = [d for d in all_docs if 'GRA' in doc_logo.get(d, ())]
base_ole = [d for d in all_docs if 'OLE' in doc_logo.get(d, ())]
rows = [('база GRA-документов', base_gra), ('база OLE-документов', base_ole),
        ('KU-NI-SU', lex_docs[('KU', 'NI', 'SU')]),
        ('KI-RI-TA2', lex_docs[('KI', 'RI', 'TA2')]),
        ('KI-RE-TA-NA', lex_docs[('KI', 'RE', 'TA', 'NA')]),
        ('KI-RE-TA2', lex_docs[('KI', 'RE', 'TA2')]),
        ('SI-RU-TE (контроль)', lex_docs[('SI', 'RU', 'TE')])]
print(f'{"кто":<22}{"чисел":>6}{"целые":>8}{"бинарн.":>9}{"12-ричн.":>9}'
      f'{"прочее":>8}')
for name, docs in rows:
    c, tot = profile(docs)
    if not tot:
        print(f'{name:<22}{"—":>6}')
        continue
    print(f'{name:<22}{tot:>6}'
          f'{c["целое"] / tot:>8.0%}{c["бинарное"] / tot:>9.0%}'
          f'{c["12-ричное"] / tot:>9.0%}{c["прочее"] / tot:>8.0%}')
print('''
Чтение: (1) p точные гипергеометрические, глобальные — симуляция
независимых нулей; (2) арбитр дескриптивный: профиль чисел зерновых
кандидатов должен быть ближе к GRA-базе (целые/бинарные), чем к OLE
(12-ричная примесь). p разведочные.''')
