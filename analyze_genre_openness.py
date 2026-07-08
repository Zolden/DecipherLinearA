# -*- coding: utf-8 -*-
"""Этап 22 (§CM): жанровый тест открытости позиций — ответ на пп.9–10
DecipherEtruscan (их вывод: «открытость позиции — свойство ЖАНРА, не
языка»; у них ритуал даёт +Δ как наш §BW, ономастика — инверсию).

Их метрика: TTR (типы/токены) инвентаря позиции 1 против позиции 2 по
документам ≥3 слов; Δ = TTR1 − TTR2. Нуль — обмен позиций внутри
документа (w1↔w2 с вероятностью 1/2), R=10000, двусторонне.
Жанры LA: административный (таблички и пр.) против религиозного
(Z*-серии). Предсказание их рамки для LA: в религиозном жанре открытие
формульное (закрытый класс, §K/§BO) → Δ должно ИНВЕРТИРОВАТЬСЯ
(TTR1 < TTR2), в административном — наш §BW-знак (Δ>0 слабо/нейтрально).
"""
import sys, pickle, random
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
docs = {'адм': [], 'религ': []}
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) < 3:
        continue
    rel = any(z in d['id'] for z in
              ('Za', 'Zb', 'Zc', 'Zd', 'Ze', 'Zf', 'Zg'))
    docs['религ' if rel else 'адм'].append((ws[0], ws[1]))

def ttr_delta(pairs):
    t1 = len({a for a, _ in pairs}) / len(pairs)
    t2 = len({b for _, b in pairs}) / len(pairs)
    return t1, t2, t1 - t2

for genre, pairs in docs.items():
    if len(pairs) < 8:
        print(f'{genre}: документов {len(pairs)} — мало, пропуск')
        continue
    t1, t2, d_obs = ttr_delta(pairs)
    sims = []
    for _ in range(R):
        sw = [(b, a) if random.random() < 0.5 else (a, b)
              for a, b in pairs]
        sims.append(ttr_delta(sw)[2])
    p = sum(1 for x in sims if abs(x) >= abs(d_obs) - 1e-12) / R
    top1 = Counter(a for a, _ in pairs).most_common(3)
    top2 = Counter(b for _, b in pairs).most_common(3)
    print(f'{genre}: документов {len(pairs)}; TTR1={t1:.2f}, TTR2={t2:.2f}, '
          f'Δ={d_obs:+.3f}, p={p:.4f}')
    print(f'   топ позиции 1: {top1}')
    print(f'   топ позиции 2: {top2}')
print('''
Чтение: p разведочные, двусторонние. Ожидание по жанровой рамке
DecipherEtruscan: в религиозном жанре LA Δ<0 (формульное закрытое
открытие), в административном Δ>=0. Совпадение знаков = четвёртое
межтрадиционное подтверждение (жанр, не язык, задаёт профиль позиций).''')
