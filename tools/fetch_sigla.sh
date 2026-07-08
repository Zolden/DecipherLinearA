#!/bin/bash
# Fetch the SigLA public data file (sigla.phis.me, Salgarella & Castellan)
# into the gitignored cache .sigla_cache.js (used by parse_sigla.py).
# We do not redistribute this file; see DATA_SOURCES.md.
set -e
cd "$(dirname "$0")/.."
curl -sL --fail https://sigla.phis.me/database.js -o .sigla_cache.js
echo "expected sha256 (as of 2026-07-08): cc624f148fd84c94fd2910b0adf92ecace25f52f9175664122bdf8384a8f1b9d"
sha256sum .sigla_cache.js
