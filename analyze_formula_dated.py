# -*- coding: utf-8 -*-
"""Этап 18 (§BY): формула возлияний × датировки SigLA.

Вопрос: покрывает ли датировочный слой SigLA носители либационной формулы
(Za-серии, каменные объекты), чтобы увидеть слот-2 (георафический, §K/§AE)
во времени. Формульные документы: содержат слово с ядром I-*301-WA
(варианты открытия A-TA-I-*301-WA-JA / (J)A-TA-I-*301-WA-E и род.) либо
принадлежат Za/Zb-сериям с ключевыми словами слота 3+ (SA-SA-RA и вар.).
"""
import sys, pickle
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

per = {}
kind = {}
for line in open('sigla_docs.tsv', encoding='utf-8'):
    if line.startswith('id\t'):
        continue
    _id, idn, k, site, p, url = line.rstrip('\n').split('\t')
    if p:
        per[idn] = p
    kind[idn] = k

def find_period(cid):
    if cid in per:
        return per[cid]
    for suf in 'abcd':
        if cid.endswith(suf) and cid[:-1] in per:
            return per[cid[:-1]]
    return per.get(cid + 'a')

corpus = pickle.load(open('corpus.pkl', 'rb'))
formula_docs = []
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    hit = [w for w in ws if 'I-*301-WA' in w or 'SA-SA-RA' in w
           or w.startswith('JA-SA-SA')]
    if hit:
        formula_docs.append((d['id'], d['site'], hit[0], ws))
print(f'документов с формульными словами: {len(formula_docs)}')

dated = 0
print(f'\n{"документ":<10}{"сайт":<6}{"период SigLA":<14}'
      f'{"тип":<16}ключевое слово')
for cid, site, key, ws in sorted(formula_docs):
    p = find_period(cid)
    kk = kind.get(cid, kind.get(cid.rstrip('abcd'), ''))
    if p:
        dated += 1
    print(f'{cid:<10}{site:<6}{p or "—":<14}{kk or "—":<16}{key}')
print(f'\nс датировкой: {dated}/{len(formula_docs)}')

buck = Counter()
for cid, site, key, ws in formula_docs:
    p = find_period(cid)
    if p:
        buck[(p.split()[0] + ' ' + p.split()[1] if len(p.split()) > 1
              else p, site)] += 1
print('период × сайт формульных документов:',
      dict(sorted(buck.items())) or '—')
print('''
Чтение: SigLA покрывает в основном административные носители (таблички
HT/KH); если формульный корпус остаётся недатированным — фиксируем это
как границу слоя, слот-2 во времени отложен до расширения датировок
(изданиями Za-объектов).''')
