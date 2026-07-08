# -*- coding: utf-8 -*-
"""Этап 15 (§BN): единая таблица якорей — сведение уровней доказательности.

11 кандидатов-омографов длины >=3 (§T/§V/§AH/§AZ/§BJ): для каждого — вся
пирамида улик: (1) точное совпадение с полным LB (обе оцифровки);
(2) класс (топоним/именная серия/прочее); (3) слот-подтверждение в скрейпе
(v5) и в linearb.xyz (v7); (4) поведение в LA (§U). Выход: anchors.tsv +
печать. Кроссворд v2 (шаблоны с одним неизвестным знаком против lb2) — тут же.
"""
import sys, pickle, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

ANCHORS = [
    # (слово, класс, слот v5 (скрейп), слот v7 (lbxyz), поведение LA)
    ('pa-i-to',     'TOP',  '—',      '—',      'записи с числами, HT (архив Феста); underdots на I/TO'),
    ('se-to-i-ja',  'TOP',  '—',      '—',      'слот 2 формулы, Прасса (у Кносса)'),
    ('su-ki-ri-ta', 'TOP',  '—',      '—',      'заголовок нодула PH; производное SU-KI-RI-TE-I-JA (HT)'),
    ('da-i-pi-ta',  'NAME', 'N6 (KN B 799)',  '—',      'записи ×2 в списках ZA8/ZA10a'),
    ('i-ta-ja',     'NAME', 'N1 (KN Ap 769)', 'N1',     'запись при OLE+DI (HT28a); также I+TA-JA разбор'),
    ('ki-da-ro',    'NAME', 'N7 (KN E 842)',  'N7',     'записи HT47a/HT117a (одна с числом)'),
    ('pa-ra-ne',    'NAME', 'N5 (KN Vc)',     'N5',     'записи с числами HT115a/b'),
    ('ta-na-ti',    'NAME', 'N5 (KN Uf)',     '—',      'записи с числами ×3-4 (HT)'),
    ('i-ja-te',     'NAME', 'N4 (PY Eq)',     'N4',     'сосуд PHZb4, без числа'),
    ('da-ma-te',    'OTHER/NAME', '—',        '—',      'заголовок столика возлияний, Кифера; ср. I-DA-MA-TE (Аркалохори)'),
    ('a-ro-te',     'OTHER', '—',             '—',      'камень CRZg4, без числа'),
]

lb2 = set()
for line in open('lb2_lexicon.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        lb2.add(line.split('\t')[0])
ns7 = {}
for line in open('lb2_name_slots.tsv', encoding='utf-8'):
    if not line.startswith('word\t'):
        w, sl, n = line.rstrip('\n').split('\t')
        ns7[w] = sl

corpus = pickle.load(open('corpus.pkl', 'rb'))
la_docs = defaultdict(set)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic']:
            la_docs[v['norm'].lower().replace('-', '-')].add(d['id'])

print(f'{"якорь":<13}{"класс":<12}{"lb2":<5}{"слот v5":<17}{"слот v7":<10}  LA-документы')
rows = []
for w, cls, s5, s7hint, beh in ANCHORS:
    in_lb2 = 'да' if w in lb2 else 'НЕТ'
    s7 = ns7.get(w, '—')
    docs = sorted(la_docs.get(w, []))
    print(f'{w:<13}{cls:<12}{in_lb2:<5}{s5:<17}{s7:<10}  {",".join(docs)}')
    rows.append((w, cls, in_lb2, s5, s7, ';'.join(docs), beh))
with open('anchors.tsv', 'w', encoding='utf-8') as f:
    f.write('word\tclass\tin_lb2\tslot_v5\tslot_v7\tla_docs\tbehavior\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
print('\nanchors.tsv записан')

# ---------------- кроссворд v2 на lb2
CONS = set('djkmnpqrstwz')
def valid_syl(s):
    if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): return True
    m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
    return bool(m and m.group(1) in CONS)
lb2t = defaultdict(list)
for w in lb2:
    syls = tuple(w.split('-'))
    if all(valid_syl(s) for s in syls):
        lb2t[len(syls)].append(syls)
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
def is_unknown(s): return s.startswith('*') or '+' in s
votes = defaultdict(list)
for w in sorted(lex):
    unk = [i for i, s in enumerate(w) if is_unknown(s)]
    if len(unk) != 1 or len(w) < 3: continue
    i = unk[0]
    syls = [None if j == i else w[j].lower() for j in range(len(w))]
    for cand in lb2t.get(len(w), ()):
        if all(syls[j] == cand[j] for j in range(len(w)) if j != i):
            votes[w[i]].append((cand[i], '-'.join(w), '-'.join(cand),
                                '-'.join(cand) in ns7))
print(f'\n=== кроссворд v2 (lb2): голосов {sum(len(v) for v in votes.values())} ===')
for sign, vs in sorted(votes.items(), key=lambda kv: -len(kv[1])):
    vals = Counter(v for v, _, _, _ in vs)
    cons = vals.most_common(1)[0]
    print(f'{sign}: {len(vs)} голосов {dict(vals)}' +
          (f'  <== согласованных {cons[1]}' if cons[1] >= 2 else ''))
    for val, law, lbw, is_name in vs[:5]:
        print(f'     {val:<5} {law:<24} == {lbw:<18}{"[СЛОТ-ИМЯ]" if is_name else ""}')
