# -*- coding: utf-8 -*-
"""Вежливый fetch корпуса DĀMOS (damos.hf.uio.no) в .damos_cache/ (gitignore).

Публичные JSON-эндпоинты /ajaxitem/N/ (robots-ограничений нет; параллельно
авторам отправлен запрос о bulk-доступе — см. contact_draft.md). Задержка
0.35 с между запросами, понятный User-Agent, резюм по уже скачанным.
Запуск: .venv/Scripts/python.exe tools/fetch_damos.py [start] [end]
"""
import json
import os
import sys
import time
import urllib.request

BASE = 'https://damos.hf.uio.no/ajaxitem/{}/'
OUT = '.damos_cache'
UA = ('DecipherLinearA-research/1.4 (+https://github.com/Zolden/'
      'DecipherLinearA; open statistical project; contact via repo issues)')

start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
end = int(sys.argv[2]) if len(sys.argv) > 2 else 5899
os.makedirs(OUT, exist_ok=True)

ok = err = skip = 0
for i in range(start, end + 1):
    path = os.path.join(OUT, f'{i:05d}.json')
    if os.path.exists(path):
        skip += 1
        continue
    req = urllib.request.Request(BASE.format(i), headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        json.loads(data)                      # валидация
        tmp = path + '.tmp'
        with open(tmp, 'wb') as f:
            f.write(data)
        os.replace(tmp, path)
        ok += 1
    except Exception as e:                    # 500 на несуществующих id и пр.
        err += 1
        with open(os.path.join(OUT, 'errors.log'), 'a', encoding='utf-8') as f:
            f.write(f'{i}\t{e}\n')
    if (ok + err) % 200 == 0 and (ok + err):
        print(f'прогресс: ok={ok} err={err} skip={skip} (id={i})', flush=True)
    time.sleep(0.35)
print(f'ИТОГО: ok={ok} err={err} skip={skip}')
