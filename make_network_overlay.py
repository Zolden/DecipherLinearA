# -*- coding: utf-8 -*-
"""Этап 27 (§DC): machine-readable оверлей наших слоёв для сетевого графа
Хогана (lineara.xyz/network/) — предложение сотрудничества к issue.

Выход: network_overlay.json — по документам (эпоха из dating.tsv, жанр)
и по словам (якоря §BN, почти-омографы §BX, зерновой класс §CP/§CT/§CX,
операторы §BO/§BR с позиционными ролями, открытие формулы). Все теги со
ссылками на секции отчёта и p-значениями. Детерминированный вывод
(sort_keys, без дат) — файл коммитится и попадает в публичное зеркало.
"""
import sys, json, pickle

sys.stdout.reconfigure(encoding='utf-8')

dating = {}
for line in open('dating.tsv', encoding='utf-8'):
    if not line.startswith('doc\t'):
        p = line.rstrip('\n').split('\t')
        if p[3] and p[3] != 'CONFLICT':
            dating[p[0]] = p[3]

corpus = pickle.load(open('corpus.pkl', 'rb'))
docs = {}
for d in corpus:
    rel = any(z in d['id'] for z in ('Za', 'Zb', 'Zc', 'Zd', 'Ze', 'Zf', 'Zg'))
    entry = {'site': d['site'], 'genre': 'religious' if rel else 'administrative'}
    if d['id'] in dating:
        entry['epoch'] = dating[d['id']]
    docs[d['id']] = entry

WORDS = {
    'PA-I-TO': ['anchor:toponym (exact LB pa-i-to; report §H/§BN)'],
    'SE-TO-I-JA': ['anchor:toponym (LB se-to-i-ja/-jo; §BN/§BX)'],
    'SU-KI-RI-TA': ['anchor:toponym (LB su-ki-ri-ta/-to; §BN/§BX)'],
    'DA-I-PI-TA': ['anchor:name-candidate (LB record-slot confirmed; §BN/§BT p=0.0004 family)'],
    'I-TA-JA': ['anchor:name-candidate (slot-confirmed; §BN/§BT)'],
    'KI-DA-RO': ['anchor:name-candidate (slot-confirmed; §BN/§BT)'],
    'PA-RA-NE': ['anchor:name-candidate (slot-confirmed; §BN/§BT)'],
    'TA-NA-TI': ['anchor:name-candidate (slot-confirmed; §BN/§BT)'],
    'I-JA-TE': ['anchor:name-candidate (slot-confirmed; §BN/§BT)'],
    'KU-RO': ['operator:total, closing block (39% final + 33% penultimate; §BO p_fam=0.008, §BR p_fam=0.028)'],
    'PO-TO-KU-RO': ['operator:grand total (§BC)'],
    'KI-RO': ['operator:deficit, non-positional line annotation (§BO/§BR)'],
    'TE': ['operator:second-position tag (54% at position 2; §BR p_fam=0.0012)'],
    'SA-RA2': ['operator:second-position account term (56% at position 2, never first/last; §BR p_fam=0.0029)'],
    'A-DU': ['operator:header, document-initial (67%; §BO p_fam=0.005)'],
    'I-DA': ['operator:cultic counterpart of A-DU (§AK/§BC)'],
    'SI-RU-TE': ['operator:libation-formula finalizer (100% religious; §BC)'],
    'A-TA-I-*301-WA-JA': ['formula:libation opening, document-initial 100% (§BO p_fam=0.0001)'],
    'KU-NI-SU': ['grain-class:candidate ~ Akk. kunāšu (pre-declared test: GRA 3/5, p=0.015; metrology 0% duodecimal; §CP/§CT)'],
    'KI-RI-TA2': ['grain-class:candidate ~ krithē-type (GRA 2/2, p=0.0175; §CP/§CT)'],
    'KI-RE-TA-NA': ['grain-class:candidate (GRA 2/3, p=0.048; §CP/§CT)'],
    'KI-RE-TA2': ['grain-class:candidate (family of KI-RI-TA2; §CP/§CU)'],
    'DI-DE-RU': ['grain-class:list entry (HT86a/95; also §BZ adaptation pair di-de-ro)'],
    'QA-RA2-WA': ['grain-class:list entry (HT86a; §BZ pair qa-ra2-wo)'],
    'SA-RU': ['grain-class:list entry (GRA 3/6, p=0.027, §CX; overlapping documents caveat)'],
    'DA-ME': ['grain-class:list entry (GRA 3/4, p=0.0064, §CX; overlapping documents caveat)'],
    'A-KA-RU': ['grain-class:list header (HT86; GRA 2/3, p=0.041, §CX)'],
    'A-RA-NA-RE': ['near-homograph: LB a-ra-na-ro (§BX/§BZ)'],
    'KA-U-DE-TA': ['near-homograph: LB ka-u-ti-ta (§BX); header before TE (HT13, §BW)'],
    'PI-TA-KE-SI': ['near-homograph: LB pi-ta-ke-u (§BX)'],
    'QA-TI-JU': ['near-homograph: LB qa-ti-ja (§BZ list)'],
    'JA-SA-SA-RA-ME': ['formula:slot-3+ core (SA-SA-RA paradigm, 10 forms; §AW)'],
    'A-DI-KI-TE-TE': ['formula:slot-2 geo-word, Petsofas cluster (site-specific p=0.012, §K; cf. Valério hypothesis)'],
    'DU-PU2-RE': ['formula:productive second element of slot-2 (§X; cf. Valério hypothesis)'],
}

overlay = {
    'meta': {
        'source': 'DecipherLinearA — reproducible statistical framework',
        'repo': 'https://github.com/Zolden/DecipherLinearA',
        'doi_all_versions': '10.5281/zenodo.21262274',
        'version': 'v1.3',
        'license': 'MIT (code); tags derive from open data credited in DATA_SOURCES.md',
        'note': 'Tags are statistical class labels with report sections and exploratory p-values; none is a translation.',
    },
    'documents': docs,
    'words': WORDS,
}
with open('network_overlay.json', 'w', encoding='utf-8') as f:
    json.dump(overlay, f, ensure_ascii=False, sort_keys=True, indent=1)
print(f'network_overlay.json: документов {len(docs)}, слов {len(WORDS)}')
