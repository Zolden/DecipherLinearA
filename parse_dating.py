# -*- coding: utf-8 -*-
"""Этап 21 (§CH): штатный слой датировок → dating.tsv.

Объединяет два независимых источника: поле context сырого lineara.xyz
(corpus_raw.json; §CF — 1388/1721) и периоды SigLA (sigla_docs.tsv).
Эпоха-консенсус: совпадение по префиксу (MM/LM/EM) либо единственный
доступный источник; противоречия помечаются CONFLICT (§CF: KNZf13).
corpus.pkl не меняется; dating.tsv — сайдкар-слой (как underdots).
Вне стресс-ростера (читает corpus_raw.json, восстановимый
tools/fetch_sources.sh); его ВЫХОД dating.tsv коммитится.
"""
import sys, json, re, pickle
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

def norm_ctx(c):
    c = (c or '').strip().upper().replace(' ', '')
    m = re.match(r'^(EM|MM|LM|MH|LH)([IVX]*)([AB]?)', c)
    return m.group(0) if m else ''

raw = json.load(open('corpus_raw.json', encoding='utf-8'))
ctx = {k: norm_ctx(r.get('context')) for k, r in raw.items()}
ctx = {k: v for k, v in ctx.items() if v}

sig = {}
for line in open('sigla_docs.tsv', encoding='utf-8'):
    if line.startswith('id\t'):
        continue
    _id, idn, kind, site, p, url = line.rstrip('\n').split('\t')
    if p:
        sig[idn] = norm_ctx(p)

def sig_period(cid):
    if cid in sig:
        return sig[cid]
    for suf in 'abcd':
        if cid.endswith(suf) and cid[:-1] in sig:
            return sig[cid[:-1]]
    return sig.get(cid + 'a', '')

def epoch(p):
    return p[:2] if p else ''

corpus = pickle.load(open('corpus.pkl', 'rb'))
rows = []
stats = Counter()
for d in corpus:
    cid = d['id']
    c = ctx.get(cid, '')
    s = sig_period(cid) or ''
    ec, es = epoch(c), epoch(s)
    if ec and es:
        cons = ec if ec == es else 'CONFLICT'
    else:
        cons = ec or es
    rows.append((cid, c, s, cons))
    stats[cons or '—'] += 1

with open('dating.tsv', 'w', encoding='utf-8') as f:
    f.write('doc\tcontext\tsigla\tepoch\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')

print(f'документов corpus.pkl: {len(rows)}')
print('эпоха-консенсус:', dict(stats.most_common()))
print('конфликты:', [r for r in rows if r[3] == 'CONFLICT'])
print('dating.tsv записан (сайдкар-слой; corpus.pkl не тронут)')
