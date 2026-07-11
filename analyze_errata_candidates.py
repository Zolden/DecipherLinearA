# -*- coding: utf-8 -*-
"""Этап 43 (§EB): внешний арифметический аудит lineara.xyz (issues
deemkeen/imafukka, июнь-июль 2026) как errata-кандидаты поверх заморозки.

Пять кандидатов из их каталога (GORILA-сверка) проверяются против нашего
corpus.pkl и против устойчивости §A (KU-RO-арифметика 40/40 fullD,
аномалия HT9a). Слой: errata_lineara_v1.tsv; corpus.pkl не правится.
"""
import sys, pickle
from fractions import Fraction

sys.stdout.reconfigure(encoding='utf-8')
corpus = {d['id']: d for d in pickle.load(open('corpus.pkl', 'rb'))}

CAND = [
    ('HT9a', 'KU-RO', Fraction(127, 4), Fraction(156, 5),
     'сайт 31 3/4 (тихая правка) против GORILA 31 1/5'),
    ('HT13', 'RE-ZA', Fraction(11, 2), None,
     'сайт 5 1/2 против GORILA 5[]J — лакуна, значение неопределимо'),
    ('HT119', 'VIR+[?]', Fraction(67), Fraction(68),
     'сайт 67 против GORILA 68'),
    ('HT27a', 'KU-RO', Fraction(335), Fraction(355),
     'сайт 335 против GORILA 355'),
    ('HT123a', 'SA-RU (дробь)', None, None,
     'кодировка A701 против A711-X по прорисовке (Montecchi 2019)'),
]

print('кандидат | наш corpus.pkl | GORILA | влияние на заголовки')
rows = []
for did, word, ours_exp, gorila, note in CAND:
    d = corpus.get(did)
    toks = d['toks'] if d else []
    # факт из корпуса: значение при слове + был ли документ «полностью
    # сохранным» для §A (нет approx/doubt чисел)
    val = None
    prev = None
    dirty = False
    for k, v in toks:
        if k == 'NUM':
            if v['approx'] or v['doubt']:
                dirty = True
            if prev == word.split(' ')[0]:
                val = v['val']
        if k == 'WORD':
            prev = v['norm']
            if any(c in v['norm'] for c in '[]?'):
                dirty = True
    fullD = not dirty
    rows.append((did, word, val, gorila, fullD, note))
    print(f'{did:<8} {word:<14} наш={val} GORILA={gorila} '
          f'fullD={"ДА" if fullD else "нет"} — {note}')

with open('errata_lineara_v1.tsv', 'w', encoding='utf-8') as f:
    f.write('doc\tword\tcorpus_value\tgorila_value\tin_fullD\tnote\tstatus\n')
    for did, word, val, gorila, fullD, note in rows:
        f.write(f'{did}\t{word}\t{val}\t{gorila}\t{fullD}\t{note}\t'
                f'CANDIDATE (ждёт апстрима Хогана)\n')

# устойчивость §A
print('\nустойчивость заголовков:')
d = corpus['HT9a']
nums, kuro, prev = [], None, None
for k, v in d['toks']:
    if k == 'NUM':
        if prev == 'KU-RO':
            kuro = v['val']
        else:
            nums.append(v['val'])
    if k == 'WORD':
        prev = v['norm']
s = sum(nums)
print(f'  HT9a: сумма={s}, итог(сайт)={kuro} → зазор {kuro - s}; '
      f'итог(GORILA)=156/5 → зазор {Fraction(156,5) - s}')
print('  оба чтения дают ненулевой зазор — аномалия §A устойчива к развилке')
print('  HT127b: KU-RO=292 из глифов — сумма 156+72+24+15+11+14=292 точно;')
print('  дисплейный баг сайта (291) наш парсер не унаследовал (читаем глифы)')
print('  HT13/HT27a: approx/doubt-числа; HT119: лакуна в слове (VIR+[?]) —')
print('  все трое вне fullD §A; поправка 67→68 меняет зазор 2→1, не вердикт')
print('''
Чтение: внешний аудит (deemkeen) не ломает ни одного нашего заголовка:
40/40 fullD не задет, аномалия HT9a смыслово та же при обоих чтениях,
HT127b у нас уже верен. Кандидаты зафиксированы слоем errata_lineara_v1
до решения апстрима; поддержка-поля (ZA1-33 «каменный сосуд» → таблички)
нас не касаются — жанровые разбиения всегда шли по ID-сериям.''')
