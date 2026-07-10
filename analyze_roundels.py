# -*- coding: utf-8 -*-
"""Этап 30 (§DL): ПРЕДРЕГИСТРАЦИЯ №2 (коммит c3fb6e4, до написания этого
файла) — тест Anastasiadou: слова на круглых пломбах = имена?

Замороженный эндпойнт: доля корпусных ГАПАКСОВ среди полных слоговых
слов-токенов на документах Wc-серий выше, чем при случайном выборе того
же числа слов-токенов из не-Wc документов (R=10000, seed=42,
односторонний p<0.05). Один прогон, публикация как вышло.
"""
import sys, pickle, random

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
from collections import Counter
lex = Counter()
tokens = []                                 # (is_wc, word)
for d in corpus:
    is_wc = 'Wc' in d['id']
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            lex[w] += 1
            tokens.append((is_wc, w))

hapax = {w for w, c in lex.items() if c == 1}
wc_toks = [w for iswc, w in tokens if iswc]
other_toks = [w for iswc, w in tokens if not iswc]
print(f'токенов: Wc {len(wc_toks)}, прочие {len(other_toks)}; '
      f'гапаксов в лексиконе: {len(hapax)}/{len(lex)}')
print('слова Wc-пломб:', ['-'.join(w) + ('*' if w in hapax else '')
                          for w in wc_toks])
obs = sum(1 for w in wc_toks if w in hapax) / len(wc_toks)
print(f'гапакс-доля на Wc: {obs:.2f}')

n = len(wc_toks)
sims = []
for _ in range(R):
    pick = random.sample(other_toks, n)
    sims.append(sum(1 for w in pick if w in hapax) / n)
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
p = (sum(1 for x in sims if x >= obs) + 1) / (R + 1)
print(f'нуль (случайные не-Wc токены): {mu:.2f}±{sd:.2f}, p={p:.4f} '
      f'((b+1)/(R+1), односторонний)')
verdict = 'ПОДТВЕРЖДЕНА' if p < 0.05 else 'НЕ ПОДТВЕРЖДЕНА'
print(f'ПРЕДРЕГИСТРАЦИЯ №2: {verdict}')
print('''
Чтение: гапакс-доля — механический прокси именного класса (§F: имена
тяготеют к единичным упоминаниям); совпадение с интерпретацией
Anastasiadou (пломбы несут имена) — конвергенция, не чтение.''')
