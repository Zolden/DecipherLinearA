# -*- coding: utf-8 -*-
"""Задача F: семантическая типизация слов распределительными признаками.

Матрица признаков на тип слова (лексикон этапа 2, 618 типов; признаки усреднены
по вхождениям):
  p_num      — доля вхождений со следующим числом
  p_frac     — доля вхождений с ДРОБНЫМ следующим числом (от всех вхождений)
  p_logo     — доля вхождений с логограммой (несиллабическое слово) в соседних 2 токенах
  p_init     — доля вхождений первым словом документа («заголовок»)
  p_after_tot— доля вхождений сразу после итога (KU-RO/KI-RO/PO-TO-KU-RO + число)
  p_tablet   — доля вхождений на табличках
  p_kuro_win — доля вхождений внутри окна суммирования (до KU-RO документа)
  log_tok    — log2 числа вхождений
Кластеризация: k-means (scipy.cluster.vq.kmeans2, seed=42), признаки
стандартизованы; k=4 (контроль k=3, k=5).

Проверки:
  1) слова-записи KU-RO-списков (метка+число в окне суммирования) — ложатся ли в
     один кластер? (χ²-подобный максимум доли, нуль = перестановка меток, R=10000)
  2) гапаксы (1 вхождение) — концентрируются ли в «именном» кластере (том же,
     что и KU-RO-записи)?
p разведочные.
"""
import sys, pickle, random
import numpy as np
from scipy.cluster.vq import kmeans2
from collections import Counter, defaultdict
from fractions import Fraction

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
np.random.seed(42)
R = 10000

corpus = pickle.load(open('corpus.pkl', 'rb'))
TOTALS = {'KU-RO', 'KI-RO', 'PO-TO-KU-RO'}

# --- проход по документам: вхождения слов лексикона с контекстом
occ = defaultdict(list)   # word tuple -> список dict-признаков вхождения
for d in corpus:
    toks = d['toks']
    # индексы токенов-слов
    widx = [i for i, (k, v) in enumerate(toks) if k == 'WORD']
    first_word = widx[0] if widx else None
    # окно суммирования: все позиции до первого KU-RO со значением
    kuro_pos = None
    for i, (k, v) in enumerate(toks):
        if k == 'WORD' and v['norm'] in TOTALS:
            # есть ли число после
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM': kuro_pos = i; break
                if toks[j][0] == 'WORD': break
        if kuro_pos is not None: break
    for ii, i in enumerate(widx):
        v = toks[i][1]
        if not (v['syllabic'] and len(v['signs']) >= 2 and v['complete']
                and not (v['gap'] or v['trunc_l'] or v['trunc_r'])):
            continue
        w = tuple(v['signs'])
        if v['norm'] in TOTALS: continue   # сами итоги не типизируем
        # следующее число
        nval = None
        for j in range(i + 1, len(toks)):
            k2, v2 = toks[j]
            if k2 == 'NUM':
                nval = v2['val']
                for j2 in range(j + 1, len(toks)):
                    if toks[j2][0] == 'NUM': nval += toks[j2][1]['val']
                    else: break
                break
            if k2 == 'DIV': continue
            break
        # соседняя логограмма (±2 токена, слова несиллабические)
        logo = False
        for j in range(max(0, i - 2), min(len(toks), i + 3)):
            k2, v2 = toks[j]
            if k2 == 'WORD' and not v2['syllabic']: logo = True
        # сразу после итога?
        after_tot = False
        for j in range(i - 1, -1, -1):
            k2, v2 = toks[j]
            if k2 in ('LB', 'DIV', 'NUM'):
                if k2 == 'NUM':
                    # ищем слово перед числом
                    for j2 in range(j - 1, -1, -1):
                        if toks[j2][0] == 'WORD':
                            after_tot = toks[j2][1]['norm'] in TOTALS; break
                        if toks[j2][0] == 'NUM': continue
                    break
                continue
            if k2 == 'WORD':
                after_tot = v2['norm'] in TOTALS
            break
        occ[w].append({
            'num': nval is not None,
            'frac': nval is not None and nval != int(nval),
            'logo': logo,
            'init': i == first_word,
            'after_tot': after_tot,
            'tablet': d['is_tablet'],
            'kuro_win': kuro_pos is not None and i < kuro_pos and nval is not None,
        })

words = sorted(occ)
print(f'типов слов с вхождениями: {len(words)}')
feats = []
for w in words:
    os_ = occ[w]; n = len(os_)
    feats.append([
        sum(o['num'] for o in os_) / n,
        sum(o['frac'] for o in os_) / n,
        sum(o['logo'] for o in os_) / n,
        sum(o['init'] for o in os_) / n,
        sum(o['after_tot'] for o in os_) / n,
        sum(o['tablet'] for o in os_) / n,
        sum(o['kuro_win'] for o in os_) / n,
        np.log2(n),
    ])
X = np.array(feats)
mu, sd = X.mean(0), X.std(0)
sd[sd == 0] = 1
Z = (X - mu) / sd
FNAMES = ['p_num', 'p_frac', 'p_logo', 'p_init', 'p_after_tot', 'p_tablet',
          'p_kuro_win', 'log_tok']

for K in (3, 4, 5):
    centro, labels = kmeans2(Z, K, minit='++', seed=42)
    print(f'\n=== k-means, k={K} ===')
    sizes = Counter(labels)
    for c in sorted(sizes):
        members = [i for i, l in enumerate(labels) if l == c]
        prof = X[members].mean(0)
        desc = ' '.join(f'{n}={v:.2f}' for n, v in zip(FNAMES, prof))
        exam = [('-'.join(words[i]), len(occ[words[i]])) for i in members[:6]]
        print(f'кластер {c} (n={sizes[c]}): {desc}')
        print(f'   примеры: {exam}')
    if K != 4: continue
    # --- проверка 1: слова KU-RO-списков в одном кластере?
    kuro_words = [i for i, w in enumerate(words)
                  if any(o['kuro_win'] for o in occ[w])]
    kw_labels = [labels[i] for i in kuro_words]
    cnt = Counter(kw_labels)
    top_share = max(cnt.values()) / len(kw_labels)
    ge = 0
    lab_list = list(labels)
    for _ in range(R):
        samp = random.sample(lab_list, len(kuro_words))
        c2 = Counter(samp)
        if max(c2.values()) / len(samp) >= top_share: ge += 1
    print(f'\nслова KU-RO-списков: {len(kuro_words)} типов; распределение по '
          f'кластерам {dict(cnt)}; макс. доля {top_share:.1%}, '
          f'p(перест.)={ge / R:.4f} (R={R}, seed=42)')
    # --- проверка 2: гапаксы
    hap = [i for i, w in enumerate(words) if len(occ[w]) == 1]
    hl = Counter(labels[i] for i in hap)
    print(f'гапаксы: {len(hap)} типов; по кластерам {dict(hl)}')
    # в каком кластере доминируют KU-RO-записи и совпадает ли он с гапаксным?
    kuro_cl = cnt.most_common(1)[0][0]
    hap_cl = hl.most_common(1)[0][0]
    hap_share_in_kuro_cl = hl.get(kuro_cl, 0) / len(hap)
    ge2 = 0
    for _ in range(R):
        samp = random.sample(lab_list, len(hap))
        if samp.count(kuro_cl) / len(hap) >= hap_share_in_kuro_cl: ge2 += 1
    print(f'доля гапаксов в кластере KU-RO-записей (кластер {kuro_cl}): '
          f'{hap_share_in_kuro_cl:.1%}, p(перест.)={ge2 / R:.4f}; '
          f'модальный кластер гапаксов: {hap_cl}')
