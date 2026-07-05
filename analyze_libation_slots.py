# -*- coding: utf-8 -*-
"""Этап 5.2 (§K): слоты формулы возлияний — тест «слот 2 географичен?».

Данные: таблица слотов этапа 2 (results.pkl['rows']: 37 документов, полосы
0..6; 1 = A-TA-I-*301-WA-JA-подобное открытие, 2 = слот-кандидат «место», 3 =
(J)A-SA-SA-RA-ME, 4 = U-NA-KA-NA-SI, 5 = I-PI-NA-MA, 6 = SI-RU-TE, 0 = прочее).

Гипотеза: если слот 2 несёт обозначение места/посвящения, его содержимое должно
быть БОЛЕЕ сайт-специфичным, чем формульные слоты 3–6: два документа одного сайта
чаще делят слово/основу слота 2, чем документы разных сайтов; для слотов 3–6
такой разницы быть не должно (формула общая).

Статистика на слот: среди пар документов с заполненным слотом
   Δ = P(делят элемент | один сайт) − P(делят элемент | разные сайты),
«делят» на двух уровнях: (а) точное слово, (б) общий знаковый БИГРАМ (грубая
«основа», ловит JA-DI-KI-TU ~ A-DI-KI-TE-TE через DI-KI). Нуль: перестановка
сайтов между документами (R=10000, seed=42). p разведочные.
"""
import sys, pickle, random, itertools
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
res = pickle.load(open('results.pkl', 'rb'))
docsx = {d['id']: d for d in corpus}
rows = res['rows']

print(f'документов в таблице слотов этапа 2: {len(rows)}')

# --- проверка покрытия: rel-документы с >=3 полными словами вне таблицы
in_rows = {doc for doc, _, _ in rows}
missed = []
for d in corpus:
    if d['typ'] != 'rel' or d['id'] in in_rows: continue
    ws = [v for k, v in d['toks'] if k == 'WORD' and v['syllabic']
          and len(v['signs']) >= 2]
    if len(ws) >= 3: missed.append((d['id'], d['site'], len(ws)))
print(f'rel-документы с >=3 словами вне таблицы (не в формуле, по этапу 2): '
      f'{len(missed)}: {missed[:12]}')

# --- инвентарь слотов
def norm_word(w):
    return w.replace('…', '').strip('-')

import os
REL_ONLY = os.environ.get('REL_ONLY') == '1'
lane_docs = defaultdict(list)   # lane -> [(doc, site, [слова])]
for doc, typ, lanes in rows:
    if REL_ONLY and doc in docsx and docsx[doc]['typ'] != 'rel':
        continue   # исключаем таблички (HT55a, HT90), попавшие в таблицу этапа 2
    site = docsx[doc]['site'] if doc in docsx else doc[:2]
    for lane, ws in lanes.items():
        ws2 = [norm_word(w) for w in ws if norm_word(w)]
        if ws2: lane_docs[lane].append((doc, site, ws2))
if REL_ONLY: print('РЕЖИМ: только rel-документы (без табличек)')

print('\n=== инвентарь слота 2 (кандидат «место/посвящение») ===')
for doc, site, ws in sorted(lane_docs[2], key=lambda x: x[1]):
    print(f'   {site:<4} {doc:<10} {ws}')

def bigrams(word):
    s = word.split('-')
    return {(s[i], s[i + 1]) for i in range(len(s) - 1)}

def share_exact(a, b):
    return bool(set(a) & set(b))

def share_bigram(a, b):
    ba = set().union(*[bigrams(w) for w in a]) if a else set()
    bb = set().union(*[bigrams(w) for w in b]) if b else set()
    return bool(ba & bb)

print('\n=== сайт-специфичность по слотам ===')
print(f'{"слот":>4}{"док":>5}{"пар same":>9}{"пар diff":>9}'
      f'{"  Δ(точн)":>10}{"p":>8}{"  Δ(бигр)":>10}{"p":>8}')
for lane in (1, 2, 3, 4, 5, 6):
    entries = lane_docs[lane]
    if len(entries) < 4:
        print(f'{lane:>4}{len(entries):>5}   — мало документов'); continue
    sites = [s for _, s, _ in entries]
    words_l = [ws for _, _, ws in entries]
    n = len(entries)
    pairs = list(itertools.combinations(range(n), 2))
    def delta(site_vec, sharef):
        same = [sharef(words_l[i], words_l[j]) for i, j in pairs
                if site_vec[i] == site_vec[j]]
        diff = [sharef(words_l[i], words_l[j]) for i, j in pairs
                if site_vec[i] != site_vec[j]]
        if not same or not diff: return None, len(same), len(diff)
        return sum(same) / len(same) - sum(diff) / len(diff), len(same), len(diff)
    dE, nS, nD = delta(sites, share_exact)
    dB, _, _ = delta(sites, share_bigram)
    if dE is None:
        print(f'{lane:>4}{n:>5}{nS:>9}{nD:>9}   — нет пар одного сайта'); continue
    geE = geB = 0
    sv = sites[:]
    for _ in range(R):
        random.shuffle(sv)
        e2, _, _ = delta(sv, share_exact)
        b2, _, _ = delta(sv, share_bigram)
        if e2 is not None and e2 >= dE - 1e-12: geE += 1
        if b2 is not None and b2 >= dB - 1e-12: geB += 1
    print(f'{lane:>4}{n:>5}{nS:>9}{nD:>9}{dE:>10.3f}{geE / R:>8.4f}'
          f'{dB:>10.3f}{geB / R:>8.4f}')

# --- дескриптивно: повторы внутри слота 2
print('\nповторы элементов слота 2 между документами:')
cnt = Counter()
for _, site, ws in lane_docs[2]:
    for w in ws: cnt[w] += 1
for w, c in cnt.most_common():
    if c >= 2:
        where = [(doc, site) for doc, site, ws in lane_docs[2] if w in ws]
        print(f'   {w}: {c} — {where}')
bg = Counter()
for _, site, ws in lane_docs[2]:
    for b in set().union(*[bigrams(w) for w in ws]):
        bg[b] += 1
print('частые бигамы слота 2:', [(f'{a}-{b}', c) for (a, b), c in bg.most_common(6) if c >= 2])
