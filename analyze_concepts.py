# -*- coding: utf-8 -*-
"""Этап 23 (§CP): «семантический туман» — порт tools/etr_concepts.py из
DecipherEtruscan на Linear A (по прямой передаче их треда: «тот же CSV,
тот же скрипт с заменой корпуса; первоочередной тест — KU-NI-SU ↔
kunāšu/полба»).

Метод: concept_lexicon.csv (230 понятий эпохи × формы в 7 расшифрованных
языках; кураторская таблица DecipherEtruscan) → скелеты звуко-классов →
(1) конвергентные понятия (Wanderwörter, нуль перестановкой форм внутри
языков) → (2) зонд по лексикону LA (чтение через LB-значения).

ДИСЦИПЛИНА LA (жёстче этрусской): глосс у LA НЕТ, поэтому hit@1-калибровка
невозможна. Замена — РАСПРЕДЕЛИТЕЛЬНАЯ проверка только для товарных
доменов: фонетический кандидат обязан со-встречаться с логограммой своего
товара (kunāšu «полба» → GRA) чаще случайного (перестановочный нуль по
документам, R=1000). Результат — не «значение», а «кандидат-соответствие,
согласующееся с товарным классом»; туман публикуется как
гипотезогенератор с этой оговоркой в каждой строке вывода.
"""
import csv
import pickle
import re
import sys
from collections import Counter, defaultdict

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
SEED = 42
R_CONV = 200
R_DOC = 1000
SIM_PAIR = 0.7
SIM_LA = 0.75
MIN_SK = 3
LANGS = ['grc', 'lat', 'hit', 'akk', 'heb', 'egy', 'sum']

DIGRAPH = {'sh': 'S', 'th': 'T', 'kh': 'K', 'ch': 'K', 'ph': 'P',
           'ts': 'S', 'dj': 'S', 'tj': 'S', 'ng': 'N'}
SINGLE = {'p': 'P', 'b': 'P', 'f': 'P', 'v': 'W', 'w': 'W',
          't': 'T', 'd': 'T', 'k': 'K', 'g': 'K', 'q': 'K', 'c': 'K',
          'x': 'K', 's': 'S', 'z': 'S', 'm': 'M', 'n': 'N', 'l': 'L',
          'r': 'R', 'j': 'J', 'y': 'J', 'h': 'H'}

def skeleton(form):
    f = form.lower().strip().strip('?')
    f = re.sub(r'[^a-z]', '', f)
    out = []
    i = 0
    while i < len(f):
        if f[i:i + 2] in DIGRAPH:
            out.append(DIGRAPH[f[i:i + 2]])
            i += 2
            continue
        c = SINGLE.get(f[i])
        if c:
            out.append(c)
        i += 1
    return ''.join(out)

def lev(a, b):
    if not a or not b:
        return max(len(a), len(b))
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

def sim(a, b):
    if not a or not b:
        return 0.0
    return 1.0 - lev(a, b) / max(len(a), len(b))

rng = np.random.default_rng(SEED)
rows = list(csv.DictReader(open('concept_lexicon.csv', encoding='utf-8')))
concepts = []
n_forms = 0
for r in rows:
    forms = {}
    for lg in LANGS:
        cell = (r.get(lg) or '').strip()
        fs = []
        for v in cell.split('/'):
            v = v.strip()
            if not v:
                continue
            sk = skeleton(v)
            if len(sk) >= 2:
                fs.append((v, sk))
                n_forms += 1
        if fs:
            forms[lg] = fs
    concepts.append({'id': r['id'], 'en': r['gloss_en'], 'ru': r['gloss_ru'],
                     'dom': r['domain'], 'forms': forms})
print(f'понятий: {len(concepts)}; форм: {n_forms} (CSV DecipherEtruscan)')

# --- 1. конвергентные понятия
def conv_score(forms):
    s = 0
    lgs = sorted(forms)
    for i in range(len(lgs)):
        for j in range(i + 1, len(lgs)):
            best = max((sim(a[1], b[1]) for a in forms[lgs[i]]
                        for b in forms[lgs[j]]), default=0)
            s += best >= SIM_PAIR
    return s

obs = [conv_score(c['forms']) for c in concepts]
cols = {lg: [c['forms'].get(lg) for c in concepts] for lg in LANGS}
pool = []
for _ in range(R_CONV):
    sh = {lg: [cols[lg][i] for i in rng.permutation(len(concepts))]
          for lg in LANGS}
    for ci in range(len(concepts)):
        f = {lg: sh[lg][ci] for lg in LANGS if sh[lg][ci]}
        pool.append(conv_score(f))
pool = np.array(pool)
p_conv = [(float(((pool >= o).sum() + 1) / (len(pool) + 1)), o) for o in obs]
conv_set = [c for c, (p, o) in zip(concepts, p_conv) if o >= 2 and p < 0.05]
print(f'конвергентных понятий (счёт>=2, p<0.05): {len(conv_set)}')

# --- 2. лексикон LA через LB-значения
corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
lex_docs = defaultdict(set)
doc_logo = defaultdict(set)
all_docs = set()
for d in corpus:
    has_w = False
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            w = tuple(v['signs'])
            if all(not s.startswith('*') and '+' not in s for s in w):
                lex[w] += 1
                lex_docs[w].add(d['id'])
                has_w = True
        if k == 'WORD' and not v['syllabic']:
            doc_logo[d['id']].add(re.split(r'[+]', v['norm'])[0])
    if has_w:
        all_docs.add(d['id'])
vocab = sorted(lex)
print(f'слов LA (полных, читаемых): {len(vocab)}; документов: {len(all_docs)}')

def la_string(w):
    return ''.join(re.sub(r'\d', '', s.lower()) for s in w)

def stems_of_la(w):
    out = {la_string(w)}
    if len(w) >= 3:
        out.add(la_string(w[:-1]))                    # финальный слот §CK
    if w[0] in ('A', 'I', 'JA') and len(w) >= 3:
        out.add(la_string(w[1:]))                     # приставки §L/§AB
    return out

sk_cache = {w: [skeleton(s) for s in stems_of_la(w)] for w in vocab}

# ярусы: A — конвергентные (все языки); B — контактный канал LA:
# akk (ближневосточная торговля) + grc (эгейский субстрат в греческом)
conv_forms = []
seen_f = set()
for c in conv_set:
    for lg, fs in c['forms'].items():
        for v, sk in fs:
            key = (c['id'], lg, v)
            if key not in seen_f:
                seen_f.add(key)
                conv_forms.append((c, lg, v, sk, 'A'))
for c in concepts:
    for lg in ('akk', 'grc'):
        for v, sk in c['forms'].get(lg, []):
            key = (c['id'], lg, v)
            if key not in seen_f:
                seen_f.add(key)
                conv_forms.append((c, lg, v, sk, 'B'))
nA = sum(1 for x in conv_forms if x[4] == 'A')
print(f'форм в зонде: {len(conv_forms)} (ярус A: {nA}; '
      f'ярус B akk+grc: {len(conv_forms) - nA})')

# --- 3. распределительная проверка товарных доменов (замена глосс-калибровки)
LOGO_MAP = {'wine': 'VIN', 'grain': 'GRA', 'barley': 'GRA', 'wheat': 'GRA',
            'emmer': 'GRA', 'olive oil': 'OLE', 'oil': 'OLE',
            'olive': 'OLIV', 'fig': 'NI', 'figs': 'NI', 'cyperus': 'CYP',
            'man': 'VIR', 'woman': 'MUL', 'copper': 'AES', 'bronze': 'AES'}

def logo_for(concept_en):
    for k, v in LOGO_MAP.items():
        if k in concept_en.lower():
            return v
    return None

def doc_test(w, logo):
    docs = lex_docs[w]
    hit = sum(1 for d in docs if logo in doc_logo.get(d, ()))
    pool_docs = sorted(all_docs)
    n = len(docs)
    sims = np.zeros(R_DOC, dtype=np.int32)
    for r_i in range(R_DOC):
        pick = rng.choice(len(pool_docs), size=n, replace=False)
        sims[r_i] = sum(1 for i in pick
                        if logo in doc_logo.get(pool_docs[i], ()))
    p = float(((sims >= hit).sum() + 1) / (R_DOC + 1))
    return hit, n, float(sims.mean()), p

# --- 4. первоочередной тест: KU-NI-SU ↔ kunāšu (полба) → GRA
print('\n=== первоочередной тест: KU-NI-SU ↔ kunāšu «полба» ===')
KNS = ('KU', 'NI', 'SU')
if KNS in lex:
    sk_w = skeleton(la_string(KNS))
    sk_k = skeleton('kunashu')
    print(f'скелеты: KU-NI-SU={sk_w}, kunāšu={sk_k}, sim={sim(sk_w, sk_k):.2f}')
    hit, n, mu, p = doc_test(KNS, 'GRA')
    print(f'документы KU-NI-SU: {sorted(lex_docs[KNS])}')
    print(f'со-встречаемость с GRA: {hit}/{n} документов '
          f'(нуль {mu:.2f}, p={p:.4f})')
    hit2, n2, mu2, p2 = doc_test(KNS, 'VIN')
    print(f'негативный контроль (VIN): {hit2}/{n2} (нуль {mu2:.2f}, '
          f'p={p2:.4f})')

# --- 5. туман: кандидаты по всему лексикону (ничьи по sim сохраняются:
# скелеты грубые, коллизии типа KRT=krithē/egertu разрешает только
# распределительная проверка)
def best_for(w):
    best_s = 0.0
    ties = []
    for sk_w in sk_cache[w]:
        if len(sk_w) < MIN_SK:
            continue
        for c, lg, v, sk, tier in conv_forms:
            if len(sk) < MIN_SK:
                continue
            s = sim(sk_w, sk)
            if s > best_s + 1e-9:
                best_s = s
                ties = [(c, lg, v, tier)]
            elif abs(s - best_s) < 1e-9 and s > 0:
                ties.append((c, lg, v, tier))
    seen_c = set()
    uniq = []
    for c, lg, v, tier in ties:
        if c['id'] not in seen_c:
            seen_c.add(c['id'])
            uniq.append((c, lg, v, tier))
    return best_s, uniq[:4]

n_fog = 0
fog_rows = []
for w in vocab:
    s, ties = best_for(w)
    if s >= SIM_LA and ties:
        dist = ''
        for c, lg, v, tier in ties:          # проверяем первый товарный
            logo = logo_for(c['en'])
            if logo:
                hit, n, mu, p = doc_test(w, logo)
                dist = (f'{logo}({c["en"]}):{hit}/{n} '
                        f'(нуль {mu:.1f}, p={p:.3f})')
                break
        c0, lg0, v0, t0 = ties[0]
        fog_rows.append(('-'.join(w), lex[w],
                         '|'.join(c['en'] for c, *_ in ties),
                         '|'.join(c['ru'] for c, *_ in ties),
                         c0['dom'], lg0,
                         '|'.join(v for _, _, v, _ in ties),
                         f'{s:.3f}', t0, dist))
        n_fog += 1

with open('concept_fog_la.csv', 'w', encoding='utf-8', newline='') as f:
    wcsv = csv.writer(f)
    wcsv.writerow(['word', 'freq', 'concept_en', 'concept_ru', 'domain',
                   'lang', 'form', 'sim', 'tier', 'logo_check'])
    for r in fog_rows:
        wcsv.writerow(r)
print(f'\nтуман: {n_fog} слов с sim>={SIM_LA} → concept_fog_la.csv')
print('строки с распределительной проверкой (товарные домены):')
for r in fog_rows:
    if r[9]:
        print(f'   {r[0]:<16} ~ {r[6]:<12} [{r[2]}/{r[3]}] sim={r[7]} '
              f'{r[9]}')
print('''
Чтение: глосс-калибровки в LA НЕ существует — туман строго
гипотезогенераторный; единственная внутренняя проверка — со-встречаемость
с логограммой товара (перестановочный нуль по документам). Ни одна строка
не является «переводом»; формулировки — «кандидат-соответствие,
согласующееся с товарным классом». Таблица понятий — данные
DecipherEtruscan (кураторская), метод — их etr_concepts.py.''')
