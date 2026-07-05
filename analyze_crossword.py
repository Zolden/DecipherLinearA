# -*- coding: utf-8 -*-
"""Этап 9.3 (§AI): кроссвордная механика — ограничения на значения знаков
без LB-двойника.

Идея: LA-слово из >=3 знаков, где ровно ОДИН знак неизвестен (*NNN), а
остальные читаемы, задаёт шаблон с джокером (например *306-TU-JA -> «?-tu-ja»).
Если шаблон совпадает со словами лексикона LB, каждое совпадение — «голос» за
значение неизвестного знака. Согласованные голоса по нескольким РАЗНЫМ словам
с одним и тем же знаком — кандидат значения.

Контроль: (1) перестановочный нуль Null-B — сколько голосов и какая
согласованность у джокер-шаблонов в псевдолексиконах; (2) сверка кандидата с
позиционным вердиктом знака (§J) и с частотами слога в LB.
Выход: таблица знак -> голоса (значение, LA-слово, LB-слово, класс LB-слова).
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 2000

# ---------------- LB-лексикон
CONS = set('djkmnpqrstwz')
def valid_syl(s):
    if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): return True
    m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
    return bool(m and m.group(1) in CONS)
lb = {}
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    w, c, ser, sites = (line.rstrip('\n').split('\t') + ['', ''])[:4]
    syls = tuple(w.split('-'))
    if len(syls) < 2 or not all(valid_syl(s) for s in syls): continue
    lb[syls] = ser
lb_by_len = defaultdict(list)
for syls in lb: lb_by_len[len(syls)].append(syls)

name_slot = set()
try:
    for line in open('lb_name_slots.tsv', encoding='utf-8'):
        if not line.startswith('word\t'):
            name_slot.add(line.split('\t')[0])
except FileNotFoundError:
    pass

# ---------------- LA-лексикон
corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1
words = sorted(lex)

def is_unknown(s):
    return s.startswith('*') or '+' in s

def patterns_of(word_list, min_len=3):
    """[(word, pos_неизвестного, [читаемые слоги с джокером])]"""
    out = []
    for w in word_list:
        unk = [i for i, s in enumerate(w) if is_unknown(s)]
        if len(unk) != 1 or len(w) < min_len: continue
        i = unk[0]
        try:
            syls = [None if j == i else w[j].lower().rstrip('23') +
                    ('2' if w[j].endswith('2') and len(w[j]) > 2 else '')
                    for j in range(len(w))]
        except Exception:
            continue
        # нормализация: RA2 -> ra2 остаётся, прочие -> нижний регистр
        syls = [None if j == i else w[j].lower() for j in range(len(w))]
        out.append((w, i, syls))
    return out

def match_votes(pats):
    """голоса: (unknown_sign, значение, la_word, lb_word)"""
    votes = []
    for w, i, syls in pats:
        L = len(syls)
        for cand in lb_by_len.get(L, ()):
            ok = all(syls[j] == cand[j] for j in range(L) if j != i)
            if ok:
                votes.append((w[i], cand[i], w, cand))
    return votes

pats = patterns_of(words)
print(f'LA-слов с ровно одним неизвестным знаком (длина >=3): {len(pats)}')
votes = match_votes(pats)
print(f'голосов (совпадений шаблона с LB): {len(votes)}\n')

by_sign = defaultdict(list)
for sign, val, law, lbw in votes: by_sign[sign].append((val, law, lbw))
print('=== голоса по знакам ===')
for sign, vs in sorted(by_sign.items(), key=lambda kv: -len(kv[1])):
    vals = Counter(v for v, _, _ in vs)
    print(f'{sign}: {len(vs)} голосов, значения: {dict(vals)}')
    for val, law, lbw in vs:
        cls = 'NAME_SLOT' if '-'.join(lbw) in name_slot else ''
        print(f'     {sign}={val:<4} из {"-".join(law):<22} == {"-".join(lbw):<18} {cls}')

# ---------------- нуль: сколько голосов у джокеров в псевдолексиконах
lengths = [len(w) for w in words]
pos_pools = {0: [], 1: [], 2: []}
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos_pools[j].append(s)
def gen_B():
    for p in pos_pools.values(): random.shuffle(p)
    idx = {0: 0, 1: 0, 2: 0}; out = []
    for L in lengths:
        w = []
        for i in range(L):
            j = 0 if i == 0 else (2 if i == L - 1 else 1)
            w.append(pos_pools[j][idx[j]]); idx[j] += 1
        out.append(tuple(w))
    return out

null_votes = []; null_signs_with_2cons = []
for _ in range(R):
    nv = match_votes(patterns_of(gen_B()))
    null_votes.append(len(nv))
    bs = defaultdict(list)
    for sign, val, _, _ in nv: bs[sign].append(val)
    n2 = sum(1 for sign, vals in bs.items()
             if len(vals) >= 2 and Counter(vals).most_common(1)[0][1] >= 2)
    null_signs_with_2cons.append(n2)
m = sum(null_votes) / R
p_tot = sum(1 for x in null_votes if x >= len(votes)) / R
obs2 = sum(1 for sign, vs in by_sign.items()
           if len(vs) >= 2 and Counter(v for v, _, _ in vs).most_common(1)[0][1] >= 2)
p2 = sum(1 for x in null_signs_with_2cons if x >= obs2) / R
print(f'\nнуль (Null-B, R={R}): всего голосов {m:.1f} (наблюдаемо {len(votes)}, '
      f'p={p_tot:.4f})')
print(f'знаков с >=2 согласными голосами: наблюдаемо {obs2}, '
      f'нуль {sum(null_signs_with_2cons) / R:.2f}, p={p2:.4f}')
