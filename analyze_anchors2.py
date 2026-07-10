# -*- coding: utf-8 -*-
"""Этап 30 (§DK): якорная таблица v2 — с колонкой DĀMOS.

Для 11 якорей §BN: частота в лексиконе DĀMOS, слот-статус в
damos_name_slots.tsv (замороженные правила), сводный статус по трём
базам (Wayback lb1, linearb.xyz lb2, DĀMOS). Выход anchors2.tsv.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')

ANCHORS = [
    ('PA-I-TO', 'топоним'), ('SE-TO-I-JA', 'топоним'),
    ('SU-KI-RI-TA', 'топоним'),
    ('DA-I-PI-TA', 'имя'), ('I-TA-JA', 'имя'), ('KI-DA-RO', 'имя'),
    ('PA-RA-NE', 'имя'), ('TA-NA-TI', 'имя'), ('I-JA-TE', 'имя'),
    ('DA-MA-TE', 'особый (PY-класс)'), ('A-RO-TE', 'особый (PY-класс)'),
]

def load(fn):
    lexi = {}
    for line in open(fn, encoding='utf-8'):
        if line.startswith('word\t'):
            continue
        p = line.rstrip('\n').split('\t')
        lexi[p[0]] = p[1]
    return lexi

dam_lex = load('damos_lexicon.tsv')
dam_slots = load('damos_name_slots.tsv')
lb1_slots = load('lb_name_slots.tsv')
lb2_slots = load('lb2_name_slots.tsv')

rows = []
print(f'{"якорь":<14}{"класс":<18}{"DĀMOS×":>8}{"слот DĀMOS":>12}'
      f'{"слот lb1":>10}{"слот lb2":>10}')
for a, cls in ANCHORS:
    la = a.lower()
    dl = dam_lex.get(la, '—')
    ds = dam_slots.get(la, '')
    s1 = lb1_slots.get(la, '')
    s2 = lb2_slots.get(la, '')
    n_src = sum(bool(x) for x in (ds, s1, s2))
    print(f'{a:<14}{cls:<18}{dl:>8}{ds or "—":>12}{s1 or "—":>10}'
          f'{s2 or "—":>10}')
    rows.append((a, cls, dl, ds, s1, s2, n_src))

with open('anchors2.tsv', 'w', encoding='utf-8') as f:
    f.write('anchor\tclass\tdamos_freq\tdamos_slots\tlb1_slots\tlb2_slots\t'
            'n_slot_sources\n')
    for r in rows:
        f.write('\t'.join(str(x) for x in r) + '\n')
n3 = sum(1 for r in rows if r[6] == 3)
n2 = sum(1 for r in rows if r[6] >= 2)
print(f'\nслот-статус в 3/3 базах: {n3}; в >=2: {n2}; anchors2.tsv записан')
print('''
Чтение: слот-колонки — замороженные правила на каждой базе; DĀMOS —
курируемая; «особые» PY-слова якорями имён не считаются (§V).''')
