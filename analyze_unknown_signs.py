# -*- coding: utf-8 -*-
"""Этап 5.1 (§J): решётка Кобер для знаков без LB-двойника.

Для знаков *NNN / компаундов / AU предсказываем КЛАСС (гласный-подобный V или
слоговой CV-подобный) и собираем свидетельства о «ряде» (партнёры по финальным
чередованиям, ближайшие соседи по контекстному профилю).

Методика:
1. Позиционный классификатор: у известных знаков (задача D) V-класс и CV-класс
   имеют разные распределения (нач/сред/кон, по типам слов). Для неизвестного
   знака считаем мультиномиальное отношение правдоподобия
   log10 LR = log10 P(счёт | профиль V) − log10 P(счёт | профиль CV).
   Порог интерпретации: |log10 LR| >= 1 (десятикратное отношение) — «уверенно».
   Контроль калибровки: тот же классификатор прогоняется по ИЗВЕСТНЫМ знакам
   (каждый исключается из пула своего класса) — считаем точность.
2. Партнёры по финальным чередованиям (из задачи C, основа >=1 и >=2) с их
   согласными рядами LB.
3. Контекстный профиль: для знаков с >=5 вхождениями — распределение соседних
   знаков (класс согласного/гласного соседа слева и справа); ближайшие известные
   знаки по косинусу. Дескриптивно.
4. Флаг двойной роли: знак употребляется и как одиночная логограмма с числом
   (товар), и внутри слов — позиционный профиль слова может не отражать
   «слоговой» роли.
"""
import sys, pickle, math, itertools
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

def lb_value(s):
    base = s.rstrip('23')
    if base in VOWELS: return ('', base)
    if klass(s) == 'CV': return (base[:-1], base[-1])
    return None

# позиционные счётчики по ТИПАМ слов (токены — отдельно, для формульных знаков)
pos = defaultdict(lambda: [0, 0, 0])
pos_tok = defaultdict(lambda: [0, 0, 0])
sign_words = defaultdict(set)
for w in words:
    for i, s in enumerate(w):
        j = 0 if i == 0 else (2 if i == len(w) - 1 else 1)
        pos[s][j] += 1
        pos_tok[s][j] += lex[w]
        sign_words[s].add(w)

# одиночное употребление с числом (роль логограммы)
solo_num = Counter()
for d in corpus:
    toks = d['toks']
    for i, (k, v) in enumerate(toks):
        if k == 'WORD' and len(v['signs']) == 1:
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM': solo_num[v['signs'][0]] += 1; break
                if toks[j][0] != 'DIV': break

# ---------- профили классов
def pooled(klass_name, exclude=None):
    tot = [0, 0, 0]
    for s, p in pos.items():
        if s == exclude: continue
        if klass(s) == klass_name:
            for j in range(3): tot[j] += p[j]
    z = sum(tot)
    return [x / z for x in tot], z

PV, nV = pooled('V')
PCV, nCV = pooled('CV')
print(f'профиль V (n={nV}): нач/сред/кон = {PV[0]:.2f}/{PV[1]:.2f}/{PV[2]:.2f}')
print(f'профиль CV (n={nCV}): {PCV[0]:.2f}/{PCV[1]:.2f}/{PCV[2]:.2f}')

def log10_lr(cnt, pv, pcv):
    lr = 0.0
    for k in range(3):
        if cnt[k]:
            lr += cnt[k] * (math.log10(pv[k]) - math.log10(pcv[k]))
    return lr

# ---------- калибровка на известных знаках (leave-one-out)
print('\n=== калибровка классификатора на известных знаках (LOO, >=5 вхождений) ===')
ok = tot = 0; wrong = []
for s, p in sorted(pos.items(), key=lambda kv: -sum(kv[1])):
    kcl = klass(s)
    if kcl == 'UNK' or sum(p) < 5: continue
    pv, _ = pooled('V', exclude=s)
    pcv, _ = pooled('CV', exclude=s)
    lr = log10_lr(p, pv, pcv)
    pred = 'V' if lr > 0 else 'CV'
    tot += 1; ok += pred == kcl
    if pred != kcl: wrong.append((s, kcl, round(lr, 2), p))
print(f'точность: {ok}/{tot} = {ok / tot:.0%}; ошибки: {wrong}')

# ---------- чередования (для партнёрских свидетельств)
def collect_alt(min_stem):
    groups = defaultdict(set)
    for w in words:
        stem, last = w[:-1], w[-1]
        if len(stem) >= min_stem: groups[stem].add(last)
    pairs = defaultdict(set)
    for stem, alts in groups.items():
        for x, y in itertools.combinations(sorted(alts), 2):
            pairs[x].add((y, stem)); pairs[y].add((x, stem))
    return pairs
alt1 = collect_alt(1); alt2 = collect_alt(2)

# ---------- контекстные профили (сосед слева/справа по C-ряду и V-столбцу)
def ctx_profile(target):
    prof = Counter(); n = 0
    for w, cnt in lex.items():
        for i, s in enumerate(w):
            if s != target: continue
            for d, nb in [(-1, w[i - 1] if i > 0 else None),
                          (+1, w[i + 1] if i < len(w) - 1 else None)]:
                if nb is None:
                    prof[(d, '#')] += 1
                else:
                    v = lb_value(nb)
                    if v is None:
                        prof[(d, 'UNK:' + nb)] += 1
                    else:
                        prof[(d, 'C' + (v[0] or '∅'))] += 1
                        prof[(d, 'V' + v[1])] += 1
                n += 1
    return prof, n

def cosine(a, b):
    keys = set(a) | set(b)
    num = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
    da = math.sqrt(sum(x * x for x in a.values()))
    db = math.sqrt(sum(x * x for x in b.values()))
    return num / (da * db) if da and db else 0.0

known_prof = {}
for s, p in pos.items():
    if klass(s) != 'UNK' and sum(p) >= 8:
        known_prof[s], _ = ctx_profile(s)

# ---------- сводная таблица по неизвестным
print('\n=== неизвестные знаки: классификация и свидетельства ===')
print('(классификация по ТИПАМ слов; tok >> типов => знак формульный, вердикт слабее)')
print(f'{"знак":<10}{"n":>4}{"tok":>5}{"нач/срд/кон":>14}{"log10LR":>9}  вердикт    '
      f'соло+число  партнёры(осн>=2) | соседи-аналоги')
rows_out = []
for s, p in sorted(pos.items(), key=lambda kv: -sum(kv[1])):
    if klass(s) != 'UNK' or sum(p) < 2: continue
    lr = log10_lr(p, PV, PCV)
    verdict = ('V-подобный' if lr >= 1 else
               'CV-подобный' if lr <= -1 else 'неуверенно')
    partners2 = sorted({x for x, _ in alt2.get(s, set())})
    partners1 = sorted({x for x, _ in alt1.get(s, set())})
    # ближайшие известные по контексту
    nn = ''
    if sum(p) >= 5:
        prof, _ = ctx_profile(s)
        sims = sorted(((cosine(prof, kp), ks) for ks, kp in known_prof.items()),
                      reverse=True)[:3]
        nn = ', '.join(f'{ks}({sim:.2f})' for sim, ks in sims)
    print(f'{s:<10}{sum(p):>4}{sum(pos_tok[s]):>5}{"/".join(map(str, p)):>14}{lr:>9.2f}  '
          f'{verdict:<10} {solo_num.get(s, 0):>6}     '
          f'{",".join(partners2) or "—":<18} | {nn}')
    rows_out.append((s, sum(p), lr, verdict, partners1))

# досье формульных знаков (токенов много, типов мало)
print('\n--- досье знаков с tok/типы >= 3 (формульные) ---')
for s, p in sorted(pos.items(), key=lambda kv: -sum(pos_tok[kv[0]])):
    if klass(s) != 'UNK': continue
    n_t, n_k = sum(p), sum(pos_tok[s])
    if n_t and n_k / n_t >= 3:
        ws = sorted(sign_words[s], key=lambda w: -lex[w])[:6]
        print(f'{s}: типов {n_t}, токенов {n_k}; слова: '
              + ', '.join(f'{"-".join(w)}×{lex[w]}' for w in ws))

# подробности чередований для неизвестных с партнёрами
print('\n--- чередования неизвестных знаков (основа >=1, с основами) ---')
for s, n, lr, verdict, partners1 in rows_out:
    al = alt1.get(s, set())
    if not al: continue
    det = defaultdict(list)
    for x, stem in al: det[x].append('-'.join(stem))
    parts = '; '.join(f'~{x} [{", ".join(st[:2])}]' for x, st in sorted(det.items()))
    print(f'{s}: {parts}')
