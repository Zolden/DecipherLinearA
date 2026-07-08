# -*- coding: utf-8 -*-
"""Этап 18 (§BW): словарь заголовков — первые слова документов.

Синтаксис записи (§BR) выделил позицию 1 (дейксис) и позицию 2 (TE,
SA-RA2). Вопросы: (а) из чего состоит инвентарь первых слов; (б) есть ли
«закрытый словарь заголовков» — повторяются ли первые слова между
документами чаще, чем ожидается от их общей частотности; (в) что стоит
на позиции 1 непосредственно перед второпозиционными TE/SA-RA2.

Нуль для (б): случайная перестановка слов внутри каждого документа
(словарь и частоты сохранены, стирается только позиция), R=10000, seed=42.
Статистика: доля документов, чьё первое слово открывает >=2 документа.
"""
import sys, pickle, random
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
docs = []
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) >= 3:
        docs.append((d['id'], d['site'], ws))
print(f'документов >=3 слов: {len(docs)}')

ANCH_TOP = {'PA-I-TO', 'SE-TO-I-JA', 'SU-KI-RI-TA'}
ANCH_NAME = {'DA-I-PI-TA', 'I-TA-JA', 'KI-DA-RO', 'PA-RA-NE', 'TA-NA-TI',
             'I-JA-TE'}
OPS = {'KU-RO', 'PO-TO-KU-RO', 'KI-RO', 'TE', 'A-DU', 'I-DA', 'SI-RU-TE',
       'SA-RA2', 'KI', 'A-TA-I-*301-WA-JA'}

firsts = Counter(ws[0] for _, _, ws in docs)
print(f'типов первых слов: {len(firsts)} на {len(docs)} документов')
print('\nтоп первых слов (>=3 документов):')
for w, c in firsts.most_common():
    if c < 3:
        break
    tag = []
    if w in OPS: tag.append('оператор')
    if w in ANCH_TOP: tag.append('ТОПОНИМ-ЯКОРЬ')
    if w in ANCH_NAME: tag.append('ИМЯ-ЯКОРЬ')
    if w.startswith('A-') or w == 'A': tag.append('A-')
    sites = {s for _, s, ws in docs if ws[0] == w}
    print(f'   {w:<18} ×{c:<3} сайтов {len(sites)} {" ".join(tag)}')

# (б) повторяемость первых слов
def rep_share(dd):
    f = Counter(ws[0] for _, _, ws in dd)
    return sum(1 for _, _, ws in dd if f[ws[0]] >= 2) / len(dd)

obs = rep_share(docs)
sims = []
for _ in range(R):
    sh = []
    for did, s, ws in docs:
        w2 = ws[:]
        random.shuffle(w2)
        sh.append((did, s, w2))
    sims.append(rep_share(sh))
m = sum(sims) / R
sd = (sum((x - m) ** 2 for x in sims) / R) ** 0.5
p = sum(1 for x in sims if x >= obs) / R
print(f'\nдоля документов с повторным первым словом: {obs:.2f} '
      f'(нуль {m:.2f}±{sd:.2f}, p={p:.4f})')

# (в) первое слово перед второпозиционными TE / SA-RA2
print('\nпары «заголовок + оператор второй позиции»:')
pair_first = Counter()
for did, s, ws in docs:
    if len(ws) >= 2 and ws[1] in ('TE', 'SA-RA2'):
        pair_first[(ws[0], ws[1])] += 1
        print(f'   {did:<10} {ws[0]} + {ws[1]}')
h1 = Counter(w for (w, op), c in pair_first.items() for _ in range(c))
multi = {w: c for w, c in h1.items() if c >= 2}
print(f'заголовков перед TE/SA-RA2: {sum(h1.values())} токенов, '
      f'{len(h1)} типов; повторные: {multi or "нет"}')
anchored = [w for w in h1 if w in ANCH_TOP | ANCH_NAME]
print(f'из них якорей: {anchored or "нет"}; на A-: '
      f'{[w for w in h1 if w.startswith("A-")] or "нет"}')
print('''
Чтение: p разведочное; нуль (перестановка внутри документа) сохраняет
словарь и частоты, поэтому избыток повторов первых слов = свойство именно
ПОЗИЦИИ, а не лексикона. Разметка якорей — по §BN.''')
