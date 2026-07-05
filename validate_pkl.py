# -*- coding: utf-8 -*-
"""Автономная валидация ЗАМОРОЖЕННОГО corpus.pkl против мини-корпуса (52 док.).

Адаптация validate.py: не требует loader.py (он не сохранился в папке) —
полный корпус берётся из corpus.pkl, мини-корпус парсится прямо из TSV.
Логика сравнения (normw, num_groups, nums_ok, KNOWN) воспроизведена из validate.py
без изменений. Ожидаемый итог по отчёту §0: 44 точных + 3 апгрейда дробей +
5 известных ревизий = 52, нерешённых 0.
"""
import re, sys, pickle
from fractions import Fraction

sys.stdout.reconfigure(encoding='utf-8')

# ---------- мини-корпус ----------
def parse_mini(path):
    docs = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        did, src, typ, site, scribe, toks = line.split('\t')
        words, groups = [], []
        cur = None  # [val, syms]
        for t in toks.split():
            if t in ('•', '/'):
                if cur is not None: groups.append(tuple(cur)); cur = None
                continue
            if t.startswith('#'):
                body = t[1:].rstrip('?')
                val = Fraction(0)
                for part in body.split('+'):
                    val += Fraction(part.lstrip('~'))  # ~ = приблизительное чтение
                if cur is None: cur = [Fraction(0), 0]
                cur[0] += val
                continue
            if t.startswith('%'):
                if cur is None: cur = [Fraction(0), 0]
                cur[1] += 1          # один неразрешённый дробный знак Янгера (%J, %E, %DD...)
                continue
            # слово
            if cur is not None: groups.append(tuple(cur)); cur = None
            w = t.replace('?', '').strip('~')  # ? = сомнение знака, ~ = усечение края
            if w and w != '‹›':                # одиночная ‹› = лакуна, не слово
                words.append(w)
        if cur is not None: groups.append(tuple(cur))
        docs.append({'id': did, 'words': words, 'groups': groups})
    return docs

# ---------- полный корпус (corpus.pkl) ----------
def normw(w):
    w = w.replace('+[?]', '').replace('+[ ]', '')
    w = w.replace('*21F', 'QIF')             # переименование знака у Дуроса
    w = re.sub(r'-?‹›-?', '-', w).strip('-')  # внутренняя лакуна: нотация мини
    return w

def words_of_full(d):
    return [normw(v['norm']) for k, v in d['toks'] if k == 'WORD']

def num_groups_full(d):
    gs = []; cur = None
    for k, v in d['toks']:
        if k == 'NUM':
            if cur is None: cur = [Fraction(0), 0]
            cur[0] += v['val']; cur[1] += sum(v['sym'].values())
        else:
            if cur is not None: gs.append(tuple(cur)); cur = None
    if cur is not None: gs.append(tuple(cur))
    return gs

def nums_ok(mg, fg):
    """True | 'frac' | False — из validate.py."""
    if len(mg) != len(fg): return False
    upgraded = False
    for (mv, ms), (fv, fs) in zip(mg, fg):
        if ms == 0 and fs == 0:
            if mv != fv: return False
        elif ms > 0 and fs == 0:      # мини не знал дробь, полный разрешил
            d = fv - mv
            if not (0 <= d < ms + 1): return False
            upgraded = True
        elif ms == 0 and fs > 0:      # мини разрешил, полный оставил глифы
            d = mv - fv
            if not (0 <= d < fs + 1): return False
            upgraded = True
        else:
            if mv != fv or ms != fs: return False
    return 'frac' if upgraded else True

KNOWN = {  # задокументированные различия ревизий (отчёт §0)
 'HT9b': 'новая ревизия убрала «10» при WA-JA-PI (= правка Янгера)',
 'HT86a': 'новая ревизия убрала лишнюю «10» на стыке строк (= правка Янгера)',
 'HT6b': 'MA-RI-‹›-I -> MA-RI-RE-I (дочитан знак RE)',
 'HT94b': 'RA-‹›-DE-ME-TE -> RA + DE-ME-TE (лакуна режет на 2 слова)',
 'HT28a': 'кластер логограмм VIR+KA-VIN одним сырым токеном новой ревизии',
}

if __name__ == '__main__':
    full = pickle.load(open('corpus.pkl', 'rb'))
    fx = {d['id']: d for d in full}
    mini = parse_mini('linear_a_mini_corpus.tsv')
    print(f'полный корпус: {len(full)} док.; мини: {len(mini)} док.')

    exact = fracup = known = 0; hard = []
    for m in mini:
        f = fx.get(m['id'])
        if not f: hard.append((m['id'], 'MISSING', None)); continue
        mw = [normw(w) for w in m['words']]
        fw = words_of_full(f)
        w_ok = mw == fw
        n_ok = nums_ok(m['groups'], num_groups_full(f))
        if w_ok and n_ok is True: exact += 1
        elif w_ok and n_ok == 'frac': fracup += 1
        elif m['id'] in KNOWN: known += 1
        else:
            hard.append((m['id'],
                         None if w_ok else (mw, fw),
                         None if n_ok else (m['groups'], num_groups_full(f))))
    print(f'точных: {exact}/52, апгрейд дробей: {fracup}, известные ревизии: {known}, нерешённых: {len(hard)}')
    for h in hard:
        print('---', h[0])
        if h[1]: print('  W mini:', h[1][0], '\n  W full:', h[1][1])
        if h[2]: print('  N mini:', [f'{v}({s})' for v, s in h[2][0]],
                       '\n  N full:', [f'{v}({s})' for v, s in h[2][1]])
