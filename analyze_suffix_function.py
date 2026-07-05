# -*- coding: utf-8 -*-
"""Задача I (этап 4): функция суффиксов/приставок без чтения.

Вопрос: маркируют ли чередующиеся показатели (-JA/∅ и др. финали; A-/JA-/∅
приставки) РАЗНЫЕ ФУНКЦИИ слова? Если да, то в парах «основа W ~ производное W+S»
контексты вхождений должны систематически различаться.

Методика (парный дизайн, чтобы не смешивать лексику разных основ):
1. Пары: W и W+S оба в лексиконе этапа 2 (финали); P+W и W (приставки P=A-, JA-).
2. Признаки вхождения: (а) есть ли число сразу после слова; (б) документ
   религиозный (typ='rel'); (в) слово — первое в документе («заголовок»);
   (г) на табличке.
3. Для каждой пары — доля признака у производного минус у основы (Δ). Тест по
   парам: точный знако-переворотный (все 2^n переприсвоений «кто в паре основа»),
   двусторонний. Плюс пул вхождений: базовые×производные на признак, точный
   Фишер (scipy).
4. Отдельно приставочная тройка формулы возлияний A-/JA-.
Секундарно (с оговоркой о лексическом конфаунде): все слова на -JA против прочих.
p разведочные, R и перечисление указаны.
"""
import sys, pickle, itertools
from collections import Counter, defaultdict
from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')

corpus = pickle.load(open('corpus.pkl', 'rb'))

# ---------------- вхождения слов лексикона с контекстными признаками
lex = Counter()
occ = defaultdict(list)
for d in corpus:
    toks = d['toks']
    widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
    for i in widx:
        v = toks[i][1]
        if not (v['syllabic'] and len(v['signs']) >= 2 and v['complete']
                and not (v['gap'] or v['trunc_l'] or v['trunc_r'])):
            continue
        w = tuple(v['signs'])
        lex[w] += 1
        nval = None
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM': nval = toks[j][1]['val']; break
            if toks[j][0] == 'DIV': continue
            break
        occ[w].append({'num': nval is not None, 'rel': d['typ'] == 'rel',
                       'init': i == widx[0], 'tab': d['is_tablet'],
                       'doc': d['id'], 'site': d['site']})
words = set(lex)
FEATS = ['num', 'rel', 'init', 'tab']

def share(w, f):
    os_ = occ[w]
    return sum(o[f] for o in os_) / len(os_)

def signflip_p(deltas):
    """Точный двусторонний знако-переворотный тест среднего."""
    n = len(deltas)
    obs = abs(sum(deltas) / n)
    tot = 0; ge = 0
    for signs in itertools.product((1, -1), repeat=n):
        t = abs(sum(s * d for s, d in zip(signs, deltas)) / n)
        tot += 1
        if t >= obs - 1e-12: ge += 1
    return ge / tot

def pair_test(pairs, title):
    if not pairs:
        print(f'\n=== {title}: пар нет ==='); return
    print(f'\n=== {title}: {len(pairs)} пар ===')
    for base, der in pairs:
        b = {f: share(base, f) for f in FEATS}
        de = {f: share(der, f) for f in FEATS}
        print(f'  {"-".join(base)} (n={lex[base]}) ~ {"-".join(der)} (n={lex[der]}): '
              + '  '.join(f'{f}: {b[f]:.2f}->{de[f]:.2f}' for f in FEATS))
        bd = sorted({o['doc'] for o in occ[base]}); dd = sorted({o['doc'] for o in occ[der]})
        print(f'      док. основы: {bd}; производного: {dd}')
    print('  --- парные Δ (производное − основа), знако-переворотный тест:')
    for f in FEATS:
        deltas = [share(der, f) - share(base, f) for base, der in pairs]
        mean = sum(deltas) / len(deltas)
        p = signflip_p(deltas) if len(deltas) >= 2 else float('nan')
        print(f'      {f}: средняя Δ={mean:+.3f}, p(знак-переворот, 2^{len(deltas)})={p:.4f}')
    print('  --- пул вхождений, точный Фишер:')
    for f in FEATS:
        b1 = sum(o[f] for base, _ in pairs for o in occ[base])
        b0 = sum(1 for base, _ in pairs for o in occ[base]) - b1
        d1 = sum(o[f] for _, der in pairs for o in occ[der])
        d0 = sum(1 for _, der in pairs for o in occ[der]) - d1
        if (b1 + d1) == 0 or (b0 + d0) == 0:
            print(f'      {f}: признак константен ({b1 + d1} против {b0 + d0}) — тест не нужен')
            continue
        OR, p = fisher_exact([[b1, b0], [d1, d0]])
        print(f'      {f}: основа {b1}/{b1 + b0}, производное {d1}/{d1 + d0}, '
              f'Фишер p={p:.4f}')

# ---------------- финальные суффиксы
by_suffix = defaultdict(list)
for w in words:
    for s in {x[-1] for x in words if len(x) == len(w) + 1}:
        if w + (s,) in words:
            by_suffix[s].append((w, w + (s,)))
for s, pairs in sorted(by_suffix.items(), key=lambda kv: -len(kv[1])):
    if len(pairs) >= 3:
        pair_test(sorted(pairs), f'финаль ∅ ~ -{s}')
small = {s: len(p) for s, p in by_suffix.items() if 2 <= len(p) < 3}
print(f'\nсуффиксы с 2 парами (не тестировались отдельно): {small}')

# ---------------- приставки
for P in ('A', 'JA'):
    pairs = [(w, (P,) + w) for w in words
             if (P,) + w in words and len(w) >= 2]
    pair_test(sorted(pairs), f'приставка ∅ ~ {P}-')
pairs_aja = [((('A',) + w), (('JA',) + w)) for w in
             [x[1:] for x in words if x[:1] == ('A',) and len(x) >= 3]
             if ('JA',) + w in words]
pair_test(sorted(pairs_aja), 'приставка A- ~ JA- (общий хвост)')

# ---------------- секундарно: все -JA слова против прочих (лексический конфаунд!)
print('\n=== секундарно: все слова на -JA против прочих (конфаунд лексики; дескриптивно) ===')
ja_words = [w for w in words if w[-1] == 'JA']
other = [w for w in words if w[-1] != 'JA']
for f in FEATS:
    j1 = sum(o[f] for w in ja_words for o in occ[w]); jt = sum(lex[w] for w in ja_words)
    o1 = sum(o[f] for w in other for o in occ[w]); ot = sum(lex[w] for w in other)
    OR, p = fisher_exact([[j1, jt - j1], [o1, ot - o1]])
    print(f'   {f}: -JA {j1}/{jt} ({j1 / jt:.1%}) против прочих {o1}/{ot} '
          f'({o1 / ot:.1%}), Фишер p={p:.4f}')
print(f'   слов на -JA: {len(ja_words)}, токенов {sum(lex[w] for w in ja_words)}')
