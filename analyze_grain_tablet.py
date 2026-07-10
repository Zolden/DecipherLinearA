# -*- coding: utf-8 -*-
"""Этап 28 (§DF-1): АУДИТ-ДЕЙСТВИЕ — зерновой класс на уровне физической
таблички (ответ на находку №3 аудита Sol, INPUT_FROM_SOL.md).

Находка аудита: гипергеометрика §CP/§CT считала СТОРОНЫ табличек (HT86a/b,
HT95a/b) независимыми документами и игнорировала географию (все документы
KU-NI-SU — HT). Здесь единица = физическая табличка (id без финальной
буквы стороны), пул — (а) все таблички корпуса с полными словами,
(б) только таблички сайта кандидата (блокировка по месту). Точная
гипергеометрика. Следствие: семейное P=0.0003 (§CT) РЕТРАГИРУЕТСЯ,
класс переименовывается в «когерентный разведочный».

Также фикс PA-SE: его полные вхождения — HT18/HT27b (не HT86/95, как
неточно сказано в §CX).
"""
import sys, pickle, re
from collections import defaultdict

from scipy.stats import hypergeom

sys.stdout.reconfigure(encoding='utf-8')

corpus = pickle.load(open('corpus.pkl', 'rb'))

def tablet(cid):
    return cid[:-1] if cid and cid[-1] in 'abcd' else cid

lex_tabs = defaultdict(set)
tab_logo = defaultdict(set)
tab_site = {}
all_tabs = set()
for d in corpus:
    tb = tablet(d['id'])
    tab_site[tb] = d['site']
    has_w = False
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex_tabs[v['norm']].add(tb)
            has_w = True
        if k == 'WORD' and not v['syllabic']:
            tab_logo[tb].add(re.split(r'[+]', v['norm'])[0])
    if has_w:
        all_tabs.add(tb)

N_all = len(all_tabs)
K_all = sum(1 for t in all_tabs if 'GRA' in tab_logo.get(t, ()))
print(f'физических табличек с полными словами: {N_all}; с GRA: {K_all}')

CANDS = ['KU-NI-SU', 'KI-RI-TA2', 'KI-RE-TA-NA', 'KI-RE-TA2', 'DI-DE-RU',
         'QA-RA2-WA', 'SA-RU', 'DA-ME', 'A-KA-RU', 'MI-NU-TE', 'PA-SE']
print(f'\n{"слово":<12}{"табл.":>6}{"GRA":>5}{"p(все)":>9}'
      f'{"p(сайт-блок)":>13}  таблички')
n_sig_all = n_sig_site = 0
for w in CANDS:
    tabs = lex_tabs.get(w, set()) & all_tabs
    if not tabs:
        print(f'{w:<12} нет полных вхождений')
        continue
    n = len(tabs)
    hit = sum(1 for t in tabs if 'GRA' in tab_logo.get(t, ()))
    p_all = float(hypergeom.sf(hit - 1, N_all, K_all, n))
    sites = {tab_site[t] for t in tabs}
    pool = {t for t in all_tabs if tab_site[t] in sites}
    Kp = sum(1 for t in pool if 'GRA' in tab_logo.get(t, ()))
    p_site = float(hypergeom.sf(hit - 1, len(pool), Kp, n))
    n_sig_all += p_all < 0.05
    n_sig_site += p_site < 0.05
    print(f'{w:<12}{n:>6}{hit:>5}{p_all:>9.4f}{p_site:>13.4f}  '
          f'{sorted(tabs)[:5]}')
print(f'\nзначимых (p<0.05): на всём пуле {n_sig_all}, '
      f'при сайт-блокировке {n_sig_site} (из {len(CANDS)})')
print('''
ВЕРДИКТ (по аудиту Sol): на уровне физической таблички с сайт-блокировкой
зерновой класс статистической значимости НЕ имеет — семейное P=0.0003
(§CT) ретрагировано; класс сохраняется как когерентный разведочный
(фонетика культурных слов + структура списков HT86/95 + чистая
метрология), требующий подтверждения на новых табличках. Единица
независимости всех будущих документных тестов — физическая табличка.''')
