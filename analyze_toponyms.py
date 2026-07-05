# -*- coding: utf-8 -*-
"""Задача H (этап 4): топонимный каркас.

Три части:
H1. Расширение омографического теста §E: к 29 топонимам добавлены
    засвидетельствованные в LB этниконы/прилагательные критских топонимов
    (pa-i-ti-jo/-ja, a-mi-ni-si-jo/-ja, ko-no-si-jo/-ja, ku-ta-ti-jo/-ja,
    ra-ti-jo, ru-ki-ti-jo/-ja, ti-ri-ti-jo/-ja, wa-ti-jo, di-ka-ta-jo — KN Fp 1).
    Нуль-модели те же, что в §E (Null-A пул, Null-B позиционный), R=10000, seed=42.
H2. Поведенческий профиль кандидатов-омографов: все вхождения (включая неполные),
    сайт, тип документа, позиция, числа рядом, производные формы (слова, деляшие
    основу с кандидатом). Дескриптивно: ведут ли себя кандидаты как топонимы.
H3. Поведенческий шорт-лист «топонимоподобных» слов LA для будущего сопоставления:
    повторяющиеся слова табличек с преобладанием позиции заголовка.
    Плюс справка: серии LB-аттестаций «identicalWords» из words_in_linearb.js
    (без контроля случайности — только дескриптивно).

Формулировки: только «кандидат», «согласуется с». Совпадение != чтение.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))

# ---------------- лексикон (фильтры этапа 2) и вспомогательные индексы
lex = Counter(); lex_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
            lex_docs[tuple(v['signs'])].add(d['id'])
words = sorted(lex)
docsx = {d['id']: d for d in corpus}

TIER1 = ['pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'ku-do-ni-ja', 'tu-ri-so',
         'su-ki-ri-ta', 'se-to-i-ja', 'di-ka-ta', 'ru-ki-to', 'e-ko-so', 'pu-so']
TIER2 = ['a-pa-ta-wa', 'da-wo', 'do-ti-ja', 'e-ra', 'ku-ta-to', 'qa-ra', 'ra-ja',
         'ra-su-to', 'ra-to', 'ri-jo-no', 'si-ra-ro', 'su-ri-mo', 'tu-ni-ja',
         'u-ta-no', 'wa-to', 'pu-na-so', 'ti-ri-to', 'qa-mo']
ETHNICA = ['pa-i-ti-jo', 'pa-i-ti-ja', 'a-mi-ni-si-jo', 'a-mi-ni-si-ja',
           'ko-no-si-jo', 'ko-no-si-ja', 'ku-ta-ti-jo', 'ku-ta-ti-ja',
           'ra-ti-jo', 'ru-ki-ti-jo', 'ru-ki-ti-ja', 'ti-ri-ti-jo',
           'ti-ri-ti-ja', 'wa-ti-jo', 'di-ka-ta-jo']

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s: return None
        out.append(s.lower())
    return '-'.join(out)

def matches(word_list, targets):
    tset = set(targets)
    return [(w, read_lb(w)) for w in word_list if read_lb(w) in tset]

# ---------------- H1: расширенный тест
print('=== H1. Омографический тест с этниконами ===')
for name, targets in [('TIER1+2 (29 топонимов)', TIER1 + TIER2),
                      ('ETHNICA (15 этниконов)', ETHNICA),
                      ('ВСЕ (44)', TIER1 + TIER2 + ETHNICA)]:
    hits = matches(words, targets)
    print(f'{name}: наблюдаемо {len(hits)}')
    for w, r in hits:
        print(f'   {"-".join(w)} == {r}  токенов={lex[w]}  док.: {sorted(lex_docs[w])}')

sign_pool = []; lengths = [len(w) for w in words]
for w in words: sign_pool.extend(w)
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
    idx = {0: 0, 1: 0, 2: 0}; out = []
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.append(tuple(w))
    return out

for name, targets in [('ETHNICA', ETHNICA), ('ВСЕ (44)', TIER1 + TIER2 + ETHNICA)]:
    obs = len(matches(words, targets))
    for nn, fn in [('Null-A', null_A), ('Null-B', null_B)]:
        random.seed(42)
        cnts = [len(matches(fn(), targets)) for _ in range(R)]
        m = sum(cnts) / R
        sd = (sum((c - m) ** 2 for c in cnts) / R) ** 0.5
        p = sum(1 for c in cnts if c >= obs) / R
        print(f'{name} / {nn}: наблюдаемо {obs}, нуль {m:.2f}±{sd:.2f}, '
              f'p={p:.4f} (R={R}, seed=42)')

# ---------------- H2: поведенческий профиль кандидатов
print('\n=== H2. Поведение кандидатов в корпусе ===')
CANDS = [('PA', 'I', 'TO'), ('SE', 'TO', 'I', 'JA'), ('SU', 'KI', 'RI', 'TA')]

def occurrences(sig):
    """Все вхождения слова (включая неполные документы), с контекстом."""
    out = []
    for d in corpus:
        toks = d['toks']
        widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
        for i in widx:
            v = toks[i][1]
            if tuple(v['signs']) != sig: continue
            nval = None
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM': nval = toks[j][1]['val']; break
                if toks[j][0] == 'WORD': break
            out.append({'doc': d['id'], 'site': d['site'], 'typ': d['typ'],
                        'support': d['support'], 'init': i == widx[0],
                        'num': nval})
    return out

for sig in CANDS:
    occ = occurrences(sig)
    print(f'\n{"-".join(sig)}:')
    for o in occ:
        print(f'   {o["doc"]} ({o["site"]}, {o["support"]}, {o["typ"]}) '
              f'{"ЗАГОЛОВОК" if o["init"] else "запись"} '
              f'{"число=" + str(o["num"]) if o["num"] is not None else "без числа"}')
    # производные: слова лексикона, делящие с кандидатом основу (все знаки, кроме
    # последнего, или кандидат — префикс слова)
    der = []
    for w in words:
        if w == sig: continue
        if w[:len(sig)] == sig or (len(w) >= len(sig) - 1 and
                                   w[:len(sig) - 1] == sig[:len(sig) - 1]):
            der.append(w)
    if der:
        print('   слова с общей основой:',
              [f'{"-".join(w)} ({",".join(sorted(lex_docs[w]))})' for w in der])

# DI-KI-TE-стем в формулах возлияний (проверка известной гипотезы «Дикте»)
print('\nDI-K-стем в формулах (гипотеза оронима Дикте; LB di-ka-ta — гласные НЕ совпадают):')
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and 'DI-KI-T' in v['norm'] or \
           (k == 'WORD' and v['norm'].startswith(('A-DI-KI', 'JA-DI-KI'))):
            print(f'   {v["norm"]} — {d["id"]} ({d["site"]}, {d["typ"]})')

# ---------------- H3: топонимоподобные слова (шорт-лист на будущее)
print('\n=== H3. Поведенческий шорт-лист «топонимоподобных» слов ===')
print('критерий: >=3 токенов, >=50% вхождений — первое слово таблички')
prof = defaultdict(lambda: [0, 0, set()])   # word -> [init_count, total, sites]
for d in corpus:
    if not d['is_tablet']: continue
    toks = d['toks']
    widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
    for i in widx:
        v = toks[i][1]
        if not (v['syllabic'] and len(v['signs']) >= 2 and v['complete']
                and not (v['gap'] or v['trunc_l'] or v['trunc_r'])):
            continue
        w = tuple(v['signs'])
        prof[w][1] += 1
        prof[w][2].add(d['site'])
        if i == widx[0]: prof[w][0] += 1
short = [(w, a, t, sorted(s)) for w, (a, t, s) in prof.items()
         if t >= 3 and a / t >= 0.5]
short.sort(key=lambda x: (-x[1], -x[2]))
for w, a, t, sites in short:
    print(f'   {"-".join(w):<22} заголовок {a}/{t}, сайты {",".join(sites)}')

# ---------------- справка: серии LB-аттестаций identicalWords (дескриптивно)
print('\n=== Справка: серии LB-аттестаций 36 identicalWords (words_in_linearb.js) ===')
print('(без контроля случайности; D-серии KN — списки пастухов: имена+топонимы)')
try:
    import re, json
    txt = open('words_in_linearb.txt', encoding='utf-8').read()
except FileNotFoundError:
    txt = None
    print('   файл words_in_linearb.txt не найден — пропущено')
if txt:
    m = re.search(r'identicalWords = new Map\(\[(.*?)\]\);', txt, re.S)
    body = m.group(1)
    entries = re.findall(r'\["([^"]+)", \[(.*?)\]\]', body, re.S)
    series_cnt = Counter(); details = []
    for wname, refs in entries:
        rr = re.findall(r"'([A-Z]+)\s+([A-Za-z]+)", refs)
        sers = {f'{site} {ser[:2] if ser[0]=="D" and site=="KN" else ser}'
                for site, ser in rr}
        for s in sers: series_cnt[s] += 1
        dser = any(site == 'KN' and ser.startswith('D') for site, ser in rr)
        details.append((wname, dser))
    nD = sum(1 for _, d in details if d)
    print(f'   слов с аттестацией в KN D-сериях (пастушьи списки): {nD}/{len(details)}')
    print('   топ серий:', series_cnt.most_common(12))
