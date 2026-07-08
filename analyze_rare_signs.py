# -*- coding: utf-8 -*-
"""Этап 16 (§BP): аудит редких знаков на концентрацию по памятникам —
перенос урока №4 из DecipherEtruscan (редкая графема может быть особенностью
ровно одного текста/резчика, а не фонемой системы).

Для каждого *-знака и компаунда: документов, сайтов, писцов; доля вхождений
в самом частом документе; флаг «одномонументный». Проверка задним числом:
не строились ли наши вердикты §J/§AP на одномонументных знаках.
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

sign_occ = defaultdict(list)   # sign -> [(doc, site, scribe)]
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic']:
            for s in v['signs']:
                if s.startswith('*') or '+' in s:
                    sign_occ[s].append((d['id'], d['site'], d['scribe']))

VERDICT_SIGNS = {'*301': 'CV', '*21F': 'CV', '*118': 'CV', '*49': 'CV',
                 '*312': 'V', '*333': 'V', '*815': 'V', '*306': 'Z-канд.',
                 '*86': '~V', '*350': '—', '*34': '—', '*314': '—'}

print(f'{"знак":<12}{"ток":>4}{"док":>4}{"сайт":>5}{"писц":>5}'
      f'{"макс.доля в 1 док":>18}  вердикт§J  флаг')
rows = []
for s, occ in sorted(sign_occ.items(), key=lambda kv: -len(kv[1])):
    n = len(occ)
    if n < 2: continue
    docs = Counter(d for d, _, _ in occ)
    sites = len({x for _, x, _ in occ})
    scribes = len({sc for _, _, sc in occ if sc})
    top_doc, top_n = docs.most_common(1)[0]
    conc = top_n / n
    flag = ''
    if len(docs) == 1:
        flag = 'ОДНОМОНУМЕНТНЫЙ'
    elif conc >= 0.8:
        flag = f'концентрирован ({top_doc})'
    verd = VERDICT_SIGNS.get(s, '')
    if n >= 3 or verd:
        print(f'{s:<12}{n:>4}{len(docs):>4}{sites:>5}{scribes:>5}'
              f'{conc:>17.0%}   {verd:<9} {flag}')
        rows.append((s, n, len(docs), flag, verd))

mono = [r for r in rows if r[3] == 'ОДНОМОНУМЕНТНЫЙ']
print(f'\nодномонументных знаков (>=2 вхождений в одном документе): {len(mono)}')
affected = [r for r in rows if r[4] and r[3]]
print('вердикты §J/§AP, задетые концентрацией:',
      [(s, v, f) for s, n, nd, f, v in affected] or 'НЕТ')
