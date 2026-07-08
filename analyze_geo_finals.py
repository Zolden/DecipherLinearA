# -*- coding: utf-8 -*-
"""Этап 22 (§CN): гео-вариантность финалей — системный тест.

§CI показал на 5 парах: варианты финала разнесены по сайтам. Здесь — все
многофинальные основы решётки §CK: статистика «сайт-чистоты» — по каждой
основе доля пар (вхождение_i, вхождение_j) с РАЗНЫМИ финалями, которые
лежат на разных сайтах; агрегат по основам. Нуль: перестановка
сайт-меток вхождений ВНУТРИ основы (структура частот финалей сохранена),
R=10000. Плюс дескриптив: сайт-профили популярных финалей.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
occ = defaultdict(list)                   # слово -> [сайт]
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 3 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            occ[tuple(v['signs'])].append(d['site'])

stems = defaultdict(list)                 # основа -> [(финал, сайт)]
for w, sites in occ.items():
    for s in sites:
        stems[w[:-1]].append((w[-1], s))
multi = {st: fs for st, fs in stems.items()
         if len({f for f, _ in fs}) >= 2}
print(f'многофинальных основ (токен-уровень): {len(multi)}')

def cross_site_share(fs):
    num = den = 0
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            if fs[i][0] != fs[j][0]:
                den += 1
                if fs[i][1] != fs[j][1]:
                    num += 1
    return num, den

obs_n = obs_d = 0
for st, fs in multi.items():
    n, dn = cross_site_share(fs)
    obs_n += n
    obs_d += dn
obs = obs_n / obs_d
print(f'пар вхождений с разными финалями: {obs_d}; из них на разных '
      f'сайтах: {obs_n} ({obs:.0%})')

sims = []
for _ in range(R):
    sn = sd_ = 0
    for st, fs in multi.items():
        sites = [s for _, s in fs]
        random.shuffle(sites)
        fs2 = [(f, s2) for (f, _), s2 in zip(fs, sites)]
        n, dn = cross_site_share(fs2)
        sn += n
        sd_ += dn
    sims.append(sn / sd_)
mu = sum(sims) / R
sd = (sum((x - mu) ** 2 for x in sims) / R) ** 0.5
p = sum(1 for x in sims if x >= obs) / R
print(f'нуль (перестановка сайтов внутри основ): {mu:.2%}±{sd:.2%}, '
      f'p={p:.4f}')

print('\nсайт-профили основ с разными финалями:')
for st, fs in sorted(multi.items()):
    prof = defaultdict(Counter)
    for f, s in fs:
        prof[f][s] += 1
    print(f'   {"-".join(st):<16} ' + '; '.join(
        f'{f}:{dict(c)}' for f, c in sorted(prof.items())))
print('''
Чтение: p разведочное, односторонний (избыток «разных сайтов» у разных
финалей = гео-обусловленность вариантов). Значимость поддержала бы
«региональную вариантность» §CI на всём материале; незначимость вернула
бы вес морфологической интерпретации.''')
