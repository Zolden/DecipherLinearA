# -*- coding: utf-8 -*-
"""Этап 26 (§DA): валидация именного слоя на разметке Хогана.

Источник: network/transactions.js из lineara.xyz (наш пин eb9afc70;
кэш .hogan_cache.js гитигнорен, строка в tools/fetch_sources.sh) —
экспертная классификация табличек (Entity List / Transfer List / …) и
РОЛИ слов (sender/recipient/…) Роберта Хогана (AURA Suppl. 15, гл. 4).

Тесты:
(A) 16 Entity-табличек его главы против документов нашего именного слоя
    (якоря §BN + почти-омографы §BX + слот-строгие v8) — гипергеометрика
    по пулу его же классифицированных табличек.
(B) его слова-«recipient» против нашего union слот-имён (прочтённых через
    LB): доля recipient-слов, являющихся нашими слот-именами, против доли
    среди прочих его слов (точный тест).
Наша разметка и его — независимы по построению (он не использует LB-
сопоставления для ролей); совпадение = взаимная валидация.
"""
import sys, json, pickle, re
from collections import Counter, defaultdict

from scipy.stats import hypergeom, fisher_exact

sys.stdout.reconfigure(encoding='utf-8')

txt = open('.hogan_cache.js', encoding='utf-8').read()
data = json.loads(txt[txt.find('['):txt.rfind(']') + 1])
print(f'табличек в разметке Хогана: {len(data)}')
types = Counter(t.get('type', '?') for t in data)
print('типы:', types.most_common())

SIGNSEQ = re.compile(r'^[A-Z][A-Z0-9*]{0,3}(-[A-Z0-9*]{1,4})*$')
roles = Counter()
word_roles = defaultdict(set)             # норм. слово -> роли
doc_ids = set()
for t in data:
    did = t['name'].replace(' ', '')
    doc_ids.add(did)
    for w in t.get('words', []):
        cand = [(w.get('transliteratedWord') or '').strip(),
                (w.get('word') or '').strip()]
        role = (w.get('description') or '').strip()
        for wd in cand:
            if wd and SIGNSEQ.match(wd.upper()):
                roles[role] += 1
                word_roles[wd.upper()].add(role)
                break

print('роли слов:', roles.most_common(12))

# --- (A) Entity-16 против именных документов
ENT16 = {'HT108', 'HT146', 'HT25a', 'HT29', 'HT3', 'HT39', 'HT63',
         'HT98a', 'HT99b', 'PE2', 'ZA10a', 'ZA14', 'ZA20', 'ZA4a',
         'ZA5b', 'ZA7a'}
NAME_WORDS = {  # якоря §BN + почти-омографы §BX + §BZ-совпадения
    'DA-I-PI-TA', 'I-TA-JA', 'KI-DA-RO', 'PA-RA-NE', 'TA-NA-TI', 'I-JA-TE',
    'A-RA-NA-RE', 'A-RA-U-DA', 'KA-U-DE-TA', 'PI-TA-KE-SI',
    'A-TI-RU', 'DI-DE-RU', 'KA-SA-RU', 'KU-NI-TE', 'KU-RU-KU',
    'PA-JA-RE', 'QA-QA-RU', 'QA-TI-JU', 'SA-MA-RO', 'TA-NA-TE',
    'TE-JA-RE', 'QA-RA2-WA'}

corpus = pickle.load(open('corpus.pkl', 'rb'))
name_docs = set()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and v['norm'] in NAME_WORDS:
            name_docs.add(d['id'])
pool = doc_ids                             # пул = его классифиц. таблички
ent_in_pool = ENT16 & pool
nd_in_pool = name_docs & pool
ov = ent_in_pool & nd_in_pool
N, K, n = len(pool), len(ent_in_pool), len(nd_in_pool)
p = float(hypergeom.sf(len(ov) - 1, N, K, n))
print(f'\n(A) пул {N} табличек; Entity-16 в пуле: {K}; именных доков: {n}; '
      f'пересечение: {len(ov)} {sorted(ov)}')
print(f'гипергеометрика: p={p:.4f}')

# --- (B) роли recipient против слот-имён LB
NS = set()
for fn in ('lb_name_slots.tsv', 'lb2_name_slots.tsv'):
    for line in open(fn, encoding='utf-8'):
        if not line.startswith('word\t'):
            NS.add(line.split('\t')[0])
def read_lb(wd):
    parts = wd.split('-')
    if any(p.startswith('*') or '+' in p for p in parts):
        return None
    return '-'.join(p.lower() for p in parts)

REC_ROLES = {'recipient', 'sender'}
a = b = c = c2 = 0
rec_hits = []
for wd, rs in word_roles.items():
    r = read_lb(wd)
    if r is None or len(wd.split('-')) < 3:
        continue
    is_rec = bool(rs & REC_ROLES)
    is_ns = r in NS
    if is_rec and is_ns:
        a += 1
        rec_hits.append(wd)
    elif is_rec:
        b += 1
    elif is_ns:
        c += 1
    else:
        c2 += 1
odds, pf = fisher_exact([[a, b], [c, c2]], alternative='greater')
print(f'\n(B) слова >=3 знаков: recipient/sender∩слот-имя={a}, '
      f'recipient прочие={b}; не-recipient∩слот-имя={c}, прочие={c2}')
print(f'Fisher (односторонний): OR={odds:.2f}, p={pf:.4f}')
print('его агенты, являющиеся нашими слот-именами:', sorted(rec_hits)[:15])
print('''
Чтение: разметка Хогана интерпретационная (роли по структуре табличек),
наша — по LB-слотам; согласие двух независимых каналов = взаимная
валидация именного слоя. p разведочные.''')
