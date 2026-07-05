# -*- coding: utf-8 -*-
"""Этап 11.2 (§AX): «посадочная полоса» — шаблонный движок формулы возлияний.

Эталонные шаблоны слотов (все засвидетельствованные варианты, §K/§AE/§AW) +
автоматический матчер: на вход — список слов документа, на выход — разметка
слотов. Валидация: сопоставление разметки движка с эталонной таблицей слотов
этапа 2 (rows) по всем rel-документам; точность на уровне слов.
Шаблон сохраняется в formula_template.json — для текста скипетра.
"""
import sys, pickle, json, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

SLOT_PATTERNS = {
    1: [r'^(J?A-)?TA-I-\*301', ],                      # открытие
    3: [r'(^|-)SA-SA(-|$)', r'^(J?A-)?SA-SA'],          # теоним SA-SA-RA
    4: [r'^U-NA-(KA|RU)', r'^JA-SA-U-NA'],              # U-NA-KA-NA-SI…
    5: [r'^I-PI-NA'],                                   # I-PI-NA-MA/-MI-NA
    6: [r'^SI-RU(-|$)'],                                # SI-RU-TE
}

def slot_of(word):
    for slot, pats in SLOT_PATTERNS.items():
        for p in pats:
            if re.search(p, word):
                return slot
    return None

def assign(words):
    """список слов -> список (слово, слот); слот 2 = между 1 и 3/4; 0 = прочее."""
    anchors = [slot_of(w) for w in words]
    out = []
    # позиция первого якоря >=3
    late = next((i for i, s in enumerate(anchors) if s in (3, 4, 5, 6)), None)
    first1 = next((i for i, s in enumerate(anchors) if s == 1), None)
    for i, (w, s) in enumerate(zip(words, anchors)):
        if s is not None:
            out.append((w, s)); continue
        if late is not None and i < late and (first1 is None or i > first1):
            out.append((w, 2))
        elif late is None and first1 is not None and i > first1:
            out.append((w, 2))   # только открытие найдено: остальное — кандидаты
        else:
            out.append((w, 0))
    return out

if __name__ == '__main__':
    corpus = pickle.load(open('corpus.pkl', 'rb'))
    res = pickle.load(open('results.pkl', 'rb'))
    docsx = {d['id']: d for d in corpus}

    # эталон: rows этапа 2 (только rel)
    gold = {}
    for doc, typ, lanes in res['rows']:
        if doc in docsx and docsx[doc]['typ'] != 'rel': continue
        m = {}
        for lane, ws in lanes.items():
            for w in ws:
                w2 = w.replace('…', '').strip('-')
                if w2: m[w2] = lane
        if m: gold[doc] = m

    print(f'валидация движка против эталона этапа 2: {len(gold)} документов')
    tot = agree = 0
    confusion = defaultdict(int)
    for doc, gmap in sorted(gold.items()):
        d = docsx[doc]
        words = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
        pred = dict(assign(words))
        for w, lane in gmap.items():
            if w not in pred: continue
            tot += 1
            p = pred[w]
            ok = (p == lane) or (lane == 0 and p == 0)
            agree += ok
            if not ok: confusion[(lane, p)] += 1
    print(f'слов сверено: {tot}; совпадений разметки: {agree} '
          f'({agree / tot:.0%})')
    print('расхождения (эталон -> движок):',
          dict(sorted(confusion.items(), key=lambda kv: -kv[1])[:8]))

    json.dump({str(k): v for k, v in SLOT_PATTERNS.items()},
              open('formula_template.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('шаблон сохранён: formula_template.json')

    # демонстрация на «сыром» документе не из эталона
    for demo in ('SYZa2', 'VRYZa1', 'IOZa7'):
        if demo in docsx:
            d = docsx[demo]
            words = [v['norm'] for k, v in d['toks'] if k == 'WORD' and v['syllabic']]
            print(f'\nдемо {demo}: ' + '; '.join(f'{w}→{s}' for w, s in assign(words)))
