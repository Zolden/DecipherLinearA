# -*- coding: utf-8 -*-
"""Этап 6, п.5 (§P): функция приставки A- (сильнейший маркер, p_max=0.002).

Три подхода:
1. Стем-парный тест (дизайн §L-v2): форма A+T против альтернативных форм той же
   основы (T само слово или P'+T с другой приставкой). Признаки: число после,
   религиозный документ, заголовок, табличка. Знако-переворотный тест + Фишер.
2. Открывающее слово формулы возлияний: варианты A-TA-I-*301-WA-JA / -WA-E /
   JA-TA-... по сайтам и носителям (дескриптивно + связь с §K слот-1 выводом).
3. Взаимодействие маркеров: основы с A- и одновременно с -JA формами; насколько
   часто A-формы сами оканчиваются на -JA (циркумфиксность формулы).
"""
import sys, pickle, random, itertools
from collections import Counter, defaultdict
from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')

corpus = pickle.load(open('corpus.pkl', 'rb'))

lex = Counter(); occ = defaultdict(list)
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
        nval = False
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM': nval = True; break
            if toks[j][0] == 'DIV': continue
            break
        occ[w].append({'num': nval, 'rel': d['typ'] == 'rel',
                       'init': i == widx[0], 'tab': d['is_tablet'],
                       'doc': d['id'], 'site': d['site'], 'sup': d['support']})
WORDS = set(lex)
FEATS = ['num', 'rel', 'init', 'tab']

def share(w, f):
    return sum(o[f] for o in occ[w]) / len(occ[w])

# ---------------- 1. стем-парный тест A-
pre = defaultdict(set)
for w in WORDS:
    if len(w) - 1 >= 2: pre[w[0]].add(w[1:])
stems = []
for T in pre.get('A', ()):
    formA = ('A',) + T
    alts = [T] if T in WORDS else []
    alts += [(P,) + T for P in pre if P != 'A' and (P,) + T in WORDS and T in pre[P]]
    alts = [a for a in alts if a != formA]
    if alts: stems.append((formA, alts))
print(f'=== стем-парный тест A-: {len(stems)} основ ===')
for formA, alts in sorted(stems):
    print(f'   {"-".join(formA)} (n={lex[formA]}) ~ '
          + ', '.join(f'{"-".join(a)}(n={lex[a]})' for a in alts))
def signflip_p(deltas):
    n = len(deltas)
    obs = abs(sum(deltas) / n)
    ge = tot = 0
    for signs in itertools.product((1, -1), repeat=n):
        t = abs(sum(s * d for s, d in zip(signs, deltas)) / n)
        tot += 1; ge += t >= obs - 1e-12
    return ge / tot
for f in FEATS:
    deltas = []
    for formA, alts in stems:
        alt_sh = sum(share(a, f) for a in alts) / len(alts)
        deltas.append(share(formA, f) - alt_sh)
    p = signflip_p(deltas)
    s1 = sum(o[f] for formA, _ in stems for o in occ[formA])
    st = sum(len(occ[formA]) for formA, _ in stems)
    a1 = sum(o[f] for _, alts in stems for a in alts for o in occ[a])
    at = sum(len(occ[a]) for _, alts in stems for a in alts)
    _, pf = fisher_exact([[s1, st - s1], [a1, at - a1]])
    print(f'{f}: Δ={sum(deltas) / len(deltas):+.3f} (знак-переворот p={p:.4f}); '
          f'пул A-формы {s1}/{st} против альтернатив {a1}/{at} (Фишер p={pf:.4f})')

# ---------------- 2. открывающее слово формулы
print('\n=== варианты открытия формулы возлияний ===')
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and ('TA-I-*301' in v['norm'] or v['norm'].startswith(
                ('A-TA-I', 'JA-TA-I', 'TA-I-*301'))):
            print(f'   {v["norm"]:<24} {d["id"]:<10} {d["site"]:<4} {d["support"]}')

# ---------------- 3. взаимодействие A- и -JA
suf = defaultdict(set)
for w in WORDS:
    if len(w) - 1 >= 2: suf[w[-1]].add(w[:-1])
a_stems = {T for T in pre.get('A', ())}
ja_stems = {T for T in suf.get('JA', ())}
a_forms = [('A',) + T for T in a_stems]
end_ja = [w for w in a_forms if w[-1] == 'JA']
print(f'\nоснов с A-: {len(a_stems)}; из A-форм оканчиваются на -JA: '
      f'{len(end_ja)} ({[",".join(w) for w in end_ja]})')
both = {T for T in a_stems if T in ja_stems or (T + ('JA',)) in WORDS}
print(f'основы, имеющие и A-форму, и -JA-форму: {len(both)}: '
      f'{[",".join(t) for t in sorted(both)][:8]}')
# базовая доля -JA-финали среди слов той же длины (контроль)
la = [w for w in WORDS if w[-1] == 'JA']
print(f'справка: доля слов на -JA в лексиконе {len(la)}/{len(WORDS)} = '
      f'{len(la) / len(WORDS):.1%}; среди A-форм {len(end_ja)}/{len(a_forms)} = '
      f'{len(end_ja) / max(1, len(a_forms)):.1%}')
