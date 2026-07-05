# -*- coding: utf-8 -*-
"""Этап 7.5 (§Y): метрология «дробного класса» — дроби × товары × сайты.

Данные: все записи «слово + число с дробной частью» (и, для контраста,
дробные числа при логограммах). Вопросы:
1. Инвентарь номиналов: какие дроби реально используются (диадические 1/2,
   1/4, 1/8… против триадических 1/3, 1/6…), по сайтам.
2. Связаны ли СЛОВА с конкретными номиналами (кандидаты «пайков»):
   взаимная информация MI(слово, номинал) на словах с >=2 дробными
   вхождениями против перестановочного нуля (номиналы перемешиваются между
   записями), R=10000, seed=42.
3. Товарный контекст: ближайшая предшествующая логограмма; распределение
   номиналов по товарам (GRA/VIN/OLE/NI/CYP…), χ²-перестановка.
"""
import sys, pickle, random, math
from fractions import Fraction
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))

records = []   # (слово|логограмма, класс, дробная_часть, товар, сайт, док)
for d in corpus:
    toks = d['toks']
    cur_logo = None
    for i, (k, v) in enumerate(toks):
        if k == 'WORD':
            if not v['syllabic']:
                cur_logo = v['norm']
            # число сразу после
            nval = None
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM':
                    nval = toks[j][1]['val']
                    for j2 in range(j + 1, len(toks)):
                        if toks[j2][0] == 'NUM': nval += toks[j2][1]['val']
                        else: break
                    break
                if toks[j][0] == 'DIV': continue
                break
            if nval is None: continue
            frac = nval - int(nval)
            if frac == 0: continue
            is_word = v['syllabic'] and len(v['signs']) >= 2 and v['complete'] \
                and not (v['gap'] or v['trunc_l'] or v['trunc_r'])
            records.append({
                'label': v['norm'],
                'kind': 'word' if is_word else 'logo',
                'frac': frac, 'whole': int(nval),
                'logo_ctx': cur_logo if not is_word or True else None,
                'site': d['site'], 'doc': d['id']})

print(f'записей с дробной частью: {len(records)} '
      f'(слова: {sum(1 for r in records if r["kind"] == "word")}, '
      f'логограммы: {sum(1 for r in records if r["kind"] == "logo")})')

# ---------------- 1. инвентарь номиналов
print('\n=== инвентарь дробных номиналов ===')
by_frac = Counter(r['frac'] for r in records)
for f, n in sorted(by_frac.items(), key=lambda kv: -kv[1]):
    dy = 'диадич.' if (1 / f).denominator == 1 and (f.denominator & (f.denominator - 1)) == 0 \
        else ('диадич.' if (f.denominator & (f.denominator - 1)) == 0 else 'триадич./смеш.')
    print(f'   {str(f):>6}: {n:>3}  ({dy})')
print('\nпо сайтам (доля триадических знаменателей 3/6/12/24):')
for site in sorted({r['site'] for r in records}):
    rs = [r for r in records if r['site'] == site]
    if len(rs) < 5: continue
    tri = sum(1 for r in rs if r['frac'].denominator % 3 == 0)
    print(f'   {site:<5} n={len(rs):>3}, триадических {tri / len(rs):.0%}')

# ---------------- 2. MI(слово, номинал)
tok_wf = [(r['label'], r['frac']) for r in records if r['kind'] == 'word']
wcnt = Counter(w for w, _ in tok_wf)
sel = [(w, f) for w, f in tok_wf if wcnt[w] >= 2]
print(f'\n=== MI(слово, номинал): слов с >=2 дробными вхождениями: '
      f'{len(set(w for w, _ in sel))}, токенов {len(sel)} ===')
def MI(pairs_):
    n = len(pairs_)
    pw = Counter(w for w, _ in pairs_); pf = Counter(f for _, f in pairs_)
    pwf = Counter(pairs_)
    mi = 0.0
    for (w, f), c in pwf.items():
        p = c / n
        mi += p * math.log2(p / (pw[w] / n * pf[f] / n))
    return mi
if len(sel) >= 6:
    obs = MI(sel)
    labs = [f for _, f in sel]; ws = [w for w, _ in sel]
    ge = 0
    for _ in range(R):
        random.shuffle(labs)
        if MI(list(zip(ws, labs))) >= obs - 1e-12: ge += 1
    print(f'MI={obs:.3f} бит, перестановочный p={ge / R:.4f} (R={R}, seed=42)')
    # слова с постоянным номиналом
    print('слова с повторяющимся одинаковым номиналом:')
    by_w = defaultdict(list)
    for w, f in sel: by_w[w].append(f)
    for w, fs in sorted(by_w.items()):
        if len(fs) >= 2 and len(set(fs)) == 1:
            docs = [r['doc'] for r in records if r['label'] == w and r['kind'] == 'word']
            print(f'   {w}: {fs[0]} ×{len(fs)}  {docs}')

# ---------------- 3. номиналы по товарам
print('\n=== дробные части при логограммах-товарах (прямые записи товар+дробь) ===')
logo_recs = [r for r in records if r['kind'] == 'logo']
by_logo = defaultdict(Counter)
for r in logo_recs:
    base = r['label'].split('+')[0]
    by_logo[base][r['frac']] += 1
for logo, cnt in sorted(by_logo.items(), key=lambda kv: -sum(kv[1].values())):
    tot = sum(cnt.values())
    if tot < 3: continue
    tri = sum(v for f, v in cnt.items() if f.denominator % 3 == 0)
    top = ', '.join(f'{f}×{v}' for f, v in cnt.most_common(4))
    print(f'   {logo:<10} n={tot:>3} триад. {tri / tot:.0%}  [{top}]')
