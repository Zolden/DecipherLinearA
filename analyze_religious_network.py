# -*- coding: utf-8 -*-
"""Этап 10.6 (§AQ): сеть религиозных элементов.

Узлы — повторяющиеся элементы религиозного регистра (слоты формулы §K/§AE,
семейства §X/§AB/§AK): последовательности знаков, ищутся как непрерывные
подпоследовательности внутри слов rel-документов (и, для контраста, tab).
Рёбра: (а) композиция — два элемента в ОДНОМ слове; (б) кодокументность —
в одном документе. Выход: элемент × сайты, композиты, матрица совместности.
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

ELEMENTS = {
    'ATAI*301': ('A', 'TA', 'I', '*301'),
    'JASASARAME-стем': ('SA', 'SA', 'RA'),
    'UNAKA/RUKA': ('U', 'NA'),
    'IPINA': ('I', 'PI', 'NA'),
    'SIRU': ('SI', 'RU'),
    'DIKITE': ('DI', 'KI', 'T'),   # T* — особая обработка ниже
    'PU2RE': ('PU2', 'RE'),
    'DUPU2RE': ('DU', 'PU2', 'RE'),
    'IDA': ('I', 'DA'),
    'TUMEI': ('TU', 'ME', 'I'),
    'SETOIJA': ('SE', 'TO', 'I', 'JA'),
    'TURUSA': ('TU', 'RU', 'SA'),
    'OSUQARE': ('O', 'SU', 'QA', 'RE'),
    'JASUMATU': ('JA', 'SU', 'MA', 'TU'),
    'TANUMUTI': ('TA', 'NU', 'MU', 'TI'),
    'SEKANASI': ('SE', 'KA', 'NA', 'SI'),
    'INATAIZUDISIKA': ('I', 'NA', 'TA', 'I'),
    'ASASARA': ('A', 'SA', 'SA'),
}

def contains(word_signs, pattern):
    n, m = len(word_signs), len(pattern)
    for i in range(n - m + 1):
        ok = True
        for j, p in enumerate(pattern):
            s = word_signs[i + j]
            if p == 'T':
                if not s.startswith('T'): ok = False; break
            elif s != p:
                ok = False; break
        if ok: return True
    return False

doc_elems = defaultdict(set)
word_elems = defaultdict(set)
elem_sites = defaultdict(Counter)
elem_docs = defaultdict(set)
for d in corpus:
    if d['typ'] != 'rel': continue
    for k, v in d['toks']:
        if k != 'WORD' or not v['syllabic']: continue
        sg = v['signs']
        found = {name for name, pat in ELEMENTS.items() if contains(sg, pat)}
        if found:
            doc_elems[d['id']] |= found
            for name in found:
                elem_sites[name][d['site']] += 1
                elem_docs[name].add(d['id'])
            if len(found) >= 2:
                word_elems[(d['id'], v['norm'])] = found

print('=== элементы: распространение (rel-документы) ===')
for name, sites in sorted(elem_sites.items(), key=lambda kv: -sum(kv[1].values())):
    print(f'   {name:<18} док. {len(elem_docs[name]):>2}, сайты {dict(sites)}')

print('\n=== композиты (2+ элемента в одном слове) ===')
for (did, norm), els in sorted(word_elems.items()):
    site = next(d['site'] for d in corpus if d['id'] == did)
    print(f'   {norm:<34} {did:<10} {site:<4} = {" + ".join(sorted(els))}')

print('\n=== кодокументность (пары элементов в одном документе, >=2 док.) ===')
pair_docs = defaultdict(set)
for did, els in doc_elems.items():
    els = sorted(els)
    for i in range(len(els)):
        for j in range(i + 1, len(els)):
            pair_docs[(els[i], els[j])].add(did)
for (a, b), docs in sorted(pair_docs.items(), key=lambda kv: -len(kv[1])):
    if len(docs) < 2: continue
    print(f'   {a} + {b}: {len(docs)} док. {sorted(docs)[:5]}')

print('\n=== документы с максимальным числом элементов ===')
for did, els in sorted(doc_elems.items(), key=lambda kv: -len(kv[1]))[:8]:
    site = next(d['site'] for d in corpus if d['id'] == did)
    print(f'   {did:<12} {site:<4} [{len(els)}]: {", ".join(sorted(els))}')
