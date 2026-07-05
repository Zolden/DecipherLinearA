# -*- coding: utf-8 -*-
"""Этап 7.6 (§Z): типологический профиль слова LA против LB.

Идея контроля: LB — греческий язык В ТОЙ ЖЕ письменности, значит различия
профилей отражают ЯЗЫК, а не письмо. Метрики по ТИПАМ слов (>=2 слогов):
  1. длина слова в знаках (среднее, распределение);
  2. доля слов с начальным чистым гласным (V-знаком);
  3. доля слов с V-знаком НЕ в начале (письмо зияний/долгих);
  4. редупликация: соседние одинаковые знаки (QA-QA-…);
  5. повтор знака в слове (в любых позициях);
  6. распределение ГЛАСНОЙ последнего знака (a/e/i/o/u);
  7. энтропия знаков (юниграммная, бит).
Бутстреп-CI (95%, R=2000 ресемплов по словам) для разностей LA−LB.
Никаких выводов о родстве: только «профиль LA отличается/не отличается от
греческого профиля в тех же графических условиях».
"""
import sys, pickle, random, math, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
B = 2000

# ---------------- LA
corpus = pickle.load(open('corpus.pkl', 'rb'))
la_words = set()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            la_words.add(tuple(v['signs']))
la_words = sorted(la_words)

VOW = {'A', 'E', 'I', 'O', 'U'}
def la_v(s):
    base = s.rstrip('23')
    if base in VOW: return base
    if not s.startswith('*') and '+' not in s and len(base) >= 2 \
       and base[-1] in VOW:
        return base[-1]
    return None
def la_is_V(s): return s.rstrip('23') in VOW

# ---------------- LB
CONS = set('djkmnpqrstwz')
def valid_syl(s):
    if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): return True
    m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
    return bool(m and m.group(1) in CONS)
lb_words = []
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    w = line.split('\t')[0]
    syls = w.split('-')
    if len(syls) >= 2 and all(valid_syl(s) for s in syls):
        lb_words.append(tuple(syls))
def lb_is_V(s): return s.rstrip('23') in ('a', 'e', 'i', 'o', 'u')
def lb_v(s):
    b = s.rstrip('23')
    return b if b in 'aeiou' and len(b) == 1 else (b[-1] if b[-1] in 'aeiou' else None)

print(f'LA: {len(la_words)} типов; LB: {len(lb_words)} типов')

def profile(words, is_V, v_of):
    n = len(words)
    length = sum(len(w) for w in words) / n
    ini_v = sum(1 for w in words if is_V(w[0])) / n
    med_v = sum(1 for w in words if any(is_V(s) for s in w[1:])) / n
    redup = sum(1 for w in words
                if any(w[i] == w[i + 1] for i in range(len(w) - 1))) / n
    rep = sum(1 for w in words if len(set(w)) < len(w)) / n
    fin_v = Counter(v_of(w[-1]) for w in words if v_of(w[-1]))
    tot_f = sum(fin_v.values())
    fin_dist = {k: fin_v.get(k.upper() if k.isupper() else k, 0) / tot_f
                for k in 'aeiou'}
    sc = Counter(s for w in words for s in w)
    tot = sum(sc.values())
    H = -sum(c / tot * math.log2(c / tot) for c in sc.values())
    return {'len': length, 'iniV': ini_v, 'medV': med_v, 'redup': redup,
            'rep': rep, 'H': H, 'fin': fin_dist}

def fin_dist_of(words, v_of):
    fin_v = Counter(v_of(w[-1]) for w in words if v_of(w[-1]))
    tot = sum(fin_v.values())
    return {k: fin_v.get(k, 0) / tot for k in 'aeiou'}

pa = profile(la_words, la_is_V, lambda s: (la_v(s) or '').lower() or None)
pb = profile(lb_words, lb_is_V, lb_v)

METRICS = [('len', 'средняя длина (знаков)'), ('iniV', 'доля слов с V-началом'),
           ('medV', 'доля слов с V не в начале'), ('redup', 'редупликация соседних'),
           ('rep', 'повтор знака в слове'), ('H', 'энтропия знаков (бит)')]
print(f'\n{"метрика":<28}{"LA":>8}{"LB":>8}{"Δ(LA−LB)":>10}{"95% CI Δ":>20}')
for key, name in METRICS:
    # бутстреп разности
    deltas = []
    for _ in range(B):
        sa = [la_words[random.randrange(len(la_words))] for _ in range(len(la_words))]
        sb = [lb_words[random.randrange(len(lb_words))] for _ in range(len(lb_words))]
        da = profile(sa, la_is_V, lambda s: (la_v(s) or '').lower() or None)[key]
        db = profile(sb, lb_is_V, lb_v)[key]
        deltas.append(da - db)
    deltas.sort()
    lo, hi = deltas[int(0.025 * B)], deltas[int(0.975 * B)]
    sig = ' *' if lo > 0 or hi < 0 else ''
    print(f'{name:<28}{pa[key]:>8.3f}{pb[key]:>8.3f}{pa[key] - pb[key]:>+10.3f}'
          f'{f"[{lo:+.3f},{hi:+.3f}]":>20}{sig}')

fa = fin_dist_of(la_words, lambda s: (la_v(s) or '').lower() or None)
fb = fin_dist_of(lb_words, lb_v)
print('\nгласная последнего знака (доли):')
print('      ' + ''.join(f'{v:>8}' for v in 'aeiou'))
print('LA:   ' + ''.join(f'{fa[v]:>8.2f}' for v in 'aeiou'))
print('LB:   ' + ''.join(f'{fb[v]:>8.2f}' for v in 'aeiou'))
