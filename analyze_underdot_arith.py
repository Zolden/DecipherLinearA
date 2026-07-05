# -*- coding: utf-8 -*-
"""Задача A (часть 2): пересчёт классификации арифметики KU-RO/KI-RO/PO-TO-KU-RO
с underdot-слоем сомнительных чтений Янгера (underdots_layer.pkl).

Методика:
1. Реимплементация извлечения событий итога (как в этапе 2): слово KU-RO / KI-RO /
   PO-TO-KU-RO, за которым идёт числовая группа V; окно = все числовые группы до
   ключевого слова (fullD = сумма окна − V). Реимплементация СВЕРЯЕТСЯ с
   results.pkl['arith'] этапа 2 по всем событиям (doc, kind, V, fullD) — это защита
   от расхождений между моим кодом и кодом этапа 2.
2. Underdot-флаги события: сколько записей окна (слово-метка или число) несут
   underdot Янгера; сомнителен ли сам итог (слово/число).
3. Классификация: точные (fullD=0), почти точные (|fullD|<=1), расходящиеся;
   отдельно — «чистые окна» (без underdot, без approx/doubt корпуса) и вопрос
   задачи: меняется ли статус HT9a (fullD=-3/4).
НИКАКОЙ подгонки чисел: underdot-слой только помечает события, он не «чинит» суммы.
"""
import sys, pickle
from fractions import Fraction
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

corpus = pickle.load(open('corpus.pkl', 'rb'))
layer = pickle.load(open('underdots_layer.pkl', 'rb'))
res = pickle.load(open('results.pkl', 'rb'))

KEYS = {'KU-RO': 'KU-RO', 'KI-RO': 'KI-RO', 'PO-TO-KU-RO': 'PO-TO-KU-RO'}

def num_groups_with_idx(doc):
    """[(value, sym_count, [tok_indices], approx_any, doubt_any)] в порядке документа,
    плюс отображение tok_index_первого -> номер группы."""
    gs = []; cur = None
    for i, (k, v) in enumerate(doc['toks']):
        if k == 'NUM':
            if cur is None: cur = [Fraction(0), 0, [], False, False]
            cur[0] += v['val']; cur[1] += sum(v['sym'].values())
            cur[2].append(i)
            cur[3] = cur[3] or v['approx']; cur[4] = cur[4] or v['doubt']
        else:
            if cur is not None: gs.append(cur); cur = None
    if cur is not None: gs.append(cur)
    return gs

def word_label_for_group(doc, g):
    """Слово непосредственно перед группой (метка записи)."""
    first = g[2][0]
    for j in range(first - 1, -1, -1):
        k, v = doc['toks'][j]
        if k == 'WORD': return j, v
        if k == 'NUM': return None, None
    return None, None

events = []
for doc in corpus:
    toks = doc['toks']
    gs = num_groups_with_idx(doc)
    # индекс: первый tok группы -> позиция группы
    by_first = {g[2][0]: gi for gi, g in enumerate(gs)}
    for i, (k, v) in enumerate(toks):
        if k == 'WORD' and v['norm'] in KEYS:
            kind = KEYS[v['norm']]
            # числовая группа сразу после слова (допуская DIV/LB между)
            vg = None
            for j in range(i + 1, len(toks)):
                kk, vv = toks[j]
                if kk == 'NUM':
                    vg = gs[by_first[j]] if j in by_first else None
                    break
                if kk == 'WORD': break
            if vg is None: continue
            V = vg[0]
            win = [g for g in gs if g[2][0] < i]          # все группы до ключевого слова
            fullD = (sum(g[0] for g in win) - V) if (win and vg[1] == 0 and
                     all(g[1] == 0 for g in win)) else None
            if vg[1] > 0: fullD = None
            # underdot-флаги
            def dotted(idx): return (doc['id'], idx) in layer
            ent_num_dot = sum(1 for g in win if any(dotted(ii) for ii in g[2]))
            ent_word_dot = 0
            for g in win:
                wi, wv = word_label_for_group(doc, g)
                if wi is not None and dotted(wi): ent_word_dot += 1
            tot_num_dot = any(dotted(ii) for ii in vg[2])
            tot_word_dot = dotted(i)
            approx_win = any(g[3] for g in win) or vg[3]
            doubt_win = any(g[4] for g in win) or vg[4]
            events.append({
                'doc': doc['id'], 'kind': kind, 'V': V, 'n_win': len(win),
                'fullD': fullD, 'ent_num_dot': ent_num_dot, 'ent_word_dot': ent_word_dot,
                'tot_num_dot': tot_num_dot, 'tot_word_dot': tot_word_dot,
                'approx': approx_win, 'doubt_corpus': doubt_win,
                'sym_total': vg[1] > 0,
            })

# ---------- сверка с этапом 2
old = res['arith']
def keyof(e): return (e['doc'], e['kind'], str(e['V']))
oldmap = defaultdict(list)
for o in old: oldmap[(o['doc'], o['kind'], str(o.get('V')))].append(o)
matched = mismatched = 0
unmatched_new, unmatched_old = [], []
used = set()
for e in events:
    k = keyof(e)
    cands = oldmap.get(k, [])
    hit = None
    for o in cands:
        if id(o) in used: continue
        hit = o; break
    if hit is None:
        unmatched_new.append(k); continue
    used.add(id(hit))
    oD = hit.get('fullD')
    if (oD is None) != (e['fullD'] is None) or (oD is not None and oD != e['fullD']):
        mismatched += 1
        print(f'РАСХОЖДЕНИЕ с этапом 2: {k} fullD этап2={oD} новый={e["fullD"]}')
    else:
        matched += 1
for o in old:
    if id(o) not in used:
        unmatched_old.append((o['doc'], o['kind'], str(o.get('V'))))
print(f'событий: новых {len(events)}, этап-2 {len(old)}; fullD совпало {matched}, '
      f'расхождений {mismatched}')
print('нет в этапе 2:', unmatched_new)
print('нет у меня:', unmatched_old)

# ---------- классификация с underdot-слоем
print('\n=== Классификация KU-RO-подобных событий с underdot-слоем ===')
print(f'{"doc":<14}{"kind":<12}{"V":>8} {"fullD":>8} {"окно":>4} '
      f'{"dotN":>4} {"dotW":>4} {"totD":>5} {"apx":>4} {"dbt":>4}')
def fmt(fr):
    if fr is None: return '—'
    return str(fr)
for e in sorted(events, key=lambda x: (x['kind'], x['doc'])):
    print(f'{e["doc"]:<14}{e["kind"]:<12}{fmt(e["V"]):>8} {fmt(e["fullD"]):>8} '
          f'{e["n_win"]:>4} {e["ent_num_dot"]:>4} {e["ent_word_dot"]:>4} '
          f'{str(e["tot_num_dot"] or e["tot_word_dot"]):>5} '
          f'{str(e["approx"]):>4} {str(e["doubt_corpus"]):>4}')

kuro = [e for e in events if e['kind'] == 'KU-RO' and e['n_win'] > 0 and e['fullD'] is not None]
exact = [e for e in kuro if e['fullD'] == 0]
def is_dotted(e): return e['ent_num_dot'] or e['ent_word_dot'] or e['tot_num_dot'] or e['tot_word_dot']
def is_dirty(e): return is_dotted(e) or e['approx'] or e['doubt_corpus']
print(f'\nKU-RO с окном и вычислимым fullD: {len(kuro)}')
print(f'  точных (fullD=0): {len(exact)}; из них с underdot в окне/итоге: '
      f'{sum(1 for e in exact if is_dotted(e))}; полностью чистых '
      f'(без underdot и без approx/doubt корпуса): {sum(1 for e in exact if not is_dirty(e))}')
mism = [e for e in kuro if e['fullD'] != 0]
print(f'  расходящихся: {len(mism)}; из них с underdot: {sum(1 for e in mism if is_dotted(e))}, '
      f'с любой грязью: {sum(1 for e in mism if is_dirty(e))}')
print('  расходящиеся БЕЗ каких-либо помет (candidates на реальную ошибку/непонимание):')
for e in mism:
    if not is_dirty(e):
        print(f'    {e["doc"]} fullD={e["fullD"]}')
ht9a = [e for e in events if e['doc'] == 'HT9a']
print('\nHT9a:', ht9a)
