#!/bin/bash
# Fetch third-party source files from the pinned upstream commit.
# We do not redistribute these files; this script obtains them from origin.
set -e
cd "$(dirname "$0")/.."
PIN=eb9afc70104aed41dc740ebd05bf7e677fb48ffe
TMP=.fetch_lineara
rm -rf "$TMP"
git clone --filter=blob:none --no-checkout https://github.com/mwenge/lineara.xyz.git "$TMP"
git -C "$TMP" checkout "$PIN" --quiet -- . 2>/dev/null || true
# 1) commentary pages (Younger's texts as scraped by lineara.xyz) -> tar
git -C "$TMP" -c core.protectNTFS=false archive -o ../commentary.tar "$PIN:commentary"
mv "$TMP/../commentary.tar" ./commentary.tar 2>/dev/null || true
# 2) raw inscription data -> corpus_raw.json (strip JS prefix/suffix)
git -C "$TMP" -c core.protectNTFS=false show "$PIN:LinearAInscriptions.js" > "$TMP/lai.js"
python - <<'PY'
import json, re
txt = open('.fetch_lineara/lai.js', encoding='utf-8').read()
i = txt.find('['); j = txt.rfind(']')
arr = json.loads(txt[i:j+1])
data = {k: v for k, v in (arr[n:n+2] for n in range(0, len(arr), 1) if False)}
# массив вида [ [id, {...}], ... ] или Map-подобный: приводим к dict
if isinstance(arr[0], list) and len(arr[0]) == 2:
    data = {a: b for a, b in arr}
else:
    raise SystemExit('unexpected format; inspect lai.js')
json.dump(data, open('corpus_raw.json', 'w', encoding='utf-8'),
          ensure_ascii=False)
print('corpus_raw.json:', len(data))
PY
# 3) imagemap
git -C "$TMP" -c core.protectNTFS=false show "$PIN:items_image_map.js" > "$TMP/imap.js"
python - <<'PY'
import json
txt = open('.fetch_lineara/imap.js', encoding='utf-8').read()
i = txt.find('['); j = txt.rfind(']')
arr = json.loads(txt[i:j+1])
data = {a: b for a, b in arr} if isinstance(arr[0], list) else arr
json.dump(data, open('imagemap.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('imagemap.json ok')
PY
rm -rf "$TMP"
echo "fetched: commentary.tar, corpus_raw.json, imagemap.json (pinned $PIN)"
