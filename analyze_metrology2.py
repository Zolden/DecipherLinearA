# -*- coding: utf-8 -*-
"""Этап 8.5 (§AD): мерная система целиком — квантование значений по товарам.

Вопросы:
1. Наименьшая единица на товар: минимальный шаг (НОД знаменателей) значений
   при GRA/OLE/VIN/CYP/NI/OLIV/*304 и его покрытие (какая доля значений кратна
   кандидату-кванту 1/4? 1/6? 1/16?).
2. Модальные номиналы («стандартные порции») по товарам.
3. Смешанные записи «целое+дробь» против чистых: у каких товаров значения
   заходят ниже 1 (дозирование), у каких — только целые (штучный счёт).
4. Перестановочный тест различия профилей знаменателей между товарами
   (перемешивание меток товара, статистика — χ² по классам знаменателя
   {2,4,8,16} vs {3,6,12} vs {5,10,20}), R=10000, seed=42.
"""
import sys, pickle, random, math
from fractions import Fraction
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))

recs = []   # (товар_base, value, doc, site)
for d in corpus:
    toks = d['toks']
    for i, (k, v) in enumerate(toks):
        if k == 'WORD' and not v['syllabic']:
            base = v['norm'].split('+')[0]
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
            if nval is not None and nval > 0:
                recs.append((base, nval, d['id'], d['site']))

by_c = defaultdict(list)
for c, v, doc, site in recs: by_c[c].append(v)
COMMS = [c for c, vs in by_c.items() if len(vs) >= 15]
COMMS.sort(key=lambda c: -len(by_c[c]))
print('товары с >=15 записями:', [(c, len(by_c[c])) for c in COMMS])

def denom_class(v):
    den = v.denominator
    if den == 1: return 'целое'
    if den % 3 == 0: return 'триадич.'
    if den % 5 == 0: return 'пятерич.'
    return 'диадич.'

print(f'\n{"товар":<8}{"n":>5}{"целых":>7}{"диад.":>7}{"триад.":>7}{"пятер.":>7}'
      f'{"минимум":>9}{"НОК знам.":>10}  модальные значения')
prof = {}
for c in COMMS:
    vs = by_c[c]
    n = len(vs)
    cls = Counter(denom_class(v) for v in vs)
    lcm = 1
    for v in vs: lcm = lcm * v.denominator // math.gcd(lcm, v.denominator)
    top = Counter(vs).most_common(3)
    prof[c] = cls
    print(f'{c:<8}{n:>5}{cls.get("целое", 0) / n:>7.0%}{cls.get("диадич.", 0) / n:>7.0%}'
          f'{cls.get("триадич.", 0) / n:>7.0%}{cls.get("пятерич.", 0) / n:>7.0%}'
          f'{str(min(vs)):>9}{lcm:>10}  '
          + ', '.join(f'{v}×{k}' for v, k in top))

# ---------------- 4. перестановочный тест профилей знаменателей (только дробные)
frecs = [(c, v) for c, v, _, _ in recs if v != int(v) and c in COMMS]
def chi2_stat(pairs_):
    cnt = defaultdict(Counter); col = Counter(); row = Counter()
    for c, v in pairs_:
        k = denom_class(v)
        cnt[c][k] += 1; col[k] += 1; row[c] += 1
    n = len(pairs_)
    x = 0.0
    for c in row:
        for k in col:
            e = row[c] * col[k] / n
            if e > 0: x += (cnt[c].get(k, 0) - e) ** 2 / e
    return x
obs = chi2_stat(frecs)
labs = [c for c, _ in frecs]; vals = [v for _, v in frecs]
ge = 0
for _ in range(R):
    random.shuffle(labs)
    if chi2_stat(list(zip(labs, vals))) >= obs - 1e-12: ge += 1
print(f'\nразличие профилей знаменателей между товарами (дробные записи, '
      f'n={len(frecs)}): χ²={obs:.1f}, перестановочный p={ge / R:.4f}')

# ---------------- покрытие квантами
print('\nпокрытие значений квантом (доля значений, кратных q):')
for c in COMMS:
    vs = by_c[c]
    row = f'{c:<8}'
    for q in (Fraction(1, 4), Fraction(1, 6), Fraction(1, 16), Fraction(1, 12),
              Fraction(1, 20), Fraction(1, 48)):
        cov = sum(1 for v in vs if (v / q).denominator == 1) / len(vs)
        row += f' q={q}:{cov:>4.0%}'
    print(row)
