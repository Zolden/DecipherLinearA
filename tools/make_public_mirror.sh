#!/bin/bash
# Сборка публичного зеркала: свежий репозиторий с одним коммитом,
# без файлов третьих лиц (их добывает tools/fetch_sources.sh) и без
# внутренних черновиков переписки.
set -e
cd "$(dirname "$0")/.."
DEST=../DecipherLinearA-public
rm -rf "$DEST"
mkdir -p "$DEST"
git ls-files | while read -r f; do
  case "$f" in
    corpus_raw.json|imagemap.json|commentary.tar|contact_draft.md|fractions_part.log)
      continue;;
  esac
  mkdir -p "$DEST/$(dirname "$f")"
  cp "$f" "$DEST/$f"
done
cd "$DEST"
git init -q
git add -A
git -c user.name="Zolden" -c user.email="sc2zolden@gmail.com" commit -q \
  -m "Linear A: reproducible statistical framework (public mirror)

Frozen validated corpus database, permutation-controlled analyses (report
sections 0-BF), calibrated morphology, onomastic layer, formula slot
engine, full seeded reproducibility (PYTHONHASHSEED=0; tools/stress_run.sh).
Third-party raw files are not redistributed: see DATA_SOURCES.md and
tools/fetch_sources.sh."
echo "public mirror ready at $DEST"
git log --oneline
ls | head -20
