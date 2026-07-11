# -*- coding: utf-8 -*-
"""Этап 36 (§DT-б): скелетные минимальные пары — порт техники этрусков
(их п.3: имена → '*', замещения в слотах; одноклассовость замещений
против нуля).

LA-версия: в документах >=3 слов слова именного слоя (якоря §BN +
почти-омографы §BX + гапаксы длины >=3 — открытая лексика) заменяются
на '*'; рамка = (левый сосед, правый сосед) вокруг каждой позиции;
рамки, засвидетельствованные с >=2 РАЗНЫМИ заполнителями, дают события
замещения. Статистика: доля событий, где оба заполнителя одного класса
(оператор§BC~оператор / '*'~'*') против нуля с перестановкой
заполнителей между рамками (R=10000, seed=42).
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

OPS = {'KU-RO', 'PO-TO-KU-RO', 'KI-RO', 'TE', 'A-DU', 'I-DA', 'SI-RU-TE',
       'SA-RA2', 'KI', 'A-TA-I-*301-WA-JA'}
NAMES = {'PA-I-TO', 'SE-TO-I-JA', 'SU-KI-RI-TA', 'DA-I-PI-TA', 'I-TA-JA',
         'KI-DA-RO', 'PA-RA-NE', 'TA-NA-TI', 'I-JA-TE', 'A-RA-NA-RE',
         'KA-U-DE-TA', 'PI-TA-KE-SI', 'QA-TI-JU'}

corpus = pickle.load(open('corpus.pkl', 'rb'))
freq = Counter()
docs = []
for d in corpus:
    ws = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
    if len(ws) >= 3:
        docs.append(ws)
    for w in ws:
        freq[w] += 1

def wclass(w):
    if w in OPS:
        return 'OP'
    if w in NAMES or (freq[w] == 1 and len(w.split('-')) >= 3):
        return 'NAME'
    return 'OTH'

def skel(w):
    return '*' if wclass(w) == 'NAME' else w

frames = defaultdict(list)          # (лев, прав) -> [класс заполнителя]
for ws in docs:
    sk = [skel(w) for w in ws]
    for i in range(1, len(ws) - 1):
        frames[(sk[i - 1], sk[i + 1])].append(wclass(ws[i]))

events = [(fr, fills) for fr, fills in frames.items()
          if len(fills) >= 2 and len(set(fills)) >= 1]
multi = [(fr, fills) for fr, fills in frames.items() if len(fills) >= 2]

def same_class_rate(frame_fills):
    same = tot = 0
    for fr, fills in frame_fills:
        for i in range(len(fills)):
            for j in range(i + 1, len(fills)):
                tot += 1
                if fills[i] == fills[j]:
                    same += 1
    return same / tot if tot else 0.0, tot

obs, n_pairs = same_class_rate(multi)
print(f'рамок с >=2 заполнителями: {len(multi)}; пар заполнителей: '
      f'{n_pairs}; одноклассовость: {obs:.3f}')
top = sorted(multi, key=lambda kv: -len(kv[1]))[:8]
for fr, fills in top:
    print(f'   [{fr[0]} _ {fr[1]}]: {Counter(fills).most_common()}')

all_fills = [c for _, fills in multi for c in fills]
sizes = [len(fills) for _, fills in multi]
sims = []
for _ in range(R):
    random.shuffle(all_fills)
    idx = 0
    sh = []
    for s in sizes:
        sh.append((None, all_fills[idx:idx + s]))
        idx += s
    r, _t = same_class_rate(sh)
    sims.append(r)
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
p = (sum(1 for x in sims if x >= obs) + 1) / (R + 1)
print(f'нуль (перестановка заполнителей): {mu:.3f}±{sd:.3f}, p={p:.4f}')
print('''
Чтение: одноклассовость замещений в фиксированных рамках = слоты записи
предпочитают заполнители одного функционального класса (парадигматический
зонд этрусков на LA). p разведочное.''')
