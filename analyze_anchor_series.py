# -*- coding: utf-8 -*-
"""Этап 31 (§DO): серии DĀMOS вокруг якорей — «какого рода имена».

Из damos_context.tsv: в каких сериях и сайтах живут слот-подтверждённые
якоря (i-ta-ja, pa-ra-ne, i-ja-te + топонимы) и лексиконные
(da-i-pi-ta, ki-da-ro, ta-na-ti); справка по семантике серий — известная
классификация LB-серий (D=овцы, B/As=люди, E=земля, Jn=бронза…) —
внешний факт микенологии, не наш вывод. Дистрибутивно.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')

SERIES_GLOSS = {   # стандартная микенологическая классификация (внешняя)
    'Da': 'овцы (м)', 'Db': 'овцы', 'Dc': 'овцы', 'Dd': 'овцы',
    'De': 'овцы', 'Dv': 'овцы (разн.)', 'B': 'люди', 'As': 'люди (списки)',
    'V': 'разное/люди', 'Ap': 'женщины', 'E': 'земля/зерно',
    'Uf': 'земля', 'Jn': 'бронза/кузнецы', 'An': 'люди (PY)',
    'Cn': 'скот (PY)', 'Ea': 'земля (PY)', 'Eb': 'земля (PY)',
    'En': 'земля (PY)', 'Eo': 'земля (PY)', 'Ep': 'земля (PY)',
    'Fp': 'масло-ритуал', 'Fh': 'масло', 'Ga': 'пряности',
}
TARGETS = ['i-ta-ja', 'pa-ra-ne', 'i-ja-te', 'da-i-pi-ta', 'ki-da-ro',
           'ta-na-ti', 'pa-i-to', 'se-to-i-ja', 'su-ki-ri-ta']

ctx = {}
for line in open('damos_context.tsv', encoding='utf-8'):
    if line.startswith('word\t'):
        continue
    p = line.rstrip('\n').split('\t')
    ctx[p[0]] = p

print(f'{"якорь":<13}{"ток":>4}{"док":>4}  сайты; серии (глосса серии — '
      f'внешний факт)')
for t in TARGETS:
    if t not in ctx:
        print(f'{t:<13}  — нет в контекстном слое')
        continue
    w, n, nd, sites, series, dmg = ctx[t]
    sers = []
    for sc in series.split(','):
        s = sc.split(':')[0]
        gl = SERIES_GLOSS.get(s, '?')
        sers.append(f'{sc} [{gl}]')
    print(f'{t:<13}{n:>4}{nd:>4}  {sites};  {"; ".join(sers)}')
print('''
Чтение: серия — контекст учёта, не «профессия»; глоссы серий — стандарт
микенологии (Docs2), приводятся как внешняя справка. Наш вывод только
дистрибутивный: якоря живут в сериях учёта людей/скота/земли, что
согласуется с именным классом.''')
