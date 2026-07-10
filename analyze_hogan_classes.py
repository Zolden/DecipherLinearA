# -*- coding: utf-8 -*-
"""Этап 27 (§DD): типы документов Хогана × наши слои.

Для каждого из его типов (transactions.js): доля документов с KU-RO,
с второпозиционными TE/SA-RA2, с зерновым классом §CP/§CX, с якорями,
среднее число полных слов. Плюс тест: KU-RO чаще в Transfer-семействе,
чем в Entity Lists (Fisher). Вне стресс-ростера (гитигнорный кэш).
"""
import sys, json, pickle
from collections import Counter, defaultdict

from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')

txt = open('.hogan_cache.js', encoding='utf-8').read()
data = json.loads(txt[txt.find('['):txt.rfind(']') + 1])
type_of = {t['name'].replace(' ', ''): t.get('type', '?') for t in data}

GRAIN = {'KU-NI-SU', 'KI-RI-TA2', 'KI-RE-TA-NA', 'KI-RE-TA2', 'DI-DE-RU',
         'QA-RA2-WA', 'SA-RU', 'DA-ME', 'A-KA-RU'}
ANCH = {'DA-I-PI-TA', 'I-TA-JA', 'KI-DA-RO', 'PA-RA-NE', 'TA-NA-TI',
        'I-JA-TE', 'PA-I-TO', 'SE-TO-I-JA', 'SU-KI-RI-TA'}

corpus = pickle.load(open('corpus.pkl', 'rb'))
feat = {}
for d in corpus:
    if d['id'] not in type_of:
        continue
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    feat[d['id']] = {
        'kuro': 'KU-RO' in ws or 'PO-TO-KU-RO' in ws,
        'sec': len(ws) >= 2 and ws[1] in ('TE', 'SA-RA2'),
        'grain': any(w in GRAIN for w in ws),
        'anchor': any(w in ANCH for w in ws),
        'nw': len(ws),
    }

groups = defaultdict(list)
for did, tp in type_of.items():
    if did in feat:
        groups[tp].append(feat[did])

print(f'{"тип Хогана":<48}{"n":>4}{"KU-RO":>7}{"вт.TE/SA":>9}'
      f'{"зерно":>7}{"якоря":>7}{"слов":>6}')
for tp, fs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    n = len(fs)
    print(f'{tp[:47]:<48}{n:>4}'
          f'{sum(f["kuro"] for f in fs) / n:>7.0%}'
          f'{sum(f["sec"] for f in fs) / n:>9.0%}'
          f'{sum(f["grain"] for f in fs) / n:>7.0%}'
          f'{sum(f["anchor"] for f in fs) / n:>7.0%}'
          f'{sum(f["nw"] for f in fs) / n:>6.1f}')

transfer = [f for tp, fs in groups.items() if 'Transfer' in tp for f in fs]
entity = [f for tp, fs in groups.items()
          if 'Entity List' in tp and 'Transfer' not in tp for f in fs]
a = sum(f['kuro'] for f in transfer)
b = len(transfer) - a
c = sum(f['kuro'] for f in entity)
d2 = len(entity) - c
odds, p = fisher_exact([[a, b], [c, d2]], alternative='greater')
print(f'\nKU-RO: Transfer-семейство {a}/{len(transfer)} против '
      f'Entity Lists {c}/{len(entity)}; Fisher p={p:.4f}')
print('''
Чтение: его типология — интерпретационная сетка; наши слои — статистика.
Согласованные градиенты (итоги в Transfer, зерно в товарных типах) =
взаимная поддержка; p разведочные.''')
