# -*- coding: utf-8 -*-
"""Этап 6, п.1 (часть 1): сборка лексикона линейного B из архивных страниц
minoan.deaditerranean.com (Wayback Machine; транслитерации Killen & Olivier 1989
для KN, Bennett для PY и др.; скрейп InsiderPhD/Linear-B-Dataset дал только
серию KN A, остальное скачано из web.archive.org по CDX-списку).

Из каждой страницы берётся entry-content до секции комментариев/References;
слова = последовательности слогов вида a-b-c (>=2 слогов, строчные, допускаются
*NN); каждому слову приписываются серии табличек, в которых оно встречено
(текущая табличка отслеживается по заголовкам вида «KN Da 1156»).
Выход: lb_lexicon.tsv (слово, число вхождений, серии, сайты).
"""
import sys, os, re, glob
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

PAGES = r'C:\Users\Zolden\AppData\Local\Temp\claude\C--OtherProjects-DecipherLinearA\326d5771-1722-4f92-9507-d4b90f84c275\scratchpad\lb_pages'

TABLET = re.compile(r'\b(KN|PY|KH|MY|TI|TH|EL)\s+([A-Z][a-z]{0,2})\s*\(?\d')
WORD = re.compile(r'(?<![a-z0-9*-])((?:[a-z][a-z0-9]?|\*\d+)(?:-(?:[a-z][a-z0-9]?|\*\d+))+)(?![a-z0-9-])')

lex = Counter(); series_of = defaultdict(set); sites_of = defaultdict(set)
n_pages = 0
for fn in sorted(glob.glob(os.path.join(PAGES, '*.html'))):
    raw = open(fn, encoding='utf-8', errors='replace').read()
    i = raw.find('entry-content')
    if i == -1: continue
    j = min([x for x in (raw.find('Responses to', i), raw.find('class="comment', i),
                         raw.find('References', i), len(raw)) if x != -1])
    body = raw[i:j]
    body = re.sub(r'<script.*?</script>', ' ', body, flags=re.S)
    txt = re.sub(r'<[^>]+>', ' ', body)
    txt = txt.replace('&#8217;', "'").replace('&#8216;', "'").replace('&#8220;', ' ').replace('&#8221;', ' ')
    txt = re.sub(r'\s+', ' ', txt)
    n_pages += 1
    cur_site, cur_series = None, None
    pos = 0
    # проходим по токенам: обновляем текущую табличку, собираем слова
    events = []
    for m in TABLET.finditer(txt):
        events.append((m.start(), 'T', (m.group(1), m.group(2))))
    for m in WORD.finditer(txt):
        events.append((m.start(), 'W', m.group(1)))
    events.sort()
    for _, kind, val in events:
        if kind == 'T':
            cur_site, cur_series = val
        else:
            w = val.strip('-')
            # отсев мусора: чисто латинские слова английского текста вида
            # 'a-b' с длинными слогами уже отрезаны регэкспом (слоги <=2 букв);
            if len(w) < 3: continue
            lex[w] += 1
            if cur_site:
                series_of[w].add(f'{cur_site} {cur_series}')
                sites_of[w].add(cur_site)

print(f'страниц: {n_pages}; типов слов: {len(lex)}; токенов: {sum(lex.values())}')
with open('lb_lexicon.tsv', 'w', encoding='utf-8') as f:
    f.write('word\tcount\tseries\tsites\n')
    for w, c in lex.most_common():
        f.write(f'{w}\t{c}\t{",".join(sorted(series_of[w]))}\t'
                f'{",".join(sorted(sites_of[w]))}\n')
print('примеры:', lex.most_common(15))
kn_d = [w for w in lex if any(s.startswith('KN D') for s in series_of[w])]
print(f'слов с аттестацией в KN D-сериях: {len(kn_d)}')
for probe in ['pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'su-ki-ri-ta', 'se-to-i-ja',
              'da-wo', 'ru-ki-to', 'ku-do-ni-ja', 'to-so', 'o-pe-ro']:
    print(f'   {probe}: {lex.get(probe, 0)}')
