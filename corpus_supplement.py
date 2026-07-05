# -*- coding: utf-8 -*-
"""Этап 8.2 (§AA): механизм пополнения корпуса БЕЗ разморозки corpus.pkl.

Замороженный corpus.pkl никогда не редактируется. Новые надписи добавляются в
corpus_supplement.json (тот же формат документа, что в corpus.pkl: id, site,
site_full, typ, support, scribe, context, is_tablet, toks=[["WORD",{...}]...]),
со служебными полями _status ('pending' = транслитерация ещё не издана/не
введена; 'ready' = можно использовать) и _source (библиография).

Использование в анализах (опционально):
    from corpus_supplement import load_corpus
    corpus = load_corpus(with_supplement=True)   # только _status == 'ready'
Все прежние скрипты по умолчанию работают со старым корпусом (воспроизводимость
отчётов v2 не нарушается).
"""
import json, os, pickle

BASE = os.path.dirname(os.path.abspath(__file__))

def load_corpus(with_supplement=False, include_pending=False):
    corpus = pickle.load(open(os.path.join(BASE, 'corpus.pkl'), 'rb'))
    if not with_supplement:
        return corpus
    path = os.path.join(BASE, 'corpus_supplement.json')
    if not os.path.exists(path):
        return corpus
    supp = json.load(open(path, encoding='utf-8'))
    ids = {d['id'] for d in corpus}
    added = []
    for doc in supp.get('documents', []):
        if doc.get('_status') != 'ready' and not include_pending:
            continue
        if doc['id'] in ids:
            raise ValueError(f'дубликат id в supplement: {doc["id"]}')
        d = {k: v for k, v in doc.items() if not k.startswith('_')}
        # минимальная валидация схемы
        for key in ('id', 'site', 'typ', 'toks'):
            assert key in d, f'{doc["id"]}: нет поля {key}'
        added.append(d)
    return corpus + added

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    c0 = load_corpus()
    c1 = load_corpus(with_supplement=True)
    supp = json.load(open(os.path.join(BASE, 'corpus_supplement.json'),
                          encoding='utf-8'))
    print(f'базовый корпус: {len(c0)}; с дополнением: {len(c1)}')
    for doc in supp.get('documents', []):
        print(f'   {doc["id"]}: _status={doc.get("_status")}, '
              f'источник: {doc.get("_source", "?")[:80]}')
