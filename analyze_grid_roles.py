# -*- coding: utf-8 -*-
"""Этап 27 (§DE): многофинальные основы §CK в ролях Хогана.

Вопрос-намёк на падеж: даёт ли Хоган РАЗНЫЕ роли разным финальным формам
одной основы (агенс в одной форме, не-агенс в другой)? Материал мал —
дескриптивно, честно. Вне ростера (гитигнорный кэш).
"""
import sys, json, pickle, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

txt = open('.hogan_cache.js', encoding='utf-8').read()
data = json.loads(txt[txt.find('['):txt.rfind(']') + 1])
SIGNSEQ = re.compile(r'^[A-Z][A-Z0-9*]{0,3}(-[A-Z0-9*]{1,4})*$')
word_roles = defaultdict(set)
for t in data:
    for w in t.get('words', []):
        for wd in ((w.get('transliteratedWord') or '').strip(),
                   (w.get('word') or '').strip()):
            if wd and SIGNSEQ.match(wd.upper()):
                word_roles[wd.upper()].add(
                    (w.get('description') or '?').strip() or '?')
                break

corpus = pickle.load(open('corpus.pkl', 'rb'))
lex = set()
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 3 \
           and v['complete'] and not (v['gap'] or v['trunc_l'] or v['trunc_r']):
            lex.add(tuple(v['signs']))

stems = defaultdict(set)
for w in lex:
    stems[w[:-1]].add(w)
multi = {s: ws for s, ws in stems.items() if len(ws) >= 2}

n_pairs = n_role_pairs = n_diff = 0
for s, ws in sorted(multi.items()):
    forms = []
    for w in sorted(ws):
        nm = '-'.join(w)
        rs = word_roles.get(nm)
        if rs:
            forms.append((nm, rs))
    if len(forms) >= 2:
        n_role_pairs += 1
        rsets = [rs for _, rs in forms]
        diff = any(r1 != r2 for i, r1 in enumerate(rsets)
                   for r2 in rsets[i + 1:])
        if diff:
            n_diff += 1
        print(f'   [{"-".join(s)}]: ' + '; '.join(
            f'{nm}={"/".join(sorted(rs))}' for nm, rs in forms) +
            ('   <-- РАЗНЫЕ роли' if diff else ''))
print(f'\nмногофинальных основ: {len(multi)}; с ролями у >=2 форм: '
      f'{n_role_pairs}; из них с разными ролями: {n_diff}')
print('''
Чтение: дескриптивно (разметка Хогана даёт роли не всем словам, и почти
все длинные слова у него агентивны — §DA); «разные роли у форм одной
основы» — лишь намёк для будущих тестов, не вывод.''')
