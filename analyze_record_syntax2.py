# -*- coding: utf-8 -*-
"""Этап 28 (§DF-2): АУДИТ-ДЕЙСТВИЕ — синтаксис записи с единым правилом
допуска и совместным документным нулём (ответ на находку №4 аудита Sol).

Находки аудита: (а) §BO/§BR строили последовательности из ВСЕХ слов без
проектного фильтра сохранности — при строгом фильтре TE-сигнал слабеет;
(б) семейный контроль симулировал тесты раздельно, а не одной совместной
перестановкой документа; (в) формулировка «~11% при равномерном нуле»
неверна (средняя 1/L по коротким документам выше).

Здесь: ЕДИНОЕ правило допуска = слово полное, без лакун/обрывов (как во
всех лексиконных тестах); нуль = совместная перестановка порядка слов
внутри каждого документа (R=10000, seed=42), из ОДНОЙ перестановки
считаются все статистики семейства (операторы × {нач, вторая, предпосл,
фин}); семейный контроль — minP по совместным симуляциям. Публикуются
оба режима фильтра для сравнения.
"""
import sys, pickle
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
R = 10000
rng = np.random.default_rng(42)

OPS = ['KU-RO', 'PO-TO-KU-RO', 'KI-RO', 'TE', 'A-DU', 'I-DA', 'SI-RU-TE',
       'SA-RA2', 'KI', 'A-TA-I-*301-WA-JA']

corpus = pickle.load(open('corpus.pkl', 'rb'))

def build_docs(strict):
    docs = []
    for d in corpus:
        ws = []
        for k, v in d['toks']:
            if k != 'WORD' or not v['syllabic']:
                continue
            if strict and not (len(v['signs']) >= 1 and v['complete']
                               and not (v['gap'] or v['trunc_l']
                                        or v['trunc_r'])):
                continue
            ws.append(v['norm'])
        if len(ws) >= 2:
            docs.append(ws)
    return docs

def positions(ws_list):
    """счётчики (op, pos) по корпусу документов"""
    c = {}
    for ws in ws_list:
        L = len(ws)
        for i, w in enumerate(ws):
            if w not in OPSET:
                continue
            key = []
            if i == 0:
                key.append('нач')
            if i == 1:
                key.append('вт')
            if i == L - 2:
                key.append('пп')
            if i == L - 1:
                key.append('фин')
            for kk in key:
                c[(w, kk)] = c.get((w, kk), 0) + 1
            c[(w, 'n')] = c.get((w, 'n'), 0) + 1
    return c

OPSET = set(OPS)
for label, strict in (('ШИРОКИЙ фильтр (как §BO/§BR)', False),
                      ('СТРОГИЙ единый фильтр', True)):
    docs = build_docs(strict)
    obs = positions(docs)
    tests = [(w, pos) for w in OPS for pos in ('нач', 'вт', 'пп', 'фин')
             if obs.get((w, 'n'), 0) >= 5]
    if not tests:
        continue
    sims = np.zeros((R, len(tests)), dtype=np.int32)
    docs_idx = [np.array(ws, dtype=object) for ws in docs]
    for r_i in range(R):
        sim_docs = []
        for arr in docs_idx:
            perm = rng.permutation(len(arr))
            sim_docs.append(list(arr[perm]))
        sc = positions(sim_docs)
        for j, (w, pos) in enumerate(tests):
            sims[r_i, j] = sc.get((w, pos), 0)
    obs_arr = np.array([obs.get(t, 0) for t in tests])
    p_raw = ((sims >= obs_arr).sum(axis=0) + 1) / (R + 1)
    p_sim = np.zeros_like(sims, dtype=np.float64)
    for j in range(len(tests)):
        order = np.sort(sims[:, j])
        idx = np.searchsorted(order, sims[:, j], side='left')
        p_sim[:, j] = (R - idx + 1) / (R + 1)
    minp = p_sim.min(axis=1)
    p_adj = np.array([((minp <= p).sum() + 1) / (R + 1) for p in p_raw])
    print(f'=== {label}: документов {len(docs)}, тестов {len(tests)} ===')
    print(f'{"оператор":<20}{"поз":>4}{"n":>4}{"набл":>6}{"ожид":>7}'
          f'{"p":>9}{"p̃сем":>9}')
    exp = sims.mean(axis=0)
    for j, (w, pos) in enumerate(tests):
        if p_raw[j] < 0.10:
            star = ' *' if p_adj[j] < 0.05 else ''
            print(f'{w:<20}{pos:>4}{obs.get((w, "n"), 0):>4}'
                  f'{obs_arr[j]:>6}{exp[j]:>7.2f}{p_raw[j]:>9.4f}'
                  f'{p_adj[j]:>9.4f}{star}')
    print()
print('''
Чтение: совместная документная перестановка = один нуль для всего
семейства (истинный minP); показаны строки с raw p<0.10. Ожидаемое —
среднее по симуляциям (уже не «1/L», а честная величина). Выводы §BO/§BR
переоцениваются по СТРОГОМУ режиму; расхождение режимов = мера
чувствительности к правилу допуска (находка аудита №4).''')
