# -*- coding: utf-8 -*-
"""Задача B: транзакционные одиночные знаки (обобщение HT118).

В HT118 записи чередуются «ИМЯ n / KI m», и под-колонка KI сходится точно:
10+4+1 = 15 = финальное KI 15. Вопрос: системно ли это для одиночных
силлабограмм, вклинивающихся между «слово+число»-записями (KI, TE, PA, QE, DI…)?

Методика.
1. «Запись» = слово WORD + числовая группа сразу за ним (DIV прозрачен).
   Документы — только таблички (is_tablet).
2. Одиночная запись знака S = слово из одного знака + число. «Вклинивание» = в
   документе есть и многознаковые записи с числами.
3. Гипотеза H1 «под-финал»: для документа с ≥2 записями S: существует ли позиция m
   (последнее вхождение S), что сумма S-записей до m == значению S в m.
   Перестановочный нуль: метки S переставляются по НЕ-итоговым записям документа
   (KU-RO/KI-RO/PO-TO-KU-RO и их числа исключены), спрашиваем как часто случайное
   подмножество того же размера суммируется в то же значение. R=10000, seed=42.
4. Гипотеза H2: под-сумма S == V(KI-RO) документа; H3: под-сумма/V(KU-RO) —
   считаем отношения; H4: отношение S-значения к значению предыдущей записи
   (парная запись) — сводка распределения по знакам.
p-значения разведочные, без поправки на множественность.
"""
import sys, pickle, random
from fractions import Fraction
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
TOTALS = {'KU-RO', 'KI-RO', 'PO-TO-KU-RO'}

def entries(doc):
    """[(norm, n_signs, syllabic, value|None, tok_idx)] в порядке документа."""
    toks = doc['toks']; out = []; i = 0
    while i < len(toks):
        k, v = toks[i]
        if k == 'WORD':
            j = i + 1; acc = Fraction(0); found = False
            while j < len(toks):
                kk = toks[j][0]
                if kk == 'NUM':
                    acc += toks[j][1]['val']; found = True; j += 1
                elif kk == 'DIV' and not found:
                    j += 1
                else:
                    break
            out.append((v['norm'], len(v['signs']), v['syllabic'],
                        acc if found else None, i))
            i = j
        else:
            i += 1
    return out

# ---------------- сбор событий
events = []       # H1-события: (doc, sign, значения до финала, финал, все не-итоговые значения)
inter_pairs = []  # H4: (sign, doc, prev_val, s_val)
sign_census = Counter(); sign_docs = defaultdict(set)

for doc in corpus:
    if not doc['is_tablet']: continue
    es = entries(doc)
    if not any(n >= 2 and val is not None for _, n, _, val, _ in es):
        continue  # нет многознаковых записей — не учётный список
    solo = [(idx, e) for idx, e in enumerate(es)
            if e[1] == 1 and e[3] is not None and e[0] not in TOTALS]
    for idx, e in solo:
        sign_census[e[0]] += 1; sign_docs[e[0]].add(doc['id'])
        if idx > 0 and es[idx-1][3] is not None and es[idx-1][1] >= 2 \
           and es[idx-1][0] not in TOTALS:
            inter_pairs.append((e[0], doc['id'], es[idx-1][3], e[3]))
    by_sign = defaultdict(list)
    for idx, e in solo: by_sign[e[0]].append((idx, e))
    for s, occ in by_sign.items():
        if len(occ) < 2: continue
        *head, last = occ
        head_vals = [e[3] for _, e in head]
        # значения всех не-итоговых записей до финального вхождения S (пул нуля)
        pool = [e[3] for idx, e in enumerate(es)
                if e[3] is not None and e[0] not in TOTALS and idx < last[0]]
        events.append({'doc': doc['id'], 'sign': s,
                       'head': head_vals, 'final': last[1][3], 'pool': pool,
                       'kuro': next((e[3] for e in es if e[0] == 'KU-RO'
                                     and e[3] is not None), None),
                       'kiro': next((e[3] for e in es if e[0] == 'KI-RO'
                                     and e[3] is not None), None)})

# ---------------- H1: под-финал с перестановочным нулём
print('=== H1: сумма головных S-записей == финальное S ===')
print(f'{"doc":<12}{"S":<6}{"голова":<24}{"финал":>8} {"счёт":>6} {"p(перест.)":>10}')
h1_hits = 0; h1_tests = 0; agg = []
for ev in events:
    ssum = sum(ev['head'])
    hit = ssum == ev['final']
    h1_tests += 1; h1_hits += hit
    k = len(ev['head'])
    pool = ev['pool']
    cnt = 0
    if len(pool) >= k:
        for _ in range(R):
            samp = random.sample(pool, k)
            if sum(samp) == ev['final']: cnt += 1
        p = cnt / R
    else:
        p = float('nan')
    agg.append((hit, p))
    print(f'{ev["doc"]:<12}{ev["sign"]:<6}{"+".join(str(x) for x in ev["head"]):<24}'
          f'{str(ev["final"]):>8} {"==" if hit else "!=":>6} {p:>10.4f}')
print(f'событий с ≥2 вхождениями S: {h1_tests}, точных под-финалов: {h1_hits}')
# совокупный нуль: сколько точных совпадений дала бы случайная разметка
ok_events = [(h, p) for h, p in agg if p == p]  # без NaN
sim_ge = 0
obs = sum(h for h, _ in ok_events)
for _ in range(R):
    tot = sum(1 for _, p in ok_events if random.random() < p)
    if tot >= obs: sim_ge += 1
print(f'совокупно: наблюдаемо {obs} попаданий из {len(ok_events)}; '
      f'ожидание нуля {sum(p for _, p in ok_events):.2f}; '
      f'P(>=набл.)={sim_ge / R:.4f} (R={R}, seed=42)')

# ---------------- H2/H3: связь под-сумм с KI-RO / KU-RO
print('\n=== H2/H3: под-сумма S (все вхождения) vs итоги документа ===')
for ev in events:
    total_s = sum(ev['head']) + ev['final']
    rel = []
    if ev['kiro'] is not None:
        rel.append(f'KI-RO={ev["kiro"]}' + (' ==SUBSUM' if ev['kiro'] == total_s else ''))
    if ev['kuro'] is not None and ev['kuro'] != 0:
        rel.append(f'S/KU-RO={Fraction(total_s) / ev["kuro"]}')
    print(f'{ev["doc"]:<12}{ev["sign"]:<6}subsum={str(total_s):<8}' + ' '.join(rel))

# один знак раз в документе, но есть и KU-RO: S/KU-RO
print('\n--- одиночные S (1 вхождение) как доля KU-RO ---')
ratio_by_sign = defaultdict(list)
for doc in corpus:
    if not doc['is_tablet']: continue
    es = entries(doc)
    kuro = next((e[3] for e in es if e[0] == 'KU-RO' and e[3] is not None), None)
    if not kuro: continue
    solo = [e for e in es if e[1] == 1 and e[3] is not None and e[0] not in TOTALS]
    for e in solo:
        ratio_by_sign[e[0]].append((doc['id'], Fraction(e[3]) / kuro))
for s, lst in sorted(ratio_by_sign.items(), key=lambda kv: -len(kv[1])):
    if len(lst) < 2: continue
    vals = Counter(r for _, r in lst)
    top = vals.most_common(1)[0]
    print(f'{s:<6}: n={len(lst)}, мода отношения {top[0]} ({top[1]} раз)',
          [f'{d}:{r}' for d, r in lst[:6]])

# ---------------- H4: отношение к предыдущей записи
print('\n=== H4: S-значение / значение предыдущей многознаковой записи ===')
by_sign_pairs = defaultdict(list)
for s, did, pv, sv in inter_pairs:
    if pv: by_sign_pairs[s].append((did, Fraction(sv) / pv))
for s, lst in sorted(by_sign_pairs.items(), key=lambda kv: -len(kv[1])):
    if len(lst) < 2: continue
    vals = Counter(r for _, r in lst)
    top = vals.most_common(2)
    print(f'{s:<6}: n={len(lst)}, топ отношений {top}',
          [f'{d}:{r}' for d, r in lst[:6]])

# ---------------- census
print('\n=== перепись одиночных знаков с числами (таблички со словными записями) ===')
for s, n in sign_census.most_common(30):
    print(f'{s:>6}: {n:>3} вхожд., {len(sign_docs[s]):>2} док.', sorted(sign_docs[s])[:10])

# ---------------- H1 раздельно: логограммы-товары vs силлабограммы
COMMOD = {'NI', 'VIN', 'GRA', 'OLIV', 'CYP', 'OLE', 'VIR', 'AROM', 'HIDE', 'TELA'}
def is_commodity(s):
    return '+' in s or s.startswith('*') or s in COMMOD
print('\n=== H1 по классам знаков ===')
for label, grp in [('логограммы-товары', [1]), ('силлабограммы', [0])]:
    sel = [(ev, hp) for ev, hp in zip(events, agg)
           if is_commodity(ev['sign']) == bool(grp[0])]
    ok = [(h, p) for (ev, (h, p)) in sel if p == p]
    obs2 = sum(h for h, _ in ok)
    exp2 = sum(p for _, p in ok)
    sim = 0
    for _ in range(R):
        tot = sum(1 for _, p in ok if random.random() < p)
        if tot >= obs2: sim += 1
    signs_here = sorted({ev['sign'] for ev, _ in sel})
    print(f'{label}: событий {len(sel)}, попаданий {obs2}, ожидание нуля {exp2:.2f}, '
          f'P(>=набл.)={sim / R:.4f}; знаки: {signs_here}')
