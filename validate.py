# -*- coding: utf-8 -*-
"""Валидация загрузчика полного корпуса против верифицированного мини-корпуса (52 док.).
Числа сравниваются группами (последовательные NUM без разделителей = одно измерение);
неразрешённые дробные знаки (%X в мини, глифы A70x в полном) допускают
несимметричное разрешение: |Δval| < число неразрешённых знаков в группе."""
import re
from fractions import Fraction
from loader import load_full, load_mini, NUM_XCHECK

full = load_full('/home/claude/corpus_raw.json','/home/claude/imagemap.json')
mini = load_mini('/mnt/user-data/uploads/linear_a_mini_corpus.tsv')
fx = {d['id']: d for d in full}

def normw(w):
    w = w.replace('+[?]','').replace('+[ ]','')
    w = w.replace('*21F','QIF')          # переименование знака у Дуроса
    w = re.sub(r'-?‹›-?','-',w).strip('-')  # внутренняя лакуна: нотация мини
    return w

def words_of(d):
    return [normw(v['norm']) for k,v in d['toks'] if k=='WORD']

def num_groups(d):
    """Группы последовательных NUM (одно числовое поле)."""
    gs = []; cur = None
    for k,v in d['toks']:
        if k=='NUM':
            if cur is None: cur = [Fraction(0), 0]
            cur[0] += v['val']; cur[1] += sum(v['sym'].values())
        else:
            if cur is not None: gs.append(tuple(cur)); cur = None
    if cur is not None: gs.append(tuple(cur))
    return gs

def nums_ok(mg, fg):
    """True | 'frac' | False"""
    if len(mg)!=len(fg): return False
    upgraded = False
    for (mv,ms),(fv,fs) in zip(mg,fg):
        if ms==0 and fs==0:
            if mv!=fv: return False
        elif ms>0 and fs==0:      # мини не знал дробь, полный разрешил
            d = fv-mv
            if not (0 <= d < ms+1): return False
            upgraded = True
        elif ms==0 and fs>0:      # мини разрешил, полный оставил глифы
            d = mv-fv
            if not (0 <= d < fs+1): return False
            upgraded = True
        else:
            if mv!=fv or ms!=fs: return False
    return 'frac' if upgraded else True

KNOWN = {  # задокументированные различия ревизий Дуроса (мини = старая ревизия / чтения Янгера)
 'HT9b':'новая ревизия убрала «10» при WA-JA-PI (= правка Янгера)',
 'HT86a':'новая ревизия убрала лишнюю «10» на стыке строк (= правка Янгера)',
 'HT6b':'MA-RI-‹›-I -> MA-RI-RE-I (дочитан знак RE)',
 'HT94b':'RA-‹›-DE-ME-TE -> RA + DE-ME-TE (лакуна режет на 2 слова)',
 'HT28a':'кластер логограмм VIR+KA-VIN одним сырым токеном новой ревизии (не слово; в лексикон не попадает)',
}
exact = fracup = known = 0; hard = []
for m in mini:
    f = fx.get(m['id'])
    if not f: hard.append((m['id'],'MISSING')); continue
    w_ok = words_of(m)==words_of(f)
    n_ok = nums_ok(num_groups(m), num_groups(f))
    if w_ok and n_ok is True: exact += 1
    elif w_ok and n_ok=='frac': fracup += 1
    elif m['id'] in KNOWN: known += 1
    else:
        hard.append((m['id'], None if w_ok else (words_of(m),words_of(f)),
                     None if n_ok else ([f'{v}({s})' for v,s in num_groups(m)],
                                        [f'{v}({s})' for v,s in num_groups(f)])))
print(f'точных: {exact}/52, апгрейд дробей: {fracup}, известные ревизии: {known}, нерешённых: {len(hard)}')
for h in hard:
    print('---', h[0])
    if len(h)>1 and h[1]: print('  W mini:', h[1][0], '\n  W full:', h[1][1])
    if len(h)>2 and h[2]: print('  N mini:', h[2][0], '\n  N full:', h[2][1])
print('чинки чисел глиф-vs-транслит:', dict(NUM_XCHECK))
# доп. проверка: PRZa1 внутренняя лакуна поймана флагом gap
pr = [v for k,v in fx['PRZa1']['toks'] if k=='WORD']
print('PRZa1 gap-флаги:', [(v['norm'], v['gap'], v['complete']) for v in pr])
