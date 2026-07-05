# -*- coding: utf-8 -*-
"""Этап 8.4 (§AC): ономастикон v3.

1. Расширенная разметка NAME-серий LB (добавлены земельные и скотоводческие
   серии, где записи возглавляются именами: KN Uf/C/E, PY Ea/Eb/En/Eo/Ep,
   MY Au/Oe) — пере-тест класс-стратификации длинных совпадений.
2. Рейтинг «имя-подобности» слов LA без оглядки на LB: логистическая эвристика
   из §F-признаков (гапакс/малое число вхождений, целое число после, табличка,
   не-заголовок, в окне суммирования). Выход: топ-30 LA-кандидатов в имена
   с LB-статусом (совпало/нет) — рабочий список ономастикона и предсказания
   для будущих сопоставлений.
"""
import sys, pickle, random, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

# ---------------- LB
CONS = set('djkmnpqrstwz')
def valid_syl(s):
    if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): return True
    m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
    return bool(m and m.group(1) in CONS)
lb = {}
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    w, c, ser, sites = (line.rstrip('\n').split('\t') + ['', ''])[:4]
    syls = w.split('-')
    if len(syls) < 2 or not all(valid_syl(s) for s in syls): continue
    lb[w] = set(x.strip() for x in ser.split(',') if x.strip())

TOP = {'pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'ku-do-ni-ja', 'tu-ri-so',
       'su-ki-ri-ta', 'se-to-i-ja', 'di-ka-ta', 'ru-ki-to', 'e-ko-so', 'pu-so',
       'a-pa-ta-wa', 'da-wo', 'do-ti-ja', 'e-ra', 'ku-ta-to', 'qa-ra', 'ra-ja',
       'ra-su-to', 'ra-to', 'ri-jo-no', 'si-ra-ro', 'su-ri-mo', 'tu-ni-ja',
       'u-ta-no', 'wa-to', 'pu-na-so', 'ti-ri-to', 'qa-mo'}
GREEK = {'to-so', 'to-sa', 'to-so-de', 'to-sa-de', 'o-pe-ro', 'do-e-ro',
         'do-e-ra', 'ko-wo', 'ko-wa', 'pa-ro', 'e-ke', 'e-ke-qe', 'e-ko-si',
         'o-na-to', 'ko-to-na', 'ko-to-i-na', 'ke-ke-me-na', 'ki-ti-me-na',
         'da-mo', 'te-o', 'te-o-jo', 'i-je-re-ja', 'i-je-re-u', 'i-je-ro',
         'ka-ko', 'ku-ru-so', 'e-ra-wo', 'a-pu-do-si', 'do-so-mo',
         'e-re-u-te-ro', 'e-re-u-te-ra', 'o-pi', 'qa-si-re-u', 'ra-wa-ke-ta',
         'wa-na-ka', 'wa-na-ka-te-ro', 'me-zo', 'me-zo-e', 'me-u-jo',
         'me-wi-jo', 'ne-wo', 'ne-wa', 'pa-ra-jo', 'pe-mo', 'pe-ma',
         'ta-ra-si-ja', 'we-to', 'di-do-si', 'e-u-ke-to', 'o-da-a2', 'te-ke',
         'a-pe-o', 'e-qe-ta', 'pe-ru-si-nu-wo', 'a-ni-ja', 'to-pe-za',
         'pa-we-a', 'pa-we-a2', 'tu-na-no', 'a-ro2-a', 'e-ne-wo', 'we-pe-za'}
NAME_SERIES = re.compile(
    r'^(KN D[a-z]?|KN As|KN B|KN V[c]?|KN Sc|KN Ap|KN Uf|KN C|KN E|'
    r'PY Jn|PY Cn|PY An|PY E[abnop]|MY Au|MY Oe)$')
def classify(w):
    if w in TOP: return 'TOP'
    if w in GREEK: return 'GREEK'
    if any(NAME_SERIES.match(s) for s in lb.get(w, ())): return 'NAME'
    return 'OTHER'
lb_all = set(lb)
print('классы LB v3:', Counter(classify(w) for w in lb_all))

# ---------------- LA
corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter(); feats = defaultdict(lambda: {'num': 0, 'int': 0, 'tab': 0,
                                              'init': 0, 'win': 0, 'rel': 0,
                                              'n': 0, 'docs': set(), 'sites': set()})
for d in corpus:
    toks = d['toks']
    widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
    kuro_pos = None
    for j, (k, v) in enumerate(toks):
        if k == 'WORD' and v['norm'] in ('KU-RO', 'PO-TO-KU-RO'):
            kuro_pos = j; break
    for i in widx:
        v = toks[i][1]
        if not (v['syllabic'] and len(v['signs']) >= 2 and v['complete']
                and not (v['gap'] or v['trunc_l'] or v['trunc_r'])):
            continue
        w = tuple(v['signs'])
        lex[w] += 1
        f = feats[w]; f['n'] += 1
        f['docs'].add(d['id']); f['sites'].add(d['site'])
        nval = None
        for j in range(i + 1, len(toks)):
            if toks[j][0] == 'NUM':
                nval = toks[j][1]['val']; break
            if toks[j][0] == 'DIV': continue
            break
        if nval is not None:
            f['num'] += 1
            if nval == int(nval): f['int'] += 1
            if kuro_pos is not None and i < kuro_pos: f['win'] += 1
        f['tab'] += d['is_tablet']
        f['init'] += i == widx[0]
        f['rel'] += d['typ'] == 'rel'
WORDS = set(lex)

def read_lb(w):
    out = []
    for s in w:
        if s.startswith('*') or '+' in s: return None
        out.append(s.lower())
    return '-'.join(out)

# ---------------- 1. пере-тест класс-стратификации (длинные >=3)
def matches_of(word_list):
    out = []
    for w in word_list:
        r = read_lb(w)
        if r and r in lb_all and len(w) >= 3:
            out.append((w, r, classify(r)))
    return out
obs = matches_of(sorted(WORDS))
print('\nдлинные совпадения v3:')
for w, r, c in sorted(obs, key=lambda x: x[2]):
    print(f'   {r:<16} {c}')
obs_cnt = Counter(c for _, _, c in obs)
words_list = sorted(lex)
lengths = [len(w) for w in words_list]
pos_pools = {0: [], 1: [], 2: []}
for w in words_list:
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
null_cnt = {c: [] for c in ('TOP', 'GREEK', 'NAME', 'OTHER')}
for _ in range(R):
    nc = Counter(c for _, _, c in matches_of(gen_B()))
    for c in null_cnt: null_cnt[c].append(nc.get(c, 0))
for c in ('NAME', 'TOP', 'GREEK', 'OTHER'):
    o = obs_cnt.get(c, 0)
    ns = null_cnt[c]
    m = sum(ns) / R
    p = sum(1 for x in ns if x >= o) / R
    print(f'   {c:<6}: наблюдаемо {o}, нуль {m:.2f}, p={p:.4f}')
oNT = obs_cnt.get('NAME', 0) + obs_cnt.get('TOP', 0)
nsNT = [null_cnt['NAME'][i] + null_cnt['TOP'][i] for i in range(R)]
print(f'   NAME+TOP: наблюдаемо {oNT}, нуль {sum(nsNT) / R:.2f}, '
      f'p={sum(1 for x in nsNT if x >= oNT) / R:.4f}')

# ---------------- 2. рейтинг имя-подобности LA-слов
def name_score(w):
    f = feats[w]
    if f['n'] == 0: return -9
    s = 0.0
    s += 1.5 * (f['int'] / f['n'])          # целое число после
    s += 1.0 * (f['tab'] / f['n'])          # табличка
    s += 1.0 * (f['win'] / f['n'])          # в окне суммирования
    s -= 1.5 * (f['init'] / f['n'])         # заголовки — не имена
    s -= 2.0 * (f['rel'] / f['n'])          # формулы — не имена
    s += 0.5 * (1 if f['n'] <= 2 else 0)    # редкость
    s += 0.3 * (len(w) >= 3)                # длина (информативность)
    return s
ranked = sorted(WORDS, key=lambda w: -name_score(w))
print('\n=== топ-30 LA-кандидатов в имена (рейтинг поведения) ===')
print(f'{"слово":<22}{"балл":>6}{"n":>3}{"LB-статус":<24}сайты')
lb_match = {w: read_lb(w) for w in WORDS}
for w in ranked[:30]:
    r = lb_match[w]
    st = ''
    if r and r in lb_all:
        st = f'== {r} [{classify(r)}]'
    print(f'{"-".join(w):<22}{name_score(w):>6.2f}{lex[w]:>3} {st:<24}'
          f'{",".join(sorted(feats[w]["sites"]))}')
n_match = sum(1 for w in ranked[:30] if lb_match[w] and lb_match[w] in lb_all)
print(f'из топ-30: совпадений с LB {n_match}')
