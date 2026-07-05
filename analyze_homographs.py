# -*- coding: utf-8 -*-
"""Задача E: омографы LA-слов с лексиконом LB (с статистическим контролем).

Читаем полные LA-слова через гомоморфные LB-значения и сопоставляем со списком
критских топонимов, засвидетельствованных в LB (Кносские таблички).
ЭТО НЕ ЧТЕНИЯ: совпадение = «кандидат-омограф», значимость оценивается
перестановочным нулём.

Списки:
- TIER1 (минимум из постановки): pa-i-to, ko-no-so, a-mi-ni-so, ku-do-ni-ja,
  tu-ri-so, su-ki-ri-ta, se-to-i-ja, di-ka-ta, ru-ki-to, e-ko-so, pu-so.
- TIER2 (стандартные топонимы Кносских табличек, McArthur, Docs^2): a-pa-ta-wa,
  da-wo, do-ti-ja, e-ra, ku-ta-to, qa-ra, ra-ja, ra-su-to, ra-to, ri-jo-no,
  si-ra-ro, su-ri-mo, tu-ni-ja, u-ta-no, wa-to, pu-na-so, ti-ri-to, qa-mo.

Нуль-модели (обе сохраняют длины слов и частоты знаков):
- Null-A: пул всех знаковых вхождений лексикона перемешивается и раздаётся в тот
  же профиль длин.
- Null-B (строже): перемешивание отдельно внутри позиционных классов
  (начальная/срединная/конечная) — сохраняет позиционную типологию знаков (задача D).
R=10000, seed=42. p разведочные.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); lex_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
            lex_docs[tuple(v['signs'])].add(d['id'])
words = sorted(lex)

TIER1 = ['pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'ku-do-ni-ja', 'tu-ri-so',
         'su-ki-ri-ta', 'se-to-i-ja', 'di-ka-ta', 'ru-ki-to', 'e-ko-so', 'pu-so']
TIER2 = ['a-pa-ta-wa', 'da-wo', 'do-ti-ja', 'e-ra', 'ku-ta-to', 'qa-ra', 'ra-ja',
         'ra-su-to', 'ra-to', 'ri-jo-no', 'si-ra-ro', 'su-ri-mo', 'tu-ni-ja',
         'u-ta-no', 'wa-to', 'pu-na-so', 'ti-ri-to', 'qa-mo']

def read_lb(w):
    """LA-слово (кортеж знаков) -> строка LB-чтения или None (нечитаемый знак)."""
    out = []
    for s in w:
        if s.startswith('*') or '+' in s: return None
        out.append(s.lower())
    return '-'.join(out)

def match_count(word_list, targets):
    hits = []
    tset = set(targets)
    for w in word_list:
        r = read_lb(w)
        if r and r in tset:
            hits.append((w, r))
    return hits

# --- наблюдаемое
for name, targets in [('TIER1', TIER1), ('TIER1+TIER2', TIER1 + TIER2)]:
    hits = match_count(words, targets)
    print(f'=== {name} ({len(targets)} топонимов) ===')
    print(f'наблюдаемо кандидатов-омографов: {len(hits)}')
    for w, r in hits:
        print(f'  {"-".join(w)} == {r}  токенов={lex[w]}  док.: {sorted(lex_docs[w])}')

# --- нуль-модели
sign_pool = []          # все вхождения знаков по типам слов (тип = 1 раз)
lengths = [len(w) for w in words]
for w in words: sign_pool.extend(w)
# позиционные классы
pos_pools = {0: [], 1: [], 2: []}
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)

def null_A():
    random.shuffle(sign_pool)
    out = []; i = 0
    for L in lengths:
        out.append(tuple(sign_pool[i:i + L])); i += L
    return out

def null_B():
    for p in pos_pools.values(): random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}
    out = []
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.append(tuple(w))
    return out

for name, targets in [('TIER1', TIER1), ('TIER1+TIER2', TIER1 + TIER2)]:
    obs = len(match_count(words, targets))
    for null_name, fn in [('Null-A (пул)', null_A), ('Null-B (позиционный)', null_B)]:
        cnts = []
        random.seed(42)
        for _ in range(R):
            cnts.append(len(match_count(fn(), targets)))
        m = sum(cnts) / R
        sd = (sum((c - m) ** 2 for c in cnts) / R) ** 0.5
        p = sum(1 for c in cnts if c >= obs) / R
        print(f'{name} / {null_name}: наблюдаемо {obs}, нуль {m:.2f}±{sd:.2f}, '
              f'p(>=набл.)={p:.4f} (R={R}, seed=42)')

# --- справка: сколько LA-слов вообще читаемы через LB
readable = sum(1 for w in words if read_lb(w))
print(f'\nсправка: читаемых через LB слов {readable}/{len(words)}')
print('справка: words_in_linearb.js (lineara.xyz) даёт 36 «identicalWords» по всему '
      'лексикону LB без контроля случайности — не сопоставимо с нашим замкнутым списком.')
