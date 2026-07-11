# -*- coding: utf-8 -*-
"""Этап 39 (§DY): «куратор-класс» LA — повторяемые неоператорные первые
слова HT (кандидаты из §DX: KA-PA, A-KA-RU, JE-DI, *21F-TU-NE).

Профиль против (а) операторов, (б) уникальных первых слов: число
документов, сопровождение GRA/логограммами, позиции, число слов в их
документах. Плюс LB-параллель масштаба: доля документов сайта, покрытая
топ-кураторами (KN-коллекторы ~30% D-серий; HT-кандидаты — ?).
Дескриптивно; чтения не приписываются.
"""
import sys, pickle, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

CUR = ['KA-PA', 'A-KA-RU', 'JE-DI', '*21F-TU-NE']
OPS = {'KU-RO', 'PO-TO-KU-RO', 'KI-RO', 'TE', 'A-DU', 'I-DA', 'SI-RU-TE',
       'SA-RA2', 'KI', 'A-TA-I-*301-WA-JA'}

corpus = pickle.load(open('corpus.pkl', 'rb'))
occ = defaultdict(list)
ht_docs = 0
for d in corpus:
    if not d['id'].startswith('HT') or any(
            z in d['id'] for z in ('Za', 'Zb', 'Zc')):
        continue
    toks = d['toks']
    ws = [(i, v['norm']) for i, (k, v) in enumerate(toks)
          if k == 'WORD' and v['syllabic']]
    seq = [w for _, w in ws]
    if len(seq) >= 2:
        ht_docs += 1
    logos = {re.split(r'[+]', v['norm'])[0] for k, v in toks
             if k == 'WORD' and not v['syllabic']}
    for j, (i, w) in enumerate(ws):
        if w in CUR:
            pos = ('перв' if j == 0 else
                   ('посл' if j == len(seq) - 1 else 'сред'))
            nxt = toks[i + 1] if i + 1 < len(toks) else (None, None)
            occ[w].append((d['id'], pos, len(seq),
                           'GRA' in logos, len(logos),
                           'ЧИСЛО' if nxt[0] == 'NUM' else
                           (nxt[1]['norm'][:10] if nxt[0] == 'WORD'
                            and nxt[1] else '—')))

print(f'HT-документов (>=2 слов, адм.): {ht_docs}')
cover = set()
for w in CUR:
    print(f'=== {w} — {len(occ[w])} вхождений ===')
    for did, pos, nw, gra, nl, nxt in occ[w]:
        cover.add(did)
        print(f'   {did:<10} поз={pos:<5} слов={nw:<3} '
              f'{"GRA" if gra else "   "} логогр.{nl} далее={nxt}')
print(f'\nпокрытие HT-документов кураторами-кандидатами: {len(cover)}/{ht_docs} '
      f'({len(cover) / ht_docs:.0%}; KN-коллекторы в D-сериях ~30% — внешняя '
      f'справка)')
print('''
Чтение: если кандидаты ведут себя как коллекторы (первая позиция,
многословные документы, товарные логограммы, повтор между табличками) —
у HT есть аналог «кураторского» слоя; дескриптивно, класс = кандидат.''')
