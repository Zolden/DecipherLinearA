# -*- coding: utf-8 -*-
"""Этап 9.7 (§AM): типология v2 — починенные парсеры (транслит в скобках) +
древнегреческий (контроль №2), этрусский, грузинский, баскский-v2 и
псевдоязык «догреческий субстрат».

Субстрат: конвенциональный список слов с -νθ-/-σσ- и др. (топонимы и
заимствования, классическая литература по субстрату), в двух проекциях:
целое слово (с греческим окончанием) и основа (окончание -os/-e/-a снято) —
вторая честнее отражает субстратный материал. Прочее — как в §AG.
"""
import sys, os, re, glob, random, unicodedata, pickle
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)

SW = r'C:\Users\Zolden\AppData\Local\Temp\claude\C--OtherProjects-DecipherLinearA\326d5771-1722-4f92-9507-d4b90f84c275\scratchpad\swadesh'

def parse_swadesh(path):
    d = open(path, encoding='utf-8', errors='replace').read()
    i = d.find('<table')
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', d[i:], re.S)
    words = []
    for r in rows[1:]:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)
        if len(cells) < 3: continue
        txt = re.sub(r'<[^>]+>', '', cells[2])
        txt = re.sub(r'&#\d+;|&[a-z]+;', ' ', txt)
        # транслитерация в скобках (грец./этрус./груз.), иначе сам текст
        par = re.findall(r'\(([^()]*[a-z][^()]*)\)', txt)
        if par:
            txt = par[0]
        txt = re.split(r'[,;/]', txt)[0].strip()
        if not txt or txt in ('—', '-', '?'): continue
        words.append(txt)
    return words

VOW = set('aeiou')
def normalize(w):
    w = w.lower()
    w = unicodedata.normalize('NFD', w)
    w = ''.join(ch for ch in w if not unicodedata.combining(ch))
    w = w.replace('š', 's').replace('ṣ', 's').replace('ç', 's').replace('ś', 's')
    w = w.replace('ḫ', 'h').replace('x', 'h').replace('χ', 'h')
    w = w.replace('θ', 't').replace('φ', 'p').replace('ê', 'e').replace('ô', 'o')
    w = w.replace('ē', 'e').replace('ō', 'o').replace('ā', 'a').replace('ī', 'i')
    w = w.replace('ū', 'u').replace('y', 'u')   # др.-греч. υ ~ u
    w = re.sub(r'[^a-z]', '', w)
    return w

def syllabify(w):
    if not w or not any(c in VOW for c in w): return None
    syls, cur = [], ''
    for ch in w:
        cur += ch
        if ch in VOW: syls.append(cur); cur = ''
    return syls

def profile(words):
    ps = [syllabify(normalize(w)) for w in words]
    ps = [p for p in ps if p and len(p) >= 2]
    n = len(ps)
    if n < 20: return None
    return {
        'n': n,
        'len': sum(len(p) for p in ps) / n,
        'iniV': sum(1 for p in ps if len(p[0]) == 1 and p[0] in VOW) / n,
        'hiat': sum(1 for p in ps if any(len(s) == 1 and s in VOW
                                         for s in p[1:])) / n,
        'red': sum(1 for p in ps if any(p[i] == p[i + 1]
                                        for i in range(len(p) - 1))) / n,
        'fin': (lambda fc: {v: fc.get(v, 0) / max(1, sum(fc.values()))
                            for v in 'aeiou'})(Counter(p[-1][-1] for p in ps)),
    }

langs = {}
for path in glob.glob(os.path.join(SW, '*.html')):
    name = os.path.basename(path)[:-5]
    if name == 'pregreek': continue
    pr = profile(parse_swadesh(path))
    if pr: langs[name] = pr

# догреческий субстрат (конвенциональный список; -нθ-/-сс- и классика)
PREGREEK = ['korinthos', 'zakunthos', 'tirunthos', 'laburinthos', 'asaminthos',
            'terebinthos', 'erebinthos', 'huakinthos', 'olunthos', 'merinthos',
            'kolokunthe', 'knossos', 'tulissos', 'amnissos', 'parnassos',
            'halikarnassos', 'ilissos', 'kephissos', 'humettos', 'lukabettos',
            'thalassa', 'kuparissos', 'narkissos', 'plinthos', 'sminthos',
            'basileus']
stems = []
for w in PREGREEK:
    s = re.sub(r'(os|e|a|us)$', '', w)
    stems.append(s)
langs['PreGreek (слова)'] = profile(PREGREEK + PREGREEK)   # дублируем до n>=20? нет:
langs['PreGreek (слова)'] = profile(PREGREEK) or profile(PREGREEK * 2)
langs['PreGreek (основы)'] = profile(stems) or profile(stems * 2)

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

print(f'{"язык":<24}{"n":>5}{"слог":>6}{"V-нач":>7}{"зиян":>6}{"ред":>6}'
      f'{"a":>6}{"e":>5}{"i":>5}{"o":>5}{"u":>5}')
for name, p in sorted(langs.items()):
    if not p: continue
    f = p['fin']
    print(f'{name:<24}{p["n"]:>5}{p["len"]:>6.2f}{p["iniV"]:>7.0%}{p["hiat"]:>6.0%}'
          f'{p["red"]:>6.1%}{f["a"]:>6.0%}{f["e"]:>5.0%}{f["i"]:>5.0%}'
          f'{f["o"]:>5.0%}{f["u"]:>5.0%}')

la = langs['LA (лексикон)']
print('\n=== близость к LA (сумма: TV(финали)+|Δзияние|+|ΔV-нач|+|Δслог|/3) ===')
scores = []
for name, p in langs.items():
    if not p or name.startswith('LA'): continue
    tv = 0.5 * sum(abs(la['fin'][v] - p['fin'][v]) for v in 'aeiou')
    s = tv + abs(la['hiat'] - p['hiat']) + abs(la['iniV'] - p['iniV']) \
        + abs(la['len'] - p['len']) / 3
    scores.append((s, name, tv))
for s, name, tv in sorted(scores):
    print(f'   {name:<24} сумма={s:.3f} (TV финалей {tv:.3f})')
