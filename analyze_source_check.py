# -*- coding: utf-8 -*-
"""Этап 20 (§CF): сверка с первоисточником lineara.xyz (corpus_raw.json).

(а) Развилки «чтение-1» каталога §CA (QI↔*21F, PA3↔JA/NU и др.): смотрим,
что даёт сырой источник (translatedWords) — верен ли наш парсер (тогда
развилка редакторская, SigLA против линии GORILA/Янгера), или расхождение
внесли мы.
(б) ОБНАРУЖЕНИЕ: у lineara.xyz есть поле датировки context (в §BQ мы
ошибочно заявили, что датировок там нет — исправляем) → кросс-сверка двух
независимых датировочных слоёв (context против SigLA) по общим документам.

corpus_raw.json — локальный файл (в git и зеркало не входит; восстановление
tools/fetch_sources.sh), поэтому скрипт ВНЕ стресс-ростера.
"""
import sys, json, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

raw = json.load(open('corpus_raw.json', encoding='utf-8'))

def norm_word(s):
    return s.replace('₂', '2').replace('₃', '3').upper()

def raw_words(rid):
    r = raw.get(rid)
    if not r:
        return []
    return [norm_word(w) for w in r.get('translatedWords', [])
            if w.strip() and w != '\n']

# --- (а) развилки чтение-1
cases = []
for line in open('divergences.tsv', encoding='utf-8'):
    if line.startswith('doc\t'):
        continue
    doc, side, word, cl, match = line.rstrip('\n').split('\t')
    if cl == 'чтение-1' and side == 'corpus':
        cases.append((doc, word, match))

print(f'случаев «чтение-1» (corpus-сторона): {len(cases)}')
verd = Counter()
FOCUS = [c for c in cases if '*21F' in c[1] or 'QI' in c[1]
         or 'PA3' in c[1] or 'JA' in c[1] or 'NU' in c[1]]
print(f'из них с QI/*21F/PA3-знаками: {len(FOCUS)}')
print(f'\n{"док":<10}{"наше слово":<22}{"в сыром источнике?":<20}вердикт')
for doc, word, match in cases:
    rws = raw_words(doc)
    if not rws:
        for suf in 'ab':
            rws += raw_words(doc + suf)
    ok = word in rws
    verd[ok] += 1
    if (doc, word, match) in FOCUS or doc in ('HT31', 'ZA15a', 'TY2'):
        print(f'{doc:<10}{word:<22}{"ДА" if ok else "НЕТ":<20}'
              f'{"парсер верен → развилка редакторская" if ok else "проверить парсер"}')
print(f'\nитого: парсер верен в {verd[True]}/{verd[True] + verd[False]} '
      f'случаев «чтение-1»')

# --- (б) датировки: context против SigLA
def norm_ctx(c):
    c = (c or '').strip().upper().replace(' ', '')
    m = re.match(r'^(EM|MM|LM|MH|LH)([IVX]*)([AB]?)', c)
    return m.group(0) if m else ''

ctx = {}
for k, r in raw.items():
    c = norm_ctx(r.get('context'))
    if c:
        ctx[k] = c
print(f'\nдатировано в lineara.xyz (context): {len(ctx)}/{len(raw)} — '
      f'исправление §BQ: датировки там ЕСТЬ')

sig = {}
for line in open('sigla_docs.tsv', encoding='utf-8'):
    if line.startswith('id\t'):
        continue
    _id, idn, kind, site, p, url = line.rstrip('\n').split('\t')
    if p:
        sig[idn] = norm_ctx(p)

def sig_period(cid):
    if cid in sig:
        return sig[cid]
    for suf in 'abcd':
        if cid.endswith(suf) and cid[:-1] in sig:
            return sig[cid[:-1]]
    return sig.get(cid + 'a')

agree = disagree = 0
dis_list = []
for cid, c in ctx.items():
    s = sig_period(cid)
    if not s:
        continue
    if c == s:
        agree += 1
    elif c[:2] == s[:2]:               # эпоха совпала (MM/LM), фаза нет
        agree += 1
        dis_list.append((cid, c, s, 'фаза'))
    else:
        disagree += 1
        dis_list.append((cid, c, s, 'ЭПОХА'))
print(f'общих датированных документов: {agree + disagree}; '
      f'эпоха совпадает: {agree} ({agree / (agree + disagree):.0%}), '
      f'противоречат по эпохе: {disagree}')
ep = [x for x in dis_list if x[3] == 'ЭПОХА']
print('противоречия по эпохе (MM против LM):')
for cid, c, s, _ in ep[:12]:
    print(f'   {cid:<10} lineara.xyz={c:<8} SigLA={s}')
ph = [x for x in dis_list if x[3] == 'фаза']
print(f'расхождения только по фазе (внутри эпохи): {len(ph)} — примеры: '
      f'{[(c, a, b) for c, a, b, _ in ph[:5]]}')
print('''
Чтение: (а) «парсер верен» = наше слово стоит в сыром translatedWords —
расхождение с SigLA относится к редакциям, не к нашему пайплайну;
(б) два независимых датировочных слоя взаимно валидируются по эпохе;
противоречия по эпохе — короткий список для ручной проверки.''')
