# -*- coding: utf-8 -*-
"""Этап 6, п.7 (§R): аномалия QA — знак ведёт себя «как гласный».

§J: QA имеет log10LR=+2.97 в пользу V-профиля (15/6/4 нач/сред/кон по типам) —
сильнейшее отклонение среди известных CV-знаков. Разбор:
1. Все QA-слова с контекстами; медиальные вхождения — не редупликация ли
   (QA-QA-...)?
2. Распределение знаков ПОСЛЕ начального QA- (гласные ряды следующего знака).
3. Класс §F QA-слов (учёт/дроби/формулы), сайты.
4. Сравнительная рамка (качественно): в LB q-ряд тоже частотен в начале слова
   (qa-si-re-u, qa-ra...) — аномалия может быть свойством ряда Q, а не ошибкой
   значений; вывод — фиксация факта, интерпретация за пределами данных.
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

lex = Counter(); lex_docs = defaultdict(list)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1
            lex_docs[w].append((d['id'], d['site'], d['typ']))
WORDS = set(lex)

qa_words = sorted(w for w in WORDS if 'QA' in w)
print(f'слов с QA: {len(qa_words)}')
ini = [w for w in qa_words if w[0] == 'QA']
med = [w for w in qa_words if 'QA' in w[1:-1]]
fin = [w for w in qa_words if w[-1] == 'QA']
print(f'начальных {len(ini)}, срединных {len(med)}, конечных {len(fin)}')

print('\n--- начальные QA-слова ---')
for w in ini:
    print(f'   {"-".join(w):<22} ×{lex[w]}  {sorted(set(x[1] for x in lex_docs[w]))}')
print('--- срединные (редупликация?) ---')
for w in med:
    redup = 'РЕДУПЛИКАЦИЯ' if any(w[i] == w[i + 1] == 'QA' or
                                   (w[i] == 'QA' and w[i - 1] == 'QA')
                                   for i in range(1, len(w) - 1)) else ''
    print(f'   {"-".join(w):<22} ×{lex[w]} {redup}')
print('--- конечные ---')
for w in fin:
    print(f'   {"-".join(w):<22} ×{lex[w]}')

# --- знак после начального QA
VOWELS = {'A', 'E', 'I', 'O', 'U'}
def v_of(s):
    base = s.rstrip('23')
    if base in VOWELS: return base
    if len(base) >= 2 and base[-1] in VOWELS: return base[-1]
    return '?'
nxt = Counter(v_of(w[1]) for w in ini)
print(f'\nгласный ряд знака после QA-: {dict(nxt)}')
# для сравнения: после других частых начальных CV (KA-, KU-, SA-)
for pref in ('KA', 'KU', 'SA', 'A'):
    ws = [w for w in WORDS if w[0] == pref and len(w) >= 2]
    cnt = Counter(v_of(w[1]) for w in ws)
    tot = sum(cnt.values())
    print(f'после {pref}-: n={tot}, ' +
          ', '.join(f'{k}:{v / tot:.0%}' for k, v in cnt.most_common(6)))

# --- контексты: числа/регистры
n_num = n_tot = n_rel = 0
for w in qa_words:
    for did, site, typ in lex_docs[w]:
        n_tot += 1
        n_rel += typ == 'rel'
print(f'\nQA-слова: токенов {n_tot}, в rel-документах {n_rel} '
      f'({n_rel / n_tot:.0%}; база по лексикону ~17%)')
