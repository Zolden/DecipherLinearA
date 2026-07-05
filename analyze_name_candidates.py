# -*- coding: utf-8 -*-
"""Этап 7.1 (§U): профилирование кандидатов-омографов из §T внутри LA.

Для 11 кандидатов (3 топонима §E + 8 длинных совпадений §T): все вхождения,
позиция в документе, следующее число, соседние слова, класс поведения
(признаки §F), сайт/носитель. Плюс полный разбор документов ZA8 и ZA10a/b
(два вхождения DA-I-PI-TA и единственная в корпусе пара «база + A-форма»
в одном документе: TA-NA-TE / A-TA-NA-TE).

Вопрос: ведут ли кандидаты себя как ИМЕНА (запись+число в учёте) или как
термины/формулы? Дескриптивно + сравнение с фоном лексикона.
"""
import sys, pickle
from collections import Counter, defaultdict
from fractions import Fraction

sys.stdout.reconfigure(encoding='utf-8')
corpus = pickle.load(open('corpus.pkl', 'rb'))
docsx = {d['id']: d for d in corpus}

CANDS = [
    ('PA', 'I', 'TO'), ('SE', 'TO', 'I', 'JA'), ('SU', 'KI', 'RI', 'TA'),
    ('DA', 'I', 'PI', 'TA'), ('PA', 'RA', 'NE'), ('I', 'TA', 'JA'),
    ('KI', 'DA', 'RO'), ('TA', 'NA', 'TI'), ('DA', 'MA', 'TE'),
    ('I', 'JA', 'TE'), ('A', 'RO', 'TE'),
]

def doc_context(doc, i):
    """Контекст вхождения слова с индексом токена i."""
    toks = doc['toks']
    widx = [j for j, (k, v) in enumerate(toks) if k == 'WORD']
    nval = None
    for j in range(i + 1, len(toks)):
        if toks[j][0] == 'NUM':
            nval = toks[j][1]['val']
            for j2 in range(j + 1, len(toks)):
                if toks[j2][0] == 'NUM': nval += toks[j2][1]['val']
                else: break
            break
        if toks[j][0] == 'DIV': continue
        break
    prev = nxt = None
    for j in range(i - 1, -1, -1):
        if toks[j][0] == 'WORD': prev = toks[j][1]['norm']; break
    for j in range(i + 1, len(toks)):
        if toks[j][0] == 'WORD': nxt = toks[j][1]['norm']; break
    # в окне суммирования?
    kuro_pos = None
    for j, (k, v) in enumerate(toks):
        if k == 'WORD' and v['norm'] in ('KU-RO', 'PO-TO-KU-RO'):
            kuro_pos = j; break
    in_win = kuro_pos is not None and i < kuro_pos and nval is not None
    return {'init': i == widx[0], 'num': nval, 'prev': prev, 'next': nxt,
            'in_kuro_win': in_win}

print('=== профили кандидатов ===')
stats = Counter()
for sig in CANDS:
    print(f'\n--- {"-".join(sig)} ---')
    n_occ = 0
    for d in corpus:
        for i, (k, v) in enumerate(d['toks']):
            if k == 'WORD' and tuple(v['signs']) == sig:
                c = doc_context(d, i)
                n_occ += 1
                stats['num'] += c['num'] is not None
                stats['init'] += c['init']
                stats['win'] += c['in_kuro_win']
                stats['tot'] += 1
                stats['rel'] += d['typ'] == 'rel'
                print(f'   {d["id"]:<12} {d["site"]:<4} {d["support"]:<14} '
                      f'{"ЗАГОЛОВОК" if c["init"] else "запись":<10} '
                      f'{"число=" + str(c["num"]) if c["num"] is not None else "без числа":<16} '
                      f'{"в окне KU-RO" if c["in_kuro_win"] else "":<14} '
                      f'[{c["prev"]} _ {c["next"]}]')
    if n_occ == 0: print('   (в лексиконе, но вхождения с фильтрами не найдены)')

print(f'\nсводно по {stats["tot"]} вхождениям кандидатов: с числом '
      f'{stats["num"]}/{stats["tot"]}, заголовков {stats["init"]}, '
      f'в окне KU-RO {stats["win"]}, в rel-документах {stats["rel"]}')
# фон лексикона
lex_num = lex_tot = 0
for d in corpus:
    toks = d['toks']
    for i, (k, v) in enumerate(toks):
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex_tot += 1
            for j in range(i + 1, len(toks)):
                if toks[j][0] == 'NUM': lex_num += 1; break
                if toks[j][0] == 'DIV': continue
                break
print(f'фон лексикона: с числом {lex_num}/{lex_tot} ({lex_num / lex_tot:.0%})')

# ---------------- полные тексты ZA8, ZA10a, ZA10b
for did in ('ZA8', 'ZA10a', 'ZA10b'):
    d = docsx.get(did)
    if not d: continue
    out = []
    for k, v in d['toks']:
        if k == 'WORD': out.append(v['norm'])
        elif k == 'NUM': out.append(str(v['val']))
        elif k == 'LB': out.append('/')
        elif k == 'DIV': out.append('•')
    print(f'\n{did} ({d["site"]}, {d["support"]}, писец {d["scribe"] or "—"}): '
          + ' '.join(out))
