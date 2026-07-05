# -*- coding: utf-8 -*-
"""Этап 12.5 (§BC): реестр операторов — черновик «служебного словаря» LA.

Оператор = повторяющийся элемент со служебным/структурным поведением
(не имя и не товар). Для каждого: дистрибуция (вхождения, сайты, регистры),
позиционный профиль (заголовок/в строке/финал), доля «с числом», функция по
нашим разделам (доказано/кандидат/неизвестно). Данные считаются из корпуса,
функции — ссылками на разделы отчёта.
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

OPS = {
    'KU-RO':       ('итог списка', '§0/этап 2: суммы сходятся; §A: чистые окна'),
    'PO-TO-KU-RO': ('гранд-итог', 'этап 2: сумма KU-RO-итогов'),
    'KI-RO':       ('недоимка/остаток', 'этап 2: fwd-списки; известная гипотеза «owed»'),
    'TE':          ('транзакционная метка заголовка', '§B: без чисел при заголовках'),
    'KI':          ('под-колонка HT118', '§B: под-финал p≈0.12, не система'),
    'A-DU':        ('надтоварный оператор-заголовок', '§AQ/§AU: 0/10 rel; состав не меняет'),
    'A-KA-RU':     ('заголовок (HT2/86)', '§H шорт-лист'),
    'I-DA':        ('религиозный элемент', '§AB/§AK: 71% rel, 7 сайтов'),
    'PU2-RE':      ('второй член композитов, свободн.', '§X: свободн.+связ.'),
    'DU-PU2-RE':   ('расширенный второй член', '§X: PK+HT композиты'),
    'SA-RA2':      ('учётный термин при товарах', 'этап 2: частотный; не имя (19 ток.)'),
    'SI-RU-TE':    ('финал формулы возлияний (слот 6)', '§K/§AS: общекритский'),
    'SI-RU':       ('вариант финала формулы', '§K: слот 6'),
    'TU-ME-I':     ('локальный элемент слота 2 (PK)', '§AE: ×2 Палекастро'),
    'NA-SI':       ('элемент формулы (AP)', '§AE: слот 2 APZa2'),
    'U-NA-KA-NA-SI': ('слот 4 формулы', '§K: общекритский'),
    'I-PI-NA-MA':  ('слот 5 формулы', '§K: общекритский'),
}

def occurrences(norm):
    occ = []
    for d in corpus:
        toks = d['toks']
        widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
        for i in widx:
            v = toks[i][1]
            if v['norm'] != norm: continue
            nval = None
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM': nval = True; break
                if toks[j][0] == 'DIV': continue
                break
            pos = ('заголовок' if i == widx[0] else
                   ('финал' if i == widx[-1] else 'строка'))
            occ.append({'site': d['site'], 'typ': d['typ'], 'pos': pos,
                        'num': bool(nval)})
    return occ

print(f'{"оператор":<14}{"n":>4}{"сайтов":>7}{"rel%":>6}{"загол%":>8}'
      f'{"финал%":>8}{"с числом%":>10}  функция')
print('-' * 100)
for op, (func, ref) in OPS.items():
    occ = occurrences(op)
    n = len(occ)
    if n == 0:
        print(f'{op:<14}{0:>4}  — не в норм-форме corpus.pkl'); continue
    sites = len({o['site'] for o in occ})
    rel = sum(o['typ'] == 'rel' for o in occ) / n
    head = sum(o['pos'] == 'заголовок' for o in occ) / n
    fin = sum(o['pos'] == 'финал' for o in occ) / n
    num = sum(o['num'] for o in occ) / n
    print(f'{op:<14}{n:>4}{sites:>7}{rel:>6.0%}{head:>8.0%}{fin:>8.0%}'
          f'{num:>10.0%}  {func}')
    print(f'{"":<14}    основание: {ref}')
