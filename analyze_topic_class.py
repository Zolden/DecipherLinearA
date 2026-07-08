# -*- coding: utf-8 -*-
"""Этап 19 (§CB): топик-класс — распределительный профиль заголовков
перед второпозиционными TE/SA-RA2 (§BW).

Для каждого заголовка — профиль по всему корпусу: частота, документы,
сайты, доля «за словом сразу число» (именной признак списков, §F),
доля вхождений в религиозных сериях (Z*-объекты), длина. Сравнение с
профилями якорных имён (§BN), топонимов и операторов (§BC). Разведочно,
без формального теста (19 типов); вердикт в дистрибутивных терминах.
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

corpus = pickle.load(open('corpus.pkl', 'rb'))

prof = defaultdict(lambda: {'n': 0, 'docs': set(), 'sites': set(),
                            'num': 0, 'rel': 0})
docs = []
for d in corpus:
    toks = d['toks']
    ws = [(i, v['norm']) for i, (k, v) in enumerate(toks)
          if k == 'WORD' and v['syllabic']]
    seq = [w for _, w in ws]
    if len(seq) >= 3:
        docs.append((d['id'], seq))
    rel = any(z in d['id'] for z in
              ('Za', 'Zb', 'Zc', 'Zd', 'Ze', 'Zf', 'Zg'))
    for i, w in ws:
        p = prof[w]
        p['n'] += 1
        p['docs'].add(d['id'])
        p['sites'].add(d['site'])
        if i + 1 < len(toks) and toks[i + 1][0] == 'NUM':
            p['num'] += 1
        if rel:
            p['rel'] += 1

headers = Counter()
for did, seq in docs:
    if seq[1] in ('TE', 'SA-RA2'):
        headers[seq[0]] += 1

ANCH = ['DA-I-PI-TA', 'I-TA-JA', 'KI-DA-RO', 'PA-RA-NE', 'TA-NA-TI',
        'I-JA-TE']
TOPO = ['PA-I-TO', 'SE-TO-I-JA', 'SU-KI-RI-TA']
OPS = ['KU-RO', 'KI-RO', 'A-DU', 'TE', 'SA-RA2']

def line(w, tag=''):
    p = prof.get(w)
    if not p or not p['n']:
        return
    print(f'   {w:<20} n={p["n"]:<4} док={len(p["docs"]):<4}'
          f'сайт={len(p["sites"]):<3} +число={p["num"] / p["n"]:>4.0%} '
          f'религ={p["rel"] / p["n"]:>4.0%}  {tag}')

print('=== заголовки перед TE/SA-RA2 ===')
for w, c in headers.most_common():
    line(w, f'(заголовок ×{c})')

def group_stats(wlist, label):
    ns = [prof[w] for w in wlist if prof.get(w, {}).get('n')]
    if not ns:
        return
    tot = sum(p['n'] for p in ns)
    num = sum(p['num'] for p in ns)
    rel = sum(p['rel'] for p in ns)
    print(f'{label:<28} токенов {tot:>4}, +число {num / tot:>4.0%}, '
          f'религ {rel / tot:>4.0%}')

print('\n=== сравнение классов (агрегаты) ===')
group_stats(list(headers), 'заголовки перед TE/SA-RA2')
group_stats(ANCH, 'якорные имена (§BN)')
group_stats(TOPO, 'топонимы-якоря')
group_stats(OPS, 'операторы')
allw = [w for w in prof if prof[w]['n'] >= 2]
tot = sum(prof[w]['n'] for w in allw)
num = sum(prof[w]['num'] for w in allw)
rel = sum(prof[w]['rel'] for w in allw)
print(f'{"лексикон (n>=2), фон":<28} токенов {tot:>4}, '
      f'+число {num / tot:>4.0%}, религ {rel / tot:>4.0%}')
print('''
Чтение: разведочно (19 типов заголовков). Признак «+число» — маркёр
именных списков (§F); высокая доля у заголовков сближает их с именным
классом, низкая — с товарно-логограммным.''')
