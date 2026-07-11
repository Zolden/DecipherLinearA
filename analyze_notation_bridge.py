# -*- coding: utf-8 -*-
"""Этап 41 (§EA): мост нотаций QI≡*21F — порт этрусской механики
«errata поверх заморозки» в нашу ситуацию (развилки редакторские, судить
чтения мы не вправе; но НОТАЦИОННУЮ эквивалентность фиксировать обязаны).

GORILA-номер *21F и слоговое чтение QI — одна графема в двух конвенциях
(§CG: 39/41 «чтение-1» — редакторские развилки, из них львиная доля —
ровно эта пара). Слой: (1) внутрикорпусные последствия слияния;
(2) сколько строк каталога разночтений растворяется мостом — остаток =
истинные редакторские различия; (3) аудит заголовочных результатов на
чувствительность к мосту. corpus.pkl не правится; слой применяется на
лету.
"""
import sys, pickle, csv
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
BRIDGE = {'QI': '*21F'}

def norm(word):
    return '-'.join(BRIDGE.get(s, s) for s in word.split('-'))

corpus = pickle.load(open('corpus.pkl', 'rb'))
types_raw, types_br = set(), set()
tok_n = 0
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic']:
            tok_n += 1
            types_raw.add(v['norm'])
            types_br.add(norm(v['norm']))
merged = sorted(w for w in types_raw if 'QI' in w.split('-'))
print(f'(1) внутри корпуса: токенов {tok_n}, типов {len(types_raw)} → '
      f'{len(types_br)} после моста (слилось {len(types_raw) - len(types_br)})')
print(f'    QI-типы корпуса: {merged}')
for w in merged:
    tgt = norm(w)
    print(f'    {w} ≡ {tgt} — {"есть двойник в корпусе" if tgt in types_raw else "двойника нет (просто нотация)"}')

# (2) каталог разночтений: сколько строк растворяет мост
rows = list(csv.DictReader(open('divergences.tsv', encoding='utf-8'),
                           delimiter='\t'))
r1 = [r for r in rows if r['class'] == 'чтение-1' and r['match']]
dissolved = kept = 0
resid = Counter()
for r in r1:
    ours = norm(r['word'])
    other = norm('-'.join(eval(r['match'])))
    if ours == other:
        dissolved += 1
    else:
        kept += 1
        a, b = r['word'].split('-'), eval(r['match'])
        for x, y in zip(a, b):
            if x != y and norm(x) != norm(y):
                resid[tuple(sorted((x, y)))] += 1
print(f'\n(2) каталог «чтение-1»: {len(r1)} строк; мост растворяет '
      f'{dissolved}, остаток {kept} — истинные редакторские различия')
print('    остаточные пары знаков:',
      ', '.join(f'{a}↔{b} ×{c}' for (a, b), c in resid.most_common()))

# (3) аудит заголовков: содержат ли якорные слова мостовые знаки
ANCHORS = ['I-JA-TE', 'I-TA-JA', 'PA-I-TO', 'PA-RA-NE', 'SE-TO-I-JA',
           'SU-KI-RI-TA', 'KU-RO', 'KI-RO', 'PO-TO-KU-RO', 'SA-RA2',
           'A-TA-I-*301-WA-JA', 'KU-NI-SU', 'KA-PA', 'A-KA-RU', 'JE-DI']
touched = [w for w in ANCHORS if norm(w) != w]
print(f'\n(3) якоря/операторы/кураторы, затронутые мостом: '
      f'{touched if touched else "НИ ОДНОГО — заголовки к мосту нечувствительны"}')
print(f'    (*21F-TU-NE куратор §DY уже в GORILA-нотации; мост не меняет)')
print('''
Чтение: мост — слой на лету, corpus.pkl заморожен. Слияние 2 QI-типов
даёт честный лексикон; остаток каталога после моста — список для
эпиграфов (наши инструменты его не решают). Заголовочные результаты
от моста не зависят.''')
