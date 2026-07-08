# -*- coding: utf-8 -*-
"""Этап 17 (§BQ): диахрония — первый хронологический срез LA.

Слой датировок из SigLA (sigla_docs.tsv, parse_sigla.py) джойнится с
corpus.pkl (нормализация id: убрать пробелы; сторона a/b — от таблички).
Вёдра: MM (= MM II–III, «протодворцовый+»), LM (= LM I–II).

Дисциплина: период почти функционально сцеплен с сайтом (Phaistos=MM,
HT/KH/ZA=LM IB) — глобальные сравнения помечаем как конфаундированные;
чистый тест — внутри сайтов, где есть оба ведра (стратифицированная
перестановка меток внутри сайта). Метрики на документ (>=2 полных слова):
доля слов на -JA, доля слов на A-, средняя длина слова, частота *301 на
слово. R=10000, seed=42, двусторонне; семейный max-|Z| по 4 метрикам.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

# --- слой датировок
per_raw = {}
for line in open('sigla_docs.tsv', encoding='utf-8'):
    if line.startswith('id\t'):
        continue
    _id, idn, kind, site, per, url = line.rstrip('\n').split('\t')
    if per:
        per_raw[idn] = per

def bucket(p):
    mm = p.startswith('MM')
    lm = p.startswith('LM')
    if mm and 'LM' in p[2:]:
        return None                     # переходные MM III-LM IA
    if mm:
        return 'MM'
    if lm:
        return 'LM'
    return None

corpus = pickle.load(open('corpus.pkl', 'rb'))
by_id = {d['id']: d for d in corpus}

# сторона a/b/c наследует датировку таблички
def find_period(cid):
    if cid in per_raw:
        return per_raw[cid]
    for suf in 'abcd':
        if cid.endswith(suf) and cid[:-1] in per_raw:
            return per_raw[cid[:-1]]
    if cid + 'a' in per_raw:
        return per_raw[cid + 'a']
    return None

matched = {}
for d in corpus:
    p = find_period(d['id'])
    if p:
        matched[d['id']] = p
print(f'документов SigLA с периодом: {len(per_raw)}; '
      f'сматчено с корпусом: {len(matched)}')

cross = Counter()
for cid, p in matched.items():
    b = bucket(p)
    if b:
        cross[(by_id[cid]['site'], b)] += 1
sites = sorted({s for s, _ in cross})
print('\nсайт × ведро (документы корпуса):')
print(f'{"сайт":<8}{"MM":>5}{"LM":>5}')
both = []
for s in sites:
    mm, lm = cross.get((s, 'MM'), 0), cross.get((s, 'LM'), 0)
    print(f'{s:<8}{mm:>5}{lm:>5}')
    if mm >= 5 and lm >= 5:
        both.append(s)
print(f'сайты с обоими вёдрами (>=5/>=5): {both or "НЕТ"}')

# --- метрики на документ
def doc_metrics(d):
    ws = []
    n301 = 0
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            ws.append(v['signs'])
            n301 += v['signs'].count('*301')
    if len(ws) < 2:
        return None
    n = len(ws)
    return (sum(1 for w in ws if w[-1] == 'JA') / n,
            sum(1 for w in ws if w[0] == 'A') / n,
            sum(len(w) for w in ws) / n,
            n301 / n)

rows = []                      # (site, bucket, metrics)
for cid, p in matched.items():
    b = bucket(p)
    if not b:
        continue
    m = doc_metrics(by_id[cid])
    if m:
        rows.append((by_id[cid]['site'], b, m))
nmm = sum(1 for _, b, _ in rows if b == 'MM')
nlm = sum(1 for _, b, _ in rows if b == 'LM')
print(f'\nдокументов с метриками: {len(rows)} (MM {nmm}, LM {nlm})')

MET = ['доля -JA', 'доля A-', 'ср. длина', '*301/слово']

def diffs(rws):
    out = []
    for i in range(4):
        a = [m[i] for _, b, m in rws if b == 'LM']
        c = [m[i] for _, b, m in rws if b == 'MM']
        if not a or not c:
            return None
        out.append(sum(a) / len(a) - sum(c) / len(c))
    return out

def perm_test(rws, stratified):
    obs = diffs(rws)
    if obs is None:
        return None
    groups = defaultdict(list)
    for s, b, m in rws:
        groups[s if stratified else '_'].append((b, m))
    cnt = [0] * 4
    cmax = 0
    sds = [[] for _ in range(4)]
    for _ in range(R):
        sim = []
        for g, items in groups.items():
            labs = [b for b, _ in items]
            random.shuffle(labs)
            sim.extend((g, lb, m) for lb, (_, m) in zip(labs, items))
        dd = diffs(sim)
        for i in range(4):
            sds[i].append(dd[i])
    # нормировка |Z| для семейного максимума
    import statistics
    zs_obs = []
    for i in range(4):
        sd = statistics.pstdev(sds[i]) or 1e-12
        zs_obs.append(abs(obs[i]) / sd)
    for r in range(R):
        zmax = max(abs(sds[i][r]) / (statistics.pstdev(sds[i]) or 1e-12)
                   for i in range(4))
        if zmax >= max(zs_obs) - 1e-12:
            cmax += 1
        for i in range(4):
            if abs(sds[i][r]) >= abs(obs[i]) - 1e-12:
                cnt[i] += 1
    res = []
    for i in range(4):
        sd = statistics.pstdev(sds[i])
        z = abs(obs[i]) / sd if sd > 1e-9 else float('nan')
        res.append((obs[i], cnt[i] / R, z))
    return res, cmax / R

for label, strat in [('ГЛОБАЛЬНО (конфаундировано сайтом!)', False),
                     ('СТРАТИФИЦИРОВАННО по сайту', True)]:
    r = perm_test(rows, strat)
    if r is None:
        print(f'\n{label}: недостаточно данных')
        continue
    res, pmax = r
    print(f'\n{label}: Δ(LM−MM), p двусторонние (R={R}):')
    for (dv, p, z), name in zip(res, MET):
        zs = f'{z:.2f}' if z == z else 'н/д (нулевая дисперсия перестановок)'
        print(f'  {name:<12} Δ={dv:+.3f}  p={p:.4f}  |Z|={zs}')
    print(f'  семейный max-|Z|: p={pmax:.4f}')

print('''
Чтение: стратифицированный тест — единственный чистый (внутри сайта);
если сайтов с обоими вёдрами нет, перестановки внутри одноведёрных сайтов
не меняют меток и честно дают p≈1 — фиксируем как «диахрония недоступна
на текущем пересечении корпусов», это результат о данных, не о языке.''')
