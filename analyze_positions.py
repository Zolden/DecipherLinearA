# -*- coding: utf-8 -*-
"""Задача D: позиционная типология знаков против LB-структуры.

Предсказание из LB-орфографии: знаки чистых гласных (A, E, I, O, U) должны иметь
ИЗБЫТОК начальной позиции в словах (в LB гласные знаки пишутся в начале слова и
в зиянии), CV-знаки — нет. Это внутренний тест переносимости LB-значений в LA,
не требующий чтения слов.

Методика:
1. Лексикон этапа 2 (618 типов). Позиции знака в слове: начальная (0), срединная,
   конечная. Основной счёт — по ТИПАМ слов (каждый тип один раз), контроль — по
   токенам (частоты вхождений).
2. Статистика V-знаков: совокупная доля начальных вхождений среди всех вхождений
   V-знаков. Нуль: перестановка метки «гласный» по знакам с сопоставимой частотой
   (все знаки с >= min_n вхождениями), R=10000, seed=42.
3. Ранговый тест: Манн-Уитни по доле начальности V против CV (перестановочный).
p разведочные.
"""
import sys, pickle, random
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = Counter()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex[tuple(v['signs'])] += 1

VOWELS = {'A', 'E', 'I', 'O', 'U'}
def is_cv(s):
    base = s.rstrip('23')
    return (not s.startswith('*') and '+' not in s and s != 'AU'
            and len(base) >= 2 and base[-1] in VOWELS and base[:-1].isalpha())

def counts(by_tokens):
    pos = defaultdict(lambda: [0, 0, 0])  # ini, med, fin
    for w, n in lex.items():
        wgt = n if by_tokens else 1
        for i, s in enumerate(w):
            j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
            pos[s][j] += wgt
    return pos

for mode, by_tok in [('ТИПЫ', False), ('токены', True)]:
    pos = counts(by_tok)
    print(f'\n=== {mode} ===')
    rows = []
    for s, (a, b, c) in pos.items():
        tot = a + b + c
        klass = 'V' if s in VOWELS else ('CV' if is_cv(s) else ('AU' if s == 'AU' else '*'))
        rows.append((s, klass, a, b, c, tot))
    rows.sort(key=lambda r: -r[5])
    print(f'{"знак":<8}{"класс":<6}{"нач":>5}{"срд":>5}{"кон":>5}{"всего":>6}{"доля нач.":>10}')
    for s, k, a, b, c, t in rows:
        if t >= 8:
            print(f'{s:<8}{k:<6}{a:>5}{b:>5}{c:>5}{t:>6}{a / t:>10.2f}')
    # --- совокупный тест: V-знаки в начальной позиции
    MINN = 5
    elig = [(s, k, a, b, c, t) for s, k, a, b, c, t in rows if t >= MINN and k in ('V', 'CV')]
    vsigns = [r for r in elig if r[1] == 'V']
    n_v = len(vsigns)
    obs_ini = sum(r[2] for r in vsigns) / max(1, sum(r[5] for r in vsigns))
    # нуль: какие знаки могли бы быть «гласными» — случайный выбор n_v знаков из elig
    ge = 0
    for _ in range(R):
        samp = random.sample(elig, n_v)
        share = sum(r[2] for r in samp) / max(1, sum(r[5] for r in samp))
        if share >= obs_ini: ge += 1
    cv = [r for r in elig if r[1] == 'CV']
    cv_ini = sum(r[2] for r in cv) / max(1, sum(r[5] for r in cv))
    print(f'V-знаки (n={n_v}, вхождений {sum(r[5] for r in vsigns)}): доля начальной '
          f'{obs_ini:.1%}; CV-знаки: {cv_ini:.1%}')
    print(f'нуль (случайные {n_v} знаков из {len(elig)}): p(доля>=набл.)={ge / R:.4f} '
          f'(R={R}, seed=42)')
    # --- ранговый тест Манна-Уитни (перестановочный)
    shares = [(r[2] / r[5], r[1]) for r in elig]
    v_sh = [x for x, k in shares if k == 'V']
    c_sh = [x for x, k in shares if k == 'CV']
    def U(a, b):
        return sum(1 for x in a for y in b if x > y) + 0.5 * sum(
            1 for x in a for y in b if x == y)
    obsU = U(v_sh, c_sh)
    allsh = v_sh + c_sh
    geU = 0
    for _ in range(R):
        random.shuffle(allsh)
        if U(allsh[:len(v_sh)], allsh[len(v_sh):]) >= obsU: geU += 1
    print(f'Манн-Уитни: U={obsU:.1f} из {len(v_sh) * len(c_sh)} '
          f'(AUC={obsU / (len(v_sh) * len(c_sh)):.2f}), p={geU / R:.4f}')
    # per-sign V подробно
    print('V-знаки подробно:', [(r[0], f'{r[2]}/{r[5]}') for r in vsigns])
