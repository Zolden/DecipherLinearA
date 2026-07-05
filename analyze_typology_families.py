# -*- coding: utf-8 -*-
"""Этап 8.6 (§AG): типологический профиль LA против конкретных языков
(Swadesh-проекция).

Источник сравнения: Swadesh-списки Викисловаря (рендеренные таблицы) для
хеттского, лувийского, аккадского, шумерского, хурритского, этрусского,
ликийского, древнегреческого (контроль пайплайна: должен лечь рядом с LB),
баскского и грузинского.

Единое пространство сравнения: фонологическая проекция. Слово → строка звуков
(нормализация: диакритика длины снята, š/ṣ/ç→s, ḫ/x→h, аффрикаты упрощены) →
слоги по гласным ядрам. LA и LB проецируются так же: знаки → значения LB →
конкатенация (pa-i-to → paito). Метрики: слогов/слово; V-начало; доля слов с
внутренним зиянием (гласная сразу после гласной); финальная гласная (a/e/i/o/u;
конечные согласные ОТБРАСЫВАЮТСЯ — как это делает запись LB); редупликация
соседних слогов. Бутстреп 95% CI (R=1000).

ЯВНЫЕ ОГОВОРКИ: Swadesh — базовая лексика, LA-лексикон — имена и термины
учёта; списки малы (100–200 слов); проекция груба. Выход — ориентировочная
таблица близости по метрикам, НЕ утверждение родства.
"""
import sys, os, re, glob, random, unicodedata, pickle
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
B = 1000

SW = r'C:\Users\Zolden\AppData\Local\Temp\claude\C--OtherProjects-DecipherLinearA\326d5771-1722-4f92-9507-d4b90f84c275\scratchpad\swadesh'

# ---------------- парсинг Swadesh-таблиц
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
        # первое словоформа до запятой/скобки/слэша
        txt = re.split(r'[,;(/]', txt)[0].strip()
        if not txt or txt in ('—', '-', '?'): continue
        words.append(txt)
    return words

def normalize(w):
    w = w.lower()
    w = unicodedata.normalize('NFD', w)
    w = ''.join(ch for ch in w if not unicodedata.combining(ch))
    w = w.replace('š', 's').replace('ṣ', 's').replace('ç', 's').replace('ś', 's')
    w = w.replace('ḫ', 'h').replace('x', 'h').replace('χ', 'h')
    w = w.replace('θ', 't').replace('φ', 'p').replace('ʔ', '').replace('ʕ', '')
    w = re.sub(r'[̄̆:ːˈˌ‿*\'ʼ’´`]', '', w)
    w = re.sub(r'[^a-z]', '', w)
    return w

VOW = set('aeiou')
def syllabify(w):
    """строка звуков -> список слогов (по гласным ядрам); None если нет гласных."""
    if not w or not any(c in VOW for c in w): return None
    syls = []
    cur = ''
    for ch in w:
        cur += ch
        if ch in VOW:
            syls.append(cur); cur = ''
    # конечные согласные отбрасываются (проекция LB)
    return syls

def profile(words):
    ps = [syllabify(normalize(w)) for w in words]
    ps = [p for p in ps if p and len(p) >= 2]
    n = len(ps)
    if n < 30: return None
    length = sum(len(p) for p in ps) / n
    ini_v = sum(1 for p in ps if p[0][0] in VOW and len(p[0]) == 1) / n
    hiat = sum(1 for p in ps if any(len(s) == 1 and s in VOW for s in p[1:])) / n
    fin = Counter(p[-1][-1] for p in ps)
    tot = sum(fin.values())
    fin_d = {v: fin.get(v, 0) / tot for v in 'aeiou'}
    red = sum(1 for p in ps if any(p[i] == p[i + 1] for i in range(len(p) - 1))) / n
    return {'n': n, 'len': length, 'iniV': ini_v, 'hiat': hiat, 'red': red,
            'fin': fin_d, 'words': ps}

# ---------------- языки
langs = {}
for path in glob.glob(os.path.join(SW, '*.html')):
    name = os.path.basename(path)[:-5]
    ws = parse_swadesh(path)
    pr = profile(ws)
    if pr: langs[name] = pr

# LA и LB в том же пространстве
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
    ok = all(re.fullmatch(r'[a-z][aeiou][23]?|[aeiou]|a[23]', s) for s in syls)
    if len(syls) >= 2 and ok:
        lb_words.add(''.join(s.rstrip('23') for s in syls))
langs['LA (лексикон)'] = profile(sorted(la_words))
langs['LB (греч. Кносс/Пилос)'] = profile(sorted(lb_words))

# ---------------- таблица метрик
print(f'{"язык":<24}{"n":>5}{"слог/сл":>8}{"V-нач":>7}{"зияние":>8}{"редупл":>8}'
      f'{"  фин: a":>8}{"e":>6}{"i":>6}{"o":>6}{"u":>6}')
for name, p in sorted(langs.items()):
    f = p['fin']
    print(f'{name:<24}{p["n"]:>5}{p["len"]:>8.2f}{p["iniV"]:>7.0%}{p["hiat"]:>8.0%}'
          f'{p["red"]:>8.1%}{f["a"]:>8.0%}{f["e"]:>6.0%}{f["i"]:>6.0%}'
          f'{f["o"]:>6.0%}{f["u"]:>6.0%}')

# ---------------- близость к LA: total variation по финалям + |Δ| по метрикам
la = langs['LA (лексикон)']
print('\n=== близость к LA (меньше = ближе) ===')
print(f'{"язык":<24}{"TV(финали)":>11}{"|Δзияние|":>10}{"|ΔV-нач|":>9}'
      f'{"|Δслог|":>8}{"сумма":>8}')
scores = []
for name, p in langs.items():
    if name.startswith('LA'): continue
    tv = 0.5 * sum(abs(la['fin'][v] - p['fin'][v]) for v in 'aeiou')
    dh = abs(la['hiat'] - p['hiat'])
    di = abs(la['iniV'] - p['iniV'])
    dl = abs(la['len'] - p['len']) / 3
    scores.append((tv + dh + di + dl, name, tv, dh, di, dl))
for s, name, tv, dh, di, dl in sorted(scores):
    print(f'{name:<24}{tv:>11.3f}{dh:>10.3f}{di:>9.3f}{dl * 3:>8.2f}{s:>8.3f}')

# бутстреп CI на суммарный балл для топ-3
print('\nбутстреп 95% CI суммарного балла (устойчивость ранжирования):')
top = [name for _, name, *_ in sorted(scores)[:4]]
for name in top:
    p = langs[name]
    vals = []
    for _ in range(B):
        samp = [p['words'][random.randrange(p['n'])] for _ in range(p['n'])]
        la_s = [la['words'][random.randrange(la['n'])] for _ in range(la['n'])]
        def prof2(ps):
            n = len(ps)
            fin = Counter(x[-1][-1] for x in ps)
            t = sum(fin.values())
            fd = {v: fin.get(v, 0) / t for v in 'aeiou'}
            hi = sum(1 for x in ps if any(len(s) == 1 and s in VOW for s in x[1:])) / n
            iv = sum(1 for x in ps if len(x[0]) == 1 and x[0] in VOW) / n
            ln = sum(len(x) for x in ps) / n
            return fd, hi, iv, ln
        fd1, h1, i1, l1 = prof2(la_s)
        fd2, h2, i2, l2 = prof2(samp)
        tv = 0.5 * sum(abs(fd1[v] - fd2[v]) for v in 'aeiou')
        vals.append(tv + abs(h1 - h2) + abs(i1 - i2) + abs(l1 - l2) / 3)
    vals.sort()
    print(f'   {name:<24} [{vals[int(0.025 * B)]:.3f}, {vals[int(0.975 * B)]:.3f}]')
