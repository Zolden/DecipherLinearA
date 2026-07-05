# -*- coding: utf-8 -*-
"""Задача C: классы финальных чередований против LB-значений (главный тест).

Идея: если гомоморфные знакам LA значения LB переносимы, то знаки, чередующиеся
в КОНЦЕ слов с общей основой (STEM-x ~ STEM-y), должны группироваться по общему
согласному (морфология меняет гласный суффикса: -a/-e/-u...), как это происходит
в языках с открытой слоговой письменностью (ср. LB: -jo/-ja, -to/-ta…).

Методика:
1. Лексикон = полные слоговые слова ≥2 знаков без лакун/усечений (618 типов,
   воспроизводит lex_tok этапа 2).
2. Финальные чередования: пары слов, совпадающих во всём, кроме последнего знака,
   с общей основой длины ≥L (основной тест L=2; контроль L=1 и L=3).
   Приставочные: пары слов, совпадающие во всём, кроме первого знака (хвост ≥2).
3. Значения LB: из самой транслитерации (DA=(d,a), JA=(j,a), A=(∅,a); RA2/PA3 —
   тот же согласный ряд, вариант знака; *NNN и компаунды исключены).
4. Статистика: доля/число чередующихся пар с ОБЩИМ СОГЛАСНЫМ и разными гласными.
   Нуль-модель 1 («метки»): случайная перестановка (C,V)-значений между узлами
   графа чередований, R=10000, seed=42.
   Нуль-модель 2 («частоты финалей»): пары финалей, взвешенные частотой знаков
   в финальной позиции лексикона — сколько same-C дала бы случайная пара финалей.
p разведочные, поправки на множественность нет.
"""
import sys, pickle, random, itertools
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
res = pickle.load(open('results.pkl', 'rb'))

# ---------------- лексикон (фильтры этапа 2)
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words = set(lex)
print(f'лексикон: {len(words)} типов, {sum(lex.values())} токенов '
      f'(этап 2: {len(res["lex_tok"])})')

# ---------------- значения LB из транслитерации
VOWELS = {'A', 'E', 'I', 'O', 'U'}
def lb_value(s):
    """знак -> (C, V) или None (нет надёжного LB-гомоморфа)."""
    if s.startswith('*') or '+' in s or s in ('AU',):  # AU — дифтонг, исключаем
        return None
    base = s.rstrip('23')          # RA2/PA3/TA2/PU2 -> тот же C-ряд
    if base in VOWELS: return ('', base)
    if len(base) >= 2 and base[-1] in VOWELS and base[:-1].isalpha():
        return (base[:-1], base[-1])
    return None

# ---------------- сбор чередований
def collect_alternations(min_stem, final=True):
    """Пары (x, y, stem): слова stem+x и stem+y (или x+tail / y+tail)."""
    groups = defaultdict(set)
    for w in words:
        if final:
            stem, last = w[:-1], w[-1]
            if len(stem) >= min_stem: groups[stem].add(last)
        else:
            head, tail = w[0], w[1:]
            if len(tail) >= min_stem: groups[tail].add(head)
    pairs = []
    for stem, alts in groups.items():
        if len(alts) >= 2:
            for x, y in itertools.combinations(sorted(alts), 2):
                pairs.append((x, y, stem))
    return pairs, groups

def run_test(pairs, title):
    print(f'\n=== {title}: {len(pairs)} чередующихся пар '
          f'({len({p[:2] for p in pairs})} уникальных пар знаков) ===')
    # рёбра с LB-значениями
    val_pairs = [(x, y, st) for x, y, st in pairs if lb_value(x) and lb_value(y)]
    nodes = sorted({s for x, y, _ in val_pairs for s in (x, y)})
    vals = {s: lb_value(s) for s in nodes}
    def stat(assign):
        sameC = sameV = sameCdiffV = 0
        for x, y, _ in val_pairs:
            cx, vx = assign[x]; cy, vy = assign[y]
            if cx == cy:
                sameC += 1
                if vx != vy: sameCdiffV += 1
            if vx == vy: sameV += 1
        return sameC, sameCdiffV, sameV
    obsC, obsCdV, obsV = stat(vals)
    n = len(val_pairs)
    if n == 0:
        print('нет пар с LB-значениями'); return
    print(f'пар с LB-значениями: {n}; общий C: {obsC} ({obsC/n:.1%}), '
          f'общий C и разные V: {obsCdV} ({obsCdV/n:.1%}), общая V: {obsV} ({obsV/n:.1%})')
    # нуль-1: перестановка значений между узлами
    geC = geCdV = geV = 0
    vlist = [vals[s] for s in nodes]
    for _ in range(R):
        random.shuffle(vlist)
        a = dict(zip(nodes, vlist))
        c, cdv, vv = stat(a)
        geC += c >= obsC; geCdV += cdv >= obsCdV; geV += vv >= obsV
    print(f'нуль-1 (перестановка меток узлов, R={R}, seed=42): '
          f'p(sameC)={geC/R:.4f}, p(sameC,diffV)={geCdV/R:.4f}, p(sameV)={geV/R:.4f}')
    # нуль-2: пары по частотам финальной (или начальной) позиции
    posfreq = Counter()
    for w, cnt in lex.items():
        s = w[-1] if 'финаль' in title or 'stem' in title else w[0]
        if lb_value(s): posfreq[s] += cnt
    sigs = list(posfreq); wts = [posfreq[s] for s in sigs]
    hitC = hitCdV = 0; trials = R
    for _ in range(trials):
        x = random.choices(sigs, wts)[0]; y = random.choices(sigs, wts)[0]
        if x == y: continue
        cx, vx = lb_value(x); cy, vy = lb_value(y)
        if cx == cy:
            hitC += 1
            if vx != vy: hitCdV += 1
    print(f'нуль-2 (случайные пары по частотам позиции): ожидание sameC '
          f'{hitC/trials:.1%}, sameC&diffV {hitCdV/trials:.1%} (наблюдаемо '
          f'{obsC/n:.1%} / {obsCdV/n:.1%})')
    # перечень пар
    by_edge = defaultdict(list)
    for x, y, st in pairs: by_edge[(x, y)].append(st)
    print('пары знаков (вес = число основ):')
    for (x, y), sts in sorted(by_edge.items(), key=lambda kv: -len(kv[1])):
        vx, vy = lb_value(x), lb_value(y)
        tag = ''
        if vx and vy:
            tag = ' <SAME-C>' if vx[0] == vy[0] else ''
            if vx[1] == vy[1]: tag += ' <same-v>'
        ex = ','.join('-'.join(s) for s in sts[:2])
        print(f'  {x}~{y} w={len(sts)}{tag}  [{ex}]')
    return by_edge

# ---------------- основной тест: финали, основа >=2
pairs2, groups2 = collect_alternations(2, final=True)
edges2 = run_test(pairs2, 'финальные чередования, основа >=2 (морфология)')

# сверка с fam этапа 2: продолжения длины 1
fam = res['fam']
fam_pairs = set()
for stem, conts in fam.items():
    singles = sorted(c[0] for c in conts if len(c) == 1)
    for x, y in itertools.combinations(singles, 2):
        fam_pairs.add((x, y))
my_pairs = {tuple(sorted((x, y))) for x, y, _ in pairs2}
fp = {tuple(sorted(p)) for p in fam_pairs}
print(f'\nсверка с fam этапа 2: у меня {len(my_pairs)} пар, из fam {len(fp)}; '
      f'пересечение {len(my_pairs & fp)}; только fam: {sorted(fp - my_pairs)[:6]}')

# ---------------- контроль: основа >=3 (строго) и >=1 (шумно)
run_test(collect_alternations(3, final=True)[0], 'финальные чередования, основа >=3 (строже)')
run_test(collect_alternations(1, final=True)[0], 'финальные чередования, основа >=1 (вся статистика, шумнее)')

# ---------------- приставки
run_test(collect_alternations(2, final=False)[0], 'приставочные чередования, хвост >=2')

# ---------------- кластеризация знаков по чередуемости (основа >=2)
print('\n=== кластеры чередуемости (связные компоненты, основа >=2) ===')
adj = defaultdict(set)
for x, y, _ in pairs2:
    adj[x].add(y); adj[y].add(x)
seen = set()
comps = []
for s in sorted(adj):
    if s in seen: continue
    comp, stack = [], [s]
    while stack:
        u = stack.pop()
        if u in seen: continue
        seen.add(u); comp.append(u)
        stack.extend(adj[u] - seen)
    comps.append(sorted(comp))
for comp in sorted(comps, key=len, reverse=True):
    cons = Counter()
    for s in comp:
        v = lb_value(s)
        if v: cons[v[0] or '∅'] += 1
    print(f'  [{len(comp)}] {" ".join(comp)}  | согласные: {dict(cons)}')

# ∅-чередования (слово == основа): для справки
groups = groups2
zero = []
for stem, alts in groups.items():
    if stem in words and len(stem) >= 2:
        for a in sorted(alts):
            zero.append((stem, a))
print(f'\n∅-чередования (основа сама — слово): {len(zero)} пар основа~знак; '
      f'топ финалей: {Counter(a for _, a in zero).most_common(8)}')
