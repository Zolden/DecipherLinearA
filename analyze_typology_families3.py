# -*- coding: utf-8 -*-
"""Этап 10.7 (§AS): типология v3 — этрусский (курируемый глоссарий),
догреческий субстрат (извлечение из Википедии + транслитератор), бутстреп-CI
для всех языков.

Этрусский: ~45 надёжно засвидетельствованных НЕзаимствованных слов (числит.,
родство, титулы, базовая лексика Liber Linteus/эпитафий; заимствования из
греческого исключены). Субстрат: греческие слова из статьи Pre-Greek substrate
(программная транслитерация политоники), с усечением греческих окончаний.
Метрики и проекция — как §AG/§AM. CI: бутстреп по словам, R=500.
"""
import sys, os, re, glob, random, unicodedata, pickle
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
B = 500

SW = r'C:\Users\Zolden\AppData\Local\Temp\claude\C--OtherProjects-DecipherLinearA\326d5771-1722-4f92-9507-d4b90f84c275\scratchpad\swadesh'

ETRUSCAN = ['apa', 'ati', 'clan', 'puia', 'ruva', 'lautun', 'lautni', 'zilath',
            'purth', 'maru', 'camthi', 'spur', 'methlum', 'rasna', 'avil',
            'ril', 'tin', 'usil', 'tiur', 'thesan', 'ais', 'aisar', 'fler',
            'sacni', 'suthi', 'hinthial', 'zich', 'cepen', 'netsvis', 'tur',
            'turuce', 'mul', 'muluvanice', 'am', 'ten', 'lupu', 'svalce',
            'cver', 'etera', 'sren', 'suthina', 'naper', 'tul', 'tular',
            'cel', 'calu', 'farthan', 'thu', 'zal', 'ci', 'mach', 'huth',
            'sar', 'zathrum', 'hupni']

GRK = {'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'e',
       'θ': 'th', 'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'ks',
       'ο': 'o', 'π': 'p', 'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'u',
       'φ': 'ph', 'χ': 'kh', 'ψ': 'ps', 'ω': 'o'}
def grk2lat(w):
    w = unicodedata.normalize('NFD', w.lower())
    w = ''.join(ch for ch in w if not unicodedata.combining(ch))
    return ''.join(GRK.get(ch, '') for ch in w)

def pregreek_from_wiki():
    path = os.path.join(SW, 'pregreek.html')
    d = open(path, encoding='utf-8', errors='replace').read()
    body = d[d.find('Examples'):d.find('References')] or d
    words = set()
    for m in re.finditer(r'[Ͱ-Ͽἀ-῿]{4,}', body):
        lat = grk2lat(m.group(0))
        lat = re.sub(r'(os|on|e|a|es)$', '', lat)
        if len(lat) >= 4: words.add(lat)
    return sorted(words)

VOW = set('aeiou')
def normalize(w):
    w = w.lower()
    w = unicodedata.normalize('NFD', w)
    w = ''.join(ch for ch in w if not unicodedata.combining(ch))
    for a, b in [('š', 's'), ('ṣ', 's'), ('ç', 's'), ('ś', 's'), ('ḫ', 'h'),
                 ('x', 'h'), ('χ', 'h'), ('θ', 't'), ('φ', 'p'), ('ē', 'e'),
                 ('ō', 'o'), ('ā', 'a'), ('ī', 'i'), ('ū', 'u'), ('y', 'u')]:
        w = w.replace(a, b)
    return re.sub(r'[^a-z]', '', w)
def syllabify(w):
    if not w or not any(c in VOW for c in w): return None
    syls, cur = [], ''
    for ch in w:
        cur += ch
        if ch in VOW: syls.append(cur); cur = ''
    return syls
def profile(words, min_n=18):
    ps = [syllabify(normalize(w)) for w in words]
    ps = [p for p in ps if p and len(p) >= 2]
    n = len(ps)
    if n < min_n: return None
    fin = Counter(p[-1][-1] for p in ps)
    tot = sum(fin.values()) or 1
    return {'n': n, 'ps': ps,
            'len': sum(len(p) for p in ps) / n,
            'iniV': sum(1 for p in ps if len(p[0]) == 1 and p[0] in VOW) / n,
            'hiat': sum(1 for p in ps if any(len(s) == 1 and s in VOW
                                             for s in p[1:])) / n,
            'fin': {v: fin.get(v, 0) / tot for v in 'aeiou'}}

def parse_swadesh(path):
    d = open(path, encoding='utf-8', errors='replace').read()
    i = d.find('<table')
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', d[i:], re.S)
    out = []
    for r in rows[1:]:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)
        if len(cells) < 3: continue
        txt = re.sub(r'<[^>]+>', '', cells[2])
        txt = re.sub(r'&#\d+;|&[a-z]+;', ' ', txt)
        par = re.findall(r'\(([^()]*[a-z][^()]*)\)', txt)
        if par: txt = par[0]
        txt = re.split(r'[,;/]', txt)[0].strip()
        if txt and txt not in ('—', '-', '?'): out.append(txt)
    return out

langs = {}
for path in glob.glob(os.path.join(SW, '*.html')):
    nm = os.path.basename(path)[:-5]
    if nm in ('pregreek', 'etruscan_wiki'): continue
    pr = profile(parse_swadesh(path))
    if pr: langs[nm] = pr
langs['Etruscan (глоссарий)'] = profile(ETRUSCAN)
pg = pregreek_from_wiki()
print(f'субстрат из Википедии: {len(pg)} основ; примеры: {pg[:12]}')
langs['PreGreek (вики-основы)'] = profile(pg)

corpus = pickle.load(open('corpus.pkl', 'rb'))
la_words = set()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            if any(s.startswith('*') or '+' in s for s in v['signs']): continue
            la_words.add(''.join(s.lower().rstrip('23') for s in v['signs']))
lb_words = set()
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    w = line.split('\t')[0]
    syls = w.split('-')
    if len(syls) >= 2 and all(re.fullmatch(r'[a-z][aeiou][23]?|[aeiou]|a[23]', s)
                              for s in syls):
        lb_words.add(''.join(s.rstrip('23') for s in syls))
langs['LA (лексикон)'] = profile(sorted(la_words))
langs['LB (греч. реальный)'] = profile(sorted(lb_words))

la = langs['LA (лексикон)']
def score_between(p1, p2):
    tv = 0.5 * sum(abs(p1['fin'][v] - p2['fin'][v]) for v in 'aeiou')
    return tv + abs(p1['hiat'] - p2['hiat']) + abs(p1['iniV'] - p2['iniV']) \
        + abs(p1['len'] - p2['len']) / 3

print(f'\n{"язык":<26}{"n":>5}{"балл":>7}{"95% CI":>18}')
rows = []
for name, p in langs.items():
    if not p or name.startswith('LA'): continue
    s = score_between(la, p)
    vals = []
    for _ in range(B):
        samp = [p['ps'][random.randrange(p['n'])] for _ in range(p['n'])]
        las = [la['ps'][random.randrange(la['n'])] for _ in range(la['n'])]
        def pr2(ps):
            n = len(ps)
            fin = Counter(x[-1][-1] for x in ps)
            t = sum(fin.values()) or 1
            return {'fin': {v: fin.get(v, 0) / t for v in 'aeiou'},
                    'hiat': sum(1 for x in ps if any(len(u) == 1 and u in VOW
                                                     for u in x[1:])) / n,
                    'iniV': sum(1 for x in ps if len(x[0]) == 1
                                and x[0] in VOW) / n,
                    'len': sum(len(x) for x in ps) / n}
        vals.append(score_between(pr2(las), pr2(samp)))
    vals.sort()
    rows.append((s, name, p['n'], vals[int(0.025 * B)], vals[int(0.975 * B)]))
for s, name, n, lo, hi in sorted(rows):
    print(f'{name:<26}{n:>5}{s:>7.3f}   [{lo:.3f}, {hi:.3f}]')
