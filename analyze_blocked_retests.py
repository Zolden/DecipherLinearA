# -*- coding: utf-8 -*-
"""Этап 29 (§DH-б): табличная целостность старых документных выводов.

По аудиту: единица независимости = физическая табличка. Проверка задним
числом для четырёх документных наблюдений (§AQ A-DU, §AK/§AS I-DA,
§BH ароматика/HT23a-класс, §K формульные документы): сколько ДОКУМЕНТОВ
против сколько ТАБЛИЧЕК, есть ли стороны-дубли, сайт-концентрация.
Дескриптивная ревизия: где вывод опирался на двойной счёт сторон.
"""
import sys, pickle
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def tablet(cid):
    return cid[:-1] if cid and cid[-1] in 'abcd' else cid

corpus = pickle.load(open('corpus.pkl', 'rb'))
occ_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic']:
            occ_docs[v['norm']].add(d['id'])

GROUPS = {
    'A-DU (§AQ/§AU)': ['A-DU'],
    'I-DA своб. (§AK)': ['I-DA'],
    'ароматика §BH (класс HT23a)': ['*22F-RI-TU-QA', 'U-NU-*21F',
                                    'JA-*21F', 'SI-*717-TA2'],
    'формула (§K, открытие)': ['A-TA-I-*301-WA-JA', 'JA-TA-I-*301-U-JA',
                               'TA-NA-I-*301-U-TI-NU', 'A-TA-I-*301-WA-E'],
    'SA-SA-RA ядро (§AW)': ['JA-SA-SA-RA-ME', 'A-SA-SA-RA-ME',
                            'SA-SA-RA-ME'],
}
print(f'{"группа":<28}{"док.":>6}{"табл.":>7}{"дубль-стороны":>15}'
      f'{"сайтов":>8}')
for label, wl in GROUPS.items():
    docs = set()
    for w in wl:
        docs |= occ_docs.get(w, set())
    tabs = {tablet(d) for d in docs}
    dup = len(docs) - len(tabs)
    sites = {d.rstrip('0123456789abcd')[:4].rstrip('WZcbagfre') or d[:2]
             for d in docs}
    sites = {t[:2] if t[:2].isalpha() else t for t in sites}
    print(f'{label:<28}{len(docs):>6}{len(tabs):>7}{dup:>15}'
          f'{len(sites):>8}   {sorted(tabs)[:6]}')
print('''
Чтение: «дубль-стороны» = сколько документов схлопывается при переходе к
физическим табличкам; 0 — вывод не зависел от сторон, >0 — соответствующие
частоты в старых секциях завышены на это число (интерпретации §AQ/§AK/
§BH/§K пересчитывать при следующем использовании; corpus.pkl не меняется).''')
