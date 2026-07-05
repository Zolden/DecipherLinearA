# -*- coding: utf-8 -*-
"""Этап 12.6 (§BD): кипро-минойская проверка преемственности — что сравнимо
без оцифрованного корпуса CM.

Статус данных: машиночитаемого корпуса CM в открытом доступе НЕТ (HoChyMin —
книга; Ferrara Corpus — книга; Валерио 2016 — диссертация без датасета).
Сравниваем то, что опубликовано числом (инвентарь, объём корпуса), с
LA-статистикой, которую считаем сами. Это ТИПОЛОГИЧЕСКОЕ сравнение письменностей,
не языков.

Литературные данные CM (Olivier HoChyMin; Ferrara; Валерио; Wikipedia):
  - силлабограмм: ~96 (три суб-корпуса CM1/CM2/CM3);
  - надписей: ~250; суммарно знаков: ~2500–3500;
  - носители: глиняные шары (booules), цилиндры, таблички Энкоми, клейма.
"""
import sys, pickle
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

# LA-инвентарь: слоговые знаки в словах
syl_signs = Counter(); all_docs = 0; total_signs = 0
docs_len = []
for d in corpus:
    n_here = 0
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic']:
            for s in v['signs']:
                if not s.startswith('*') or s[1:].rstrip('BCF').isdigit():
                    pass
                n_here += 1
                syl_signs[s] += 1
    if n_here:
        all_docs += 1; total_signs += n_here; docs_len.append(n_here)

base = {s for s in syl_signs if not s.startswith('*') and '+' not in s}
star = {s for s in syl_signs if s.startswith('*') and '+' not in s}
docs_len.sort()
print('=== LA (наш корпус) ===')
print(f'документов со слоговым текстом: {all_docs}; знаков-токенов: {total_signs}')
print(f'инвентарь: базовых силлабограмм {len(base)}, *-знаков {len(star)}, '
      f'итого {len(base) + len(star)}')
print(f'медианная длина документа: {docs_len[len(docs_len) // 2]} знаков; '
      f'90-й перцентиль: {docs_len[int(0.9 * len(docs_len))]}')

print('''
=== CM (литература) против LA ===
| параметр | CM | LA (наш счёт) |
|---|---|---|
| силлабограмм | ~96 | {} |
| надписей | ~250 | {} |
| знаков всего | ~2500–3500 | {} |
| медианная длина | короткие (клейма/шары) | {} |

Выводы уровня письменности (не языка):
1. Размеры инвентарей совместимы (СМ ~96 ~ LA ~{}): оба — V/CV-силлабарии
   эгейского типа; преемственность НЕ опровергается.
2. Профили корпусов противоположны по жанру: LA — административные архивы
   (числа, итоги), CM — метки/шары/личные предметы; прямое позиционное
   сравнение слов будет смещено жанром — предупреждение будущему тесту.
3. Для настоящего теста преемственности (частоты, позиции, слова) нужна
   оцифровка HoChyMin — в открытом доступе отсутствует; кандидат на запрос
   (Ferrara/Valério активны на academia.edu) — добавлено в contact_draft.md.
'''.format(len(base) + len(star), all_docs, total_signs,
           docs_len[len(docs_len) // 2], len(base) + len(star)))
