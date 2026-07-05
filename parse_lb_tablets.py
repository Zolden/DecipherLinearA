# -*- coding: utf-8 -*-
"""Этап 9.1 (§AH, часть 1): потабличный разбор LB-страниц и именные СЛОТЫ.

Токенизация каждой таблички (архив deaditerranean, 217 страниц Wayback):
слова (a-b-c), логограммы (VIR, MUL, OVIS…, с гендерными суффиксами),
числа. Слот-эвристики имён (консервативные, по стандартной структуре серий):
  N1: слово непосредственно ПЕРЕД логограммой людей/скота/металла
      (VIR, MUL, OVIS, CAP, SUS, BOS, EQU, AES);
  N2: слово сразу ПОСЛЕ pa-ro («у такого-то» — коллекторы KN D);
  N3: ПЕРВОЕ слово таблички KN D-серии (пастух);
  N4: слово непосредственно ПЕРЕД e-ke / e-ke-qe (землевладельцы PY E-серий).
Слова из греческого стоп-листа и топонимы исключаются. Выход:
lb_name_slots.tsv (слово, слоты, число табличек, серии).
"""
import sys, os, re, glob
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

PAGES = r'C:\Users\Zolden\AppData\Local\Temp\claude\C--OtherProjects-DecipherLinearA\326d5771-1722-4f92-9507-d4b90f84c275\scratchpad\lb_pages'

TABLET = re.compile(r'\b(KN|PY|KH|MY|TI|TH|EL)\s+([A-Z][a-z]{0,2})\s*\(?(\d+)')
WORD = re.compile(r'(?<![a-zA-Z0-9*-])((?:[a-z][a-z0-9]?|\*\d+)'
                  r'(?:-(?:[a-z][a-z0-9]?|\*\d+))+)(?![a-z0-9-])')
LOGO = re.compile(r'(?<![A-Za-z])(VIR|MUL|OVIS|CAP|SUS|BOS|EQU|AES|GRA|VIN|OLE|'
                  r'FAR|HORD|NI|CYP|TELA|LANA|AUR)([a-z]?)(?![A-Za-z])')

GREEK = {'to-so', 'to-sa', 'to-so-de', 'to-sa-de', 'o-pe-ro', 'do-e-ro',
         'do-e-ra', 'ko-wo', 'ko-wa', 'pa-ro', 'e-ke', 'e-ke-qe', 'e-ko-si',
         'o-na-to', 'ko-to-na', 'ko-to-i-na', 'ke-ke-me-na', 'ki-ti-me-na',
         'da-mo', 'te-o', 'te-o-jo', 'i-je-re-ja', 'i-je-re-u', 'i-je-ro',
         'ka-ko', 'ku-ru-so', 'e-ra-wo', 'a-pu-do-si', 'do-so-mo', 'o-pi',
         'qa-si-re-u', 'ra-wa-ke-ta', 'wa-na-ka', 'wa-na-ka-te-ro', 'me-zo',
         'me-zo-e', 'me-u-jo', 'me-wi-jo', 'ne-wo', 'ne-wa', 'pa-ra-jo',
         'pe-mo', 'pe-ma', 'ta-ra-si-ja', 'a-ta-ra-si-jo', 'we-to', 'di-do-si',
         'e-u-ke-to', 'o-da-a2', 'te-ke', 'a-pe-o', 'e-qe-ta', 'pe-ru-si-nu-wo',
         'a-ni-ja', 'to-pe-za', 'pa-we-a', 'pa-we-a2', 'tu-na-no', 'o-u-qe',
         'e-me', 'du-wo-u-pi', 'ki-ri-ta', 'su-za', 'ka-po', 'we-je-we',
         'a-pe-e-ke', 'e-re-u-te-ra', 'e-re-u-te-ro', 'ko-to-no-o-ko',
         'to-me', 'a-no-no', 'wo-zo', 'wo-ze', 'o-wo-ze', 'e-to-ni-jo',
         'a-ki-ti-to', 'ki-ti-to', 'wo-i-ko-de', 'do-de', 'pa-si', 'e-pi'}
TOP = {'pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'ku-do-ni-ja', 'tu-ri-so',
       'su-ki-ri-ta', 'se-to-i-ja', 'di-ka-ta', 'ru-ki-to', 'e-ko-so', 'pu-so',
       'a-pa-ta-wa', 'da-wo', 'do-ti-ja', 'e-ra', 'ku-ta-to', 'qa-ra', 'ra-ja',
       'ra-su-to', 'ra-to', 'ri-jo-no', 'si-ra-ro', 'su-ri-mo', 'tu-ni-ja',
       'u-ta-no', 'wa-to', 'pu-na-so', 'ti-ri-to', 'qa-mo', 'da-*22-to',
       'pi-ko-to?', 'e-ki-si-jo', 'pu-ro', 'pa-ki-ja-na', 'pa-ki-ja-ne',
       'ro-u-so', 'a-ke-re-wa', 'ti-mi-to-a-ke-e', 'me-ta-pa', 'pe-to-no'}

NUM = re.compile(r'(?<![A-Za-z0-9-])(\d+)(?![A-Za-z0-9])')

def tokenize(txt):
    events = []
    covered = []
    for m in TABLET.finditer(txt):
        events.append((m.start(), 'T', (m.group(1), m.group(2), m.group(3))))
        covered.append((m.start(), m.end()))
    for m in WORD.finditer(txt):
        events.append((m.start(), 'W', m.group(1)))
    for m in LOGO.finditer(txt):
        events.append((m.start(), 'L', m.group(1)))
    for m in NUM.finditer(txt):
        # числа внутри номеров табличек не считаем
        if any(a <= m.start() < b for a, b in covered): continue
        events.append((m.start(), 'N', m.group(1)))
    events.sort()
    return events

slots = defaultdict(lambda: defaultdict(set))   # word -> slot -> tablets
series_of = defaultdict(set)
n_tab = 0
for fn in sorted(glob.glob(os.path.join(PAGES, '*.html'))):
    raw = open(fn, encoding='utf-8', errors='replace').read()
    i = raw.find('entry-content')
    if i == -1: continue
    j = min([x for x in (raw.find('Responses to', i), raw.find('class="comment', i),
                         raw.find('page_item', i), len(raw)) if x != -1])
    body = re.sub(r'<script.*?</script>', ' ', raw[i:j], flags=re.S)
    txt = re.sub(r'<[^>]+>', ' ', body)
    txt = re.sub(r'\s+', ' ', txt)
    events = tokenize(txt)
    cur = None; buf = []
    def flush():
        global n_tab
        if cur is None or not buf: return
        n_tab += 1
        site, ser, num = cur
        tid = f'{site} {ser} {num}'
        wser = f'{site} {ser}'
        first_w = next((v for t, v in buf if t == 'W'), None)
        for k, (t, v) in enumerate(buf):
            if t != 'W': continue
            w = v
            series_of[w].add(wser)
            nxt = buf[k + 1] if k + 1 < len(buf) else (None, None)
            prv = buf[k - 1] if k > 0 else (None, None)
            if nxt[0] == 'L' and nxt[1] in ('VIR', 'MUL', 'OVIS', 'CAP', 'SUS',
                                            'BOS', 'EQU', 'AES'):
                slots[w]['N1'].add(tid)
            # N1b: одно слово между именем и логограммой людей/скота
            # (пары «имя , имя VIR 2» — лакуны/запятые скрейп рвёт)
            nxt2 = buf[k + 2] if k + 2 < len(buf) else (None, None)
            if nxt[0] == 'W' and nxt2[0] == 'L' and nxt2[1] in (
                    'VIR', 'MUL', 'OVIS', 'CAP', 'SUS', 'BOS', 'EQU', 'AES'):
                slots[w]['N1b'].add(tid)
            if prv[0] == 'W' and prv[1] == 'pa-ro':
                slots[w]['N2'].add(tid)
            if site == 'KN' and ser.startswith('D') and len(ser) <= 2 \
               and w == first_w:
                slots[w]['N3'].add(tid)
            # N6: первое слово личных списков B/As/V/Ap (KN B 799: имя, имя, … VIR)
            if site == 'KN' and ser in ('B', 'As', 'V', 'Vc', 'Ap') \
               and w == first_w:
                slots[w]['N6'].add(tid)
            # N7: слово непосредственно перед GRA в земельно-зерновых сериях
            if nxt[0] == 'L' and nxt[1] == 'GRA' and (
                    (site == 'KN' and ser in ('E', 'F', 'Uf')) or
                    (site == 'PY' and ser in ('Ea', 'Eb', 'En', 'Eo', 'Ep'))):
                slots[w]['N7'].add(tid)
            if nxt[0] == 'W' and nxt[1] in ('e-ke', 'e-ke-qe', 'o-na-to'):
                slots[w]['N4'].add(tid)
            # N5: голое «слово + число» в именных сериях (формат Vc/B/As/E/Uf/Ag)
            if nxt[0] == 'N' and site in ('KN', 'PY', 'MY') and (
                    ser in ('Vc', 'V', 'B', 'As', 'E', 'Uf', 'Ag', 'Ai', 'Ap')
                    or (site == 'PY' and ser in ('Jn', 'An', 'Cn'))):
                slots[w]['N5'].add(tid)
    for ev in events:
        if ev[1] == 'T':
            flush(); cur = ev[2]; buf = []
        else:
            buf.append((ev[1], ev[2]))
    flush()

# фильтр валидности слога + стоп-листы
CONS = set('djkmnpqrstwz')
def valid(w):
    for s in w.split('-'):
        if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): continue
        m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
        if not (m and m.group(1) in CONS): return False
    return True

names = {}
for w, sl in slots.items():
    if not valid(w) or w in GREEK or w in TOP: continue
    if len(w.split('-')) < 2: continue
    tabs = set().union(*sl.values())
    names[w] = (sorted(sl.keys()), len(tabs))

print(f'табличек разобрано: {n_tab}; слов в именных слотах: {len(names)}')
sl_cnt = Counter()
for w, (sl, n) in names.items():
    for s in sl: sl_cnt[s] += 1
print('по слотам:', dict(sl_cnt))
with open('lb_name_slots.tsv', 'w', encoding='utf-8') as f:
    f.write('word\tslots\tn_tablets\tseries\n')
    for w, (sl, n) in sorted(names.items(), key=lambda kv: -kv[1][1]):
        f.write(f'{w}\t{",".join(sl)}\t{n}\t{",".join(sorted(series_of[w]))}\n')
print('топ-15:', [w for w, _ in sorted(names.items(), key=lambda kv: -kv[1][1])[:15]])
