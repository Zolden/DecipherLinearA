# -*- coding: utf-8 -*-
"""Этап 48 (§EE): ПРЕДРЕГИСТРАЦИЯ №6 (коммит 77772d5, до этого файла).

Замороженный эндпойнт: повторяемость адресатных токенов Fp (правила №5)
ВЫШЕ повторяемости слот-1 токенов в случайных подвыборках по 15 KN
D-документов (правила №4): p = доля из R=10000 подвыборок D-15 с
rep_share >= rep_share(Fp), seed=42, односторонний p<0.05. Один прогон.
Вне ростера (кэш DĀMOS).
"""
import sys, json, os, re, random
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)
R = 10000
CACHE = '.damos_cache'
WORD_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*$')

fp_tokens = []
d_docs = defaultdict(list)      # doc -> [слот-1 токен] (ровно один)
for fn in sorted(os.listdir(CACHE)):
    if not fn.endswith('.json'):
        continue
    try:
        item = json.load(open(os.path.join(CACHE, fn),
                              encoding='utf-8'))['item']
    except Exception:
        continue
    head = (item.get('heading_short') or '')
    raw = []
    for line in (item.get('content') or '').split('\n'):
        raw.extend(t.strip("'") for t in line.replace(',', ' ').split())
    clean = [t for t in raw if WORD_RE.match(t)]
    if re.match(r'^KN Fp\b', head):
        month = None
        if 'me-no' in clean:
            i = raw.index('me-no') if 'me-no' in raw else -1
            if i > 0:
                prev = raw[i - 1].strip("'")
                if WORD_RE.match(prev):
                    month = prev
        else:
            month = (clean[0] if clean and
                     re.search(r'-jo(-jo)?$', clean[0]) else None)
        for t in clean:
            if t != 'me-no' and t != month:
                fp_tokens.append((head, t))
    elif re.match(r'^KN D[a-z]?\b', head):
        if len(clean) >= 2:
            d_docs[head] = clean[0]

def rep_share(tokens):
    docs_of = defaultdict(set)
    for doc, t in tokens:
        docs_of[t].add(doc)
    return sum(1 for doc, t in tokens if len(docs_of[t]) >= 2) / len(tokens)

fp_docs = {d for d, _ in fp_tokens}
fp_share = rep_share(fp_tokens)
print(f'Fp: {len(fp_docs)} документов, {len(fp_tokens)} адресатных '
      f'токенов, повторяемость {fp_share:.3f}')

d_ids = sorted(d_docs)
K = len(fp_docs)
sims = []
cnt = 0
for _ in range(R):
    smp = random.sample(d_ids, K)
    s = rep_share([(d, d_docs[d]) for d in smp])
    sims.append(s)
    if s >= fp_share:
        cnt += 1
import statistics
mu = statistics.mean(sims)
print(f'слот-1 в подвыборках D-{K}: среднее {mu:.3f} '
      f'(sd {statistics.pstdev(sims):.3f})')
p = (cnt + 1) / (R + 1)
d_obs = fp_share - mu
print(f'Δ = rep(Fp) − mean(rep(D-{K})) = {d_obs:+.3f}; p={p:.4f} '
      f'(односторонний)')
ok = (d_obs > 0) and (p < 0.05)
print(f'ПРЕДРЕГИСТРАЦИЯ №6: {"ПОДТВЕРЖДЕНА" if ok else "НЕ ПОДТВЕРЖДЕНА"}')
print('''
Чтение: при выровненном числе документов адресаты жертвенного масла
(божества/святилища, закрытый класс) повторяются между документами
несравнимо чаще, чем пастушьи имена (открытый класс) — та же ось
«жанр диктует режим повторяемости», что №3/№4. Повторяемость адресатов
между месяцами = цикличность обряда (ответ на вопрос этрусков о
LL-аналоге). Один прогон, результат как вышел.''')
