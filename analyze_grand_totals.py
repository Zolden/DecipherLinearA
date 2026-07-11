# -*- coding: utf-8 -*-
"""Этап 52 (§EH): арифметика второго порядка — PO-TO-KU-RO и KI-RO.

§A установил: KU-RO = сумма позиций (40/40 в полностью сохранных).
Вопросы второго порядка, чистая арифметика без чтений:
(1) PO-TO-KU-RO («гранд-итог»): равен ли он сумме KU-RO документа?
    сумме всех позиций? Перечисляем все документы с PO-TO-KU-RO.
(2) KI-RO: §BO показал непозиционность; здесь — арифметический профиль:
    в документах с KU-RO и KI-RO вместе — равен ли KI-RO разнице
    KU-RO − сумма сохранных позиций (кандидат «недостача»)?
    Плюс перечень KI-RO-документов со структурой.
"""
import sys, pickle
from fractions import Fraction

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

def doc_entries(d):
    """[(слово, значение)] по порядку + флаг повреждений чисел."""
    out, prev, dirty = [], None, False
    for k, v in d['toks']:
        if k == 'WORD':
            prev = v['norm'] if v else None
            if v and any(c in v['norm'] for c in '[]?'):
                dirty = True
        elif k == 'NUM':
            if v['approx'] or v['doubt']:
                dirty = True
            out.append((prev, v['val']))
            prev = None
    return out, dirty

print('(1) KI-RO как заголовок секции-реестра (KI-RO + имена + локальный '
      'KU-RO):')
ok = tot = 0
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if 'KI-RO' not in ws or 'KU-RO' not in ws:
        continue
    _, dirty = doc_entries(d)
    # секция по потоку токенов: KI-RO ... (имя, число)* ... KU-RO n
    names = []
    in_sec = False
    closing = None
    prev = None
    for k, v in d['toks']:
        if k == 'WORD' and v:
            prev = v['norm']
            if prev == 'KI-RO':
                in_sec = True
                names = []
        elif k == 'NUM':
            if prev == 'KU-RO' and in_sec:
                closing = v['val']
                in_sec = False
            elif in_sec and prev not in (None, 'KI-RO'):
                names.append((prev, v['val']))
            prev = None
    if closing is None:
        continue
    s = sum(v for _, v in names)
    ones = all(v == 1 for _, v in names)
    verdict = (closing == s == len(names)) if ones else (closing == s)
    print(f'   {d["id"]:<12} повреждения={"есть" if dirty else "нет"} '
          f'имён={len(names)} (все ×1: {ones}) локальный KU-RO={closing} '
          f'→ {"ТОЧНО" if verdict else "нет"}')
    if not dirty:
        tot += 1
        ok += verdict
print(f'   итог по сохранным: {ok}/{tot} точных секций')

print('\n(2) PO-TO-KU-RO на уровне ФИЗИЧЕСКОЙ таблички (HT122a+b):')
by_id = {d['id']: d for d in corpus}
a, _ = doc_entries(by_id['HT122a'])
b, _ = doc_entries(by_id['HT122b'])
kuro_a = next(v for w, v in a if w == 'KU-RO')
post_a = [(w, v) for w, v in a[[w for w, _ in a].index('KU-RO') + 1:]]
kuro_b = next(v for w, v in b if w == 'KU-RO')
grand = next(v for w, v in b if w == 'PO-TO-KU-RO')
s = kuro_a + sum(v for _, v in post_a) + kuro_b
print(f'   KU-RO(a)={kuro_a} + постскрипт{[(w, str(v)) for w, v in post_a]} '
      f'+ KU-RO(b)={kuro_b} = {s}; PO-TO-KU-RO={grand} → '
      f'{"ТОЧНО" if s == grand else "нет"}')
print('   (HT131b: второй PO-TO-KU-RO, но KU-RO не сохранны — не судится)')

n_kiro = sum(1 for d in corpus if 'KI-RO' in
             [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']])
print(f'\nвсего документов с KI-RO: {n_kiro}')
print('''
Чтение: арифметика записи трёхуровневая — строка → секционный KU-RO →
PO-TO-KU-RO физической таблички (обе стороны + постскрипт). KI-RO
открывает реестры персон «по одному» с точным локальным итогом —
функциональный профиль аннотации по людям (не позиционный оператор
§BO подтверждается арифметически). Без чтений; вердикты по-документные,
повреждённые не судятся.''')
