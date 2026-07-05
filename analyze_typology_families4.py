# -*- coding: utf-8 -*-
"""Этап 11.7 (§AY): типология v4 — леммы Wiktionary в родных алфавитах
(этрусский Old Italic, лидийский, ликийский, карийский) + прежний набор.

Транслитерация — стандартные значения букв (Bonfante для этрусского, Melchert
для ликийского/лидийского, Adiego для карийского — ПРИБЛИЖЁННО, помечено).
Носовые ã/ẽ → a/e; θ→t, φ→p, χ→k; ś→s. Метрики/проекция как §AG/§AM/§AT.
"""
import sys, os, re, glob, json, random, unicodedata, pickle
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
B = 500

SW = r'C:\Users\Zolden\AppData\Local\Temp\claude\C--OtherProjects-DecipherLinearA\326d5771-1722-4f92-9507-d4b90f84c275\scratchpad\swadesh'

OLD_ITALIC = {'𐌀': 'a', '𐌁': 'b', '𐌂': 'k', '𐌃': 'd', '𐌄': 'e', '𐌅': 'v',
              '𐌆': 'z', '𐌇': 'h', '𐌈': 't', '𐌉': 'i', '𐌊': 'k', '𐌋': 'l',
              '𐌌': 'm', '𐌍': 'n', '𐌎': 's', '𐌏': 'o', '𐌐': 'p', '𐌑': 's',
              '𐌒': 'q', '𐌓': 'r', '𐌔': 's', '𐌕': 't', '𐌖': 'u', '𐌗': 'ks',
              '𐌘': 'p', '𐌙': 'k', '𐌚': 'f', '𐌛': 'r', '𐌜': 's', '𐌝': 'i'}
LYDIAN = {'𐤠': 'a', '𐤡': 'b', '𐤢': 'g', '𐤣': 'd', '𐤤': 'e', '𐤥': 'w',
          '𐤦': 'i', '𐤧': 'i', '𐤨': 'k', '𐤩': 'l', '𐤪': 'm', '𐤫': 'n',
          '𐤬': 'o', '𐤭': 'r', '𐤮': 's', '𐤯': 't', '𐤰': 'u', '𐤱': 'f',
          '𐤲': 'q', '𐤳': 's', '𐤴': 't', '𐤵': 'a', '𐤶': 'e', '𐤷': 'l',
          '𐤸': 'n', '𐤹': 'k'}
LYCIAN = {'𐊀': 'a', '𐊁': 'e', '𐊂': 'b', '𐊃': 'b', '𐊄': 'g', '𐊅': 'd',
          '𐊆': 'i', '𐊇': 'w', '𐊈': 'z', '𐊉': 'h', '𐊊': 'j', '𐊋': 'k',
          '𐊌': 'q', '𐊍': 'l', '𐊎': 'm', '𐊏': 'n', '𐊐': 'm', '𐊑': 'n',
          '𐊒': 'u', '𐊓': 'p', '𐊔': 'k', '𐊕': 'r', '𐊖': 's', '𐊗': 't',
          '𐊘': 't', '𐊙': 'a', '𐊚': 'e', '𐊛': 'h', '𐊜': 'h'}
CARIAN = {'𐊠': 'a', '𐊡': 'b', '𐊢': 'd', '𐊣': 'l', '𐊤': 'u', '𐊥': 'r',
          '𐊦': 'l', '𐊧': 'a', '𐊨': 'q', '𐊩': 's', '𐊪': 'm', '𐊫': 'o',
          '𐊬': 'g', '𐊭': 't', '𐊮': 's', '𐊯': 'e', '𐊰': 's', '𐊱': '?',
          '𐊲': 'u', '𐊳': 'n', '𐊴': 'k', '𐊵': 'n', '𐊶': 'w', '𐊷': 'p',
          '𐊸': 's', '𐊹': 'i', '𐊺': 'e', '𐊻': 'w', '𐊼': 'k', '𐊽': 'k',
          '𐊾': 'd', '𐊿': 'w', '𐋀': 'l', '𐋁': 'l', '𐋂': 'z', '𐋃': 'l',
          '𐋄': 'n'}

def translit(w, table):
    out = ''.join(table.get(ch, '') for ch in w)
    return out if '?' not in out else ''

def load_cat(lang, table):
    path = os.path.join(SW, f'cat_{lang}.json')
    d = json.load(open(path, encoding='utf-8'))
    words = []
    for m in d.get('query', {}).get('categorymembers', []):
        t = m['title']
        if ':' in t: continue
        lat = translit(t, table) if any(ord(c) > 0x10000 for c in t) else t.lower()
        if len(lat) >= 3: words.append(lat)
    return sorted(set(words))

VOW = set('aeiou')
def normalize(w):
    w = w.lower()
    w = unicodedata.normalize('NFD', w)
    w = ''.join(ch for ch in w if not unicodedata.combining(ch))
    for a, b in [('š', 's'), ('ṣ', 's'), ('ç', 's'), ('ś', 's'), ('ḫ', 'h'),
                 ('x', 'h'), ('χ', 'h'), ('θ', 't'), ('φ', 'p'), ('ē', 'e'),
                 ('ō', 'o'), ('ā', 'a'), ('ī', 'i'), ('ū', 'u'), ('y', 'u'),
                 ('v', 'w')]:
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

langs = {}
langs['Etruscan (Wikt+глосс)'] = profile(
    load_cat('Etruscan', OLD_ITALIC) +
    ['apa', 'ati', 'clan', 'puia', 'ruva', 'zilath', 'spur', 'methlum',
     'rasna', 'avil', 'tin', 'usil', 'tiur', 'thesan', 'ais', 'aisar',
     'fler', 'suthi', 'hinthial', 'zich', 'cepen', 'tur', 'mul', 'lupu',
     'svalce', 'cver', 'tular', 'cel', 'calu', 'thu', 'zal', 'ci', 'mach',
     'huth', 'sar', 'zathrum'])
langs['Lydian (Wikt)'] = profile(load_cat('Lydian', LYDIAN), min_n=15)
langs['Lycian (Wikt)'] = profile(load_cat('Lycian', LYCIAN), min_n=15)
langs['Carian (Wikt, прибл.)'] = profile(load_cat('Carian', CARIAN), min_n=15)

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
for nm in ('Hittite', 'Luwian', 'Sumerian', 'Basque', 'Hurrian', 'Akkadian',
           'Georgian', 'Ancient_Greek'):
    pr = profile(parse_swadesh(os.path.join(SW, nm + '.html')))
    if pr: langs[nm] = pr

corpus = pickle.load(open('corpus.pkl', 'rb'))
la_words = set()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            if any(s.startswith('*') or '+' in s for s in v['signs']): continue
            la_words.add(''.join(s.lower().rstrip('23') for s in v['signs']))
langs['LA (лексикон)'] = profile(sorted(la_words))
lb_words = set()
for line in open('lb_lexicon.tsv', encoding='utf-8'):
    if line.startswith('word\t'): continue
    w = line.split('\t')[0]
    syls = w.split('-')
    if len(syls) >= 2 and all(re.fullmatch(r'[a-z][aeiou][23]?|[aeiou]|a[23]', s)
                              for s in syls):
        lb_words.add(''.join(s.rstrip('23') for s in syls))
langs['LB (греч.)'] = profile(sorted(lb_words))

la = langs['LA (лексикон)']
def score_between(p1, p2):
    tv = 0.5 * sum(abs(p1['fin'][v] - p2['fin'][v]) for v in 'aeiou')
    return tv + abs(p1['hiat'] - p2['hiat']) + abs(p1['iniV'] - p2['iniV']) \
        + abs(p1['len'] - p2['len']) / 3

print(f'{"язык":<26}{"n":>5}{"балл":>7}{"95% CI":>18}   финали a/e/i/o/u')
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
    fins = '/'.join(f'{p["fin"][v]:.0%}' for v in 'aeiou')
    rows.append((s, name, p['n'], vals[int(0.025 * B)], vals[int(0.975 * B)], fins))
for s, name, n, lo, hi, fins in sorted(rows):
    print(f'{name:<26}{n:>5}{s:>7.3f}   [{lo:.3f}, {hi:.3f}]   {fins}')
