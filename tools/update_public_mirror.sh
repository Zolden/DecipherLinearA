#!/bin/bash
# Обновление ОПУБЛИКОВАННОГО зеркала: синк отслеживаемых файлов (минус
# исключения) в ../DecipherLinearA-public поверх существующей истории +
# коммит. После запуска: cd ../DecipherLinearA-public && git push
set -e
cd "$(dirname "$0")/.."
DEST=../DecipherLinearA-public
[ -d "$DEST/.git" ] || { echo "нет $DEST/.git — сначала make_public_mirror.sh"; exit 1; }
git ls-files | while read -r f; do
  case "$f" in
    corpus_raw.json|imagemap.json|commentary.tar|contact_draft.md|fractions_part.log|.lbxyz_cache.js|INPUT_FROM_SOL.md)
      continue;;
  esac
  mkdir -p "$DEST/$(dirname "$f")"
  cp "$f" "$DEST/$f"
done
cd "$DEST"
git add -A
MSG="${1:-Update from research repo}"
git -c user.name="Zolden" -c user.email="sc2zolden@gmail.com" commit -q \
  -m "$MSG" \
  || echo "нет изменений"
echo "готово; для публикации: cd $DEST && git push"
git log --oneline | head -3
