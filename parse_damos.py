# -*- coding: utf-8 -*-
"""Этап 29 (§DH): парсер корпуса DĀMOS (кэш .damos_cache/*.json, gitignore;
восстановление tools/fetch_damos.py) → damos_lexicon.tsv +
damos_name_slots.tsv.

ЗАМОРОЖЕННЫЕ правила слотов N1–N7 (v7-пайплайн, предрегистрация в
hypotheses.tsv, коммит 677a5da ДО скачивания). Механическая адаптация к
формату DĀMOS: логограммы людей/скота/металла заданы стандартными
кодами Bennett (*100 VIR, *102 MUL, *106 OVIS, *107 CAP, *108 SUS,
*109 BOS, *105 EQU, *140 AES, *120 GRA) — это транскрипция тех же правил,
не их изменение. Токенизация: слова = [a-z]+(-[a-z0-9]+)*; маркёры
повреждений ]/[ срезаются с краёв токена, токены с внутренними скобками/
'?' исключаются из слотов (в лексикон — только чистые).
"""
import sys, json, os, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

CACHE = '.damos_cache'
PEOPLE = {'*100', '*102', '*105', '*106', '*107', '*108', '*109', '*140',
          'VIR', 'MUL', 'OVIS', 'CAP', 'SUS', 'BOS', 'EQU', 'AES'}
GRA = {'*120', 'GRA'}
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')
NUM_RE = re.compile(r'^\d+$')

lex = Counter()
lex_docs = defaultdict(set)
slots = defaultdict(lambda: defaultdict(set))
n_items = 0
n_lines = 0

for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    n_items += 1
    head = (item.get('heading_short') or '').strip()
    m = re.match(r'^([A-Z]{2})\s+([A-Za-z]+)', head)
    site = m.group(1) if m else ''
    series = (item.get('series') or '')
    subser = (item.get('subseries') or '')
    ser = (series + subser).strip()
    content = item.get('content') or ''
    doc_id = head or fn
    for raw_line in content.split('\n'):
        n_lines += 1
        toks = []
        for rt in raw_line.replace(',', ' ').split():
            t = rt.strip('][')
            if not t or '?' in t or ']' in t or '[' in t:
                toks.append(('X', rt))
                continue
            if WORD_RE.match(t):
                toks.append(('W', t))
            elif NUM_RE.match(t):
                toks.append(('N', t))
            else:
                toks.append(('L', t.upper()))
        ws = [(i, t) for i, (k, t) in enumerate(toks) if k == 'W']
        for j, (i, w) in enumerate(ws):
            key = tuple(w.split('-'))
            lex[key] += 1
            lex_docs[key].add(doc_id)
            nxt = toks[i + 1] if i + 1 < len(toks) else (None, None)
            nx2 = toks[i + 2] if i + 2 < len(toks) else (None, None)
            prv = toks[i - 1] if i > 0 else (None, None)
            base = (lambda s: re.split(r'[+]', s)[0] if s else '')
            if nxt[0] == 'L' and base(nxt[1]) in PEOPLE:
                slots[key]['N1'].add(doc_id)
            if nxt[0] == 'W' and nx2[0] == 'L' and base(nx2[1]) in PEOPLE:
                slots[key]['N1b'].add(doc_id)
            if prv[0] == 'W' and prv[1] == 'pa-ro':
                slots[key]['N2'].add(doc_id)
            if site == 'KN' and series == 'D' and len(ser) <= 2 \
               and j == 0:
                slots[key]['N3'].add(doc_id)
            if nxt[0] == 'W' and nxt[1] in ('e-ke', 'e-ke-qe', 'o-na-to'):
                slots[key]['N4'].add(doc_id)
            if nxt[0] == 'N' and ((site == 'KN' and ser in
                    ('Vc', 'V', 'B', 'As', 'E', 'Uf', 'Ag', 'Ai', 'Ap'))
                    or (site == 'PY' and ser in ('Jn', 'An', 'Cn'))):
                slots[key]['N5'].add(doc_id)
            if site == 'KN' and ser in ('B', 'As', 'V', 'Vc', 'Ap') \
               and j == 0:
                slots[key]['N6'].add(doc_id)
            if nxt[0] == 'L' and base(nxt[1]) in GRA and (
                    (site == 'KN' and ser in ('E', 'F', 'Uf')) or
                    (site == 'PY' and ser in ('Ea', 'Eb', 'En', 'Eo', 'Ep'))):
                slots[key]['N7'].add(doc_id)

print(f'документов: {n_items}; строк: {n_lines}; '
      f'лексикон: {len(lex)} типов, {sum(lex.values())} токенов')
with open('damos_lexicon.tsv', 'w', encoding='utf-8') as f:
    f.write('word\tcount\tn_docs\n')
    for w, c in lex.most_common():
        f.write(f'{"-".join(w)}\t{c}\t{len(lex_docs[w])}\n')
ns = 0
with open('damos_name_slots.tsv', 'w', encoding='utf-8') as f:
    f.write('word\tslots\tn_docs\n')
    for w in sorted(slots):
        ss = sorted(slots[w])
        docs = set()
        for s in ss:
            docs |= slots[w][s]
        f.write(f'{"-".join(w)}\t{",".join(ss)}\t{len(docs)}\n')
        ns += 1
print(f'слот-имён: {ns} → damos_name_slots.tsv')
