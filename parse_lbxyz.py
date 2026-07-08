# -*- coding: utf-8 -*-
"""Этап 14 (§BJ, часть 1): полный корпус линейного B с linearb.xyz.

Источник: github.com/mwenge/linearb.xyz (commit 84e0b00e), файл
LinearBInscriptions.js — 5889 документов (KN 4223, PY 986, TH 363, MY 87,
TI 24…) с потабличными токенами (transliteratedWords), сериями (label) и
писцами. Локальный кэш: .lbxyz_cache.js (в git не входит — см. fetch-скрипт).

Выход:
  lb2_lexicon.tsv    — слово, частота, сайты, число документов;
  lb2_name_slots.tsv — слот-имена (N1 перед логограммой людей/скота/металла,
                       N2 после pa-ro, N3 первое слово KN D-серий,
                       N5 «слово+число» в именных сериях, N6 первое слово
                       личных списков B/As/V/Ap, N7 перед GRA в E/Uf/PY-E).
"""
import sys, json, re
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

txt = open('.lbxyz_cache.js', encoding='utf-8').read()
arr = json.loads(txt[txt.find('['):txt.rfind(']') + 1])
docs = dict(arr)
print(f'документов: {len(docs)}')

CONS = set('djkmnpqrstwz')
def valid_word(w):
    syls = w.split('-')
    if len(syls) < 2: return False
    for s in syls:
        if s in ('a', 'e', 'i', 'o', 'u', 'a2', 'a3'): continue
        m = re.fullmatch(r'([a-z])([aeiou])([23])?', s)
        if not (m and m.group(1) in CONS): return False
    return True

PEOPLE_LOGO = re.compile(r'^(VIR|MUL|OVIS|CAP|SUS|BOS|EQU|AES)(:.*)?$')
GREEK = {'to-so', 'to-sa', 'to-so-de', 'o-pe-ro', 'do-e-ro', 'do-e-ra',
         'ko-wo', 'ko-wa', 'pa-ro', 'e-ke', 'e-ke-qe', 'o-na-to', 'ko-to-na',
         'ke-ke-me-na', 'ki-ti-me-na', 'da-mo', 'te-o', 'te-o-jo', 'i-je-re-ja',
         'qa-si-re-u', 'wa-na-ka', 'me-zo', 'me-u-jo', 'ne-wo', 'pa-ra-jo',
         'pe-mo', 'ta-ra-si-ja', 'we-to', 'o-da-a2', 'to-sa-de', 'a-pe-o',
         'e-qe-ta', 'i-je-re-u', 'i-je-ro', 'ka-ko', 'ku-ru-so', 'e-ra-wo'}
TOPON = {'pa-i-to', 'ko-no-so', 'a-mi-ni-so', 'ku-do-ni-ja', 'tu-ri-so',
         'su-ki-ri-ta', 'se-to-i-ja', 'di-ka-ta', 'ru-ki-to', 'e-ko-so',
         'pu-so', 'a-pa-ta-wa', 'da-wo', 'do-ti-ja', 'e-ra', 'ku-ta-to',
         'qa-ra', 'ra-ja', 'ra-su-to', 'ra-to', 'ri-jo-no', 'si-ra-ro',
         'su-ri-mo', 'tu-ni-ja', 'u-ta-no', 'wa-to', 'pu-na-so', 'ti-ri-to',
         'qa-mo', 'da-*22-to', 'pu-ro', 'pa-ki-ja-na', 'ro-u-so', 'a-ke-re-wa',
         'me-ta-pa', 'pe-to-no', 'ti-mi-to-a-ke-e'}

lex = Counter(); lex_sites = defaultdict(set); lex_docs = defaultdict(set)
slots = defaultdict(lambda: defaultdict(set))
NAME_SERIES_N5 = re.compile(r'^KN (Vc?|B|As|E|Uf|Ag|Ai|Ap)\b|^PY (Jn|An|Cn)\b')
D_SERIES = re.compile(r'^KN D[a-z]?\b')
B_SERIES = re.compile(r'^KN (B|As|V|Vc|Ap)\b')
GRA_SERIES = re.compile(r'^KN (E|F|Uf)\b|^PY E[abnop]\b')

for key, rec in docs.items():
    tw = rec.get('transliteratedWords') or []
    label = rec.get('label') or rec.get('name') or key
    site = rec.get('site') or key[:2]
    words_here = [w for w in tw if isinstance(w, str) and valid_word(w)]
    first_w = words_here[0] if words_here else None
    for i, tok in enumerate(tw):
        if not isinstance(tok, str): continue
        if valid_word(tok):
            lex[tok] += 1
            lex_sites[tok].add(site)
            lex_docs[tok].add(label)
            if tok in GREEK or tok in TOPON: continue
            # скобки/лакуны прозрачны для смежности
            def nx(k):
                j = i + 1; seen = 0
                while j < len(tw):
                    t = tw[j]
                    if isinstance(t, str) and t in ('[', ']', ']vest.', 'vest.'):
                        j += 1; continue
                    if seen == k: return t
                    seen += 1; j += 1
                return ''
            def pv():
                j = i - 1
                while j >= 0:
                    t = tw[j]
                    if isinstance(t, str) and t in ('[', ']'):
                        j -= 1; continue
                    return t
                return ''
            nxt = nx(0)
            nxt2 = nx(1)
            prv = pv()
            if isinstance(nxt, str) and PEOPLE_LOGO.match(nxt):
                slots[tok]['N1'].add(label)
            elif isinstance(nxt2, str) and isinstance(nxt, str) \
                    and valid_word(nxt) and PEOPLE_LOGO.match(nxt2):
                slots[tok]['N1b'].add(label)
            if prv == 'pa-ro':
                slots[tok]['N2'].add(label)
            if tok == first_w and D_SERIES.match(label):
                slots[tok]['N3'].add(label)
            if isinstance(nxt, str) and re.fullmatch(r'\d+', nxt) \
                    and NAME_SERIES_N5.match(label):
                slots[tok]['N5'].add(label)
            if tok == first_w and B_SERIES.match(label):
                slots[tok]['N6'].add(label)
            if isinstance(nxt, str) and nxt.startswith('GRA') \
                    and GRA_SERIES.match(label):
                slots[tok]['N7'].add(label)
            # N4: слово перед e-ke / e-ke-qe / o-na-to (землевладельцы)
            if nxt in ('e-ke', 'e-ke-qe', 'o-na-to'):
                slots[tok]['N4'].add(label)

print(f'лексикон: {len(lex)} типов, {sum(lex.values())} токенов')
with open('lb2_lexicon.tsv', 'w', encoding='utf-8') as f:
    f.write('word\tcount\tsites\tn_docs\n')
    for w, c in lex.most_common():
        f.write(f'{w}\t{c}\t{",".join(sorted(lex_sites[w]))}\t{len(lex_docs[w])}\n')

names = {w: sl for w, sl in slots.items()}
print(f'слот-имён: {len(names)}')
sl_cnt = Counter()
for w, sl in names.items():
    for s in sl: sl_cnt[s] += 1
print('по слотам:', dict(sl_cnt))
with open('lb2_name_slots.tsv', 'w', encoding='utf-8') as f:
    f.write('word\tslots\tn_tablets\n')
    for w, sl in sorted(names.items(), key=lambda kv: -sum(len(v) for v in kv[1].values())):
        tabs = set().union(*sl.values())
        f.write(f'{w}\t{",".join(sorted(sl))}\t{len(tabs)}\n')
print('топ-12:', [w for w, _ in sorted(names.items(), key=lambda kv: -sum(len(v) for v in kv[1].values()))[:12]])
