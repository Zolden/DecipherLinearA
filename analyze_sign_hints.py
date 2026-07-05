# -*- coding: utf-8 -*-
"""Этап 10.3 (§AN): паспорта неизвестных знаков v2 — сведение независимых улик.

Для каждого знака без LB-двойника сводятся:
  У1 позиционный вердикт (§J: V-подобный / CV-подобный, log10LR);
  У2 контекстные соседи-аналоги (косинус профилей окружения, топ-3);
  У3 кроссворд-голоса (§AI: совпадения джокер-шаблонов с LB);
  У4 одиночные употребления с числами (роль логограммы/единицы);
  У5 чередования (партнёры по основам).
Флаг КОНВЕРГЕНЦИЯ: согласный ряд кроссворд-голоса совпадает с модальным рядом
контекстных соседей. Это НЕ чтения — это досье ограничений.
"""
import sys, pickle, math, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))

lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words = sorted(lex)

VOWELS = {'A', 'E', 'I', 'O', 'U'}
def klass(s):
    if s in VOWELS: return 'V'
    base = s.rstrip('23')
    if (not s.startswith('*') and '+' not in s and s != 'AU'
            and len(base) >= 2 and base[-1] in VOWELS and base[:-1].isalpha()):
        return 'CV'
    return 'UNK'
def row_of(s):
    base = s.rstrip('23')
    return base[:-1] if klass(s) == 'CV' else ('∅' if klass(s) == 'V' else '?')

pos = defaultdict(lambda: [0, 0, 0])
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos[s][j] += 1

def pooled(kn, exclude=None):
    tot = [0, 0, 0]
    for s, p in pos.items():
        if s != exclude and klass(s) == kn:
            for j in range(3): tot[j] += p[j]
    z = sum(tot) or 1
    return [x / z for x in tot]
PV, PCV = pooled('V'), pooled('CV')
def lr(p):
    x = 0.0
    for k in range(3):
        if p[k]: x += p[k] * (math.log10(PV[k]) - math.log10(PCV[k]))
    return x

def ctx_profile(target):
    prof = Counter()
    for w, cnt in lex.items():
        for i, s in enumerate(w):
            if s != target: continue
            for d, nb in [(-1, w[i - 1] if i > 0 else None),
                          (+1, w[i + 1] if i < len(w) - 1 else None)]:
                if nb is None: prof[(d, '#')] += 1
                else:
                    r = row_of(nb)
                    v = nb.rstrip('23')[-1] if klass(nb) != 'UNK' else '?'
                    prof[(d, 'C' + r)] += 1
                    prof[(d, 'V' + v)] += 1
    return prof
def cosine(a, b):
    keys = set(a) | set(b)
    num = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    da = math.sqrt(sum(x * x for x in a.values())) or 1
    db = math.sqrt(sum(x * x for x in b.values())) or 1
    return num / (da * db)
known_prof = {s: ctx_profile(s) for s, p in pos.items()
              if klass(s) != 'UNK' and sum(p) >= 8}

# кроссворд-голоса (§AI, повтор inline)
CONS = set('djkmnpqrstwz')
def valid_syl(x):
    if x in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): return True
    m = re.fullmatch(r'([a-z])([aeiou])([23])?', x)
    return bool(m and m.group(1) in CONS)
lb_by_len = defaultdict(list)
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    syls = tuple(line.split('\t')[0].split('-'))
    if len(syls) >= 2 and all(valid_syl(s) for s in syls):
        lb_by_len[len(syls)].append(syls)
def is_unknown(s): return s.startswith('*') or '+' in s
votes = defaultdict(list)
for w in words:
    unk = [i for i, s in enumerate(w) if is_unknown(s)]
    if len(unk) != 1 or len(w) < 3: continue
    i = unk[0]
    syls = [None if j == i else w[j].lower() for j in range(len(w))]
    for cand in lb_by_len.get(len(w), ()):
        if all(syls[j] == cand[j] for j in range(len(w)) if j != i):
            votes[w[i]].append((cand[i], '-'.join(w), '-'.join(cand)))

# одиночные с числами
solo_num = Counter()
for d in corpus:
    toks = d['toks']
    for i, (k, v) in enumerate(toks):
        if k == 'WORD' and len(v['signs']) == 1:
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM': solo_num[v['signs'][0]] += 1; break
                if toks[j][0] != 'DIV': break

# чередования (основа >=1)
alt = defaultdict(set)
groups = defaultdict(set)
for w in words:
    if len(w[:-1]) >= 1: groups[w[:-1]].add(w[-1])
for stem, alts in groups.items():
    for x in alts:
        for y in alts:
            if x != y: alt[x].add(y)

print('=== паспорта неизвестных знаков v2 ===')
for s, p in sorted(pos.items(), key=lambda kv: -sum(kv[1])):
    if klass(s) != 'UNK' or sum(p) < 3: continue
    l = lr(p)
    verdict = 'V' if l >= 1 else ('CV' if l <= -1 else '?')
    prof = ctx_profile(s)
    sims = sorted(((cosine(prof, kp), ks) for ks, kp in known_prof.items()),
                  reverse=True)[:3]
    nb_rows = Counter(row_of(ks) for _, ks in sims)
    vs = votes.get(s, [])
    vote_rows = Counter()
    for val, _, _ in vs:
        m = re.fullmatch(r'([a-z]?)([aeiou])[23]?', val)
        if m: vote_rows[(m.group(1) or '∅').upper()] += 1
    conv = ''
    if vs and sims:
        top_nb = nb_rows.most_common(1)[0][0]
        if vote_rows.get(top_nb.upper() if top_nb != '∅' else '∅', 0) > 0:
            conv = ' <== КОНВЕРГЕНЦИЯ РЯДА'
    print(f'\n{s}: типов {sum(p)}, поз. {p} -> {verdict} (log10LR={l:+.2f}); '
          f'соло+число ×{solo_num.get(s, 0)}')
    print(f'   соседи-аналоги: ' + ', '.join(f'{ks}({sim:.2f})' for sim, ks in sims)
          + f'; ряды соседей: {dict(nb_rows)}')
    if vs:
        print(f'   кроссворд-голоса: ' + '; '.join(
            f'{val} ({law}=={lbw})' for val, law, lbw in vs[:4]) + conv)
    partners = sorted(alt.get(s, set()))[:8]
    if partners:
        print(f'   чередуется с: {",".join(partners)}')
