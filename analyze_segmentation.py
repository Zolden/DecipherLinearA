# -*- coding: utf-8 -*-
"""Этап 5.3 (§L): морфологическая сегментация лексикона с нуль-калибровкой
и функциональный тест маркеров v2.

1. Кандидат-суффикс S (1–2 знака) / кандидат-приставка P (1 знак).
   Парадигматическая поддержка support(S) = число РАЗНЫХ основ T (len>=2), для
   которых T+S — слово лексикона И основа независимо засвидетельствована
   (T — слово, или T+S' — слово при S'≠S). Аналогично для приставок (хвост >=2).
2. Нуль-модель: Null-B из §E — знаки перемешиваются внутри позиционных классов
   (начальный/срединный/конечный), длины слов и позиционные частоты знаков
   сохранены. R=2000, seed=42. Для каждого конкретного маркера:
   p = P(support в нуле >= наблюдаемой); плюс FWE-контроль:
   p_max = P(МАКСИМАЛЬНАЯ поддержка какого-либо маркера той же длины в нуле >=
   наблюдаемой) — «мог ли хоть какой-то случайный маркер быть столь же силён».
3. Сегментация: маркеры с p<0.05 → жадная сегментация лексикона (самый длинный
   значимый суффикс с независимо засвидетельствованной основой). Доля покрытия.
4. Функциональный тест v2 (расширение §I): для каждого значимого финального
   маркера S пары «форма T+S ~ альтернативные формы той же основы (T или T+S')»,
   признаки вхождений (число после; религиозный документ; заголовок; табличка),
   знако-переворотный тест по основам + Фишер по пулу вхождений.
p разведочные; множественность контролируется только указанным p_max.
"""
import sys, pickle, random, itertools
from collections import Counter, defaultdict
from scipy.stats import fisher_exact

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 2000

corpus = pickle.load(open('corpus.pkl', 'rb'))

# ---------------- лексикон и вхождения с признаками
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
        nval = None
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM': nval = True; break
            if toks[j][0] == 'DIV': continue
            break
        occ[w].append({'num': bool(nval), 'rel': d['typ'] == 'rel',
                       'init': i == widx[0], 'tab': d['is_tablet']})
WORDS = set(lex)
words_list = sorted(WORDS)
print(f'лексикон: {len(WORDS)} типов')

# ---------------- поддержка маркеров
def supports(word_set):
    """suffix -> set(stems), prefix -> set(tails)"""
    suf = defaultdict(set); pre = defaultdict(set)
    for w in word_set:
        for k in (1, 2):
            if len(w) - k >= 2:
                suf[w[-k:]].add(w[:-k])
        if len(w) - 1 >= 2:
            pre[w[:1]].add(w[1:])
    # независимая засвидетельствованность основы
    out_s = {}
    for S, stems in suf.items():
        good = set()
        for T in stems:
            if T in word_set: good.add(T); continue
            for k2 in (1, 2):
                found = False
                for S2, st2 in suf.items():
                    if S2 != S and len(S2) == k2 and T in st2:
                        found = True; break
                if found: good.add(T); break
        if good: out_s[S] = good
    out_p = {}
    for P, tails in pre.items():
        good = set()
        for T in tails:
            if T in word_set: good.add(T); continue
            for P2, t2 in pre.items():
                if P2 != P and T in t2: good.add(T); break
        if good: out_p[P] = good
    return out_s, out_p

obs_suf, obs_pre = supports(WORDS)

# ---------------- Null-B
lengths = [len(w) for w in words_list]
pos_pools = {0: [], 1: [], 2: []}
for w in words_list:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)

def null_B():
    for p in pos_pools.values(): random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = set()
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.add(tuple(w))
    return out

null_suf = defaultdict(list); null_pre = defaultdict(list)
null_max = {1: [], 2: [], 'pre': []}
for _ in range(R):
    ns, np_ = supports(null_B())
    for S in obs_suf: null_suf[S].append(len(ns.get(S, ())))
    for P in obs_pre: null_pre[P].append(len(np_.get(P, ())))
    for L in (1, 2):
        vals = [len(v) for S, v in ns.items() if len(S) == L]
        null_max[L].append(max(vals) if vals else 0)
    vals = [len(v) for v in np_.values()]
    null_max['pre'].append(max(vals) if vals else 0)

def report(obs, null_tbl, maxkey_fn, title, min_support=3):
    print(f'\n=== {title} ===')
    print(f'{"маркер":<10}{"осн":>4}{"нуль μ±σ":>12}{"p":>8}{"p_max":>8}  основы (примеры)')
    sig = []
    for S, stems in sorted(obs.items(), key=lambda kv: -len(kv[1])):
        n = len(stems)
        if n < min_support: continue
        nd = null_tbl[S]
        m = sum(nd) / len(nd)
        sd = (sum((x - m) ** 2 for x in nd) / len(nd)) ** 0.5
        p = sum(1 for x in nd if x >= n) / len(nd)
        pm = sum(1 for x in null_max[maxkey_fn(S)] if x >= n) / R
        ex = ', '.join('-'.join(t) for t in sorted(stems)[:4])
        mark = ' *' if p < 0.05 else ''
        print(f'{"-".join(S):<10}{n:>4}{m:>8.2f}±{sd:.2f}{p:>8.4f}{pm:>8.4f}  {ex}{mark}')
        if p < 0.05: sig.append(S)
    return sig

sig_suf = report(obs_suf, null_suf, lambda S: len(S), 'финальные маркеры (суффиксы)')
sig_pre = report(obs_pre, null_pre, lambda S: 'pre', 'начальные маркеры (приставки)')
print(f'\nзначимые (p<0.05): суффиксы {["-".join(s) for s in sig_suf]}, '
      f'приставки {["-".join(s) for s in sig_pre]}')

# ---------------- сегментация
seg = {}
for w in words_list:
    best = None
    for k in (2, 1):
        S = w[-k:]
        if tuple(S) in sig_suf and len(w) - k >= 2 and w[:-k] in obs_suf.get(tuple(S), ()):
            best = (w[:-k], S); break
    seg[w] = best
n_seg = sum(1 for v in seg.values() if v)
print(f'сегментировано слов: {n_seg}/{len(words_list)} ({n_seg / len(words_list):.1%})')

# ---------------- функциональный тест v2
FEATS = ['num', 'rel', 'init', 'tab']
def share(w, f):
    os_ = occ[w]
    return sum(o[f] for o in os_) / len(os_)

def signflip_p(deltas):
    n = len(deltas)
    obs = abs(sum(deltas) / n)
    ge = tot = 0
    if n > 16:
        random.seed(42)
        for _ in range(4096):
            t = abs(sum(random.choice((1, -1)) * d for d in deltas) / n)
            tot += 1; ge += t >= obs - 1e-12
    else:
        for signs in itertools.product((1, -1), repeat=n):
            t = abs(sum(s * d for s, d in zip(signs, deltas)) / n)
            tot += 1; ge += t >= obs - 1e-12
    return ge / tot

print('\n=== функциональный тест v2: маркер против альтернативных форм той же основы ===')
for S in sig_suf:
    stems = obs_suf[S]
    pairs = []   # (форма с S, [альтернативные формы])
    for T in stems:
        formS = T + S
        alts = [T] if T in WORDS else []
        for k2 in (1, 2):
            for S2 in obs_suf:
                if S2 != S and len(S2) == k2 and T in obs_suf[S2] and T + S2 in WORDS:
                    alts.append(T + S2)
        alts = [a for a in alts if a != formS]
        if alts: pairs.append((formS, alts))
    if len(pairs) < 4: continue
    print(f'\n--- маркер -{"-".join(S)}: {len(pairs)} основ ---')
    for f in FEATS:
        deltas = []
        for formS, alts in pairs:
            alt_sh = sum(share(a, f) for a in alts) / len(alts)
            deltas.append(share(formS, f) - alt_sh)
        mean = sum(deltas) / len(deltas)
        p = signflip_p(deltas)
        # пул вхождений
        s1 = sum(o[f] for formS, _ in pairs for o in occ[formS])
        st = sum(len(occ[formS]) for formS, _ in pairs)
        a1 = sum(o[f] for _, alts in pairs for a in alts for o in occ[a])
        at = sum(len(occ[a]) for _, alts in pairs for a in alts)
        if 0 < s1 + a1 and (st - s1) + (at - a1) > 0:
            _, pf = fisher_exact([[s1, st - s1], [a1, at - a1]])
        else:
            pf = float('nan')
        print(f'   {f}: Δ={mean:+.3f} (знак-переворот p={p:.4f}); '
              f'пул {s1}/{st} против {a1}/{at} (Фишер p={pf:.4f})')
