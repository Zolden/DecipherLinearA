# -*- coding: utf-8 -*-
"""Этап 31 (§DN): ПРЕДРЕГИСТРАЦИЯ №3 (коммит ef4e218, до этого файла) —
межпломбовая повторяемость чистых слов на Wc.

Замороженный эндпойнт: среди чистых слоговых полных слов (>=2 знаков,
без */+) доля ТОКЕНОВ на Wc-документах, чей тип встречается на >=2 разных
Wc-документах, выше внутринаборной повторяемости случайных наборов того же
числа не-Wc документов (R=10000, seed=42, односторонний). Один прогон.
"""
import sys, pickle, random
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
docs = []                                  # (is_wc, doc_id, [слова])
for d in corpus:
    ws = []
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']) \
           and all(not s.startswith('*') and '+' not in s
                   for s in v['signs']):
            ws.append(tuple(v['signs']))
    if ws:
        docs.append(('Wc' in d['id'], d['id'], ws))

wc_docs = [(i, w) for iswc, i, w in docs if iswc]
other_docs = [(i, w) for iswc, i, w in docs if not iswc]
print(f'Wc-документов с чистыми словами: {len(wc_docs)}; '
      f'не-Wc: {len(other_docs)}')

def rep_share(dset):
    type_docs = defaultdict(set)
    for did, ws in dset:
        for w in ws:
            type_docs[w].add(did)
    tot = hit = 0
    for did, ws in dset:
        for w in ws:
            tot += 1
            if len(type_docs[w]) >= 2:
                hit += 1
    return hit / tot if tot else 0.0, tot

obs, n_tok = rep_share(wc_docs)
print(f'Wc: токенов {n_tok}, межпломбовая повторяемость {obs:.3f}')
for did, ws in wc_docs:
    print(f'   {did:<12} {[" -".join([])] and ""}{["-".join(w) for w in ws]}')

n_docs = len(wc_docs)
sims = []
for _ in range(R):
    pick = random.sample(other_docs, n_docs)
    s, _t = rep_share(pick)
    sims.append(s)
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
p = (sum(1 for x in sims if x >= obs) + 1) / (R + 1)
print(f'нуль (наборы из {n_docs} не-Wc документов): {mu:.3f}±{sd:.3f}, '
      f'p={p:.4f} (односторонний)')
verdict = 'ПОДТВЕРЖДЕНА' if p < 0.05 else 'НЕ ПОДТВЕРЖДЕНА'
print(f'ПРЕДРЕГИСТРАЦИЯ №3: {verdict}')
print('''
Чтение: повторяемость слова на РАЗНЫХ пломбах — механический прокси
«печати одного лица/учреждения» (Anastasiadou); результат публикуется
как вышел, чтения не приписываются.''')
