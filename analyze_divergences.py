# -*- coding: utf-8 -*-
"""Этап 19 (§CA): каталог разночтений SigLA ↔ corpus.pkl.

По 310+ общим документам — двусторонний список слов, отсутствующих на
другой стороне, с автоклассификацией:
  чтение-1     — на другой стороне есть слово той же длины, Хэмминг 1;
  сегментация  — слово = конкатенация двух слов другой стороны (или
                 наоборот его половины там есть);
  край±1       — усечение/добавка одного знака с края (лакуны, стыки);
  прочее       — остальное (в т.ч. подлинные разночтения >1 знака).
Выход: divergences.tsv + сводка. Корпус не правится; список — материал
для точечной сверки и corpus_supplement.
"""
import sys, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

SUBSCRIPT = {56: 'PA3', 66: 'TA2', 76: 'RA2', 68: 'RO2', 79: 'ZU',
             118: '*118'}                  # 79: в таблице SigLA нет чтения
def code_to_our(code, reading):
    if code.startswith('AB'):
        n = int(code[2:])
        if n in SUBSCRIPT:
            return SUBSCRIPT[n]
        return reading.upper() if reading else None
    return '*' + code[1:].lstrip('0') if code[1:].lstrip('0') else None

byw = defaultdict(lambda: defaultdict(dict))
for line in open('sigla_signs.tsv', encoding='utf-8'):
    if line.startswith('doc\t'):
        continue
    d, widx, ln, wp, pos, code, reading = line.rstrip('\n').split('\t')
    byw[d][int(widx)][int(pos)] = code_to_our(code, reading)
sig_words = defaultdict(list)
for d, ws in byw.items():
    for widx in sorted(ws):
        w = [ws[widx][k] for k in sorted(ws[widx])]
        if not any(x is None for x in w) and len(w) >= 2:
            sig_words[d.replace(' ', '')].append(tuple(w))

corpus = pickle.load(open('corpus.pkl', 'rb'))
cor_words = defaultdict(list)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2:
            cor_words[d['id']].append(tuple(v['signs']))

def ham1(a, b):
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1

def classify(w, other):
    oset = set(other)
    for o in oset:
        if ham1(w, o):
            return 'чтение-1', o
    for k in range(2, len(w) - 1):
        if w[:k] in oset and w[k:] in oset:
            return 'сегментация', (w[:k], w[k:])
    for o in oset:
        for j in range(2, len(o) - 1):
            if o[:j] == w or o[j:] == w:
                return 'сегментация', o
    for o in oset:
        if o[:-1] == w or o[1:] == w or w[:-1] == o or w[1:] == o:
            return 'край±1', o
    return 'прочее', ''

rows = []
cls_cnt = Counter()
doc_div = Counter()
for did in sorted(set(sig_words) & set(
        c for c in cor_words) | set(sig_words)):
    cands = {c for c in cor_words if c == did or c.rstrip('abcd') == did}
    if did not in sig_words or not cands:
        continue
    cws = [w for c in cands for w in cor_words[c]]
    sws = sig_words[did]
    cset, sset = set(cws), set(sws)
    for w in sws:
        if w not in cset:
            cl, mt = classify(w, cws)
            rows.append((did, 'SigLA', '-'.join(w), cl,
                         str(mt) if mt else ''))
            cls_cnt[('SigLA', cl)] += 1
            doc_div[did] += 1
    for w in cws:
        if w not in sset:
            cl, mt = classify(w, sws)
            rows.append((did, 'corpus', '-'.join(w), cl,
                         str(mt) if mt else ''))
            cls_cnt[('corpus', cl)] += 1
            doc_div[did] += 1

with open('divergences.tsv', 'w', encoding='utf-8') as f:
    f.write('doc\tside\tword\tclass\tmatch\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')
print(f'разночтений всего: {len(rows)} в {len(doc_div)} документах '
      f'(divergences.tsv)')
print('\nпо классам:')
for (side, cl), c in sorted(cls_cnt.items()):
    print(f'   {side:<7} {cl:<13} {c}')
print('\nсамые расходящиеся документы:')
for did, c in doc_div.most_common(8):
    print(f'   {did:<10} {c}')
ex = [r for r in rows if r[3] == 'чтение-1'][:12]
print('\nпримеры «чтение-1» (кандидаты точечной сверки):')
for did, side, w, cl, mt in ex:
    print(f'   {did:<10} {side:<7} {w:<22} ~ {mt}')
print('''
Чтение: классы автоматические, «прочее» включает лакуны и решения
редакторов о нечитаемом; каталог — не приговор какой-то стороне, а
рабочий список для эпиграфической сверки (corpus.pkl не правится).''')
